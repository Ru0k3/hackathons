from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/checkout")
@router.post("/portal")
@router.get("/status")
@router.post("/webhook")
async def billing_removed():
    raise HTTPException(
        status_code=410,
        detail="Billing has been removed. ModeOn is free.",
    )
