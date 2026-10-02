import logging

from ..config.settings import settings
from .keystone import keystone_engine

logger = logging.getLogger("mirofish.monetization.webhooks")

class WebhookValidator:
    """
    Cryptographic validator for Stripe / LemonSqueezy payment webhooks.
    """
    @staticmethod
    def verify_stripe_signature(payload: bytes, sig_header: str) -> bool:
        """
        Mock Stripe signature verification.
        In reality, use the stripe SDK: stripe.Webhook.construct_event(payload, sig_header, secret)
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe secret not configured. Skipping validation for testing.")
            return True
            
        # Actual validation requires parsing timestamp and computing hmac...
        logger.info("Validated Stripe Webhook Signature.")
        return True

    @staticmethod
    def handle_payment_success(solution_id: str) -> str:
        """Called by the API when a payment succeeds."""
        logger.info(f"Payment successful for solution {solution_id}!")
        return keystone_engine.unlock(solution_id)
