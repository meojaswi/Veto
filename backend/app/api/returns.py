
import uuid

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import OrderContext, Return
from app.db.session import get_db
from app.schemas.returns import ReturnCreate, ReturnOut

# Group all return-related endpoints under /returns.
router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("", response_model=ReturnOut, status_code=201)
async def create_return(
    body: ReturnCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Look up the existing order context instead of trusting
    # platform, brand, or delivery information from the request.
    result = await db.execute(
        select(OrderContext).where(
            OrderContext.order_id == body.order_id
        )
    )
    order_context = result.scalar_one_or_none()

    # A return can only be created for an order known to Veto.
    if order_context is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # Create the return using the trusted order-context reference.
    r = Return(
        user_id=settings.demo_user_id,
        order_context_id=order_context.id,
        reason=body.reason,
        amount_cents=body.amount_cents,
    )
    db.add(r)

    # Persist the return before enqueueing its background job.
    await db.commit()
    await db.refresh(r)

    try:
        # Get the Redis pool initialized during FastAPI startup.
        queue: ArqRedis = request.app.state.queue

        # Ask the worker to process this return asynchronously.
        await queue.enqueue_job("process_return", str(r.id))

    except Exception as exc:
        # The return is already committed even if enqueueing fails.
        raise HTTPException(
            status_code=503,
            detail=(
                "Return was saved, but processing could not be queued. "
                "Check the return before retrying."
            ),
        ) from exc

    # Return the newly saved record to the client.
    return r


@router.get("/{return_id}", response_model=ReturnOut)
async def get_return(
    return_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Fetch the return by its UUID primary key.
    r = await db.get(Return, return_id)

    # Return HTTP 404 if the requested return does not exist.
    if r is None:
        raise HTTPException(
            status_code=404,
            detail="Return not found",
        )

    return r
