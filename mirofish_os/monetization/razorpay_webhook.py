from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import logging

logger = logging.getLogger("mirofish.monetization.razorpay")

router = APIRouter()

# You will need to put your Razorpay Webhook Secret in .env later
RAZORPAY_WEBHOOK_SECRET = "your_webhook_secret_here"

@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):
    """
    This endpoint listens to Razorpay servers. 
    When a customer pays ₹199, Razorpay calls this URL automatically.
    The AI OS will verify the signature and unlock the customer's IP/Session.
    """
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    # Verify Razorpay Signature (Security Check)
    expected_signature = hmac.new(
        key=RAZORPAY_WEBHOOK_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.error("Fraudulent payment attempt detected!")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse Payload
    payload = await request.json()
    
    if payload.get("event") == "payment.captured":
        payment_data = payload["payload"]["payment"]["entity"]
        amount = payment_data.get("amount") / 100 # Razorpay sends in paise
        email = payment_data.get("email")
        
        logger.info(f"💰 SUCCESS! Received ₹{amount} from {email}. Unlocking AI access...")
        
        # Here we would update the SQLite Database to mark this user's session as Premium
        # (Auto-Unlock Logic)
        
        return {"status": "success", "message": "User upgraded to Premium"}

    return {"status": "ignored"}
