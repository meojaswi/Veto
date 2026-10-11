
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from app.api import returns
from app.config import settings
from app.db.models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a Redis connection pool for background jobs.
    app.state.queue = await create_pool(
        RedisSettings.from_dsn(settings.redis_url)
    )

    try:
        yield
    finally:
        # Close Redis connections and database engine on shutdown.
        await app.state.queue.aclose()
        await engine.dispose()


app = FastAPI(title="Veto", lifespan=lifespan)
app.include_router(returns.router)


@app.get("/health")
async def health():
    return {"ok": True}
