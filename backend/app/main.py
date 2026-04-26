import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth,
    billing,
    export,
    gdpr,
    mix_match,
    occasion_styling,
    outfit_check,
    outfits,
    profile,
    laundry,
    shopping_list,
    shopping,
    swipe_session,
    wardrobe,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modeon")

app = FastAPI(
    title="ModeOn API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/api/auth",         tags=["Auth"])
app.include_router(gdpr.router,         prefix="/api/account",      tags=["Account"])
app.include_router(profile.router,      prefix="/api/profile",      tags=["Profile"])
app.include_router(wardrobe.router,     prefix="/api/wardrobe",     tags=["Wardrobe"])
app.include_router(outfits.router,      prefix="/api/outfits",      tags=["Outfits"])
app.include_router(outfit_check.router, prefix="/api/outfit-check", tags=["Outfit Check"])
app.include_router(laundry.router,      prefix="/api/laundry",      tags=["Laundry"])
app.include_router(shopping.router,     prefix="/api/shopping",     tags=["Shopping"])
app.include_router(billing.router,          prefix="/api/billing",        tags=["Billing"])
app.include_router(export.router,           prefix="/api/outfits",        tags=["Export"])
app.include_router(mix_match.router,        prefix="/api/outfits",        tags=["Mix & Match"])
app.include_router(occasion_styling.router, prefix="/api/outfits",        tags=["Occasion Styling"])
app.include_router(shopping_list.router,    prefix="/api/shopping-list",  tags=["Shopping List"])
app.include_router(swipe_session.router,    prefix="/api/outfits",        tags=["Swipe Session"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}
