from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(UTC)

class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    BLOCKED = "blocked"
    STALLED = "stalled"
    FAILED = "failed"
    COMPLETED = "completed"

class TaskPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

class TaskSchema(BaseModel):
    id: str = Field(..., description="Unique task identifier")
    name: str
    priority: TaskPriority = TaskPriority.NORMAL
    payload: dict[str, Any] = Field(default_factory=dict[str, Any])
    dependencies: list[str] = Field(default_factory=list, description="IDs of tasks that must complete first")
    created_at: datetime = Field(default_factory=utcnow)
    status: AgentState = AgentState.IDLE

class AgentHeartbeat(BaseModel):
    agent_id: str
    task_id: str | None = None
    state: AgentState
    last_ping: datetime = Field(default_factory=utcnow)
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0
