"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class PriceDataBase(BaseModel):
    """Base schema for price data."""
    price_usd: float
    price_change_24h: Optional[float] = None
    price_change_7d: Optional[float] = None
    price_change_30d: Optional[float] = None
    volume: Optional[float] = None
    source: str
    market: str = "ICE"


class PriceDataCreate(PriceDataBase):
    """Schema for creating price records."""
    pass


class PriceData(PriceDataBase):
    """Schema for price data response."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class NewsArticleBase(BaseModel):
    """Base schema for news articles."""
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: str
    published_at: Optional[datetime] = None


class NewsArticleCreate(NewsArticleBase):
    """Schema for creating news articles."""
    pass


class NewsArticle(NewsArticleBase):
    """Schema for news article response."""
    id: int
    fetched_at: datetime
    importance_score: float
    sentiment: Optional[str] = None
    categories: Optional[str] = None

    class Config:
        from_attributes = True


class MarketFactorBase(BaseModel):
    """Base schema for market factors."""
    name: str
    description: Optional[str] = None
    category: str
    impact_score: float = 0.5
    confidence: float = 0.5


class MarketFactorCreate(MarketFactorBase):
    """Schema for creating market factors."""
    pass


class MarketFactor(MarketFactorBase):
    """Schema for market factor response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PriceComparison(BaseModel):
    """Price comparison data."""
    current: float
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None
    change_30d: Optional[float] = None
    change_ytd: Optional[float] = None
    high_52_week: Optional[float] = None
    low_52_week: Optional[float] = None
    percent_from_high: Optional[float] = None
    percent_from_low: Optional[float] = None


class MarketOverview(BaseModel):
    """Market overview summary."""
    summary: str
    key_events: List[str]
    sentiment: str  # bullish, bearish, neutral


class MarketOutlook(BaseModel):
    """Market outlook and trends."""
    summary: str
    trends_to_watch: List[str]
    risk_factors: List[str]
    opportunities: List[str]


class AnalysisReport(BaseModel):
    """Complete analysis report."""
    timestamp: datetime
    price_comparison: PriceComparison
    market_overview: MarketOverview
    market_outlook: MarketOutlook
    key_factors: List[MarketFactor]
    latest_news: List[NewsArticle]
    overall_sentiment: str
    confidence_score: float


class DashboardData(BaseModel):
    """Dashboard data for frontend."""
    current_price: float
    price_change_24h: Optional[float] = None
    price_change_percent_24h: Optional[float] = None
    high_52_week: Optional[float] = None
    low_52_week: Optional[float] = None
    market_sentiment: str
    last_updated: datetime
    quick_stats: dict
