from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
from dotenv import load_dotenv

def scrape_page(url, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        Stealth().apply_stealth_sync(page)

        page.goto(url, wait_until="networkidle")

        html = page.content()

        browser.close()

    return html


def prune_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "head", "noscript", "svg", "form"]):
        tag.decompose()

    text = md(str(soup), heading_style="ATX", strip=["img"])
    return re.sub(r"\n{3,}", "\n\n", text)

url = "https://carnegieendowment.org/events"
html = scrape_page(url, headless=True)
cleaned_markdown = prune_to_markdown(html)
print(cleaned_markdown)