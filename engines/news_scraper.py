"""
engines/news_scraper.py
Handles all news scraping operations:
  - Google News RSS scraping
  - Article classification by risk category
  - Producing region identification
  - Deduplication and sorting
"""

import streamlit as st
import pandas as pd
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote_plus
import time

from config.settings import NEWS_CACHE_TTL, NEWS_DELAY_BETWEEN, NEWS_MAX_PER_QUERY


@st.cache_data(ttl=NEWS_CACHE_TTL, show_spinner=False)
def scrape_google_news_rss(query: str, max_results: int = 15) -> list[dict]:
    """Fetch articles from Google News RSS for a given query."""
    encoded_query = quote_plus(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:max_results]:
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "published"):
                try:
                    pub_date = datetime.strptime(
                        entry.published, "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pub_date = None

            title = entry.get("title", "")
            source = ""
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip()
                source = parts[1].strip()

            articles.append({
                "title": title,
                "source": source,
                "link": entry.get("link", ""),
                "published": pub_date,
                "summary": BeautifulSoup(
                    entry.get("summary", entry.get("description", "")),
                    "html.parser",
                ).get_text(strip=True)[:300],
                "query": query,
            })
        return articles
    except Exception:
        return []


def classify_article(article: dict, risk_categories: dict) -> list[str]:
    """Classify an article into risk categories based on keyword matching."""
    text = f"{article['title']} {article['summary']}".lower()
    matched = []
    for category, config in risk_categories.items():
        score = sum(1 for kw in config["keywords"] if kw.lower() in text)
        if score >= 1:
            matched.append(category)
    return matched if matched else ["📊 General Market"]


def identify_regions(article: dict, producing_regions: dict) -> list[str]:
    """Identify which producing regions are mentioned in an article."""
    text = f"{article['title']} {article['summary']}".lower()
    matched = []
    for region, info in producing_regions.items():
        for kw in info["keywords"]:
            if kw.lower() in text:
                matched.append(region)
                break
    return matched


@st.cache_data(ttl=NEWS_CACHE_TTL, show_spinner=False)
def fetch_all_risk_news(
    risk_categories: dict,
    producing_regions: dict,
) -> pd.DataFrame:
    """Scrape news across all risk categories, classify and tag regions."""
    all_articles = []
    seen_titles = set()

    for category, config in risk_categories.items():
        for query in config["queries"]:
            articles = scrape_google_news_rss(query, max_results=NEWS_MAX_PER_QUERY)
            for article in articles:
                title_key = article["title"].lower().strip()
                if title_key in seen_titles or len(title_key) < 10:
                    continue
                seen_titles.add(title_key)

                article["categories"] = classify_article(article, risk_categories)
                article["regions"] = identify_regions(article, producing_regions)
                article["primary_category"] = article["categories"][0]
                all_articles.append(article)

            time.sleep(NEWS_DELAY_BETWEEN)

    if not all_articles:
        return pd.DataFrame()

    df = pd.DataFrame(all_articles)
    if "published" in df.columns:
        df = df.sort_values("published", ascending=False, na_position="last")
    return df.reset_index(drop=True)
