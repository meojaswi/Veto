import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ReturnCreate(BaseModel):
    order_id: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=2000)
    amount_cents: int = Field(gt=0)

    # Demo-only order context for policy evaluation.
    # In production, these fields must come from a trusted order source.
    platform: str = Field(min_length=1, max_length=100)
    brand: str = Field(min_length=1, max_length=150)
    product_category: str = Field(min_length=1, max_length=100)
    delivered_at: date
    requested_at: date


class ReturnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    order_id: str
    reason: str
    amount_cents: int
    status: str
    created_at: datetime
