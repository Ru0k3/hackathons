from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from triage_agent import TriageAgent

app = FastAPI(title="Triage Agent API")
agent = TriageAgent()


class InputModel(BaseModel):
    data: Dict[str, Any]


@app.post("/evaluate")
def evaluate(input_model: InputModel):
    try:
        result = agent.deliberate(input_model.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
