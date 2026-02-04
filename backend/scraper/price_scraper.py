"""Price scraper for cocoa commodity prices using FREE data sources."""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Thread pool for running sync yfinance calls
_executor = ThreadPoolExecutor(max_workers=2)


class PriceScraper:
    """Scraper for cocoa price data from multiple FREE sources."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.timeout = httpx.Timeout(30.0)

    async def get_current_price(self) -> Optional[Dict[str, Any]]:
        """Get current cocoa price from multiple FREE sources."""
        results = await asyncio.gather(
            self._get_yfinance_price(),  # FREE & reliable
            self._scrape_trading_economics(),
            self._scrape_investing_com(),
            self._scrape_business_insider(),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, dict) and result.get("price_usd"):
                return result

        logger.error("Failed to fetch cocoa price from all sources")
        return None

    async def _get_yfinance_price(self) -> Optional[Dict[str, Any]]:
        """Get cocoa price using yfinance (FREE, no API key needed)."""
        try:
            import yfinance as yf

            # Run yfinance in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                _executor,
                self._fetch_yfinance_data
            )
            return result
        except ImportError:
            logger.warning("yfinance not installed, skipping")
            return None
        except Exception as e:
            logger.warning(f"yfinance fetch failed: {e}")
            return None

    def _fetch_yfinance_data(self) -> Optional[Dict[str, Any]]:
        """Synchronous yfinance data fetch."""
        import yfinance as yf

        # CC=F is the cocoa futures ticker on Yahoo Finance
        ticker = yf.Ticker("CC=F")
        hist = ticker.history(period="5d")

        if hist.empty:
            return None

        current_price = float(hist["Close"].iloc[-1])
        prev_price = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price

        change_24h = current_price - prev_price

        # Get 52-week data
        hist_year = ticker.history(period="1y")
        high_52 = float(hist_year["High"].max()) if not hist_year.empty else None
        low_52 = float(hist_year["Low"].min()) if not hist_year.empty else None

        return {
            "price_usd": current_price,
            "price_change_24h": change_24h,
            "high_52_week": high_52,
            "low_52_week": low_52,
            "source": "Yahoo Finance",
            "market": "ICE",
            "timestamp": datetime.utcnow(),
        }

    async def _scrape_trading_economics(self) -> Optional[Dict[str, Any]]:
        """Scrape cocoa price from Trading Economics."""
        url = "https://tradingeconomics.com/commodity/cocoa"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")

                price_elem = soup.select_one("#ctl00_ContentPlaceHolder1_ctl00_ctl01_Price")
                if not price_elem:
                    price_elem = soup.select_one('[data-symbol="CC1:COM"]')

                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._parse_price(price_text)

                    if price:
                        change_elem = soup.select_one(".delta-positive, .delta-negative")
                        change_24h = None
                        if change_elem:
                            change_text = change_elem.get_text(strip=True)
                            change_24h = self._parse_change(change_text)

                        return {
                            "price_usd": price,
                            "price_change_24h": change_24h,
                            "source": "Trading Economics",
                            "market": "ICE",
                            "timestamp": datetime.utcnow(),
                        }
        except Exception as e:
            logger.warning(f"Trading Economics scrape failed: {e}")

        return None

    async def _scrape_investing_com(self) -> Optional[Dict[str, Any]]:
        """Scrape cocoa price from Investing.com."""
        url = "https://www.investing.com/commodities/us-cocoa"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                headers = {**self.headers, "Accept-Encoding": "gzip, deflate"}
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")

                price_elem = soup.select_one('[data-test="instrument-price-last"]')
                if not price_elem:
                    price_elem = soup.select_one(".instrument-price_last__KQzyA")

                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._parse_price(price_text)

                    if price:
                        change_elem = soup.select_one('[data-test="instrument-price-change"]')
                        change_24h = None
                        if change_elem:
                            change_text = change_elem.get_text(strip=True)
                            change_24h = self._parse_change(change_text)

                        return {
                            "price_usd": price,
                            "price_change_24h": change_24h,
                            "source": "Investing.com",
                            "market": "ICE",
                            "timestamp": datetime.utcnow(),
                        }
        except Exception as e:
            logger.warning(f"Investing.com scrape failed: {e}")

        return None

    async def _scrape_business_insider(self) -> Optional[Dict[str, Any]]:
        """Scrape cocoa price from Business Insider Markets."""
        url = "https://markets.businessinsider.com/commodities/cocoa-price"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")

                price_elem = soup.select_one(".price-section__current-value")
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._parse_price(price_text)

                    if price:
                        change_elem = soup.select_one(".price-section__relative-value")
                        change_24h = None
                        if change_elem:
                            change_text = change_elem.get_text(strip=True)
                            change_24h = self._parse_change(change_text)

                        return {
                            "price_usd": price,
                            "price_change_24h": change_24h,
                            "source": "Business Insider",
                            "market": "ICE",
                            "timestamp": datetime.utcnow(),
                        }
        except Exception as e:
            logger.warning(f"Business Insider scrape failed: {e}")

        return None

    async def get_historical_data(self, days: int = 365) -> List[Dict[str, Any]]:
        """Get historical price data for technical analysis."""
        # This would typically use an API or more sophisticated scraping
        # For now, we'll return a placeholder
        return []

    async def get_52_week_stats(self) -> Optional[Dict[str, float]]:
        """Get 52-week high and low prices."""
        url = "https://tradingeconomics.com/commodity/cocoa"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")

                stats = {}
                table = soup.select_one("table.table-hover")
                if table:
                    rows = table.select("tr")
                    for row in rows:
                        cells = row.select("td")
                        if len(cells) >= 2:
                            label = cells[0].get_text(strip=True).lower()
                            value = cells[1].get_text(strip=True)

                            if "52" in label and "high" in label:
                                stats["high_52_week"] = self._parse_price(value)
                            elif "52" in label and "low" in label:
                                stats["low_52_week"] = self._parse_price(value)

                return stats if stats else None
        except Exception as e:
            logger.warning(f"Failed to get 52-week stats: {e}")

        return None

    def _parse_price(self, text: str) -> Optional[float]:
        """Parse price from text string."""
        if not text:
            return None

        # Remove currency symbols and commas
        cleaned = re.sub(r"[^\d.,]", "", text)
        cleaned = cleaned.replace(",", "")

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _parse_change(self, text: str) -> Optional[float]:
        """Parse price change from text string."""
        if not text:
            return None

        # Handle percentage or absolute change
        is_negative = "-" in text or "▼" in text
        cleaned = re.sub(r"[^\d.,]", "", text)
        cleaned = cleaned.replace(",", "")

        try:
            value = float(cleaned)
            return -value if is_negative else value
        except ValueError:
            return None
