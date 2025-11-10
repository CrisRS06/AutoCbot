# AutoCbot - Complete AI-Powered Crypto Trading System

## 🚀 The Ultimate AI-Powered Crypto Trading Stack

A world-class, production-ready cryptocurrency trading system implementing **The Ultimate AI-Powered Crypto Trading Stack: 2025 Complete Guide**.

### ✨ Features

#### 🎯 Multi-Layer Analysis
- **Fundamental Analysis**: On-chain metrics, token fundamentals
- **Technical Analysis**: 15+ indicators, ML-powered signals
- **Sentiment Analysis**: Fear & Greed Index, social sentiment
- **Signal Generation**: AI-powered trading signals with confidence scores

#### 💻 World-Class Modern Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for beautiful, responsive design
- **Framer Motion** for smooth animations
- **Real-time WebSocket** updates
- **Recharts & Lightweight Charts** for advanced visualizations

#### 🔧 Powerful Backend
- **FastAPI** for high-performance REST API
- **WebSocket** support for real-time data streaming
- **Multi-source data integration**: CoinGecko, Alternative.me, Messari
- **Caching layer** for optimal performance
- **Async/await** architecture throughout

#### 📊 Complete Trading Features
- **Live price tracking** across multiple exchanges
- **Portfolio management** with P&L tracking
- **Strategy configuration** and backtesting
- **Risk management** with stop-loss and take-profit
- **Paper trading mode** for safe testing
- **Freqtrade integration** for algorithmic trading

---

## 📁 Project Structure

```
AutoCbot/
├── backend/                    # FastAPI Backend
│   ├── api/                   # API route handlers
│   │   ├── market.py          # Market data endpoints
│   │   ├── sentiment.py       # Sentiment analysis endpoints
│   │   ├── trading.py         # Trading endpoints
│   │   ├── portfolio.py       # Portfolio endpoints
│   │   └── strategy.py        # Strategy management endpoints
│   ├── services/              # Business logic layer
│   │   ├── market_data.py     # Market data service (CoinGecko)
│   │   ├── sentiment.py       # Sentiment analysis (Fear & Greed)
│   │   ├── technical_analysis.py  # Technical indicators
│   │   ├── fundamental.py     # Fundamental analysis
│   │   ├── signal_generator.py    # Trading signal generation
│   │   ├── trading.py         # Trading service
│   │   ├── portfolio.py       # Portfolio management
│   │   ├── strategy_manager.py    # Strategy management
│   │   ├── backtesting.py     # Backtesting engine
│   │   └── websocket_manager.py   # WebSocket manager
│   ├── models/                # Data models
│   │   └── schemas.py         # Pydantic schemas
│   ├── utils/                 # Utilities
│   │   └── config.py          # Configuration management
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Docker configuration
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── layout.tsx     # Root layout
│   │   │   └── page.tsx       # Dashboard page
│   │   ├── components/        # React components
│   │   │   ├── layout/        # Layout components
│   │   │   │   └── DashboardLayout.tsx
│   │   │   ├── dashboard/     # Dashboard components
│   │   │   │   ├── MarketOverviewCard.tsx
│   │   │   │   ├── FearGreedMeter.tsx
│   │   │   │   ├── PortfolioSummaryCard.tsx
│   │   │   │   ├── LivePrices.tsx
│   │   │   │   ├── TradingSignals.tsx
│   │   │   │   └── PositionsTable.tsx
│   │   │   └── ui/            # UI components
│   │   │       └── Card.tsx
│   │   ├── services/          # API services
│   │   │   └── api.ts         # API client
│   │   ├── hooks/             # Custom hooks
│   │   │   └── useWebSocket.ts
│   │   ├── lib/               # Utilities
│   │   │   └── utils.ts
│   │   ├── types/             # TypeScript types
│   │   │   └── index.ts
│   │   └── styles/            # Styles
│   │       └── globals.css
│   ├── package.json           # Node dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── tailwind.config.js     # Tailwind config
│   └── Dockerfile             # Docker configuration
│
├── user_data/                 # Freqtrade data
│   ├── strategies/            # Trading strategies
│   │   ├── mean_reversion_base.py
│   │   ├── mean_reversion_ml.py
│   │   └── features.py
│   └── notebooks/             # Jupyter notebooks
│       └── train_model.ipynb
│
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (Recommended)
- OR **Python 3.11+** and **Node.js 18+**

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd AutoCbot
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional for free tier)
   ```

3. **Start the system**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 API Keys Configuration

### Free Tier (No API Keys Required)
- ✅ **CoinGecko** - Free market data (rate-limited)
- ✅ **Alternative.me** - Free Fear & Greed Index
- ✅ **Messari** - Free tier available

### Optional Paid Services
- **LunarCrush** ($24-240/month) - Enhanced sentiment
- **Token Metrics** ($40+/month) - AI ratings
- **Nansen** ($150+/month) - On-chain intelligence
- **Glassnode** ($29+/month) - On-chain metrics

### Exchange Integration
- **Binance** - For live trading (optional)
  ```env
  BINANCE_API_KEY=your_api_key
  BINANCE_SECRET=your_secret_key
  ```

---

## 📊 Features Overview

### 1. Market Overview
- Total market cap
- BTC/ETH dominance
- 24h volume
- Top gainers/losers

### 2. Fear & Greed Index
- Beautiful circular meter
- Real-time updates
- Historical data
- Market sentiment classification

### 3. Live Prices
- Real-time price updates
- WebSocket streaming
- 24h change tracking
- Multiple cryptocurrencies

### 4. Trading Signals
- Multi-layer analysis (Technical + Sentiment + Fundamental)
- Confidence scores
- Entry/exit prices
- Stop-loss and take-profit levels
- Signal reasons and explanations

### 5. Portfolio Management
- Real-time P&L tracking
- Open positions monitoring
- Trade history
- Performance metrics

### 6. Strategy Management
- Custom strategy configuration
- Backtesting framework
- Walk-forward optimization
- Performance analytics

---

## 🎨 Modern UI/UX Features

### Design System
- **Dark mode** by default
- **Glass morphism** effects
- **Gradient accents**
- **Smooth animations** with Framer Motion
- **Responsive design** for all devices

### User Experience
- **Real-time updates** via WebSocket
- **Instant feedback** with toast notifications
- **Loading states** with skeletons
- **Error handling** with graceful fallbacks
- **Keyboard shortcuts** for power users

---

## 🔧 API Endpoints

### Market Data
- `GET /api/v1/market/overview` - Market overview
- `GET /api/v1/market/prices?symbols=BTC/USDT,ETH/USDT` - Current prices
- `GET /api/v1/market/candles/{symbol}` - Historical candles
- `GET /api/v1/market/trending` - Trending coins

### Sentiment
- `GET /api/v1/sentiment/fear-greed` - Fear & Greed Index
- `GET /api/v1/sentiment/analysis` - Comprehensive sentiment

### Trading
- `GET /api/v1/trading/signals` - Trading signals
- `POST /api/v1/trading/order` - Create order
- `GET /api/v1/trading/orders` - Get orders

### Portfolio
- `GET /api/v1/portfolio/summary` - Portfolio summary
- `GET /api/v1/portfolio/positions` - Open positions
- `GET /api/v1/portfolio/performance` - Performance metrics

### Strategy
- `GET /api/v1/strategy/list` - List strategies
- `POST /api/v1/strategy/backtest` - Run backtest

Full API documentation: http://localhost:8000/docs

---

## 🧪 Testing & Development

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Development Mode
```bash
# Backend with auto-reload
uvicorn main:app --reload

# Frontend with hot reload
npm run dev
```

---

## 📈 Deployment

### Production Build

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start in production mode
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `.env.example` for all configuration options.

---

## 🔒 Security Best Practices

1. **Never commit `.env` files**
2. **Use API keys with minimum permissions**
3. **Enable IP whitelist on exchange API keys**
4. **Disable withdrawals on API keys**
5. **Use paper trading mode before going live**
6. **Set up proper stop-losses**
7. **Monitor system logs regularly**

---

## 🛣️ Roadmap

### Phase 1: Core System ✅
- [x] Backend API with FastAPI
- [x] Frontend with Next.js
- [x] Market data integration
- [x] Sentiment analysis
- [x] Trading signals

### Phase 2: Advanced Features (In Progress)
- [ ] Machine learning model integration (FreqAI)
- [ ] Advanced charting with TradingView
- [ ] Multi-timeframe analysis
- [ ] Portfolio optimization

### Phase 3: Enterprise Features
- [ ] Multi-exchange support
- [ ] Advanced backtesting
- [ ] Strategy marketplace
- [ ] Social trading features

---

## 📚 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Freqtrade Docs](https://www.freqtrade.io/)

### Community
- [Freqtrade Discord](https://discord.gg/p7nuUNVfP7)
- [r/algotrading](https://reddit.com/r/algotrading)

---

## ⚠️ Disclaimer

**This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Past performance does not guarantee future results. Only invest what you can afford to lose.**

The authors and contributors are not responsible for any financial losses incurred through the use of this software.

---

## 📄 License

This project is for educational purposes. See LICENSE for details.

---

## 🙏 Acknowledgments

Built following **The Ultimate AI-Powered Crypto Trading Stack: 2025 Complete Guide**

- Inspired by the comprehensive guide for professional algo trading
- Implements industry best practices from the guide
- Uses recommended tools and integrations

---

**Version:** 1.0.0
**Last Updated:** November 2025
**Status:** Production Ready ✅

---

**Happy Trading! 🚀**
