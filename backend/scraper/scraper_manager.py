"""Scraper manager for coordinating all data collection."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from .price_scraper import PriceScraper
from .news_scraper import NewsScraper
from backend.models.database import PriceRecord, NewsRecord, MarketFactorRecord

logger = logging.getLogger(__name__)


class ScraperManager:
    """Manages all scrapers and coordinates data collection."""

    def __init__(self):
        self.price_scraper = PriceScraper()
        self.news_scraper = NewsScraper()

    async def run_full_scrape(self, db: AsyncSession) -> Dict[str, Any]:
        """Run full data collection from all sources."""
        results = {
            "price": None,
            "news_count": 0,
            "errors": [],
            "timestamp": datetime.utcnow(),
        }

        # Scrape price data
        try:
            price_data = await self.price_scraper.get_current_price()
            if price_data:
                # Calculate additional price changes
                price_data = await self._enrich_price_data(price_data, db)

                # Save to database
                price_record = PriceRecord(**{
                    k: v for k, v in price_data.items()
                    if k in ["price_usd", "price_change_24h", "price_change_7d",
                             "price_change_30d", "volume", "source", "market"]
                })
                db.add(price_record)
                await db.commit()

                results["price"] = price_data
                logger.info(f"Saved price: ${price_data['price_usd']}")
        except Exception as e:
            logger.error(f"Price scraping error: {e}")
            results["errors"].append(f"Price scrape failed: {str(e)}")

        # Scrape news
        try:
            news_articles = await self.news_scraper.fetch_all_news(limit=50)

            for article in news_articles:
                # Check if article already exists
                existing = await db.execute(
                    select(NewsRecord).where(NewsRecord.url == article["url"])
                )
                if existing.scalar_one_or_none():
                    continue

                news_record = NewsRecord(
                    title=article["title"],
                    summary=article.get("summary"),
                    url=article["url"],
                    source=article["source"],
                    published_at=article.get("published_at"),
                    importance_score=article.get("importance_score", 0.5),
                    sentiment=article.get("sentiment"),
                    categories=article.get("categories"),
                )
                db.add(news_record)
                results["news_count"] += 1

            await db.commit()
            logger.info(f"Saved {results['news_count']} new articles")
        except Exception as e:
            logger.error(f"News scraping error: {e}")
            results["errors"].append(f"News scrape failed: {str(e)}")

        return results

    async def _enrich_price_data(
        self, price_data: Dict[str, Any], db: AsyncSession
    ) -> Dict[str, Any]:
        """Enrich price data with historical comparisons."""
        current_price = price_data["price_usd"]

        # Get price from 7 days ago
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(PriceRecord)
            .where(PriceRecord.timestamp >= week_ago)
            .order_by(PriceRecord.timestamp)
            .limit(1)
        )
        week_price = result.scalar_one_or_none()
        if week_price:
            price_data["price_change_7d"] = current_price - week_price.price_usd

        # Get price from 30 days ago
        month_ago = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(
            select(PriceRecord)
            .where(PriceRecord.timestamp >= month_ago)
            .order_by(PriceRecord.timestamp)
            .limit(1)
        )
        month_price = result.scalar_one_or_none()
        if month_price:
            price_data["price_change_30d"] = current_price - month_price.price_usd

        return price_data

    async def get_latest_price(self, db: AsyncSession) -> Optional[PriceRecord]:
        """Get the most recent price record."""
        result = await db.execute(
            select(PriceRecord).order_by(desc(PriceRecord.timestamp)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_price_history(
        self, db: AsyncSession, days: int = 30
    ) -> List[PriceRecord]:
        """Get price history for the specified number of days."""
        start_date = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(PriceRecord)
            .where(PriceRecord.timestamp >= start_date)
            .order_by(PriceRecord.timestamp)
        )
        return result.scalars().all()

    async def get_52_week_stats(self, db: AsyncSession) -> Dict[str, float]:
        """Get 52-week high and low from database."""
        year_ago = datetime.utcnow() - timedelta(days=365)

        # Get max price
        from sqlalchemy import func
        result = await db.execute(
            select(func.max(PriceRecord.price_usd))
            .where(PriceRecord.timestamp >= year_ago)
        )
        high_52 = result.scalar()

        # Get min price
        result = await db.execute(
            select(func.min(PriceRecord.price_usd))
            .where(PriceRecord.timestamp >= year_ago)
        )
        low_52 = result.scalar()

        # If no data in DB, try scraping
        if not high_52 or not low_52:
            scraped_stats = await self.price_scraper.get_52_week_stats()
            if scraped_stats:
                return scraped_stats

        return {
            "high_52_week": high_52,
            "low_52_week": low_52,
        }

    async def get_latest_news(
        self, db: AsyncSession, limit: int = 20
    ) -> List[NewsRecord]:
        """Get latest news articles."""
        result = await db.execute(
            select(NewsRecord)
            .order_by(desc(NewsRecord.importance_score), desc(NewsRecord.published_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_news_by_category(
        self, db: AsyncSession, category: str, limit: int = 10
    ) -> List[NewsRecord]:
        """Get news articles by category."""
        result = await db.execute(
            select(NewsRecord)
            .where(NewsRecord.categories.contains(category))
            .order_by(desc(NewsRecord.published_at))
            .limit(limit)
        )
        return result.scalars().all()
