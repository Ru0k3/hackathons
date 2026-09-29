MEETINGS_DB = {}


def save_meeting(meeting_id: str, data: dict):
    MEETINGS_DB[meeting_id] = data


def get_user_meetings(slack_id: str):
    return [
        meeting for meeting in MEETINGS_DB.values()
        if slack_id in meeting.get("users", [])
    ]
