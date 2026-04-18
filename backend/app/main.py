from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.auth.slack_auth import router as auth_router
from app.users.users import router as users_router
from app.meetings.meetings import router as meetings_router
from app.meetings.email_meeting import router as email_router

app = FastAPI(title="Negotiator AI")

@app.get("/")
def health():
    return {"status": "running"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
app.include_router(email_router, prefix="/meetings", tags=["Email"])
