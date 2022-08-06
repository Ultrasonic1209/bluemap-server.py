import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from models import Base


async def async_main():
    engine = create_async_engine(
        f"mysql+asyncmy://bluemap:iDislikeLife@server.ultras-playroom.xyz/bluemap",
        echo=True,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

asyncio.run(async_main())