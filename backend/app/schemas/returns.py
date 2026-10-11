
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReturnCreate(BaseModel):
    # Identifies the order whose return is being requested.
    order_id: str = Field(min_length=1, max_length=64)

    # Customer-provided reason for requesting the return.
    reason: str = Field(min_length=1, max_length=2000)

    # Return amount in the smallest currency unit (e.g. paise).
    amount_cents: int = Field(gt=0)


class ReturnOut(BaseModel):
    # Allows Pydantic to serialize SQLAlchemy model instances.
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    order_context_id: uuid.UUID
    reason: str
    amount_cents: int
    status: str
    created_at: datetime
