import threading
import time
from datetime import datetime


def schedule_reminder(slack_id: str, meeting_time_iso: str):
    meeting_time = datetime.fromisoformat(meeting_time_iso)
    delay = meeting_time.timestamp() - time.time() - 3600

    if delay <= 0:
        return

    def send():
        time.sleep(delay)
        print(f"Reminder sent to {slack_id}")

    threading.Thread(target=send, daemon=True).start()
