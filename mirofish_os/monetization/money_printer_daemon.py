import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import random

# Force UTF-8 encoding for Windows console to prevent emoji crashes
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup paths
root_dir = r"C:\Users\tarun\Downloads\MiroFish-main (1)\MiroFish-main"
sys.path.append(os.path.join(root_dir, "mirofish_os", "monetization"))

# Level 5 Upgrade: Log Rotation (Prevents Hard Drive Bloat)
log_path = os.path.join(root_dir, "mirofish_os", "monetization", "money_printer.log")
logger = logging.getLogger("mirofish.monetization.daemon")
logger.setLevel(logging.INFO)
# Max 5MB per file, keep last 3 backups.
handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

from autonomous_hustler import run_autonomous_campaign

async def run_with_exponential_backoff():
    """
    Level 5 Upgrade: Auto-Healing & Exponential Backoff.
    If the internet drops or API blocks us, it doesn't crash.
    It waits 2 mins, then 4 mins, then 8 mins, up to 1 hour.
    """
    max_retries = 5
    base_delay = 120 # 2 minutes

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("🚀 [LEVEL 5 THREAD] Initiating Autonomous Campaign...")
            # We run the synchronous hustler in a background thread so it doesn't block the async loop
            await asyncio.to_thread(run_autonomous_campaign)
            logger.info("✅ Campaign cycle completed successfully.")
            return True # Success
        except Exception as e:
            logger.error(f"⚠️ CRITICAL FAULT caught in cycle: {str(e)}")
            if attempt == max_retries:
                logger.critical("🚨 MAX RETRIES REACHED. System requires human intervention.")
                return False
            
            # Exponential Backoff calculation
            wait_time = base_delay * (2 ** (attempt - 1))
            logger.warning(f"🔄 Auto-Healing: Retrying in {wait_time/60} minutes... (Attempt {attempt+1}/{max_retries})")
            await asyncio.sleep(wait_time)

async def main_loop():
    print("==================================================")
    print(" 🤖 SPARKY DIGITAL - LEVEL 5 ENTERPRISE DAEMON ON")
    print("==================================================")
    print("Features Active: Async Event Loop | Log Rotation | Exponential Backoff | Auto-Healing")
    
    while True:
        success = await run_with_exponential_backoff()
        
        if not success:
            print("\n[!] Daemon paused due to consecutive critical errors. Check logs.")
            # We don't crash, we just pause for a long time before trying again
            await asyncio.sleep(3600) 
            continue
            
        # Normal wait time before next hunt (5 to 10 minutes)
        wait_time = random.randint(300, 600)
        print(f"\n⏳ Cycle complete. Deep sleep for {wait_time // 60} minutes to bypass rate-limits...")
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n🛑 Master requested shutdown. Gracefully stopping Level 5 Daemon.")
