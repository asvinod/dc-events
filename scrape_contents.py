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
    with sync_playwright() as p: # start Playwright engine
        browser = p.chromium.launch( # Chromium browser instance
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"], # stealth measure
        )
        context = browser.new_context( # fresh browser profile
            viewport={"width": 1280, "height": 800}, # browser window size
            user_agent=( # Basically trying to appear s a real Chrome browser on a Mac
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page) # new page within context, applies stealth to prevent site detecting browser automation
        try:
            page.goto(url, wait_until="networkidle", timeout=60000) # wait until no more than 2 active network requests
        except:
            page.goto(url, wait_until="domcontentloaded", timeout=60000) # fallback 
        html = page.content() # returns rendered HTML 
        browser.close() # close browser 
    return html


def clean_html(html: str, char_limit: int = 50_000) -> str:
    soup = BeautifulSoup(html, "html.parser") # parse raw HTML string to BS tree object
    for tag in soup(REMOVE_TAGS): # remove unwanted tags [soup(..) = soup.find_all(..)]
        tag.decompose()
    for tag in soup.find_all(True): # removing specific attributes for matched tags
        for attr in ATTRS_TO_STRIP:
            tag.attrs.pop(attr, None)
    cleaned = str(soup) # regex cleanup
    cleaned = re.sub(r"\n\s*\n", "\n", cleaned) # multiple blank lines to a single newline
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned) # two or more spaces/tabs into single space
    if len(cleaned) > char_limit: # limit to prevent overfeeding prompt 
        cleaned = cleaned[:char_limit]
    return cleaned