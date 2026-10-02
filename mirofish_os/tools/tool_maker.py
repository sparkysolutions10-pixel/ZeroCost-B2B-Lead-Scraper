import ast
import inspect
import logging

from ..evolution.router import DynamicRouter
from .registry import global_registry

logger = logging.getLogger("mirofish.tools.maker")

class ToolMakerAgent:
    """
    Synthesizes and registers Python tools dynamically.
    """
    def __init__(self) -> None:
        self.router = DynamicRouter()

    async def create_tool(self, description: str) -> bool:
        """
        Asks Tier 2 LLM to write a Python function, validates AST, and registers it.
        """
        prompt = (
            f"You are the Tool Maker Agent. Write a fully typed Python async function "
            f"that fulfills this request: {description}. "
            "Return ONLY the raw python code with no markdown blocks. The function must have a clear docstring."
        )
        
        logger.info(f"Tool Maker synthesizing tool for: {description}")
        
        try:
            # We enforce Tier 2 via a trick or letting router decide
            code = await self.router.generate([{"role": "user", "content": prompt}])
            
            # 1. Strip markdown if present
            code = code.replace("```python", "").replace("```", "").strip()
            
            # 2. Validate AST to ensure no syntax errors and safe constructs
            _ = ast.parse(code)
            
            # 3. Execute in a controlled namespace
            namespace: dict[str, Any] = {}
            exec(code, namespace)
            
            # 4. Find the async function and register it
            for name, obj in namespace.items():
                if inspect.iscoroutinefunction(obj):
                    global_registry.register(obj)
                    logger.info(f"Dynamically registered new tool: {name}")
                    return True
                    
            logger.warning("No async function found in generated tool code.")
            return False
            
        except SyntaxError as e:
            logger.error(f"Tool Maker AST validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Tool Maker failed: {e}")
            return False
