# Modeon Backend — Placeholder

This directory will contain the **FastAPI** backend service for Modeon.

## Architecture

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI + Uvicorn |
| Auth | Supabase Auth (JWT validation) |
| Database | Supabase (PostgreSQL + Row Level Security) |
| File Storage | Azure Blob Storage |
| AI | Azure OpenAI — GPT-4o (outfit generation, compatibility scoring, outfit check) |
| AI Vision | Azure OpenAI GPT-4o Vision (outfit check photo analysis) |
| Background Removal | rembg (Python) |
| Clothing Classifier | Custom CV pipeline (see `services/cv_pipeline.py`) |
| Payments | Stripe (Checkout + Webhooks + Customer Portal) |
| Export | Pillow — composed outfit image cards |

## Directory Structure

```
app/
├── main.py           # FastAPI init, CORS, router registration
├── config.py         # Pydantic settings (reads env vars)
├── dependencies.py   # JWT auth dependency, subscription check middleware
├── routers/          # One router per feature domain
├── services/         # Business logic
├── models/           # Pydantic request/response schemas
└── db/               # Supabase client + schema SQL
```

## Environment Variables Required

```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
AZURE_BLOB_CONNECTION_STRING=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_GPT4O=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
ALLOWED_ORIGINS=http://localhost:3000
```

## Setup (when ready to implement)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
