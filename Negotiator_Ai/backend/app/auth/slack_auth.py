import os
import requests
from fastapi import APIRouter, Form, HTTPException

router = APIRouter()

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
REDIRECT_URI = "negotiator://slack-auth"


@router.post("/slack")
def slack_login(code: str = Form(...)):
    if not SLACK_CLIENT_ID or not SLACK_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Slack credentials missing")

    token_response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    ).json()

    if not token_response.get("ok"):
        raise HTTPException(status_code=400, detail="Slack OAuth failed")

    access_token = token_response["access_token"]

    user_info = requests.get(
        "https://slack.com/api/users.identity",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    return {
        "slack_id": user_info["user"]["id"],
        "name": user_info["user"]["name"]
    }
