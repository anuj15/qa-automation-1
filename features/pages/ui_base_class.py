"""Base class for all UI page objects."""

import logging

from playwright.async_api import Page

from features.utils.config_manager import get_config
from features.utils.log_manager import get_logger


class UIBaseClass:
    """Base class for all page objects using Playwright."""

    def __init__(self, page: Page) -> None:
        """
        Initialize page object.

        :param page: Playwright page object
        """
        self.page = page
        self.logger = get_logger()
        self.config = get_config()
        self.dynamic_wait = self.config.get("dynamic_wait_time") or 30000  # milliseconds

    async def navigate_to(self, url: str) -> None:
        """
        Navigate to a URL.

        :param url: URL to navigate to
        """
        self.logger.info(f"Navigating to: {url}")
        await self.page.goto(url)

    async def wait_for_element(self, selector: str, timeout: int | None = None) -> None:
        """
        Wait for an element to be visible.

        :param selector: Element selector
        :param timeout: Timeout in milliseconds
        """
        timeout = timeout or self.dynamic_wait
        await self.page.locator(selector).wait_for(timeout=timeout, state="visible")

    async def click(self, selector: str) -> None:
        """
        Click an element.

        :param selector: Element selector
        """
        self.logger.info(f"Clicking element: {selector}")
        await self.page.locator(selector).click()

    async def fill(self, selector: str, text: str) -> None:
        """
        Fill a text input.

        :param selector: Element selector
        :param text: Text to fill
        """
        self.logger.info(f"Filling element {selector} with: {text}")
        await self.page.locator(selector).fill(text)

    async def get_text(self, selector: str) -> str:
        """
        Get text content of an element.

        :param selector: Element selector
        :return: Text content
        """
        return await self.page.locator(selector).text_content()

    async def is_visible(self, selector: str) -> bool:
        """
        Check if an element is visible.

        :param selector: Element selector
        :return: True if visible, False otherwise
        """
        return await self.page.locator(selector).is_visible()
