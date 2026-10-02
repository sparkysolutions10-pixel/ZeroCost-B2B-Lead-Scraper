import asyncio
import logging

from .types import AgentState, TaskSchema

logger = logging.getLogger("mirofish.core.queue")

class TaskQueue:
    """
    High-throughput async priority queue with Dead-Letter Queue (DLQ) support.
    Sorts by priority, manages dependencies (DAG).
    """
    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[Any] = asyncio.PriorityQueue()
        self._tasks_db: dict[str, TaskSchema] = {}
        self._dlq: dict[str, TaskSchema] = {}
        
    async def submit(self, task: TaskSchema) -> None:
        self._tasks_db[task.id] = task
        # Format for PriorityQueue: (priority_int, task_id)
        await self._queue.put((task.priority.value, task.id))
        logger.debug(f"Task {task.id} submitted with priority {task.priority.name}")

    async def get_next(self) -> TaskSchema | None:
        """
        Retrieves the next highest priority task whose dependencies are resolved.
        (Simplified DAG handling: skips if deps not completed)
        """
        # In a highly optimized system, we'd use a real topological sort index.
        # For memory efficiency, we fetch and if blocked, we re-queue (or put aside).
        pending = []
        target_task = None
        
        while not self._queue.empty():
            prio, task_id = await self._queue.get()
            task = self._tasks_db.get(task_id)
            if not task:
                continue
                
            # Check dependencies
            deps_resolved = all(
                self._tasks_db.get(d) and self._tasks_db[d].status == AgentState.COMPLETED 
                for d in task.dependencies
            )
            
            if deps_resolved:
                target_task = task
                break
            else:
                pending.append((prio, task_id))
                
        # Re-queue pending tasks
        for p, tid in pending:
            await self._queue.put((p, tid))
            
        if target_task:
            target_task.status = AgentState.RUNNING
        return target_task

    def dead_letter(self, task_id: str, reason: str) -> None:
        if task_id in self._tasks_db:
            task = self._tasks_db.pop(task_id)
            task.status = AgentState.FAILED
            task.payload["dlq_reason"] = reason
            self._dlq[task_id] = task
            logger.error(f"Task {task_id} moved to DLQ. Reason: {reason}")
