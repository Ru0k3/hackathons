"""
stripe_service.py
Billing/Stripe has been removed - ModeOn is free.
This module is kept as a placeholder so existing imports do not break.
"""


class StripeService:
    async def create_checkout_session(self, *args, **kwargs):
        raise NotImplementedError("Billing has been removed.")

    async def create_portal_session(self, *args, **kwargs):
        raise NotImplementedError("Billing has been removed.")

    async def handle_webhook(self, *args, **kwargs):
        raise NotImplementedError("Billing has been removed.")
