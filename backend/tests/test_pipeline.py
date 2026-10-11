
import pytest

from app.worker.pipeline.graph import return_graph


@pytest.mark.asyncio
async def test_valid_return_requires_human_review():
    state = await return_graph.ainvoke({
        "return_id": "test-return-001",
        "order_id": "ORDER-1001",
        "reason": "Damaged product",
        "amount_cents": 150000,
    })

    assert state["decision"] == "needs_review"
    assert state["governance_action"] == "human_review"
    assert state["decision_reason"]
    assert state["intake_valid"] is True

#Invalid input tests#


@pytest.mark.asyncio
async def test_missing_order_id_requires_human_review():
    state = await return_graph.ainvoke({
        "return_id": "test-return-002",
        "order_id": "",
        "reason": "Damaged product",
        "amount_cents": 150000,
    })

    print("PIPELINE STATE:", state)

    assert state["intake_valid"] is False
    assert state["intake_errors"]
    assert state["governance_action"] == "human_review"



@pytest.mark.asyncio
async def test_valid_return_does_not_auto_approve():
    state = await return_graph.ainvoke({
        "return_id": "test-return-003",
        "order_id": "ORDER-1001",
        "reason": "Wrong item received",
        "amount_cents": 50000,
    })

    assert state["decision"] == "needs_review"
    assert "verified" in state["decision_reason"].lower()
    assert state["governance_action"] == "human_review"

