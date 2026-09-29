from __future__ import annotations

from datetime import datetime


def build_negotiation_message(
    *,
    user_a: str,
    user_b: str,
    decision_kind: str,
    start: datetime | None,
    end: datetime | None,
    explanation: str,
) -> str:
    """
    MVP stub.

    Replace this with IBM Watsonx Orchestrate / watsonx.ai call if desired.
    """
    if decision_kind == "perfect_overlap" and start and end:
        return (
            f"Hi {user_a} and {user_b} - I found a time that works for both of you: "
            f"{start:%a %b %d, %H:%M}-{end:%H:%M}. I've booked it."
        )
    if decision_kind == "compromise" and start and end:
        return (
            f"Hi {user_a} and {user_b} - I couldn't find a perfect overlap, so I'm suggesting a compromise: "
            f"{start:%a %b %d, %H:%M}-{end:%H:%M}. {explanation}"
        )
    return f"Hi {user_a} and {user_b} - I couldn't find a workable slot. {explanation}"

