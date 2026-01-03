import sys
import asyncio
from typing import List

# ✅ Windows + Python 3.12 + Playwright FIX
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from playwright.sync_api import sync_playwright


class WebPageReader:
    """
    Browser-based webpage reader using Playwright.
    Works correctly on Windows with Python 3.12.
    """

    def __init__(self, url: str):
        self.url = url

    def get_visible_text(self) -> List[str]:
        lines = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(self.url, timeout=60000)
            page.wait_for_load_state("networkidle")

            body_text = page.locator("body").inner_text()
            browser.close()

        for line in body_text.split("\n"):
            clean_line = line.strip()
            if clean_line:
                lines.append(clean_line)

        return lines
