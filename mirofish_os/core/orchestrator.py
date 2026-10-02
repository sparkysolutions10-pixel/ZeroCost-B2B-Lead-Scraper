import asyncio
import logging
from typing import Any

from ..config.settings import settings
from .heartbeat import Sentinel
from .queue import TaskQueue
from .types import AgentState

logger = logging.getLogger("mirofish.core.orchestrator")

class ApexOrchestrator:
    """
    The Master Daemon. Integrates the Priority Queue and Heartbeat Sentinel.
    Routes tasks to worker pools respecting the i5 hardware limits.
    """
    def __init__(self) -> None:
        self.queue = TaskQueue()
        self.sentinel = Sentinel()
        self.max_workers = settings.MAX_WORKERS
        self._running = False
        self._workers: list[asyncio.Task[Any]] = []

    async def _worker_loop(self, worker_id: int) -> None:
        logger.info(f"Worker {worker_id} started.")
        while self._running:
            task = await self.queue.get_next()
            if not task:
                await asyncio.sleep(0.5)
                continue
                
            logger.info(f"[Worker {worker_id}] Executing task: {task.id} ({task.name})")
            
            # Simulate execution wrap (in reality, this routes to agents)
            try:
                self.sentinel.ping(agent_id=f"worker_{worker_id}", state=AgentState.RUNNING, memory_mb=50.0, cpu=10.0)
                
                # Mock execution block
                await asyncio.sleep(1.0)
                
                task.status = AgentState.COMPLETED
                logger.info(f"[Worker {worker_id}] Task {task.id} completed.")
                self.sentinel.ping(agent_id=f"worker_{worker_id}", state=AgentState.IDLE, memory_mb=10.0, cpu=1.0)
            except Exception as e:
                logger.error(f"[Worker {worker_id}] Task {task.id} failed: {e!s}")
                self.queue.dead_letter(task.id, str(e))

    async def start(self) -> None:
        self._running = True
        # Start Sentinel
        self._workers.append(asyncio.create_task(self.sentinel.watch_loop()))
        
        # Start Workers bounded by CPU core count
        for i in range(self.max_workers):
            self._workers.append(asyncio.create_task(self._worker_loop(i)))
            
        logger.info(f"Apex Orchestrator online with {self.max_workers} worker tasks.")

    async def stop(self) -> None:
        self._running = False
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        logger.info("Apex Orchestrator shut down gracefully.")
