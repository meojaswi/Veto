import uuid

from sqlalchemy import select

from app.db.models import Return, ReturnDecision
from app.db.session import SessionLocal
from app.worker.pipeline.graph import return_graph


async def process_return(ctx, return_id: str):
    return_uuid = uuid.UUID(return_id)

    async with SessionLocal() as db:
        result = await db.execute(
            select(Return).where(Return.id == return_uuid)
        )
        item = result.scalar_one_or_none()

        if item is None:
            return {"error": "Return not found"}

        # Avoid processing a completed return again.
        if item.status == "needs_review":
            return {
                "return_id": return_id,
                "status": item.status,
                "skipped": True,
            }

        item.status = "processing"
        await db.commit()

        try:
            state = await return_graph.ainvoke({
                "return_id": str(item.id),
                "order_id": item.order_id,
                "reason": item.reason,
                "amount_cents": item.amount_cents,
            })

            record = await db.get(
                ReturnDecision,
                return_uuid,
            )

            if record is None:
                record = ReturnDecision(return_id=return_uuid)
                db.add(record)

            record.decision = state["decision"]
            record.rationale = state["decision_reason"]
            record.governance_action = state["governance_action"]
            record.intake_errors = state.get("intake_errors", [])

            item.status = "needs_review"

            await db.commit()

            return {
                "return_id": return_id,
                "status": item.status,
            }

        except Exception:
            await db.rollback()
            raise