from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
import streamlit as st


@dataclass(frozen=True)
class ApiConfig:
    base_url: str


def api(cfg: ApiConfig, method: str, path: str, json_body=None):
    url = cfg.base_url.rstrip("/") + path
    r = requests.request(method=method, url=url, json=json_body, timeout=15)
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code} {r.text}")
    return r.json()


st.set_page_config(page_title="Negotiator AI", layout="wide")
st.title("Negotiator AI — Smart Meeting Scheduler")

cfg = ApiConfig(
    base_url=st.sidebar.text_input(
        "API Base URL", value="http://127.0.0.1:8001"
    )
)

col1, col2 = st.columns([1, 1])

# ================= LEFT PANEL =================
with col1:
    st.subheader("My Availability")

    username = st.text_input("Username", value="user_a")
    busy_text = st.text_area(
        "Busy times (one per line)",
        height=160,
        placeholder="Tue 09:00-11:00\n2026-02-02 13:00-15:00",
    )
    pref_text = st.text_area(
        "Preferences (free text)",
        height=120,
        placeholder="I hate Mondays\nNo mornings\nPrefer after 4pm",
    )

    if st.button("Save my profile", type="primary"):
        payload = {
            "username": username,
            "timezone": "local",
            "busy_text": busy_text,
            "preferences_text": pref_text,
        }
        out = api(cfg, "POST", "/profile", json_body=payload)
        st.success(f"Saved profile for {out['username']}.")

    st.divider()

    st.subheader("Known users")
    if st.button("Refresh user list"):
        try:
            out = api(cfg, "GET", "/users")
            st.session_state["users"] = out["users"]
        except Exception as e:
            st.error(str(e))

    st.write(st.session_state.get("users", []))


# ================= RIGHT PANEL =================
with col2:
    st.subheader("Book a Meeting")

    user_a = st.text_input("User A", value="user_a")
    user_b = st.text_input("User B", value="user_b")

    horizon_days = st.slider("Search horizon (days)", 1, 30, 7)
    slot_minutes = st.select_slider(
        "Slot length (minutes)", options=[15, 30, 45, 60], value=30
    )
    workday = st.slider("Working hours", 0, 24, (9, 17))

    if st.button("Schedule with User B"):
        payload = {
            "user_a": user_a,
            "user_b": user_b,
            "horizon_days": int(horizon_days),
            "slot_minutes": int(slot_minutes),
            "workday_start_hour": int(workday[0]),
            "workday_end_hour": int(workday[1]),
        }

        try:
            out = api(cfg, "POST", "/schedule", json_body=payload)
        except Exception as e:
            st.error(str(e))
            st.stop()

        # ===== Agent Thinking =====
        st.subheader("AI / Agent Status")
        thinking = out.get("thinking", [])
        st.text_area(
            "Thinking log",
            value="\n".join(thinking),
            height=150,
            key="thinking_box",
        )

        # ===== Decision =====
        st.subheader("Decision")
        st.success(out.get("explanation", ""))

        if out.get("start") and out.get("end"):
            start_dt = datetime.fromisoformat(out["start"])
            end_dt = datetime.fromisoformat(out["end"])

            formatted = (
                f"{start_dt.strftime('%A, %b %d')} | "
                f"{start_dt.strftime('%I:%M %p')} - "
                f"{end_dt.strftime('%I:%M %p')}"
            )

            st.markdown(f"### 📌 Selected Slot\n{formatted}")

        # ===== Available Slots =====
        if out.get("top_slots"):
            st.subheader("🗓 Available Time Slots")

            parsed_slots = [
                datetime.fromisoformat(slot["start"])
                for slot in out["top_slots"]
            ]

            for i, slot in enumerate(out["top_slots"], start=1):
                start_dt = datetime.fromisoformat(slot["start"])
                end_dt = datetime.fromisoformat(slot["end"])

                formatted = (
                    f"{start_dt.strftime('%A, %b %d')} | "
                    f"{start_dt.strftime('%I:%M %p')} - "
                    f"{end_dt.strftime('%I:%M %p')}"
                )

                st.markdown(f"**Option {i}**  \n{formatted}")
                st.divider()

        # ===== Weekly Grid =====
        if out.get("all_slots"):

            st.subheader("📊 Weekly Availability View")

            # Parse ALL slots (not top 5)
            all_slots = out["all_slots"]

            parsed_slots = [
                datetime.fromisoformat(slot["start"])
                for slot in all_slots
            ]

            if parsed_slots:

                first_date = min(parsed_slots).date()
                days = [first_date + timedelta(days=i) for i in range(7)]

                slot_lookup = set(parsed_slots)

                # Generate time rows based on working hours
                time_rows = []
                current_hour = workday[0]

                while current_hour < workday[1]:
                    minute = 0
                    while minute < 60:
                        if minute + slot_minutes > 60:
                            break
                        time_rows.append((current_hour, minute))
                        minute += slot_minutes
                    current_hour += 1

                # Header row
                header = st.columns(8)
                header[0].markdown("**Time**")
                for i, day in enumerate(days):
                    header[i + 1].markdown(f"**{day.strftime('%a')}**")

                # Grid body
                for hour, minute in time_rows:
                    row = st.columns(8)
                    row[0].markdown(f"{hour:02d}:{minute:02d}")

                    for i, day in enumerate(days):
                        cell_dt = datetime.combine(day, datetime.min.time()).replace(
                            hour=hour, minute=minute
                        )

                        if cell_dt in slot_lookup:
                            row[i + 1].markdown("🟢")
                        else:
                            row[i + 1].markdown("—")
