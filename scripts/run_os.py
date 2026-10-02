import os
import sys
import asyncio
import logging

# Ensure absolute path resolution for relative imports within mirofish_os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mirofish_os.config.hardware import HardwareProfiler
from mirofish_os.core.orchestrator import ApexOrchestrator
from mirofish_os.brain.memory import SQLiteMemory
from mirofish_os.evolution.qa_swarm.watchdog import watchdog
from mirofish_os.evolution.mythos import MythosAI
from mirofish_os.monetization.server import PaywallServer

# Configure global logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("mirofish.main")

async def boot_os():
    logger.info("Initializing MiroFish Universal Autonomous OS...")
    
    # 1. Hardware Tuning
    HardwareProfiler.apply_optimizations()
    
    # 2. Enable QA Watchdog
    watchdog.enable()
    
    # 3. Mount Memory
    memory = SQLiteMemory()
    await memory.connect()
    
    # 4. Start Master Orchestrator (Apex Daemon)
    apex = ApexOrchestrator()
    await apex.start()
    
    # 5. Start Mythos AI Evolution Loop
    mythos = MythosAI()
    asyncio.create_task(mythos.listen())
    
    # 6. Start Paywall Server (runs indefinitely)
    paywall = PaywallServer()
    
    try:
        await paywall.run()
    except KeyboardInterrupt:
        logger.info("Shutdown signal received.")
    finally:
        await apex.stop()
        await memory.close()
        logger.info("MiroFish OS offline. Goodbye.")

if __name__ == "__main__":
    try:
        # In a real WSL2 deployment with uvloop installed, asyncio.run will use uvloop
        asyncio.run(boot_os())
    except KeyboardInterrupt:
        pass
