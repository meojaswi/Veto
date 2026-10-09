from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import returns
from app.db.models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:  # temporary: Alembic replaces this
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Veto", lifespan=lifespan)
app.include_router(returns.router)


@app.get("/health")
async def health():
    return {"ok": True}
