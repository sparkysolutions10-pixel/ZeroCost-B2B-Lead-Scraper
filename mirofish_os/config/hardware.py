import logging
from typing import Any
import multiprocessing
import os

import psutil

from .settings import settings

logger = logging.getLogger("mirofish.hardware")

class HardwareProfiler:
    """
    Hardware Profiler & Concurrency Optimizer for WSL2 on Dell i5 / 16GB RAM.
    Ensures the OS respects system boundaries and tunes asyncio/thread pools accordingly.
    """

    @staticmethod
    def get_cpu_count() -> int:
        return multiprocessing.cpu_count()

    @staticmethod
    def get_memory_info() -> dict[str, Any]:
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "percent_used": mem.percent
        }

    @classmethod
    def apply_optimizations(cls) -> None:
        """
        Applies uvloop (if on Linux/WSL2) and sets thread pool sizes based on 
        the 8-core CPU constraint to prevent context-switching overhead.
        """
        # 1. Apply uvloop for blazing fast asyncio
        if os.name != "nt":
            try:
                import asyncio

                import uvloop
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                logger.info("uvloop activated for high-performance async I/O.")
            except ImportError:
                logger.warning("uvloop not installed, falling back to standard asyncio.")

        # 2. Log hardware status
        cpu = cls.get_cpu_count()
        mem = cls.get_memory_info()
        logger.info(f"Hardware Profile: CPU Cores: {cpu} | Memory: {mem['total_gb']} GB total ({mem['available_gb']} GB avail)")

        # 3. Warn if system is starved
        if mem["available_gb"] < 2.0:
            logger.warning("CRITICAL: Less than 2GB RAM available. Whisper STT or local LLMs may OOM kill.")

        if cpu > settings.MAX_WORKERS:
            logger.info(f"Capping thread pools to {settings.MAX_WORKERS} workers to avoid context-switch thrashing.")
