import os

def patch(file, old, new):
    if not os.path.exists(file): return
    with open(file, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace(old, new)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(c)

patch('mirofish_os/interface/voice/stt.py', 'def _transcribe() -> None:', 'def _transcribe() -> str:')
patch('mirofish_os/interface/voice/stt.py', 'def __init__(self, model_size="base") -> None:', 'def __init__(self, model_size: str = "base") -> None:')
patch('mirofish_os/interface/voice/stt.py', 'def __init__(self, model_size="base"):', 'def __init__(self, model_size: str = "base") -> None:')
patch('mirofish_os/interface/voice/tts.py', 'def __init__(self, voice="en-US-AriaNeural") -> None:', 'def __init__(self, voice: str = "en-US-AriaNeural") -> None:')
patch('mirofish_os/interface/voice/tts.py', 'def __init__(self, voice="en-US-AriaNeural"):', 'def __init__(self, voice: str = "en-US-AriaNeural") -> None:')
patch('mirofish_os/tools/browser.py', 'self.playwright = None', 'self.playwright: Any | None = None')
patch('mirofish_os/tools/browser.py', 'self.browser = None', 'self.browser: Any | None = None')
patch('mirofish_os/core/queue.py', 'self._queue = asyncio.PriorityQueue()', 'self._queue: asyncio.PriorityQueue[Any] = asyncio.PriorityQueue()')
patch('mirofish_os/tools/tool_maker.py', 'namespace = {}', 'namespace: dict[str, Any] = {}')
patch('mirofish_os/evolution/qa_swarm/watchdog.py', 'def _excepthook(exc_type, exc_value, exc_traceback) -> None:', 'def _excepthook(exc_type: type, exc_value: BaseException, exc_traceback: Any) -> None:')
patch('mirofish_os/evolution/qa_swarm/watchdog.py', 'def _excepthook(exc_type, exc_value, exc_traceback):', 'def _excepthook(exc_type: type, exc_value: BaseException, exc_traceback: Any) -> None:')

for f in ['mirofish_os/brain/session.py', 'mirofish_os/config/hardware.py', 'mirofish_os/evolution/router.py', 'mirofish_os/brain/memory.py', 'mirofish_os/core/orchestrator.py', 'mirofish_os/evolution/mythos.py', 'mirofish_os/evolution/qa_swarm/watchdog.py', 'mirofish_os/tools/browser.py']:
    patch(f, 'import logging', 'import logging\nfrom typing import Any')

patch('mirofish_os/evolution/router.py', 'def _groq_sync() -> None:', 'def _groq_sync() -> str:')
patch('mirofish_os/evolution/router.py', 'def _gemini_sync() -> None:', 'def _gemini_sync() -> str:')
patch('mirofish_os/monetization/tunnels.py', 'self.process = None', 'self.process: Any | None = None')
patch('mirofish_os/core/rca.py', 'def _analyze_logs(self) -> None:', 'def _analyze_logs(self) -> list[str]:')
patch('mirofish_os/core/rca.py', 'self.recent_anomalies: list = []', 'self.recent_anomalies: list[str] = []')
patch('mirofish_os/monetization/server.py', 'async def stripe_webhook(request: Request) -> None:', 'async def stripe_webhook(request: Request) -> dict[str, Any]:')
patch('mirofish_os/core/orchestrator.py', 'async def _worker_loop(self, worker_id: int):', 'async def _worker_loop(self, worker_id: int) -> None:')
patch('mirofish_os/brain/blackboard.py', 'async def _safe_invoke(self, cb: Callable[..., Any], topic: str, content: Any):', 'async def _safe_invoke(self, cb: Callable[..., Any], topic: str, content: Any) -> None:')
patch('mirofish_os/tools/registry.py', 'self._tools: dict[str, Callable] = {}', 'self._tools: dict[str, Callable[..., Any]] = {}')
