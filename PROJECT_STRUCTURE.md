# 📁 AutoCbot Project Structure

This document describes the complete, organized structure of the AutoCbot project after professional cleanup.

---

## 🎯 Overview

AutoCbot is a full-stack cryptocurrency trading platform with:
- **Backend:** FastAPI + Python 3.11+
- **Frontend:** React + Next.js + TypeScript
- **Database:** PostgreSQL/SQLite
- **ML:** LightGBM for price predictions
- **Deployment:** Cloud-ready (Render, Railway, VPS)

---

## 📂 Root Directory

```
AutoCbot/
├── README.md                     # Main project documentation
├── PROJECT_STRUCTURE.md          # This file
├── .gitignore                    # Git exclusions (professional)
│
├── backend/                      # Python FastAPI backend
├── frontend/                     # React + Next.js frontend
├── tests/                        # Test suites (smoke, UX)
└── docs/                         # Organized documentation
```

---

## 🔙 Backend Structure (`backend/`)

### Core Application

```
backend/
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
│
├── api/                          # REST API endpoints
│   ├── __init__.py
│   ├── auth.py                  # Authentication (login, register, logout)
│   ├── strategy.py              # Trading strategies CRUD
│   ├── trading.py               # Trading signals & execution
│   ├── settings.py              # User settings management
│   ├── market.py                # Market data endpoints
│   ├── portfolio.py             # Portfolio management
│   └── sentiment.py             # Sentiment analysis data
│
├── services/                     # Business logic layer
│   ├── __init__.py
│   ├── market_data.py           # Market data aggregation
│   ├── sentiment.py             # Sentiment analysis service
│   ├── signal_generator.py      # AI trading signal generation
│   ├── backtesting.py           # Backtesting engine
│   ├── backtest_engine.py       # Core backtest logic
│   ├── strategy_manager.py      # Strategy CRUD operations
│   ├── user_settings.py         # User settings with encryption
│   ├── technical_analysis.py    # Technical indicators
│   ├── fundamental.py           # Fundamental analysis
│   ├── risk_manager.py          # Risk management
│   ├── portfolio.py             # Portfolio tracking
│   ├── trading.py               # Trade execution
│   ├── websocket_manager.py     # WebSocket connections
│   ├── exchanges/               # Exchange connectors
│   │   ├── base_exchange.py    # Base exchange interface
│   │   ├── binance_connector.py # Binance integration
│   │   ├── paper_trading_exchange.py # Paper trading
│   │   └── exchange_factory.py # Exchange factory
│   └── market_data/             # Market data providers
│       ├── aggregator.py       # Data aggregation
│       ├── base_provider.py    # Provider interface
│       ├── binance_provider.py # Binance data
│       ├── glassnode_provider.py # On-chain data
│       └── lunarcrush_provider.py # Social metrics
│
├── database/                     # Database layer
│   ├── __init__.py
│   ├── base.py                  # SQLAlchemy base
│   ├── models.py                # Database models
│   └── session.py               # Database session management
│
├── models/                       # Pydantic schemas
│   ├── __init__.py
│   ├── schemas.py               # API request/response schemas
│   └── settings.py              # Settings schemas
│
├── utils/                        # Utility modules
│   ├── __init__.py
│   ├── auth.py                  # JWT & password utilities
│   ├── encryption.py            # Fernet encryption (API keys)
│   ├── rate_limit.py            # Rate limiting (SlowAPI)
│   ├── config.py                # Configuration management
│   ├── feature_flags.py         # Feature toggle system
│   └── metrics.py               # Metrics & monitoring
│
├── middleware/                   # FastAPI middleware
│   ├── __init__.py
│   └── security.py              # Security headers, request ID
│
├── alembic/                      # Database migrations
│   ├── env.py                   # Alembic environment
│   ├── script.py.mako           # Migration template
│   └── versions/                # Migration scripts
│       ├── 600c4339cb4f_initial_migration_create_all_tables.py
│       ├── a1b2c3d4e5f6_make_user_password_required_mvp.py
│       ├── b2c3d4e5f6g7_add_user_settings_table_with_encryption.py
│       └── c3d4e5f6g7h8_add_token_blacklist_table.py
│
├── scripts/                      # Maintenance scripts
│   ├── cleanup_token_blacklist.py # Token cleanup automation
│   ├── backup.sh                # Database backup script
│   ├── deploy.sh                # Deployment script
│   ├── monitor.py               # System monitoring
│   └── tax_calculator.py        # Tax calculation utility
│
├── tests/                        # Backend tests
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   └── unit/                    # Unit tests
│       ├── __init__.py
│       └── test_risk_manager.py
│
└── user_data/                    # User-generated data
    ├── strategies/              # Trading strategy implementations
    │   ├── features.py         # Feature engineering
    │   ├── mean_reversion_base.py # Base strategy
    │   └── mean_reversion_ml.py # ML-enhanced strategy
    └── notebooks/               # Jupyter notebooks
        └── (ML training notebooks)
```

### Key Backend Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, middleware, routes |
| `api/auth.py` | User registration, login, JWT tokens, logout |
| `services/signal_generator.py` | ML-powered trading signal generation |
| `database/models.py` | SQLAlchemy ORM models (User, Strategy, Trade, etc.) |
| `utils/encryption.py` | Fernet encryption for sensitive API keys |
| `utils/rate_limit.py` | SlowAPI rate limiting configuration |

---

## 🎨 Frontend Structure (`frontend/`)

```
frontend/
├── package.json                  # NPM dependencies
├── tsconfig.json                 # TypeScript configuration
├── next.config.js                # Next.js configuration
│
└── src/
    ├── app/                      # Next.js app router
    │   ├── layout.tsx           # Root layout
    │   ├── page.tsx             # Home page
    │   ├── login/               # Login page
    │   ├── register/            # Registration page
    │   ├── dashboard/           # Dashboard page
    │   └── strategies/          # Strategy management
    │
    ├── components/               # React components
    │   ├── ui/                  # UI primitives
    │   ├── charts/              # Trading charts
    │   ├── forms/               # Form components
    │   └── layout/              # Layout components
    │
    ├── services/                 # API clients
    │   ├── api.ts               # Axios configuration
    │   ├── auth.ts              # Authentication API
    │   ├── strategies.ts        # Strategy API
    │   └── trading.ts           # Trading API
    │
    ├── hooks/                    # Custom React hooks
    │   ├── useAuth.ts           # Authentication hook
    │   ├── useStrategies.ts     # Strategy management
    │   └── useWebSocket.ts      # WebSocket connection
    │
    ├── types/                    # TypeScript types
    │   ├── api.ts               # API types
    │   ├── strategy.ts          # Strategy types
    │   └── user.ts              # User types
    │
    ├── lib/                      # Utility functions
    │   └── utils.ts             # Helper functions
    │
    └── styles/                   # Styling
        └── globals.css          # Global styles
```

---

## 🧪 Tests Structure (`tests/`)

```
tests/
├── conftest.py                   # Pytest configuration (root)
├── requirements.txt              # Test dependencies
│
├── smoke/                        # Smoke tests (quick validation)
│   ├── test_backend_health.py  # Backend health check
│   ├── test_environment.py      # Environment validation
│   └── test_frontend_alive.py  # Frontend connectivity
│
└── ux/                          # UX tests (Playwright)
    ├── package.json             # Playwright dependencies
    ├── playwright.config.ts     # Playwright configuration
    ├── README.md                # UX testing guide
    ├── critical-flows/          # Critical user flows
    ├── dead-buttons/            # Dead button detection
    ├── states/                  # State management tests
    └── helpers/                 # Test helpers
```

---

## 📚 Documentation Structure (`docs/`)

```
docs/
├── guides/                       # User guides
│   ├── GETTING_STARTED.md       # Complete setup guide
│   └── QUICKSTART.md            # 5-minute quickstart
│
├── deployment/                   # Deployment documentation
│   ├── DEPLOYMENT_GUIDE.md      # Cloud deployment options
│   └── POST_DEPLOYMENT_SETUP.md # Monitoring & maintenance
│
├── architecture/                 # Technical documentation
│   ├── COMPLETE_SYSTEM_README.md # System architecture
│   ├── API_CONTRACTS_REGISTRY.md # API specifications
│   ├── FEATURE_FLAGS_CATALOG.md # Feature toggles
│   ├── E2E_FEATURE_MATRIX.md    # Feature coverage matrix
│   └── ROLES_AND_PLANS_MATRIX.md # User roles & plans
│
├── reports/                      # Audit & assessment reports
│   ├── PRODUCTION_READINESS_REPORT.md # Security audit (89/100)
│   ├── BACKEND_AUDIT_REPORT.md  # Backend code audit
│   ├── SYSTEM_QUALITY_AUDIT_REPORT.md # Quality assessment
│   ├── FINAL_SYSTEM_CERTIFICATION_REPORT.md # Certification
│   ├── MVP_FINAL_REPORT.md      # MVP completion report
│   ├── UX_AUDIT_REPORT.md       # UX assessment
│   ├── UX_AUDIT_EXECUTIVE_REPORT.md # Executive summary
│   ├── UX_AUDIT_DISCOVERY.md    # UX discovery findings
│   └── UX_INTERACTIVE_ELEMENTS_AUDIT.md # Interactive audit
│
└── development/                  # Development documentation
    ├── MVP_LAUNCH_CHECKLIST.md  # Pre-launch checklist
    ├── MVP_SCOPE_AND_TRADEOFFS.md # MVP decisions
    ├── MVP_JOURNEYS.md          # User journey maps
    └── IMPLEMENTATION_SUMMARY.md # Implementation details
```

---

## 🗂️ Data & Configuration Files

### Environment & Configuration

```
.env                              # Environment variables (NEVER commit)
.env.example                      # Template for .env
backend/.env                      # Backend-specific env vars
backend/autocbot.db               # SQLite database (git-ignored)
```

### Git & IDE

```
.gitignore                        # Git exclusions (professional)
.git/                             # Git repository (hidden)
.vscode/                          # VSCode settings (git-ignored)
.idea/                            # PyCharm settings (git-ignored)
```

---

## 🔄 Data Flow

### 1. Authentication Flow
```
Frontend → POST /api/v1/auth/login
         → backend/api/auth.py
         → backend/utils/auth.py (JWT creation)
         → backend/database/models.py (User lookup)
         → Return JWT tokens
```

### 2. Trading Signal Flow
```
Frontend → GET /api/v1/trading/signals
         → backend/api/trading.py (auth check)
         → backend/services/signal_generator.py
         → backend/services/market_data.py (fetch prices)
         → backend/services/sentiment.py (sentiment analysis)
         → LightGBM model prediction
         → Return trading signals with confidence
```

### 3. Strategy Backtest Flow
```
Frontend → POST /api/v1/backtest/run
         → backend/api/strategy.py
         → backend/services/backtesting.py
         → backend/services/backtest_engine.py
         → Simulate trades on historical data
         → Calculate metrics (Sharpe, drawdown, etc.)
         → backend/database/models.py (save results)
         → Return backtest report
```

---

## 🔐 Security Architecture

### Layer 1: Network Security
- CORS protection (configurable origins)
- Rate limiting (SlowAPI)
- Security headers (HSTS, XSS, etc.)

### Layer 2: Authentication
- JWT tokens (access + refresh)
- Token blacklist for logout
- Password strength validation

### Layer 3: Authorization
- Per-user data isolation (user_id filtering)
- Role-based access (superuser)

### Layer 4: Data Security
- API key encryption (Fernet)
- Password hashing (Bcrypt)
- SQL injection protection (ORM)

---

## 📦 Dependencies

### Backend Key Dependencies
```
fastapi==0.109.0                  # Web framework
uvicorn==0.27.0                   # ASGI server
sqlalchemy==2.0.25                # ORM
alembic==1.13.1                   # Migrations
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # Password hashing
slowapi==0.1.9                    # Rate limiting
lightgbm==4.2.0                   # Machine learning
ccxt==4.2.25                      # Exchange integration
pandas==2.1.4                     # Data processing
```

### Frontend Key Dependencies
```
react                             # UI library
next                              # React framework
typescript                        # Type safety
tailwindcss                       # Styling
axios                             # HTTP client
```

---

## 🚀 Deployment Structure

### Development
```
localhost:8000                    # Backend API
localhost:3000                    # Frontend
```

### Production (Cloud)
```
https://autocbot-api.onrender.com # Backend (Render)
https://autocbot.onrender.com     # Frontend (Render)
PostgreSQL                        # Database (Render)
```

### Production (VPS)
```
https://yourdomain.com            # Nginx reverse proxy
  → http://localhost:8000         # Backend (Uvicorn)
  → http://localhost:3000         # Frontend (Next.js)
PostgreSQL                        # Database (local or managed)
```

---

## 📈 File Count Summary

| Category | Count | Notes |
|----------|-------|-------|
| **Python files** | ~50 | Backend + services |
| **TypeScript files** | ~30 | Frontend components |
| **Test files** | ~15 | Smoke + UX tests |
| **Documentation** | 25 | Guides, reports, architecture |
| **Migrations** | 4 | Database schema versions |
| **Scripts** | 5 | Maintenance & deployment |
| **Total** | ~130 files | Organized professionally |

---

## 🎯 Navigation Guide

### "I want to..."

**...understand the system**
→ Start with `README.md`, then `docs/architecture/COMPLETE_SYSTEM_README.md`

**...run it locally**
→ Follow `docs/guides/GETTING_STARTED.md`

**...deploy to production**
→ Read `docs/deployment/DEPLOYMENT_GUIDE.md`

**...understand the API**
→ Check `docs/architecture/API_CONTRACTS_REGISTRY.md` or `/docs` endpoint

**...modify the ML model**
→ Look at `backend/services/signal_generator.py` and `backend/user_data/strategies/`

**...add a new feature**
→ Read `docs/development/IMPLEMENTATION_SUMMARY.md` first

**...review security**
→ See `docs/reports/PRODUCTION_READINESS_REPORT.md`

**...understand costs**
→ Check `docs/deployment/DEPLOYMENT_GUIDE.md` comparison table

---

## 🔧 Maintenance

### Weekly Tasks
- Review logs in `backend/logs/`
- Check `backend/autocbot.db` size
- Run `backend/scripts/cleanup_token_blacklist.py`

### Monthly Tasks
- Update dependencies (`pip list --outdated`)
- Review security audit checklist
- Retrain ML models if needed

### Quarterly Tasks
- Full security audit
- Performance optimization
- Backup verification

---

## 📝 Notes

### Design Principles
1. **Separation of Concerns** - API, Services, Database clearly separated
2. **DRY** - Utilities shared across modules
3. **Security First** - Encryption, isolation, validation everywhere
4. **Documentation** - Every major component documented
5. **Testability** - Modular design for easy testing

### Naming Conventions
- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case()`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Status:** ✅ Complete & Organized
