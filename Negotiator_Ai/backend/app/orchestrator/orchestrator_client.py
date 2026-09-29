import os
import requests


class OrchestratorClient:
    """
    Primary decision-maker interface.
    This represents watsonx Orchestrate.

    Behavior:
    - Try Orchestrate if configured
    - Fallback cleanly if unavailable
    """

    def __init__(self):
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.url = os.getenv("WATSONX_ORCHESTRATE_URL")

    def decide_meeting(self, context: dict) -> dict:
        # 🔁 If not configured, fallback
        if not self.api_key or not self.url:
            return {
                "decision": "FALLBACK",
                "reason": "orchestrator_not_configured"
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "intent": "schedule_meeting",
            "context": context
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers,
                timeout=10
            )
        except requests.RequestException:
            return {
                "decision": "FALLBACK",
                "reason": "network_error"
            }

        if response.status_code != 200:
            return {
                "decision": "FALLBACK",
                "reason": "orchestrator_unavailable"
            }

        data = response.json()

        # Expected orchestrator response format
        if data.get("decision") == "CONFIRMED":
            return {
                "decision": "CONFIRMED",
                "result": data.get("result")
            }

        return {
            "decision": "FALLBACK",
            "reason": "no_decision"
        }
