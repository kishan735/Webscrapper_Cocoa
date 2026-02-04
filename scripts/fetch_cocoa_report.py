#!/usr/bin/env python3
"""
Fetch cocoa price data and generate a report.
Can be run locally or via GitHub Actions.
"""

import json
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def fetch_price_data():
    """Fetch cocoa price using yfinance (FREE, no API key needed)."""
    try:
        import yfinance as yf

        ticker = yf.Ticker("CC=F")  # Cocoa futures
        hist = ticker.history(period="5d")

        if hist.empty:
            return {"error": "No price data available"}

        current_price = float(hist["Close"].iloc[-1])
        prev_price = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price

        # Get 52-week data
        hist_year = ticker.history(period="1y")
        high_52 = float(hist_year["High"].max()) if not hist_year.empty else None
        low_52 = float(hist_year["Low"].min()) if not hist_year.empty else None

        change_24h = current_price - prev_price
        change_percent = (change_24h / prev_price * 100) if prev_price else 0

        return {
            "price_usd": round(current_price, 2),
            "change_24h": round(change_24h, 2),
            "change_percent_24h": round(change_percent, 2),
            "high_52_week": round(high_52, 2) if high_52 else None,
            "low_52_week": round(low_52, 2) if low_52 else None,
            "source": "Yahoo Finance",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}


def generate_ai_analysis(price_data):
    """Generate AI analysis using Groq (FREE)."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "AI analysis unavailable - no GROQ_API_KEY configured"

    try:
        import httpx

        prompt = f"""Analyze the current cocoa market:

Price: ${price_data.get('price_usd', 'N/A')} per metric ton
24h Change: {price_data.get('change_percent_24h', 'N/A')}%
52-Week High: ${price_data.get('high_52_week', 'N/A')}
52-Week Low: ${price_data.get('low_52_week', 'N/A')}

Provide a brief 2-3 sentence market analysis and outlook."""

        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a commodity market analyst specializing in cocoa."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 300,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI analysis failed: {str(e)}"


def main():
    print("=" * 50)
    print("COCOA PRICE TRACKER - Report")
    print("=" * 50)
    print(f"Generated: {datetime.utcnow().isoformat()} UTC")
    print()

    # Fetch price data
    print("Fetching price data from Yahoo Finance...")
    price_data = fetch_price_data()

    if "error" in price_data:
        print(f"ERROR: {price_data['error']}")
        sys.exit(1)

    print(f"\n📊 COCOA PRICE")
    print(f"   Current: ${price_data['price_usd']:,.2f} / metric ton")
    print(f"   24h Change: ${price_data['change_24h']:+,.2f} ({price_data['change_percent_24h']:+.2f}%)")
    if price_data['high_52_week']:
        print(f"   52-Week High: ${price_data['high_52_week']:,.2f}")
    if price_data['low_52_week']:
        print(f"   52-Week Low: ${price_data['low_52_week']:,.2f}")

    # Generate AI analysis
    print("\n🤖 AI ANALYSIS")
    analysis = generate_ai_analysis(price_data)
    print(f"   {analysis}")

    # Save report
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "price_data": price_data,
        "ai_analysis": analysis,
    }

    with open("cocoa_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Report saved to cocoa_report.json")
    print("=" * 50)


if __name__ == "__main__":
    main()
