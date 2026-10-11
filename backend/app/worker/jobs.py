import uuid

from sqlalchemy import select

from app.db.models import OrderContext, Return, ReturnDecision
from app.db.session import SessionLocal
from app.worker.pipeline.graph import return_graph


async def process_return(ctx, return_id: str):
    return_uuid = uuid.UUID(return_id)

    async with SessionLocal() as db:
        # 1. Fetch the return request
        result = await db.execute(
            select(Return).where(Return.id == return_uuid)
        )
        item = result.scalar_one_or_none()

        if item is None:
            return {"error": "Return not found"}

        # 2. Fetch the associated order context
        result = await db.execute(
            select(OrderContext).where(
                OrderContext.id == item.order_context_id
            )
        )
        order_context = result.scalar_one_or_none()

        if order_context is None:
            raise ValueError(
                f"OrderContext not found for return {return_id}"
            )

        # 3. Avoid processing a completed review request again
        if item.status == "needs_review":
            return {
                "return_id": return_id,
                "status": item.status,
                "skipped": True,
            }

        # 4. Mark the return as processing
        item.status = "processing"
        await db.commit()

        try:
            # 5. Execute the LangGraph pipeline
            state = await return_graph.ainvoke(
                {
                    "return_id": str(item.id),
                    "order_id": order_context.order_id,
                    "reason": item.reason,
                    "amount_cents": item.amount_cents,
                }
            )

            # 6. Save the proposed decision
            record = await db.get(ReturnDecision, return_uuid)

            if record is None:
                record = ReturnDecision(return_id=return_uuid)
                db.add(record)

            record.decision = state["decision"]
            record.rationale = state["decision_reason"]
            record.governance_action = state["governance_action"]
            record.intake_errors = state.get("intake_errors", [])

            # 7. Route the request for human review
            item.status = "needs_review"

            await db.commit()

            return {
                "return_id": return_id,
                "status": item.status,
                "decision": record.decision,
                "governance_action": record.governance_action,
            }

        except Exception:

            await db.rollback()

            # Persist the failure status
            failed_return = await db.get(Return, return_uuid)

            if failed_return is not None:
                failed_return.status = "failed"
                await db.commit()

            # Let arq know the job failed
            raise