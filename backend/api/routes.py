"""API routes for Cocoa Price Tracker."""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.models.database import (
    get_db, PriceRecord, NewsRecord, MarketFactorRecord, AnalysisRecord
)
from backend.models.schemas import (
    PriceData, NewsArticle, MarketFactor, AnalysisReport
)
from backend.scraper import ScraperManager
from backend.analyzer import ImportanceAnalyzer, AIAnalyzer, MarketAnalyzer

router = APIRouter(prefix="/api/v1", tags=["api"])

# Initialize services
scraper_manager = ScraperManager()
importance_analyzer = ImportanceAnalyzer()
ai_analyzer = AIAnalyzer()
market_analyzer = MarketAnalyzer()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/price/current")
async def get_current_price(db: AsyncSession = Depends(get_db)):
    """Get the current cocoa price."""
    # Try to get from database first (within last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(PriceRecord)
        .where(PriceRecord.timestamp >= one_hour_ago)
        .order_by(desc(PriceRecord.timestamp))
        .limit(1)
    )
    price_record = result.scalar_one_or_none()

    if price_record:
        return {
            "price_usd": price_record.price_usd,
            "change_24h": price_record.price_change_24h,
            "change_7d": price_record.price_change_7d,
            "change_30d": price_record.price_change_30d,
            "source": price_record.source,
            "market": price_record.market,
            "timestamp": price_record.timestamp.isoformat(),
            "cached": True,
        }

    # Fetch fresh data
    price_data = await scraper_manager.price_scraper.get_current_price()
    if not price_data:
        raise HTTPException(status_code=503, detail="Unable to fetch current price")

    return {
        **price_data,
        "timestamp": datetime.utcnow().isoformat(),
        "cached": False,
    }


@router.get("/price/history")
async def get_price_history(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get historical price data."""
    start_date = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(PriceRecord)
        .where(PriceRecord.timestamp >= start_date)
        .order_by(PriceRecord.timestamp)
    )
    records = result.scalars().all()

    return {
        "period_days": days,
        "data_points": len(records),
        "prices": [
            {
                "timestamp": r.timestamp.isoformat(),
                "price_usd": r.price_usd,
                "source": r.source,
            }
            for r in records
        ],
    }


@router.get("/price/stats")
async def get_price_stats(db: AsyncSession = Depends(get_db)):
    """Get price statistics including 52-week high/low."""
    stats = await scraper_manager.get_52_week_stats(db)

    # Get latest price
    latest = await scraper_manager.get_latest_price(db)

    if latest and stats:
        position = market_analyzer.analyze_price_position(
            latest.price_usd,
            stats.get("high_52_week", 0),
            stats.get("low_52_week", 0)
        )
        stats.update(position)

    return stats or {"message": "Insufficient data for statistics"}


@router.get("/news", response_model=List[NewsArticle])
async def get_news(
    limit: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get latest news articles."""
    query = select(NewsRecord).order_by(
        desc(NewsRecord.importance_score),
        desc(NewsRecord.published_at)
    ).limit(limit)

    if category:
        query = query.where(NewsRecord.categories.contains(category))

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/news/{news_id}")
async def get_news_article(news_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific news article with analysis."""
    result = await db.execute(
        select(NewsRecord).where(NewsRecord.id == news_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Analyze impact
    impact_analysis = await ai_analyzer.analyze_news_impact({
        "title": article.title,
        "summary": article.summary,
        "source": article.source,
    })

    return {
        "article": article,
        "impact_analysis": impact_analysis,
    }


@router.get("/factors")
async def get_market_factors(db: AsyncSession = Depends(get_db)):
    """Get current market factors affecting cocoa prices."""
    result = await db.execute(
        select(MarketFactorRecord)
        .where(MarketFactorRecord.is_active == True)
        .order_by(desc(MarketFactorRecord.impact_score))
    )
    factors = result.scalars().all()

    if not factors:
        # Return default factors if none in database
        default_factors = [
            {
                "name": "West African Weather",
                "category": "supply",
                "description": "Weather conditions in Ivory Coast and Ghana",
                "impact_score": 0.8,
            },
            {
                "name": "Global Chocolate Demand",
                "category": "demand",
                "description": "Consumer demand for chocolate products",
                "impact_score": 0.6,
            },
            {
                "name": "Currency Movements",
                "category": "market",
                "description": "USD strength affecting commodity prices",
                "impact_score": 0.5,
            },
        ]
        return {"factors": default_factors, "source": "default"}

    return {
        "factors": [
            {
                "id": f.id,
                "name": f.name,
                "category": f.category,
                "description": f.description,
                "impact_score": f.impact_score,
                "confidence": f.confidence,
                "updated_at": f.updated_at.isoformat(),
            }
            for f in factors
        ],
        "source": "database",
    }


@router.get("/analysis/overview")
async def get_market_overview(db: AsyncSession = Depends(get_db)):
    """Get comprehensive market overview."""
    # Get latest price
    latest_price = await scraper_manager.get_latest_price(db)
    if not latest_price:
        # Fetch fresh data
        price_data = await scraper_manager.price_scraper.get_current_price()
        if not price_data:
            raise HTTPException(status_code=503, detail="Unable to fetch price data")
        current_price = price_data["price_usd"]
    else:
        current_price = latest_price.price_usd

    # Get price changes
    stats = await scraper_manager.get_52_week_stats(db)
    price_changes = {
        "24h": latest_price.price_change_24h if latest_price else 0,
        "7d": latest_price.price_change_7d if latest_price else 0,
        "30d": latest_price.price_change_30d if latest_price else 0,
        "high_52": stats.get("high_52_week") if stats else None,
        "low_52": stats.get("low_52_week") if stats else None,
    }

    # Get recent news
    news_result = await db.execute(
        select(NewsRecord)
        .order_by(desc(NewsRecord.importance_score))
        .limit(10)
    )
    recent_news = [
        {"title": n.title, "summary": n.summary, "sentiment": n.sentiment, "source": n.source}
        for n in news_result.scalars().all()
    ]

    # Get market factors
    factors_result = await db.execute(
        select(MarketFactorRecord).where(MarketFactorRecord.is_active == True)
    )
    market_factors = [
        {"name": f.name, "impact_score": f.impact_score, "category": f.category}
        for f in factors_result.scalars().all()
    ]

    # Generate AI overview
    overview = await ai_analyzer.generate_market_overview(
        current_price, price_changes, recent_news, market_factors
    )

    return {
        "current_price": current_price,
        "price_changes": price_changes,
        "overview": overview,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/analysis/outlook")
async def get_market_outlook(db: AsyncSession = Depends(get_db)):
    """Get forward-looking market outlook."""
    # Get current data
    latest_price = await scraper_manager.get_latest_price(db)
    current_price = latest_price.price_usd if latest_price else 0

    # Calculate sentiment from news
    news_result = await db.execute(
        select(NewsRecord).order_by(desc(NewsRecord.published_at)).limit(20)
    )
    news_list = [
        {"sentiment": n.sentiment, "importance_score": n.importance_score}
        for n in news_result.scalars().all()
    ]

    sentiment_data = importance_analyzer.calculate_aggregate_sentiment(news_list, [])

    # Get factors
    factors_result = await db.execute(
        select(MarketFactorRecord).where(MarketFactorRecord.is_active == True)
    )
    factors = [
        {"name": f.name, "impact_score": f.impact_score}
        for f in factors_result.scalars().all()
    ]

    # Generate outlook
    outlook = await ai_analyzer.generate_market_outlook(
        {
            "price": current_price,
            "trend": "stable",
            "sentiment": sentiment_data.get("sentiment", "neutral"),
        },
        [],
        factors
    )

    return {
        "outlook": outlook,
        "sentiment": sentiment_data,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/analysis/digest")
async def get_daily_digest(db: AsyncSession = Depends(get_db)):
    """Get daily market digest."""
    # Get price data
    latest = await scraper_manager.get_latest_price(db)
    stats = await scraper_manager.get_52_week_stats(db)

    price_data = {
        "current": latest.price_usd if latest else 0,
        "change_24h": latest.price_change_24h if latest else 0,
        "high_52": stats.get("high_52_week") if stats else 0,
        "low_52": stats.get("low_52_week") if stats else 0,
    }

    # Get news
    news_result = await db.execute(
        select(NewsRecord)
        .order_by(desc(NewsRecord.importance_score))
        .limit(5)
    )
    news_articles = [
        {"title": n.title, "summary": n.summary, "source": n.source}
        for n in news_result.scalars().all()
    ]

    # Generate digest
    digest = await ai_analyzer.generate_daily_digest(price_data, news_articles, [])

    return {
        "digest": digest,
        "price_data": price_data,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/scrape/trigger")
async def trigger_scrape(db: AsyncSession = Depends(get_db)):
    """Manually trigger a data scrape."""
    results = await scraper_manager.run_full_scrape(db)
    return {
        "status": "completed",
        "results": results,
    }
