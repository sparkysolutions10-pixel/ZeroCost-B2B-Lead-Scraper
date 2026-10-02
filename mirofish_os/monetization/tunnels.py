import asyncio
import logging

logger = logging.getLogger("mirofish.monetization.tunnels")

class TunnelManager:
    """
    Automated Webhook Endpoint exposure via Cloudflare (cloudflared) or Ngrok.
    """
    def __init__(self, port: int = 5055):
        self.port = port
        self.process: Any | None = None

    async def start_cloudflare(self) -> None:
        logger.info(f"Starting Cloudflare Tunnel on port {self.port}...")
        try:
            # cloudflared tunnel --url http://localhost:5055
            self.process = await asyncio.create_subprocess_exec(
                "cloudflared", "tunnel", "--url", f"http://localhost:{self.port}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            # In a real daemon, we'd parse stdout/stderr to extract the generated URL
            logger.info("Cloudflare tunnel subprocess initiated.")
        except FileNotFoundError:
            logger.error("cloudflared not installed. Webhooks will not be externally accessible.")

    async def stop(self) -> None:
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("Tunnel stopped.")
