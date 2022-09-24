"""
By Ultrasonic1209
I have no clue what I'm doing
"""

import gzip
from contextvars import ContextVar
from io import BytesIO
from typing import TypedDict

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import sessionmaker

import sanic, toml
from sanic.response import json

from models import Map, MapMeta, MapTile, Map

class ConfigSql(TypedDict):
    database_url: str

class ConfigServer(TypedDict):
    bind: str
    port: int
    access_log: bool
    threads: int
    forwarded_secret: str

class Config(TypedDict):
    sql: ConfigSql
    server: ConfigServer

app = sanic.Sanic("bluemap-server")

with open('config.toml', 'r') as f:
    extconfig: Config = toml.load(f)

dburl = extconfig["sql"]["database_url"]

serverbind = extconfig["server"]["bind"]
serverport = extconfig["server"]["port"]
accesslog = extconfig["server"]["access_log"]
threads = extconfig["server"]["threads"]
secret = extconfig["server"]["forwarded_secret"]

app.config.ACCESS_LOG = accesslog

if secret != "":
    app.config.FORWARDED_SECRET = secret

bind = create_async_engine(
    dburl,
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
    response.body = meta.value
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
    response.body = meta.value
    response.headers["content-type"] = "application/json"
    response.headers["content-encoding"] = "gzip"
    response.headers["vary"] = "Accept-Encoding"
    
    return response

@app.get("/maps/<world:str>/tiles/<lod:int>/<params:path>")
async def get_tile(request: sanic.Request, world: str, lod: int, params: str):
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

        maptile: MapTile = await session.get(MapTile, {
            "map": map.id,
            "lod": lod,
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
    if threads <= 0:
        app.run(host=serverbind, port=serverport, fast=True)
    else:
        app.run(host=serverbind, port=serverport, workers=threads)