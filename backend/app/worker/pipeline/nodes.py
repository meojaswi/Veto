from app.worker.pipeline.state import ReturnState


def intake_node(state: ReturnState) -> dict:
    errors = []

    if not state.get("order_id", "").strip():
        errors.append("Missing order ID")

    if not state.get("reason", "").strip():
        errors.append("Missing return reason")

    if state.get("amount_cents", 0) <= 0:
        errors.append("Invalid return amount")

    return {
        "intake_valid": not errors,
        "intake_errors": errors,
    }


def decision_node(state: ReturnState) -> dict:
    if not state["intake_valid"]:
        return {
            "decision": "needs_review",
            "decision_reason": (
                "Intake validation failed."
            ),
        }

    return {
        "decision": "needs_review",
        "decision_reason": (
            "Order and return policy must be verified before deciding eligibility."
        ),
    }


def governance_gate_node(state: ReturnState) -> dict:
    return {
        "governance_action": "human_review",
    }