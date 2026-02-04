"""Importance analyzer for scoring market factors and news."""

import re
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ImportanceAnalyzer:
    """Analyzes and scores the importance of market factors and news."""

    def __init__(self):
        # Factor weights for cocoa market
        self.factor_weights = {
            # Supply-side factors (most impactful for cocoa)
            "weather_west_africa": 0.95,
            "ivory_coast_production": 0.90,
            "ghana_production": 0.85,
            "harvest_season": 0.80,
            "disease_outbreak": 0.85,

            # Demand-side factors
            "chocolate_demand": 0.70,
            "emerging_market_consumption": 0.65,
            "seasonal_demand": 0.60,

            # Market factors
            "futures_market": 0.75,
            "currency_movements": 0.60,
            "speculation": 0.55,

            # Geopolitical factors
            "government_policy": 0.70,
            "trade_regulations": 0.65,
            "political_stability": 0.75,

            # Other factors
            "shipping_logistics": 0.50,
            "storage_costs": 0.40,
        }

        # Keywords associated with each factor
        self.factor_keywords = {
            "weather_west_africa": [
                "weather", "rain", "drought", "flood", "climate", "el nino",
                "la nina", "harmattan", "dry season", "wet season"
            ],
            "ivory_coast_production": [
                "ivory coast", "cote d'ivoire", "ivorian", "abidjan",
                "ccc", "conseil cafe cacao"
            ],
            "ghana_production": [
                "ghana", "ghanaian", "cocobod", "accra"
            ],
            "harvest_season": [
                "harvest", "main crop", "mid crop", "crop year",
                "planting", "yield", "production forecast"
            ],
            "disease_outbreak": [
                "disease", "swollen shoot", "black pod", "pest",
                "frosty pod", "moniliasis"
            ],
            "chocolate_demand": [
                "chocolate", "confectionery", "consumer demand",
                "retail", "sales", "consumption"
            ],
            "futures_market": [
                "ice futures", "nyse", "london cocoa", "futures contract",
                "forward", "derivative", "options"
            ],
            "government_policy": [
                "government", "policy", "regulation", "subsidy",
                "minimum price", "living income"
            ],
            "trade_regulations": [
                "export", "import", "tariff", "trade", "eu regulation",
                "deforestation"
            ],
            "currency_movements": [
                "dollar", "euro", "cfa franc", "cedi", "exchange rate",
                "currency"
            ],
        }

        # Impact modifiers for sentiment
        self.sentiment_modifiers = {
            "positive": {
                "supply": -0.1,  # More supply = lower prices (negative for bulls)
                "demand": 0.15,  # More demand = higher prices
                "general": 0.1,
            },
            "negative": {
                "supply": 0.15,  # Less supply = higher prices (positive for bulls)
                "demand": -0.1,  # Less demand = lower prices
                "general": -0.1,
            },
            "neutral": {
                "supply": 0,
                "demand": 0,
                "general": 0,
            },
        }

    def analyze_news_importance(self, news_article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze importance of a news article."""
        title = news_article.get("title", "")
        content = news_article.get("content") or news_article.get("summary", "")
        text = f"{title} {content}".lower()

        # Identify factors mentioned
        factors_found = self._identify_factors(text)

        # Calculate base importance score
        base_score = self._calculate_base_score(factors_found)

        # Apply recency modifier
        recency_modifier = self._calculate_recency_modifier(
            news_article.get("published_at")
        )

        # Apply source credibility modifier
        source_modifier = self._get_source_credibility(news_article.get("source", ""))

        # Calculate final importance score
        importance_score = min(
            1.0,
            base_score * recency_modifier * source_modifier
        )

        # Determine impact direction
        impact_direction = self._determine_impact_direction(text, factors_found)

        return {
            "importance_score": round(importance_score, 3),
            "factors": factors_found,
            "impact_direction": impact_direction,
            "recency_modifier": recency_modifier,
            "source_modifier": source_modifier,
        }

    def analyze_market_factor(
        self, factor_name: str, description: str, current_state: str
    ) -> Dict[str, Any]:
        """Analyze a specific market factor."""
        base_weight = self.factor_weights.get(factor_name, 0.5)

        # Analyze current state sentiment
        sentiment = self._analyze_sentiment(current_state)

        # Determine impact on price
        category = self._get_factor_category(factor_name)
        impact_modifier = self.sentiment_modifiers.get(sentiment, {}).get(
            category, 0
        )

        impact_score = base_weight * (1 + impact_modifier)

        return {
            "factor_name": factor_name,
            "base_weight": base_weight,
            "sentiment": sentiment,
            "category": category,
            "impact_score": round(impact_score, 3),
            "price_impact": "bullish" if impact_score > 0.5 else "bearish" if impact_score < -0.5 else "neutral",
        }

    def rank_factors(
        self, factors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank factors by their impact score."""
        return sorted(
            factors,
            key=lambda x: abs(x.get("impact_score", 0)),
            reverse=True
        )

    def calculate_aggregate_sentiment(
        self, news_articles: List[Dict[str, Any]], factors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate aggregate market sentiment from news and factors."""
        if not news_articles and not factors:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "bullish_signals": 0,
                "bearish_signals": 0,
            }

        bullish_score = 0
        bearish_score = 0
        total_weight = 0

        # Analyze news sentiment
        for article in news_articles:
            importance = article.get("importance_score", 0.5)
            sentiment = article.get("sentiment", "neutral")

            if sentiment == "positive":
                bullish_score += importance
            elif sentiment == "negative":
                bearish_score += importance
            total_weight += importance

        # Analyze factor sentiment
        for factor in factors:
            impact = factor.get("impact_score", 0)
            weight = abs(impact)

            if impact > 0:
                bullish_score += weight
            elif impact < 0:
                bearish_score += weight
            total_weight += weight

        # Calculate aggregate
        if total_weight == 0:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "bullish_signals": 0,
                "bearish_signals": 0,
            }

        net_sentiment = (bullish_score - bearish_score) / total_weight
        confidence = min(1.0, total_weight / 10)  # Scale confidence

        if net_sentiment > 0.1:
            sentiment = "bullish"
        elif net_sentiment < -0.1:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "net_score": round(net_sentiment, 3),
            "bullish_signals": int(bullish_score * 10),
            "bearish_signals": int(bearish_score * 10),
        }

    def _identify_factors(self, text: str) -> List[Tuple[str, float]]:
        """Identify market factors mentioned in text."""
        factors = []

        for factor, keywords in self.factor_keywords.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                weight = self.factor_weights.get(factor, 0.5)
                relevance = min(1.0, matches * 0.3)
                factors.append((factor, weight * relevance))

        return factors

    def _calculate_base_score(self, factors: List[Tuple[str, float]]) -> float:
        """Calculate base importance score from identified factors."""
        if not factors:
            return 0.3  # Minimum score for cocoa-related content

        # Use the highest factor weight plus diminishing returns for others
        sorted_factors = sorted(factors, key=lambda x: x[1], reverse=True)
        score = sorted_factors[0][1]

        for factor, weight in sorted_factors[1:]:
            score += weight * 0.2  # Diminishing returns

        return min(1.0, score)

    def _calculate_recency_modifier(self, published_at: datetime = None) -> float:
        """Calculate modifier based on article recency."""
        if not published_at:
            return 0.8  # Unknown date penalty

        age = datetime.utcnow() - published_at
        hours_old = age.total_seconds() / 3600

        if hours_old < 6:
            return 1.0
        elif hours_old < 24:
            return 0.95
        elif hours_old < 72:
            return 0.85
        elif hours_old < 168:  # 1 week
            return 0.70
        else:
            return 0.50

    def _get_source_credibility(self, source: str) -> float:
        """Get credibility modifier for news source."""
        credibility_scores = {
            "reuters": 1.0,
            "bloomberg": 1.0,
            "financial times": 0.95,
            "wall street journal": 0.95,
            "confectionery news": 0.90,
            "investing.com": 0.85,
            "trading economics": 0.85,
            "google news": 0.75,
        }

        source_lower = source.lower()
        for key, score in credibility_scores.items():
            if key in source_lower:
                return score

        return 0.70  # Default for unknown sources

    def _determine_impact_direction(
        self, text: str, factors: List[Tuple[str, float]]
    ) -> str:
        """Determine if the content suggests bullish or bearish impact."""
        bullish_keywords = [
            "shortage", "supply deficit", "crop failure", "lower production",
            "strong demand", "price increase", "rally", "surge", "high prices"
        ]
        bearish_keywords = [
            "surplus", "oversupply", "bumper crop", "higher production",
            "weak demand", "price drop", "decline", "falling prices"
        ]

        bullish_count = sum(1 for kw in bullish_keywords if kw in text)
        bearish_count = sum(1 for kw in bearish_keywords if kw in text)

        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        return "neutral"

    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis."""
        text = text.lower()

        positive_words = ["increase", "improve", "strong", "growth", "better", "rise"]
        negative_words = ["decrease", "decline", "weak", "drop", "worse", "fall"]

        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    def _get_factor_category(self, factor_name: str) -> str:
        """Get category for a factor."""
        supply_factors = [
            "weather_west_africa", "ivory_coast_production", "ghana_production",
            "harvest_season", "disease_outbreak"
        ]
        demand_factors = [
            "chocolate_demand", "emerging_market_consumption", "seasonal_demand"
        ]

        if factor_name in supply_factors:
            return "supply"
        elif factor_name in demand_factors:
            return "demand"
        return "general"
