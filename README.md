# Cocoa Price Tracker

A real-time commodity price tracking application focused on cocoa, providing price updates, news aggregation, importance analysis, and AI-powered market insights.

## Features

- **Real-time Price Tracking**: Live cocoa prices from multiple sources (ICE Futures)
- **News Aggregation**: Automated collection of cocoa-related news from RSS feeds and web sources
- **Importance Analysis**: Scoring system for news and market factors based on their potential price impact
- **AI-Powered Analysis**: Market overview, outlook, and daily digests powered by OpenAI
- **Technical Indicators**: 52-week high/low, price changes, trend analysis
- **PWA Support**: Installable progressive web app for mobile access

## Architecture

```
├── backend/
│   ├── api/           # FastAPI routes and endpoints
│   ├── analyzer/      # AI and importance analysis modules
│   ├── models/        # Database models and schemas
│   ├── scraper/       # Web scrapers for prices and news
│   └── main.py        # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API service layer
│   │   └── styles/      # CSS styles
│   └── index.html
└── data/              # SQLite database storage
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env and add your OpenAI API key (optional, for AI features)
# OPENAI_API_KEY=your_key_here

# Create data directory
mkdir -p ../data

# Run the backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Dashboard
- `GET /api/dashboard/summary` - Complete dashboard data
- `GET /api/dashboard/price-chart?period=30d` - Price chart data
- `GET /api/dashboard/news-feed?limit=10` - News feed
- `GET /api/dashboard/key-factors` - Market factors

### API v1
- `GET /api/v1/price/current` - Current cocoa price
- `GET /api/v1/price/history?days=30` - Historical prices
- `GET /api/v1/price/stats` - Price statistics
- `GET /api/v1/news` - News articles
- `GET /api/v1/factors` - Market factors
- `GET /api/v1/analysis/overview` - Market overview
- `GET /api/v1/analysis/outlook` - Market outlook
- `GET /api/v1/analysis/digest` - Daily digest
- `POST /api/v1/scrape/trigger` - Trigger data scrape

## Data Sources

### Price Data
- Trading Economics
- Investing.com
- Business Insider Markets

### News Sources
- Google News RSS (cocoa-related queries)
- Reuters Commodities
- Confectionery News

## Configuration

Environment variables (`.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI analysis | - |
| `DATABASE_URL` | SQLite database path | `sqlite+aiosqlite:///./data/cocoa_tracker.db` |
| `SCRAPE_INTERVAL_MINUTES` | Auto-scrape interval | `30` |
| `NEWS_FETCH_LIMIT` | Max news articles per scrape | `50` |
| `DEBUG` | Debug mode | `true` |

## Key Market Factors Tracked

- **Supply Side**: West African weather, Ivory Coast/Ghana production, harvest seasons, disease outbreaks
- **Demand Side**: Chocolate demand, emerging market consumption, seasonal patterns
- **Market Factors**: Futures trading, currency movements, speculation
- **Geopolitical**: Government policies, trade regulations, political stability

## Technology Stack

### Backend
- FastAPI - Async web framework
- SQLAlchemy - Database ORM with async support
- BeautifulSoup4 - Web scraping
- OpenAI API - AI-powered analysis
- APScheduler - Background job scheduling

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Recharts - Charts and visualizations
- Lucide React - Icons
- React Router - Navigation

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Backend (use production server)
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Disclaimer

This application provides market data for informational purposes only. It should not be considered financial advice. Always conduct your own research before making investment decisions.
