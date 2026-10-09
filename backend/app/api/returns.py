import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Return
from app.db.session import get_db
from app.schemas.returns import ReturnCreate, ReturnOut

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("", response_model=ReturnOut, status_code=201)
async def create_return(body: ReturnCreate, db: AsyncSession = Depends(get_db)):
    r = Return(user_id=settings.demo_user_id, **body.model_dump())
    db.add(r)
    await db.commit()
    return r


@router.get("/{return_id}", response_model=ReturnOut)
async def get_return(return_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    r = await db.get(Return, return_id)
    if not r:
        raise HTTPException(404, "Return not found")
    return r
