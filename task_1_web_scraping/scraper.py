"""
CodeAlpha Task 1: Web Scraping
Scrapes book details from Books to Scrape, a website created for scraping practice.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({
        "User-Agent": "CodeAlpha-Data-Analytics-Internship/1.0"
    })
    return session


def parse_book(card: Any, page_url: str) -> dict[str, Any]:
    link = card.select_one("h3 a")
    price_text = card.select_one(".price_color").get_text(strip=True)
    availability = card.select_one(".availability").get_text(" ", strip=True)
    rating_classes = card.select_one("p.star-rating").get("class", [])
    rating_text = next((c for c in rating_classes if c in RATING_MAP), None)

    return {
        "title": link.get("title", "").strip(),
        "price_gbp": float(price_text.replace("£", "").replace("Â", "")),
        "rating_text": rating_text,
        "rating_numeric": RATING_MAP.get(rating_text),
        "in_stock": "In stock" in availability,
        "product_url": urljoin(page_url, link.get("href", "")),
        "image_url": urljoin(page_url, card.select_one("img").get("src", "")),
    }


def scrape_books(delay_seconds: float = 0.5) -> pd.DataFrame:
    session = build_session()
    current_url = START_URL
    rows: list[dict[str, Any]] = []

    while current_url:
        response = session.get(current_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select("article.product_pod")
        rows.extend(parse_book(card, current_url) for card in cards)

        next_link = soup.select_one("li.next a")
        current_url = urljoin(current_url, next_link["href"]) if next_link else None
        time.sleep(delay_seconds)

    df = pd.DataFrame(rows).drop_duplicates(subset=["product_url"])
    df["title_length"] = df["title"].str.len()
    return df


if __name__ == "__main__":
    output = Path(__file__).parent / "data" / "books_scraped.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    data = scrape_books()
    data.to_csv(output, index=False)
    print(f"Saved {len(data):,} books to {output}")
