import logging
from typing import Any
import sys
import traceback

from mirofish_os.brain.blackboard import global_blackboard
from .fixer import FixerAgent

logger = logging.getLogger("mirofish.evolution.qa_swarm.watchdog")

class WatchdogAgent:
    """
    Real-time exception & stderr sentinel.
    Hooks into sys.excepthook to intercept unhandled exceptions and pin them to the Blackboard.
    """
    def __init__(self) -> None:
        self.original_excepthook = sys.excepthook
        self.fixer = FixerAgent()

    def enable(self) -> None:
        sys.excepthook = self.custom_excepthook
        logger.info("QA Swarm Watchdog enabled on sys.excepthook.")

    def custom_excepthook(self, exc_type, exc_value, exc_traceback):
        logger.error("Watchdog caught an unhandled exception!")
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # In a fully async system, we dispatch a background task to process it
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.handle_exception(tb_str))
        except RuntimeError:
            # If no running loop
            pass
            
        # Still call original to not break default behavior completely
        self.original_excepthook(exc_type, exc_value, exc_traceback)

    async def handle_exception(self, tb_str: str):
        await global_blackboard.pin("qa.exceptions", {"traceback": tb_str})
        await self.fixer.analyze_and_fix(tb_str)

watchdog = WatchdogAgent()
