"""Dashboard API endpoints for the frontend."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from backend.models.database import get_db, PriceRecord, NewsRecord, MarketFactorRecord
from backend.models.schemas import DashboardData
from backend.scraper import ScraperManager
from backend.analyzer import ImportanceAnalyzer, AIAnalyzer, MarketAnalyzer

dashboard_router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

scraper_manager = ScraperManager()
importance_analyzer = ImportanceAnalyzer()
ai_analyzer = AIAnalyzer()
market_analyzer = MarketAnalyzer()


@dashboard_router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get complete dashboard summary for frontend."""

    # Get latest price
    latest_price = await scraper_manager.get_latest_price(db)

    # If no data, try fetching fresh
    if not latest_price:
        price_data = await scraper_manager.price_scraper.get_current_price()
        if price_data:
            current_price = price_data["price_usd"]
            change_24h = price_data.get("price_change_24h", 0)
        else:
            current_price = 0
            change_24h = 0
    else:
        current_price = latest_price.price_usd
        change_24h = latest_price.price_change_24h or 0

    # Get 52-week stats
    stats = await scraper_manager.get_52_week_stats(db)
    high_52 = stats.get("high_52_week") if stats else None
    low_52 = stats.get("low_52_week") if stats else None

    # Calculate percent change
    change_percent = (change_24h / (current_price - change_24h) * 100) if current_price and change_24h else 0

    # Get recent news count
    week_ago = datetime.utcnow() - timedelta(days=7)
    news_count = await db.execute(
        select(func.count(NewsRecord.id)).where(NewsRecord.fetched_at >= week_ago)
    )
    news_this_week = news_count.scalar() or 0

    # Calculate sentiment
    news_result = await db.execute(
        select(NewsRecord).order_by(desc(NewsRecord.published_at)).limit(20)
    )
    news_list = [
        {"sentiment": n.sentiment, "importance_score": n.importance_score}
        for n in news_result.scalars().all()
    ]
    sentiment_data = importance_analyzer.calculate_aggregate_sentiment(news_list, [])

    return {
        "price": {
            "current": current_price,
            "formatted": f"${current_price:,.2f}" if current_price else "N/A",
            "change_24h": change_24h,
            "change_percent_24h": round(change_percent, 2),
            "high_52_week": high_52,
            "low_52_week": low_52,
            "currency": "USD",
            "unit": "per metric ton",
        },
        "market": {
            "sentiment": sentiment_data.get("sentiment", "neutral"),
            "confidence": sentiment_data.get("confidence", 0),
            "bullish_signals": sentiment_data.get("bullish_signals", 0),
            "bearish_signals": sentiment_data.get("bearish_signals", 0),
        },
        "stats": {
            "news_this_week": news_this_week,
            "data_freshness": latest_price.timestamp.isoformat() if latest_price else None,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@dashboard_router.get("/price-chart")
async def get_price_chart_data(
    period: str = "30d",
    db: AsyncSession = Depends(get_db)
):
    """Get price data for chart visualization."""

    # Parse period
    period_days = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365,
    }.get(period, 30)

    start_date = datetime.utcnow() - timedelta(days=period_days)

    result = await db.execute(
        select(PriceRecord)
        .where(PriceRecord.timestamp >= start_date)
        .order_by(PriceRecord.timestamp)
    )
    records = result.scalars().all()

    # Format for chart
    chart_data = [
        {
            "timestamp": r.timestamp.isoformat(),
            "date": r.timestamp.strftime("%Y-%m-%d"),
            "price": r.price_usd,
        }
        for r in records
    ]

    # Calculate min/max for chart scaling
    prices = [r.price_usd for r in records] if records else [0]

    return {
        "period": period,
        "data_points": len(chart_data),
        "data": chart_data,
        "range": {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices) if prices else 0,
        },
    }


@dashboard_router.get("/news-feed")
async def get_news_feed(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get news feed for dashboard."""

    result = await db.execute(
        select(NewsRecord)
        .order_by(desc(NewsRecord.importance_score), desc(NewsRecord.published_at))
        .limit(limit)
    )
    articles = result.scalars().all()

    return {
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary[:200] + "..." if a.summary and len(a.summary) > 200 else a.summary,
                "url": a.url,
                "source": a.source,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "importance_score": a.importance_score,
                "sentiment": a.sentiment,
                "sentiment_color": _get_sentiment_color(a.sentiment),
                "categories": a.categories.split(",") if a.categories else [],
            }
            for a in articles
        ],
        "count": len(articles),
    }


@dashboard_router.get("/key-factors")
async def get_key_factors(db: AsyncSession = Depends(get_db)):
    """Get key market factors for dashboard display."""

    result = await db.execute(
        select(MarketFactorRecord)
        .where(MarketFactorRecord.is_active == True)
        .order_by(desc(func.abs(MarketFactorRecord.impact_score)))
        .limit(5)
    )
    factors = result.scalars().all()

    if not factors:
        # Return default factors
        return {
            "factors": [
                {
                    "name": "West African Weather",
                    "category": "supply",
                    "impact": "high",
                    "direction": "bullish",
                    "description": "Dry conditions in Ivory Coast affecting yields",
                },
                {
                    "name": "European Demand",
                    "category": "demand",
                    "impact": "medium",
                    "direction": "bullish",
                    "description": "Strong chocolate demand ahead of Easter",
                },
                {
                    "name": "USD Strength",
                    "category": "market",
                    "impact": "medium",
                    "direction": "bearish",
                    "description": "Strong dollar pressuring commodity prices",
                },
            ],
            "source": "default",
        }

    return {
        "factors": [
            {
                "id": f.id,
                "name": f.name,
                "category": f.category,
                "impact": _classify_impact(f.impact_score),
                "direction": "bullish" if f.impact_score > 0 else "bearish",
                "impact_score": f.impact_score,
                "confidence": f.confidence,
                "description": f.description,
            }
            for f in factors
        ],
        "source": "database",
    }


@dashboard_router.get("/quick-analysis")
async def get_quick_analysis(db: AsyncSession = Depends(get_db)):
    """Get quick AI-generated analysis for dashboard."""

    # Get latest price
    latest = await scraper_manager.get_latest_price(db)
    current_price = latest.price_usd if latest else 0

    # Get recent news
    news_result = await db.execute(
        select(NewsRecord)
        .order_by(desc(NewsRecord.importance_score))
        .limit(5)
    )
    news = [
        {"title": n.title, "summary": n.summary, "source": n.source}
        for n in news_result.scalars().all()
    ]

    # Generate quick overview
    price_data = {
        "current": current_price,
        "change_24h": latest.price_change_24h if latest else 0,
        "high_52": 0,
        "low_52": 0,
    }

    digest = await ai_analyzer.generate_daily_digest(price_data, news, [])

    return {
        "analysis": digest,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _get_sentiment_color(sentiment: str) -> str:
    """Get color for sentiment display."""
    colors = {
        "positive": "#22c55e",  # green
        "negative": "#ef4444",  # red
        "neutral": "#6b7280",   # gray
    }
    return colors.get(sentiment, colors["neutral"])


def _classify_impact(score: float) -> str:
    """Classify impact level."""
    abs_score = abs(score)
    if abs_score >= 0.7:
        return "high"
    elif abs_score >= 0.4:
        return "medium"
    return "low"
