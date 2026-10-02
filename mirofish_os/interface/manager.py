import logging

from ..brain.memory import SQLiteMemory
from ..brain.session import SessionManager
from ..evolution.router import DynamicRouter

logger = logging.getLogger("mirofish.interface.manager")

class ManagerAgent:
    """
    The Gemini-like Conversational Front-End.
    Maintains user context via SQLite memory and routing intents.
    """
    def __init__(self, memory: SQLiteMemory, router: DynamicRouter):
        self.memory = memory
        self.session_manager = SessionManager()
        self.router = router

    async def chat(self, session_id: str, user_input: str) -> str:
        logger.info(f"[Session {session_id}] User: {user_input}")
        
        # 1. Update active session context
        self.session_manager.add_message(session_id, "user", user_input)
        
        # 2. Persist to long-term SQLite
        await self.memory.store(session_id, "user", user_input)
        
        # 3. Retrieve semantic context (Optional step based on query complexity)
        # historical_context = await self.memory.search(user_input, limit=3)
        
        # 4. Route task to appropriate LLM
        context = self.session_manager.get_context(session_id)
        
        # The router decides if it needs Groq (fast) or Gemini (complex)
        response_text = await self.router.generate(context)
        
        # 5. Store response
        self.session_manager.add_message(session_id, "assistant", response_text)
        await self.memory.store(session_id, "assistant", response_text)
        
        return response_text
