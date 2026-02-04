"""Database configuration and models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class PriceRecord(Base):
    """Historical price data for cocoa."""

    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    price_usd = Column(Float, nullable=False)
    price_change_24h = Column(Float, nullable=True)
    price_change_7d = Column(Float, nullable=True)
    price_change_30d = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    source = Column(String(100), nullable=False)
    market = Column(String(50), default="ICE")  # ICE Futures or other markets


class NewsRecord(Base):
    """News articles related to cocoa."""

    __tablename__ = "news_records"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False, unique=True)
    source = Column(String(200), nullable=False)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    importance_score = Column(Float, default=0.5)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    categories = Column(String(500), nullable=True)  # JSON array as string


class MarketFactorRecord(Base):
    """Market factors affecting cocoa prices."""

    __tablename__ = "market_factors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # weather, supply, demand, geopolitical, etc.
    impact_score = Column(Float, default=0.5)  # -1 to 1, negative = bearish, positive = bullish
    confidence = Column(Float, default=0.5)  # 0 to 1
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisRecord(Base):
    """AI-generated analysis reports."""

    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    current_price = Column(Float, nullable=False)
    price_vs_week = Column(Float, nullable=True)
    price_vs_month = Column(Float, nullable=True)
    high_52_week = Column(Float, nullable=True)
    low_52_week = Column(Float, nullable=True)
    market_overview = Column(Text, nullable=True)
    market_outlook = Column(Text, nullable=True)
    key_factors = Column(Text, nullable=True)  # JSON array as string
    recommendation = Column(String(50), nullable=True)  # bullish, bearish, neutral


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
