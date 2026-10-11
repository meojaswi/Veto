from typing import Literal, TypedDict


class ReturnState(TypedDict, total=False):
  #total=False means at the beginning of the workflow all the fields are not important to be present
    return_id: str
    order_id: str
    reason: str
    amount_cents: int

    intake_valid: bool
    intake_errors: list[str]

    decision: Literal[
        "eligible",
        "ineligible",
        "needs_review",
    ]
    decision_reason: str

    governance_action: Literal["human_review"]