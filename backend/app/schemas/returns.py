import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReturnCreate(BaseModel):
    order_id: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=2000)
    amount_cents: int = Field(gt=0)


class ReturnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: str
    order_id: str
    reason: str
    amount_cents: int
    status: str
    created_at: datetime
