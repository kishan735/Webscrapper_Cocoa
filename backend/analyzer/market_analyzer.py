"""Market analyzer for technical and fundamental analysis."""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analyzes market data for technical indicators and trends."""

    def __init__(self):
        pass

    def calculate_technical_indicators(
        self, prices: List[float], timestamps: List[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate technical indicators from price data."""
        if not prices or len(prices) < 2:
            return {}

        prices_array = np.array(prices)

        indicators = {
            "current_price": prices[-1],
            "high": float(np.max(prices_array)),
            "low": float(np.min(prices_array)),
            "average": float(np.mean(prices_array)),
            "std_dev": float(np.std(prices_array)),
        }

        # Moving averages
        if len(prices) >= 7:
            indicators["sma_7"] = float(np.mean(prices_array[-7:]))
        if len(prices) >= 20:
            indicators["sma_20"] = float(np.mean(prices_array[-20:]))
        if len(prices) >= 50:
            indicators["sma_50"] = float(np.mean(prices_array[-50:]))

        # Price changes
        indicators["change_1d"] = self._calculate_change(prices, 1)
        indicators["change_7d"] = self._calculate_change(prices, 7)
        indicators["change_30d"] = self._calculate_change(prices, 30)

        # Volatility (standard deviation of returns)
        if len(prices) >= 20:
            returns = np.diff(prices_array[-20:]) / prices_array[-21:-1]
            indicators["volatility_20d"] = float(np.std(returns) * np.sqrt(252))  # Annualized

        # RSI (Relative Strength Index)
        if len(prices) >= 15:
            indicators["rsi_14"] = self._calculate_rsi(prices_array, 14)

        # Trend direction
        indicators["trend"] = self._determine_trend(prices_array)

        # Support and resistance levels
        if len(prices) >= 20:
            indicators["support"] = self._find_support(prices_array)
            indicators["resistance"] = self._find_resistance(prices_array)

        return indicators

    def analyze_price_position(
        self, current_price: float, high_52: float, low_52: float
    ) -> Dict[str, Any]:
        """Analyze current price position within 52-week range."""
        if not high_52 or not low_52:
            return {}

        range_52 = high_52 - low_52
        position_in_range = (current_price - low_52) / range_52 if range_52 > 0 else 0.5

        return {
            "high_52_week": high_52,
            "low_52_week": low_52,
            "range_52_week": range_52,
            "position_in_range": round(position_in_range, 3),
            "percent_from_high": round((current_price - high_52) / high_52 * 100, 2),
            "percent_from_low": round((current_price - low_52) / low_52 * 100, 2),
            "range_position": self._classify_range_position(position_in_range),
        }

    def generate_price_summary(
        self, price_data: Dict[str, Any], indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive price summary."""
        current = price_data.get("price_usd", 0)

        summary = {
            "current_price": current,
            "formatted_price": f"${current:,.2f}",
            "currency": "USD",
            "unit": "per metric ton",
            "timestamp": price_data.get("timestamp", datetime.utcnow()),
        }

        # Add changes
        if "change_1d" in indicators:
            summary["change_24h"] = {
                "absolute": indicators["change_1d"],
                "percent": indicators["change_1d"] / (current - indicators["change_1d"]) * 100 if current != indicators["change_1d"] else 0,
            }

        if "change_7d" in indicators:
            summary["change_7d"] = {
                "absolute": indicators["change_7d"],
                "percent": indicators["change_7d"] / (current - indicators["change_7d"]) * 100 if current != indicators["change_7d"] else 0,
            }

        # Add technical data
        summary["technical"] = {
            "trend": indicators.get("trend", "unknown"),
            "volatility": indicators.get("volatility_20d"),
            "rsi": indicators.get("rsi_14"),
            "sma_20": indicators.get("sma_20"),
        }

        # Add 52-week data if available
        if "high_52_week" in indicators:
            summary["range_52_week"] = {
                "high": indicators["high_52_week"],
                "low": indicators["low_52_week"],
                "position": indicators.get("position_in_range"),
            }

        return summary

    def _calculate_change(self, prices: List[float], periods: int) -> float:
        """Calculate price change over specified periods."""
        if len(prices) <= periods:
            return 0
        return prices[-1] - prices[-periods - 1]

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0  # Neutral

        deltas = np.diff(prices[-(period + 1):])
        gains = deltas.copy()
        losses = deltas.copy()

        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)

        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(float(rsi), 2)

    def _determine_trend(self, prices: np.ndarray) -> str:
        """Determine current price trend."""
        if len(prices) < 10:
            return "insufficient_data"

        # Compare short-term and long-term averages
        short_ma = np.mean(prices[-5:])
        long_ma = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)

        # Also check recent price action
        recent_change = (prices[-1] - prices[-5]) / prices[-5]

        if short_ma > long_ma * 1.02 and recent_change > 0.01:
            return "strong_uptrend"
        elif short_ma > long_ma:
            return "uptrend"
        elif short_ma < long_ma * 0.98 and recent_change < -0.01:
            return "strong_downtrend"
        elif short_ma < long_ma:
            return "downtrend"
        else:
            return "sideways"

    def _find_support(self, prices: np.ndarray) -> float:
        """Find support level from recent price data."""
        recent_lows = []
        window = 5

        for i in range(window, len(prices) - window):
            if prices[i] == min(prices[i - window:i + window + 1]):
                recent_lows.append(prices[i])

        if recent_lows:
            return float(np.mean(recent_lows[-3:]))
        return float(np.min(prices[-20:]))

    def _find_resistance(self, prices: np.ndarray) -> float:
        """Find resistance level from recent price data."""
        recent_highs = []
        window = 5

        for i in range(window, len(prices) - window):
            if prices[i] == max(prices[i - window:i + window + 1]):
                recent_highs.append(prices[i])

        if recent_highs:
            return float(np.mean(recent_highs[-3:]))
        return float(np.max(prices[-20:]))

    def _classify_range_position(self, position: float) -> str:
        """Classify position within 52-week range."""
        if position >= 0.9:
            return "near_52_week_high"
        elif position >= 0.7:
            return "upper_range"
        elif position >= 0.3:
            return "mid_range"
        elif position >= 0.1:
            return "lower_range"
        else:
            return "near_52_week_low"
