import gzip
from contextvars import ContextVar
from io import BytesIO

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import sessionmaker

import sanic
from sanic.response import json

from models import Base, Map, MapMeta, MapTile, MapTileType

app = sanic.Sanic("bluemap-server")

bind = create_async_engine(
    f"mysql+asyncmy://bluemap:iDislikeLife@server.ultras-playroom.xyz/bluemap",
    echo=True,
    pool_pre_ping=True,
)

# https://stackoverflow.com/a/70390426/4784039
is_numeric = lambda x: x.replace('.', '', 1).replace('-', '', 1).isdigit()

_base_model_session_ctx = ContextVar("session")

@app.middleware("request")
async def inject_session(request):
    request.ctx.session = sessionmaker(bind, AsyncSession, expire_on_commit=False)()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()

@app.get("/maps/<world:str>/.rstate")
async def get_render_state(request: sanic.Request, world: str):
    session: AsyncSession = request.ctx.session

    async with session.begin():
        getMapStmt = select(Map).where(Map.map_id == world)
        getMapRes: Result = await session.execute(getMapStmt)
        getMapRow = getMapRes.first()

        map: Map = getMapRow["Map"]

        if map is None:
            return json({})

        meta: MapMeta = await session.get(MapMeta, {
            "map": map.id,
            "key": "render_state"
        })

        if meta is None:
            return json({})

    response = sanic.HTTPResponse()
    buffer = BytesIO()
    gz = gzip.GzipFile(mode="wb", fileobj=buffer)
    gz.write(meta.value)
    gz.close()
    response.body = buffer.getvalue()
    response.headers["content-type"] = "application/octet-stream"
    response.headers["content-encoding"] = "gzip"
    response.headers["vary"] = "Accept-Encoding"
    
    return response

@app.get("/maps/<world:str>/<reqmeta:ext=json>")
async def get_meta(request: sanic.Request, world: str, reqmeta: str, ext: str):

    session: AsyncSession = request.ctx.session

    async with session.begin():
        getMapStmt = select(Map).where(Map.map_id == world)
        getMapRes: Result = await session.execute(getMapStmt)
        getMapRow = getMapRes.first()

        map: Map = getMapRow["Map"]

        if map is None:
            return json({})

        meta: MapMeta = await session.get(MapMeta, {
            "map": map.id,
            "key": reqmeta
        })

        if meta is None:
            return json({})

    response = sanic.HTTPResponse()
    buffer = BytesIO()
    gz = gzip.GzipFile(mode="wb", fileobj=buffer)
    gz.write(meta.value)
    gz.close()
    response.body = buffer.getvalue()
    response.headers["content-type"] = "application/json"
    response.headers["content-encoding"] = "gzip"
    response.headers["vary"] = "Accept-Encoding"
    
    return response

@app.get("/maps/<world:str>/<maptype:str>/<params:path>")
async def get_tile(request: sanic.Request, world: str, maptype: str, params: str):
    session: AsyncSession = request.ctx.session

    parsedparams = params.split("/")
    if len(parsedparams) == 0: return json({})
    if not parsedparams[len(parsedparams) - 1].endswith(".json"): return json({})

    parsedparams[len(parsedparams) - 1] = parsedparams[len(parsedparams) - 1][:-5]

    isX = False
    isZ = False

    x = ""
    z = ""
    for param in parsedparams:
        if param.startswith("x"):
            isX = True
            isZ = False
            param = param[1:]
        elif param.startswith("z"):
            isX = False
            isZ = True
            param = param[1:]
        if is_numeric(param):
            if isX:
                x += param
            elif isZ:
                z += param
        else:
            return json({"error": f"unknown coordinate fragment {param}"})


    async with session.begin():
        getMapStmt = select(Map).where(Map.map_id == world)
        getMapRes: Result = await session.execute(getMapStmt)
        getMapRow = getMapRes.first()

        map: Map = getMapRow["Map"]

        if map is None:
            return json({})

        getTypeStmt = select(MapTileType).where(MapTileType.type == maptype)
        getTypeRes: Result = await session.execute(getTypeStmt)
        getTypeRow = getTypeRes.first()
        
        maptiletype: MapTileType = getTypeRow["MapTileType"]

        if maptiletype is None:
            return json({})

        maptile: MapTile = await session.get(MapTile, {
            "map": map.id,
            "type": maptiletype.id,
            "x": int(x),
            "z": int(z),
        })

        if maptile is None:
            return json({})

        response = sanic.HTTPResponse()
        response.body = maptile.data
        response.headers["content-type"] = "application/json"
        response.headers["content-encoding"] = "gzip"
        response.headers["vary"] = "Accept-Encoding"
        
        return response


if __name__ == "__main__":
    app.run(fast=True, dev=True)