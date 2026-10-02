import logging
from typing import Any

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .registry import global_registry

logger = logging.getLogger("mirofish.tools.browser")

class InvisibleBrowser:
    """
    Headless Playwright Integration.
    Extracts semantic markdown from DOMs to bypass anti-bot and save tokens.
    """
    def __init__(self) -> None:
        self.playwright: Any | None = None
        self.browser: Any | None = None

    async def start(self) -> None:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Invisible Browser online.")

    async def fetch_markdown(self, url: str) -> str:
        """Fetches a URL and returns semantic text content to save LLM tokens."""
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            content = await page.content()
            
            # Simple DOM parser to Markdown
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            text = soup.get_text(separator="\n\n", strip=True)
            return text
        except Exception as e:
            logger.error(f"Browser failed to fetch {url}: {e}")
            return f"Error fetching {url}"
        finally:
            await page.close()

    async def stop(self) -> None:
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

browser_instance = InvisibleBrowser()

# Register as a tool
async def web_search_tool(url: str) -> str:
    """Fetches the main text content of a webpage."""
    return await browser_instance.fetch_markdown(url)

global_registry.register(web_search_tool)
