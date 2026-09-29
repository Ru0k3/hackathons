"""
In-memory database for Negotiator AI
-----------------------------------
Hackathon choice:
- Simple
- Fast
- Explainable
- Easy to replace with real DB later
"""

# =========================
# USER STORAGE
# Key   -> Slack User ID
# Value -> User profile dict
# =========================
USERS = {}

# =========================
# MEETING STORAGE
# Key   -> Meeting ID
# Value -> Meeting details
# =========================
MEETINGS = {}


# =========================
# USER HELPERS
# =========================
def save_user_profile(slack_id: str, profile: dict) -> None:
    USERS[slack_id] = profile


def get_user_profile(slack_id: str):
    return USERS.get(slack_id)


def user_exists(slack_id: str) -> bool:
    return slack_id in USERS


# =========================
# MEETING HELPERS
# =========================
def save_meeting(meeting_id: str, meeting: dict) -> None:
    MEETINGS[meeting_id] = meeting


def get_user_meetings(slack_id: str):
    return [
        meeting for meeting in MEETINGS.values()
        if slack_id in meeting.get("users", [])
    ]
