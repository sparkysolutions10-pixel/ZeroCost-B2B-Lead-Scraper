import inspect
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("mirofish.tools.registry")

class ToolRegistry:
    """
    Dynamic Tool Registry.
    Stores and executes Python tools, and auto-generates JSON schemas for LLMs.
    """
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, func: Callable[..., Any]) -> None:
        name = func.__name__
        self._tools[name] = func
        logger.debug(f"Registered tool: {name}")

    def generate_schemas(self) -> list[dict[str, Any]]:
        """Auto-generates OpenAI/Gemini compatible JSON schemas from docstrings & typing."""
        schemas = []
        for name, func in self._tools.items():
            sig = inspect.signature(func)
            schema = {
                "name": name,
                "description": func.__doc__ or f"Executes {name}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            # Highly simplified introspector
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                schema["parameters"]["properties"][param_name] = {"type": "string"}
                if param.default == inspect.Parameter.empty:
                    schema["parameters"]["required"].append(param_name)
            schemas.append(schema)
        return schemas

    async def execute(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self._tools:
            raise ValueError(f"Tool {tool_name} not found.")
        func = self._tools[tool_name]
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)

global_registry = ToolRegistry()
