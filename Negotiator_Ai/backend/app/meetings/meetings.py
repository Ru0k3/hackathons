from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.storage.memory_db import USERS, MEETINGS
from app.ai.negotiator import negotiate
from app.orchestrator.orchestrator_client import OrchestratorClient
import uuid

router = APIRouter()
orchestrator = OrchestratorClient()


class MeetingRequest(BaseModel):
    user_a: str
    user_b: str
    duration: int


@router.post("/schedule")
def schedule_meeting(req: MeetingRequest):
    if req.user_a not in USERS or req.user_b not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    context = {
        "user_a": USERS[req.user_a],
        "user_b": USERS[req.user_b],
        "duration": req.duration
    }

    decision = orchestrator.decide_meeting(context)

    if decision.get("decision") == "CONFIRMED":
        result = decision["result"]
    else:
        result = negotiate(
            USERS[req.user_a],
            USERS[req.user_b],
            req.duration
        )

    if result["status"] == "NO_OVERLAP":
        return {"status": "NO_OVERLAP"}

    meeting_id = str(uuid.uuid4())
    MEETINGS[meeting_id] = {
        "users": [req.user_a, req.user_b],
        "day": result["day"],
        "start": result["start"],
        "end": result["end"],
        "status": "CONFIRMED"
    }

    return {
        "status": "CONFIRMED",
        "meeting_id": meeting_id,
        "details": MEETINGS[meeting_id]
    }
