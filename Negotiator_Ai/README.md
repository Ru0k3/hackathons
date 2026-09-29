# Negotiator AI (Smart Meeting Scheduler) — MVP

This is a hackathon-friendly MVP that matches the PRD:

- **Frontend**: Streamlit dashboard + “AI thinking” status window
- **Backend**: FastAPI with:
  - constraint normalizer (preferences → constraints)
  - matching engine (overlap search + compromise suggestion)
  - Watsonx integration stub (pluggable)
- **Storage**: SQLite (temporary user availability)

## Quickstart (Windows / PowerShell)

1) Create and activate a venv

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install deps

```bash
pip install -r requirements.txt
```

3) Start the API

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

4) Start the UI (in a second terminal)

```bash
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal.

## What inputs are supported (MVP)

- **Busy times**: paste lines like:
  - `2026-02-02 13:00-15:00`
  - `Tue 09:00-11:30`
  - `Mon 14:00-16:00`
- **Preferences**: free text such as:
  - `I hate Mondays`
  - `No mornings`
  - `Prefer after 4pm`

The system searches within the next 7 days (default) and proposes:
- a **perfect overlap** if possible
- otherwise a **best compromise** based on preferences.

## Project layout

- `app.py`: Streamlit UI
- `backend/`: FastAPI app
  - `backend/main.py`: API routes
  - `backend/db.py`: SQLite helpers
  - `backend/logic/`: normalizer + matcher + negotiation text

## Watsonx

This MVP ships with a stub that produces a polite negotiation message.
If you want real Watsonx calls, add credentials and implement `backend/logic/watsonx.py`.

