import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..config.settings import settings
from .tunnels import TunnelManager
from .webhooks import WebhookValidator

# AI Core Imports
from ..brain.memory import SQLiteMemory
from ..evolution.router import DynamicRouter
from ..interface.manager import ManagerAgent
from .razorpay_webhook import router as razorpay_router

logger = logging.getLogger("mirofish.monetization.server")

# Global variables for OS engines
os_memory: SQLiteMemory | None = None
os_router: DynamicRouter | None = None
os_manager: ManagerAgent | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the AI core components for the web server
    global os_memory, os_router, os_manager
    logger.info("Initializing OS AI Core for Web Interface...")
    os_memory = SQLiteMemory()
    await os_memory.connect()
    os_router = DynamicRouter()
    os_manager = ManagerAgent(memory=os_memory, router=os_router)
    
    yield
    
    # Shutdown
    if os_memory:
        await os_memory.close()
    logger.info("OS AI Core shut down.")

app = FastAPI(title="MiroFish Paywall Architect & OS Web UI", version="1.0.0", lifespan=lifespan)
app.include_router(razorpay_router)

# Web Chat Models
class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request) -> dict[str, Any]:
    """Listens for Stripe payment intent success."""
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")
    
    if not WebhookValidator.verify_stripe_signature(payload, sig_header):
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    solution_id = "test_solution_123"
    
    unlocked_content = WebhookValidator.handle_payment_success(solution_id)
    if not unlocked_content:
        return {"status": "ok", "message": "No pending keystone for this ID."}
        
    logger.info(f"Delivering unlocked keystone for {solution_id}")
    return {"status": "success", "delivered": True}

@app.get("/chat", response_class=HTMLResponse)
async def chat_ui():
    """Serves the Premium Web GUI"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "interface", "web", "index.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Web UI not found")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat_api(req: ChatRequest) -> dict[str, Any]:
    """The REST endpoint that the HTML GUI talks to."""
    if not os_manager:
        raise HTTPException(status_code=500, detail="OS Manager not initialized")
    try:
        response = await os_manager.chat(req.session_id, req.message)
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"status": "error", "detail": str(e)}

class PaywallServer:
    def __init__(self) -> None:
        self.tunnel = TunnelManager(port=settings.WEBHOOK_PORT)
        
    async def run(self) -> None:
        await self.tunnel.start_cloudflare()
        
        import uvicorn
        config = uvicorn.Config(
            app=app,
            host=settings.HOST,
            port=settings.WEBHOOK_PORT,
            log_level="info",
            loop="uvloop" if sys.platform != "win32" else "asyncio"
        )
        server = uvicorn.Server(config)
        logger.info(f"Paywall Server listening on {settings.HOST}:{settings.WEBHOOK_PORT}")
        await server.serve()
