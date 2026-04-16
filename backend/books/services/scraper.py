from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


RATING_MAP = {
    "One": 1.0,
    "Two": 2.0,
    "Three": 3.0,
    "Four": 4.0,
    "Five": 5.0,
}


@dataclass
class ScrapedBook:
    title: str
    author: str
    description: str
    rating: float
    reviews_count: int
    book_url: str


class SeleniumBookScraper:
    def __init__(self, headless: bool = True, timeout: int = 20) -> None:
        self.headless = headless
        self.timeout = timeout

    def _driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)

    def scrape_books(self, base_url: str = "https://books.toscrape.com/", pages: int = 1) -> List[dict]:
        if pages < 1:
            return []

        books: List[dict] = []
        with self._driver() as driver:
            for page in range(1, pages + 1):
                page_url = f"{base_url}catalogue/page-{page}.html"
                driver.get(page_url)
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product_pod"))
                )
                elements = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")
                detail_links = [urljoin(page_url, e.get_attribute("href")) for e in elements]

                for link in detail_links:
                    detail = self.scrape_single_book(link)
                    if detail:
                        books.append(detail)
        return books

    def scrape_single_book(self, url: str) -> Optional[dict]:
        with self._driver() as driver:
            driver.get(url)
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product_main"))
            )
            html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
        product_main = soup.select_one("div.product_main")
        if not product_main:
            return None

        title = product_main.select_one("h1").get_text(strip=True)
        rating_classes = product_main.select_one("p.star-rating").get("class", [])
        rating_name = next((cls for cls in rating_classes if cls in RATING_MAP), "One")
        rating = RATING_MAP.get(rating_name, 1.0)

        description_node = soup.select_one("#product_description ~ p")
        description = description_node.get_text(" ", strip=True) if description_node else ""

        reviews_count = 0
        table_rows = soup.select("table.table.table-striped tr")
        for row in table_rows:
            th = row.select_one("th")
            td = row.select_one("td")
            if not th or not td:
                continue
            if th.get_text(strip=True) == "Number of reviews":
                try:
                    reviews_count = int(td.get_text(strip=True))
                except ValueError:
                    reviews_count = 0

        author = self._infer_author_from_description(description)

        return ScrapedBook(
            title=title,
            author=author,
            description=description,
            rating=rating,
            reviews_count=reviews_count,
            book_url=url,
        ).__dict__

    def scrape_books_fallback_requests(self, base_url: str = "https://books.toscrape.com/") -> List[dict]:
        response = requests.get(base_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("article.product_pod h3 a")
        books: List[dict] = []
        for link in links:
            detail_url = urljoin(base_url, "catalogue/" + link.get("href", ""))
            detail = self.scrape_single_book(detail_url)
            if detail:
                books.append(detail)
        return books

    @staticmethod
    def _infer_author_from_description(description: str) -> str:
        if " by " in description:
            candidate = description.split(" by ")[-1].split(".")[0].strip()
            if 2 <= len(candidate) <= 100:
                return candidate
        return "Unknown Author"
