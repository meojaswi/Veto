from langgraph.graph import END, START, StateGraph

from app.worker.pipeline.nodes import (
    intake_node,
    decision_node,
    governance_gate_node,
)
from app.worker.pipeline.state import ReturnState


def after_intake(state: ReturnState) -> str:
    if not state["intake_valid"]:
        return "governance_gate"

    return "decision"


builder = StateGraph(ReturnState)

builder.add_node("intake", intake_node)
builder.add_node("decision", decision_node)
builder.add_node("governance_gate", governance_gate_node)

builder.add_edge(START, "intake")

builder.add_conditional_edges(
    "intake",
    after_intake,
    {
        "decision": "decision",
        "governance_gate": "governance_gate",
    },
)

builder.add_edge("decision", "governance_gate")
builder.add_edge("governance_gate", END)

return_graph = builder.compile()