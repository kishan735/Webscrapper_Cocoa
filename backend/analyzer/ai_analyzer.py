"""AI-powered analyzer for generating market insights."""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from openai import AsyncOpenAI

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AIAnalyzer:
    """AI-powered analysis and consolidation of market data."""

    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

        self.system_prompt = """You are an expert commodity market analyst specializing in cocoa.
Your role is to analyze market data, news, and factors to provide clear, actionable insights.

Guidelines:
- Be concise and factual
- Focus on price-relevant information
- Highlight key risks and opportunities
- Use professional market terminology
- Always cite the factors driving your analysis
- Express uncertainty when data is limited"""

    async def generate_market_overview(
        self,
        current_price: float,
        price_changes: Dict[str, float],
        recent_news: List[Dict[str, Any]],
        market_factors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate comprehensive market overview."""

        if not self.client:
            return self._generate_fallback_overview(
                current_price, price_changes, recent_news, market_factors
            )

        # Prepare context
        news_summary = self._summarize_news(recent_news[:10])
        factors_summary = self._summarize_factors(market_factors)

        prompt = f"""Analyze the current cocoa market situation:

CURRENT PRICE: ${current_price:,.2f} per metric ton

PRICE CHANGES:
- 24h: {price_changes.get('24h', 'N/A')}%
- 7d: {price_changes.get('7d', 'N/A')}%
- 30d: {price_changes.get('30d', 'N/A')}%
- 52-week high: ${price_changes.get('high_52', 'N/A')}
- 52-week low: ${price_changes.get('low_52', 'N/A')}

RECENT NEWS:
{news_summary}

MARKET FACTORS:
{factors_summary}

Provide analysis in the following JSON format:
{{
    "market_summary": "2-3 sentence summary of current market state",
    "key_events": ["list of 3-5 key events affecting the market"],
    "price_drivers": ["list of main factors driving current prices"],
    "sentiment": "bullish/bearish/neutral",
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"AI overview generation failed: {e}")
            return self._generate_fallback_overview(
                current_price, price_changes, recent_news, market_factors
            )

    async def generate_market_outlook(
        self,
        current_data: Dict[str, Any],
        historical_trend: List[Dict[str, Any]],
        market_factors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate forward-looking market outlook."""

        if not self.client:
            return self._generate_fallback_outlook(market_factors)

        factors_summary = self._summarize_factors(market_factors)

        prompt = f"""Based on current cocoa market conditions, provide a forward-looking outlook:

CURRENT PRICE: ${current_data.get('price', 0):,.2f}
RECENT TREND: {current_data.get('trend', 'stable')}
MARKET SENTIMENT: {current_data.get('sentiment', 'neutral')}

KEY FACTORS:
{factors_summary}

Provide outlook in the following JSON format:
{{
    "outlook_summary": "2-3 sentence forward outlook",
    "trends_to_watch": ["list of 3-5 trends to monitor"],
    "risk_factors": ["list of key risks"],
    "opportunities": ["list of potential opportunities"],
    "short_term_bias": "bullish/bearish/neutral",
    "medium_term_bias": "bullish/bearish/neutral"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1000,
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"AI outlook generation failed: {e}")
            return self._generate_fallback_outlook(market_factors)

    async def analyze_news_impact(
        self, news_article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze potential price impact of a news article."""

        if not self.client:
            return {
                "impact_assessment": "Analysis unavailable",
                "price_impact": "neutral",
                "confidence": 0.5,
            }

        prompt = f"""Analyze this cocoa market news for price impact:

TITLE: {news_article.get('title', '')}
CONTENT: {news_article.get('summary', '')[:500]}
SOURCE: {news_article.get('source', '')}

Provide analysis in JSON format:
{{
    "impact_assessment": "Brief assessment of market impact",
    "price_impact": "bullish/bearish/neutral",
    "magnitude": "low/medium/high",
    "confidence": 0.0-1.0,
    "affected_factors": ["list of affected market factors"]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"AI news analysis failed: {e}")
            return {
                "impact_assessment": "Analysis unavailable",
                "price_impact": "neutral",
                "confidence": 0.5,
            }

    async def generate_daily_digest(
        self,
        price_data: Dict[str, Any],
        news_articles: List[Dict[str, Any]],
        market_factors: List[Dict[str, Any]],
    ) -> str:
        """Generate a daily market digest."""

        if not self.client:
            return self._generate_fallback_digest(price_data, news_articles)

        news_summary = self._summarize_news(news_articles[:5])

        prompt = f"""Create a concise daily cocoa market digest:

PRICE: ${price_data.get('current', 0):,.2f}
24H CHANGE: {price_data.get('change_24h', 0):.2f}%
52W RANGE: ${price_data.get('low_52', 0):,.2f} - ${price_data.get('high_52', 0):,.2f}

TOP NEWS:
{news_summary}

Write a 150-200 word market digest covering:
1. Current price action
2. Key news and developments
3. What to watch today
Keep it professional and actionable."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=400,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI digest generation failed: {e}")
            return self._generate_fallback_digest(price_data, news_articles)

    def _summarize_news(self, news_articles: List[Dict[str, Any]]) -> str:
        """Create text summary of news articles."""
        if not news_articles:
            return "No recent news available."

        summaries = []
        for article in news_articles[:5]:
            title = article.get("title", "Untitled")
            source = article.get("source", "Unknown")
            sentiment = article.get("sentiment", "neutral")
            summaries.append(f"- [{sentiment.upper()}] {title} ({source})")

        return "\n".join(summaries)

    def _summarize_factors(self, factors: List[Dict[str, Any]]) -> str:
        """Create text summary of market factors."""
        if not factors:
            return "No significant factors identified."

        summaries = []
        for factor in factors[:5]:
            name = factor.get("name", factor.get("factor_name", "Unknown"))
            impact = factor.get("impact_score", 0)
            direction = "bullish" if impact > 0 else "bearish" if impact < 0 else "neutral"
            summaries.append(f"- {name}: {direction} (impact: {abs(impact):.2f})")

        return "\n".join(summaries)

    def _generate_fallback_overview(
        self,
        current_price: float,
        price_changes: Dict[str, float],
        recent_news: List[Dict[str, Any]],
        market_factors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate overview without AI when API unavailable."""
        change_24h = price_changes.get("24h", 0)
        trend = "up" if change_24h > 0 else "down" if change_24h < 0 else "flat"

        # Count sentiment from news
        positive = sum(1 for n in recent_news if n.get("sentiment") == "positive")
        negative = sum(1 for n in recent_news if n.get("sentiment") == "negative")

        sentiment = "bullish" if positive > negative else "bearish" if negative > positive else "neutral"

        key_events = [n.get("title", "") for n in recent_news[:3]]

        return {
            "market_summary": f"Cocoa is trading at ${current_price:,.2f}, {trend} {abs(change_24h):.1f}% in the last 24 hours. Market sentiment appears {sentiment}.",
            "key_events": key_events,
            "price_drivers": [f.get("name", "") for f in market_factors[:3]],
            "sentiment": sentiment,
            "confidence": 0.6,
        }

    def _generate_fallback_outlook(
        self, market_factors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate outlook without AI when API unavailable."""
        bullish_factors = [f for f in market_factors if f.get("impact_score", 0) > 0]
        bearish_factors = [f for f in market_factors if f.get("impact_score", 0) < 0]

        bias = "bullish" if len(bullish_factors) > len(bearish_factors) else "bearish" if len(bearish_factors) > len(bullish_factors) else "neutral"

        return {
            "outlook_summary": f"Based on current factors, the near-term outlook appears {bias}.",
            "trends_to_watch": ["West African weather patterns", "Global chocolate demand", "Currency movements"],
            "risk_factors": ["Supply disruptions", "Regulatory changes", "Economic slowdown"],
            "opportunities": ["Seasonal price patterns", "Supply chain improvements"],
            "short_term_bias": bias,
            "medium_term_bias": "neutral",
        }

    def _generate_fallback_digest(
        self, price_data: Dict[str, Any], news_articles: List[Dict[str, Any]]
    ) -> str:
        """Generate digest without AI when API unavailable."""
        price = price_data.get("current", 0)
        change = price_data.get("change_24h", 0)

        digest = f"""COCOA DAILY DIGEST

Current Price: ${price:,.2f}
24h Change: {change:+.2f}%

TOP HEADLINES:
"""
        for article in news_articles[:3]:
            digest += f"• {article.get('title', 'No title')}\n"

        digest += "\nStay informed and trade wisely."
        return digest
