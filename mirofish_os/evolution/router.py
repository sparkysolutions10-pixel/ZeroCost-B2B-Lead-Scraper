import asyncio
import logging
from typing import Any

from openai import AsyncOpenAI

from ..config.settings import settings

logger = logging.getLogger("mirofish.evolution.router")

class DynamicRouter:
    """
    Tiered LLM Router powered by OpenRouter (Unified Endpoint).
    Tier 1 (Fast/Triage): Llama 3.1 8B Instruct
    Tier 2 (Deep Code Synthesis): Gemini Pro 1.5
    """
    def __init__(self) -> None:
        self.client = None
        if settings.LLM_API_KEY:
            logger.info("Initializing OpenRouter unified client...")
            self.client = AsyncOpenAI(
                base_url=settings.LLM_BASE_URL,
                api_key=settings.LLM_API_KEY
            )
        else:
            logger.warning("No LLM_API_KEY provided for OpenRouter!")

    def _determine_tier(self, context: list[dict[str, Any]]) -> int:
        """
        Heuristic function to decide routing.
        If prompt contains 'agent', 'fable', 'autonomous', 'research', route to Tier 3.
        If prompt contains 'architecture', 'refactor', 'complex code', route to Tier 2.
        Otherwise, Tier 1.
        """
        last_msg = context[-1]["content"].lower()
        tier3_keywords = ["agent", "fable", "autonomous", "research", "scrape", "system"]
        if any(k in last_msg for k in tier3_keywords):
            return 3
            
        complex_keywords = ["refactor", "architect", "rewrite", "core source code", "deep logic"]
        if any(k in last_msg for k in complex_keywords):
            return 2
        return 1

    async def generate(self, context: list[dict[str, Any]]) -> str:
        if not self.client:
            return "System error: No LLM endpoints available (LLM_API_KEY is missing)."

        tier = self._determine_tier(context)
        
        # OpenRouter standardizes the message formats
        if tier == 1:
            logger.info("Routing to Tier 1: meta-llama/llama-3.1-8b-instruct")
            model = "meta-llama/llama-3.1-8b-instruct"
        elif tier == 2:
            logger.info("Routing to Tier 2: google/gemini-pro-1.5")
            model = "google/gemini-pro-1.5"
        else:
            logger.info("Routing to Tier 3: anthropic/claude-5.1-fable")
            model = "anthropic/claude-5.1-fable"

        try:
            if not self.client:
                raise Exception("No API Client")
                
            response = await self.client.chat.completions.create(
                model=model,
                messages=context,
                temperature=0.7,
            )
            return response.choices[0].message.content or "No response from AI."
        except Exception as e:
            logger.warning(f"OpenRouter generation failed: {e}. Falling back to AirLLM Offline Engine...")
            # Fallback to local AirLLM execution
            from .local_llm import offline_llm_engine
            # Convert messages back to string prompt for basic local generation
            prompt_str = "\n".join([f"{m['role']}: {m['content']}" for m in context])
            return await offline_llm_engine.generate_offline(prompt_str)

