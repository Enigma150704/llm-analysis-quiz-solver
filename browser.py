"""
Headless browser wrapper using Playwright for rendering JavaScript-rendered quiz pages
"""
import asyncio
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages headless browser instances for quiz page rendering"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def start(self):
        """Start the browser instance"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = await context.new_page()
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def navigate(self, url: str, timeout: int = 30000) -> str:
        """
        Navigate to a URL and return the rendered HTML content
        
        Args:
            url: URL to navigate to
            timeout: Timeout in milliseconds
            
        Returns:
            Rendered HTML content
        """
        if not self.page:
            await self.start()
        
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=timeout)
            # Wait a bit more for any JavaScript that runs after networkidle
            await asyncio.sleep(2)
            
            # Get the rendered HTML
            content = await self.page.content()
            logger.info(f"Successfully navigated to {url}")
            return content
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout loading {url}, returning partial content")
            return await self.page.content()
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            raise
    
    async def extract_text(self, url: str) -> str:
        """
        Extract visible text from a page
        
        Args:
            url: URL to extract text from
            
        Returns:
            Visible text content
        """
        if not self.page:
            await self.start()
        
        await self.navigate(url)
        text = await self.page.evaluate("() => document.body.innerText")
        return text
    
    async def download_file(self, url: str, file_path: str = None) -> bytes:
        """
        Download a file from a URL
        
        Args:
            url: URL to download from
            file_path: Optional path to save file (if None, returns bytes)
            
        Returns:
            File content as bytes
        """
        if not self.page:
            await self.start()
        
        try:
            async with self.page.expect_download() as download_info:
                await self.page.goto(url)
            download = await download_info.value
            content = await download.path()
            with open(content, 'rb') as f:
                file_bytes = f.read()
            return file_bytes
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            raise
    
    async def take_screenshot(self, url: str) -> bytes:
        """
        Take a screenshot of a page
        
        Args:
            url: URL to screenshot
            
        Returns:
            Screenshot as PNG bytes
        """
        if not self.page:
            await self.start()
        
        await self.navigate(url)
        screenshot = await self.page.screenshot(full_page=True)
        return screenshot
    
    async def close(self):
        """Close the browser instance"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

