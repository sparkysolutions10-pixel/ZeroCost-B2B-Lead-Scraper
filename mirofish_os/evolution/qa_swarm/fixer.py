import logging

from ...brain.blackboard import global_blackboard
from ..router import DynamicRouter

logger = logging.getLogger("mirofish.evolution.qa_swarm.fixer")

class FixerAgent:
    """
    Automated patch generator. Takes tracebacks, queries Gemini Pro, and generates an AST diff.
    """
    def __init__(self) -> None:
        self.router = DynamicRouter()

    async def analyze_and_fix(self, tb_str: str) -> None:
        logger.info("Fixer Agent analyzing traceback...")
        
        prompt = (
            "You are an Elite QA Swarm Fixer. Analyze the following traceback and "
            "generate a valid Python diff or patched code to resolve the issue:\n\n"
            f"{tb_str}"
        )
        
        # Route to Tier 2 for code generation
        try:
            fix_proposal = await self.router.generate([{"role": "user", "content": prompt}])
            logger.info("Fix proposal generated. Pinning to blackboard.")
            await global_blackboard.pin("qa.fixes", {"traceback": tb_str, "patch": fix_proposal})
            
            # In a full setup, Mythos AI picks this up and applies it in the Shadow Sandbox
        except Exception as e:
            logger.error(f"Fixer Agent failed to generate patch: {e}")
