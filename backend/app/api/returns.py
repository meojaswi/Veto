
import uuid

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Return
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
    # Create a new Return object using the demo user and validated request data.
    r = Return(
        user_id=settings.demo_user_id,
        **body.model_dump(),
    )

    # Stage the new return in the current database session.
    db.add(r)

    # Persist the return in PostgreSQL before enqueueing the background job.
    # This ensures the worker can find the return when it starts processing.
    await db.commit()

    # Refresh the object with the latest database values, including its generated ID.
    await db.refresh(r)

    try:
        # Get the Redis queue pool initialized during FastAPI startup.
        queue: ArqRedis = request.app.state.queue

        # Enqueue a background job; the arq worker will call process_return
        # with this return ID and execute the LangGraph workflow.
        await queue.enqueue_job("process_return", str(r.id))

    except Exception as exc:
        # The database commit has already succeeded, so the return still exists.
        # Return 503 to indicate that background processing could not be queued.
        # Check the saved return before retrying to avoid creating duplicates.
        raise HTTPException(
            status_code=503,
            detail=(
                "Return was saved, but processing could not be queued. "
                "Check the return before retrying."
            ),
        ) from exc

    # Return the saved record to the client with HTTP 201 Created.
    return r


@router.get("/{return_id}", response_model=ReturnOut)
async def get_return(
    return_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Fetch the return by its UUID primary key.
    r = await db.get(Return, return_id)

    # Return HTTP 404 if no record exists for the requested ID.
    if not r:
        raise HTTPException(404, "Return not found")

    # Return the database record; FastAPI serializes it using ReturnOut.
    return r
