"""News scraper for cocoa-related articles and updates."""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import httpx
from bs4 import BeautifulSoup
import feedparser
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class NewsScraper:
    """Scraper for cocoa-related news from multiple sources."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.timeout = httpx.Timeout(30.0)

        # RSS feeds for cocoa news
        self.rss_feeds = [
            {
                "url": "https://news.google.com/rss/search?q=cocoa+price+commodity&hl=en-US&gl=US&ceid=US:en",
                "source": "Google News",
            },
            {
                "url": "https://news.google.com/rss/search?q=cocoa+market+trading&hl=en-US&gl=US&ceid=US:en",
                "source": "Google News",
            },
            {
                "url": "https://news.google.com/rss/search?q=ivory+coast+ghana+cocoa&hl=en-US&gl=US&ceid=US:en",
                "source": "Google News",
            },
        ]

        # Keywords for relevance scoring
        self.high_importance_keywords = [
            "price surge", "price drop", "record high", "record low",
            "supply shortage", "harvest", "production cut", "export ban",
            "ivory coast", "ghana", "weather", "drought", "flood",
            "ICE futures", "cocoa futures", "market crash", "rally",
        ]

        self.medium_importance_keywords = [
            "cocoa", "chocolate", "cacao", "farming", "farmers",
            "supply chain", "demand", "consumption", "forecast",
            "trading", "commodity", "futures", "market",
        ]

    async def fetch_all_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch news from all sources."""
        all_news = []

        # Fetch from RSS feeds
        rss_tasks = [self._fetch_rss_feed(feed) for feed in self.rss_feeds]
        rss_results = await asyncio.gather(*rss_tasks, return_exceptions=True)

        for result in rss_results:
            if isinstance(result, list):
                all_news.extend(result)

        # Fetch from web scrapers
        web_tasks = [
            self._scrape_reuters_commodities(),
            self._scrape_confectionery_news(),
        ]
        web_results = await asyncio.gather(*web_tasks, return_exceptions=True)

        for result in web_results:
            if isinstance(result, list):
                all_news.extend(result)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_news = []
        for article in all_news:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_news.append(article)

        # Sort by importance score and recency
        unique_news.sort(
            key=lambda x: (x.get("importance_score", 0), x.get("published_at", datetime.min)),
            reverse=True,
        )

        return unique_news[:limit]

    async def _fetch_rss_feed(self, feed_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch and parse an RSS feed."""
        url = feed_config["url"]
        source = feed_config["source"]

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                feed = feedparser.parse(response.text)
                articles = []

                for entry in feed.entries[:20]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    link = entry.get("link", "")

                    # Parse publication date
                    published_at = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])

                    # Clean summary from HTML
                    if summary:
                        soup = BeautifulSoup(summary, "lxml")
                        summary = soup.get_text(strip=True)[:500]

                    # Calculate importance score
                    importance = self._calculate_importance(title, summary)

                    # Determine sentiment
                    sentiment = self._analyze_basic_sentiment(title, summary)

                    articles.append({
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "source": source,
                        "published_at": published_at,
                        "fetched_at": datetime.utcnow(),
                        "importance_score": importance,
                        "sentiment": sentiment,
                        "categories": self._extract_categories(title, summary),
                    })

                return articles

        except Exception as e:
            logger.warning(f"RSS feed fetch failed for {url}: {e}")
            return []

    async def _scrape_reuters_commodities(self) -> List[Dict[str, Any]]:
        """Scrape Reuters for commodities news."""
        url = "https://www.reuters.com/markets/commodities/"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")
                articles = []

                # Find article links
                article_elements = soup.select("article")[:15]

                for article in article_elements:
                    title_elem = article.select_one("h3, h2, .media-story-card__headline__tFMEu")
                    link_elem = article.select_one("a[href]")

                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        href = link_elem.get("href", "")

                        # Filter for cocoa-related articles
                        if not self._is_cocoa_related(title):
                            continue

                        full_url = urljoin("https://www.reuters.com", href)

                        articles.append({
                            "title": title,
                            "summary": "",
                            "url": full_url,
                            "source": "Reuters",
                            "published_at": datetime.utcnow(),
                            "fetched_at": datetime.utcnow(),
                            "importance_score": self._calculate_importance(title, ""),
                            "sentiment": self._analyze_basic_sentiment(title, ""),
                            "categories": self._extract_categories(title, ""),
                        })

                return articles

        except Exception as e:
            logger.warning(f"Reuters scrape failed: {e}")
            return []

    async def _scrape_confectionery_news(self) -> List[Dict[str, Any]]:
        """Scrape Confectionery News for industry updates."""
        url = "https://www.confectionerynews.com/Article?keyword=cocoa"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")
                articles = []

                article_elements = soup.select(".Teaser")[:15]

                for article in article_elements:
                    title_elem = article.select_one(".Teaser-title, h2, h3")
                    link_elem = article.select_one("a[href]")
                    summary_elem = article.select_one(".Teaser-intro, .summary")

                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        href = link_elem.get("href", "")
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""

                        full_url = urljoin("https://www.confectionerynews.com", href)

                        articles.append({
                            "title": title,
                            "summary": summary[:500],
                            "url": full_url,
                            "source": "Confectionery News",
                            "published_at": datetime.utcnow(),
                            "fetched_at": datetime.utcnow(),
                            "importance_score": self._calculate_importance(title, summary),
                            "sentiment": self._analyze_basic_sentiment(title, summary),
                            "categories": self._extract_categories(title, summary),
                        })

                return articles

        except Exception as e:
            logger.warning(f"Confectionery News scrape failed: {e}")
            return []

    def _is_cocoa_related(self, text: str) -> bool:
        """Check if text is related to cocoa."""
        text_lower = text.lower()
        cocoa_keywords = ["cocoa", "cacao", "chocolate", "ivory coast", "ghana cocoa"]
        return any(keyword in text_lower for keyword in cocoa_keywords)

    def _calculate_importance(self, title: str, summary: str) -> float:
        """Calculate importance score based on keywords."""
        text = f"{title} {summary}".lower()
        score = 0.3  # Base score

        # High importance keywords
        for keyword in self.high_importance_keywords:
            if keyword in text:
                score += 0.15

        # Medium importance keywords
        for keyword in self.medium_importance_keywords:
            if keyword in text:
                score += 0.05

        return min(score, 1.0)

    def _analyze_basic_sentiment(self, title: str, summary: str) -> str:
        """Basic sentiment analysis based on keywords."""
        text = f"{title} {summary}".lower()

        positive_words = ["surge", "rally", "rise", "gain", "jump", "soar", "record high", "bullish", "optimistic"]
        negative_words = ["drop", "fall", "decline", "crash", "plunge", "record low", "bearish", "concern", "crisis"]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def _extract_categories(self, title: str, summary: str) -> str:
        """Extract categories from text."""
        text = f"{title} {summary}".lower()
        categories = []

        category_keywords = {
            "price": ["price", "cost", "value", "trading"],
            "supply": ["supply", "production", "harvest", "yield", "export"],
            "demand": ["demand", "consumption", "sales", "buying"],
            "weather": ["weather", "climate", "drought", "rain", "flood"],
            "geopolitical": ["government", "policy", "regulation", "politics", "conflict"],
            "market": ["market", "futures", "trading", "ICE", "commodity"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)

        return ",".join(categories) if categories else "general"
