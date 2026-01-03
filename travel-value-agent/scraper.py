# scraper.py
# Robust Playwright scraper for JS-heavy websites (Windows-safe)

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import json
import time

URL = "https://www.thomascook.in/holidays/india-tour-packages/uttarakhand-tour-packages"
OUTPUT_FILE = "scraped_output.json"


def scrape():
    lines = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load DOM only (do NOT wait for network idle)
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        # Give JS time to render cards
        time.sleep(8)

        try:
            body_text = page.locator("body").inner_text()
        except PlaywrightTimeout:
            body_text = ""

        browser.close()

    for line in body_text.split("\n"):
        clean = line.strip()
        if clean:
            lines.append(clean)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(lines, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    scrape()
