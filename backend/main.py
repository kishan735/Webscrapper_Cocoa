"""Main FastAPI application for Cocoa Price Tracker."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.config import get_settings
from backend.models.database import init_db, AsyncSessionLocal
from backend.api.routes import router
from backend.api.dashboard import dashboard_router
from backend.scraper import ScraperManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()
scheduler = AsyncIOScheduler()
scraper_manager = ScraperManager()


async def scheduled_scrape():
    """Background task to scrape data periodically."""
    logger.info("Running scheduled scrape...")
    try:
        async with AsyncSessionLocal() as db:
            results = await scraper_manager.run_full_scrape(db)
            logger.info(f"Scrape completed: {results}")
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Cocoa Price Tracker...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Schedule periodic scraping
    scheduler.add_job(
        scheduled_scrape,
        "interval",
        minutes=settings.scrape_interval_minutes,
        id="periodic_scrape",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started (interval: {settings.scrape_interval_minutes} min)")

    # Run initial scrape
    asyncio.create_task(scheduled_scrape())

    yield

    # Shutdown
    scheduler.shutdown()
    logger.info("Cocoa Price Tracker stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Real-time cocoa commodity price tracking and analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "api": "/api/v1",
            "dashboard": "/api/dashboard",
            "docs": "/docs",
        },
    }


@app.get("/status")
async def status():
    """Application status endpoint."""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
