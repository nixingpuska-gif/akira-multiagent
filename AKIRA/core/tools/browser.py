import asyncio

try:
    from playwright.async_api import async_playwright
except Exception:  # pragma: no cover
    async_playwright = None


class BrowserTool:
    def __init__(self, headless: bool = False, proxy: str | None = None):
        self._pw = None
        self._browser = None
        self._page = None
        self._headless = headless
        self._proxy = proxy
        self._lock = asyncio.Lock()

    async def _ensure(self):
        if async_playwright is None:
            raise RuntimeError("Playwright not installed.")
        if not self._pw:
            self._pw = await async_playwright().start()
            launch_kwargs = {"headless": self._headless}
            if self._proxy:
                launch_kwargs["proxy"] = {"server": self._proxy}
            self._browser = await self._pw.chromium.launch(**launch_kwargs)
            self._page = await self._browser.new_page()

    async def goto(self, url: str) -> str:
        async with self._lock:
            await self._ensure()
            await self._page.goto(url)
            return f"Opened {url}"

    async def click(self, selector: str) -> str:
        async with self._lock:
            await self._ensure()
            await self._page.click(selector)
            return f"Clicked {selector}"

    async def type(self, selector: str, text: str) -> str:
        async with self._lock:
            await self._ensure()
            await self._page.fill(selector, text)
            return f"Typed into {selector}"

    async def content(self) -> str:
        async with self._lock:
            await self._ensure()
            return await self._page.content()

    async def _close_unlocked(self):
        if self._page:
            try:
                await self._page.close()
            except Exception:
                pass
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._pw:
            try:
                await self._pw.stop()
            except Exception:
                pass
        self._page = None
        self._browser = None
        self._pw = None

    async def close(self):
        async with self._lock:
            await self._close_unlocked()

    async def set_proxy(self, proxy: str | None) -> str:
        async with self._lock:
            if proxy == self._proxy:
                return "OK"
            self._proxy = proxy
            await self._close_unlocked()
            return "OK"
