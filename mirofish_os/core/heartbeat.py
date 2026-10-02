import asyncio
import logging

from .rca import rca_engine
from .types import AgentHeartbeat, AgentState, utcnow

logger = logging.getLogger("mirofish.core.heartbeat")

class Sentinel:
    """
    Heartbeat & Liveness monitor.
    Checks agent registries to ensure no task is stalled.
    """
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.registry: dict[str, AgentHeartbeat] = {}
        
    def ping(self, agent_id: str, state: AgentState, memory_mb: float, cpu: float) -> None:
        self.registry[agent_id] = AgentHeartbeat(
            agent_id=agent_id,
            state=state,
            last_ping=utcnow(),
            memory_usage_mb=memory_mb,
            cpu_percent=cpu
        )

    async def watch_loop(self) -> None:
        """Background daemon task."""
        while True:
            now = utcnow()
            for agent_id, hb in list(self.registry.items()):
                if hb.state in (AgentState.COMPLETED, AgentState.FAILED):
                    continue
                    
                delta = (now - hb.last_ping).total_seconds()
                if delta > self.timeout_seconds:
                    logger.error(f"Agent {agent_id} timeout! No ping in {delta}s.")
                    hb.state = AgentState.STALLED
                    rca_engine.analyze_stall(agent_id, hb.memory_usage_mb, hb.cpu_percent)
                    # The orchestrator will pick up the stalled state and kill/requeue
            
            await asyncio.sleep(5) # Poll every 5s
