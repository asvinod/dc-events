from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import re

REMOVE_TAGS = [
    "script", "style", "nav", "footer", "head",
    "noscript", "svg", "form", "iframe", "picture",
]

ATTRS_TO_STRIP = [
    "src", "srcset", "data-src", "data-srcset",
    "style", "ping", "rel", "integrity", "crossorigin",
    "loading", "decoding", "fetchpriority", "sizes",
]

def scrape_page(url: str, headless: bool = True) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        html = page.content()
        browser.close()
    return html


def clean_html(html: str, char_limit: int = 50_000) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(REMOVE_TAGS):
        tag.decompose()
    for element in soup.find_all(string=lambda t: isinstance(t, str) and not t.strip()):
        pass
    for tag in soup.find_all(True):
        for attr in ATTRS_TO_STRIP:
            tag.attrs.pop(attr, None)
    cleaned = str(soup)
    cleaned = re.sub(r"\n\s*\n", "\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned) 
    if len(cleaned) > char_limit:
        cleaned = cleaned[:char_limit]
    return cleaned


if __name__ == "__main__":
    url = "https://carnegieendowment.org/events"
    print(f"Scraping: {url}")

    raw_html = scrape_page(url, headless=True)
    cleaned = clean_html(raw_html)

    print(f"Cleaned HTML size: {len(cleaned):,} chars")
    print("-" * 60)
    print(cleaned[:2000])