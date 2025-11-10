# API CONTRACTS REGISTRY

**Project:** AutoCbot MVP
**Date:** 2025-11-10
**Total Endpoints:** 47

---

## AUTHENTICATION ENDPOINTS (6)

| Method | Path | Auth | Request | Response | Errors | Status |
|--------|------|------|---------|----------|--------|--------|
| POST | `/api/auth/register` | 🌐 | `{email, password}` | `{id, email, ...}` | 400, 422, 500 | ✅ |
| POST | `/api/auth/login` | 🌐 | `{email, password}` | `{access_token, refresh_token}` | 401, 403, 422 | ✅ |
| POST | `/api/auth/refresh` | 🔒 | Bearer refresh_token | `{access_token, refresh_token}` | 401, 422 | ⚠️ No revocation |
| GET | `/api/auth/me` | 🔒 | Bearer token | `{id, email, is_active}` | 401, 403 | ✅ |
| POST | `/api/auth/logout` | 🔒 | Bearer token | `{message}` | 401 | ⚠️ Client-side only |
| PUT | `/api/auth/change-password` | 🔒 | `{current_password, new_password}` | `{message}` | 401, 422 | ⚠️ No strength check |

---

## TRADING ENDPOINTS (11)

| Method | Path | Auth | Purpose | Status | Issues |
|--------|------|------|---------|--------|--------|
| GET | `/api/trading/signals` | 🌐 | Get trading signals | ✅ | ❌ Should require auth |
| GET | `/api/trading/signal/{symbol}` | 🌐 | Single signal | ✅ | ❌ Should require auth |
| POST | `/api/trading/order` | 🔒 | Create order | ✅ | None |
| POST | `/api/trading/smart-order` | 🔒 | Auto position sizing | ✅ | None |
| GET | `/api/trading/orders` | 🔒 | Get orders | ✅ | None |
| DELETE | `/api/trading/order/{id}` | 🔒 | Cancel order | ✅ | None |
| GET | `/api/trading/positions` | 🔒 | Open positions | ✅ | None |
| GET | `/api/trading/balance` | 🔒 | Account balance | ✅ | None |
| GET | `/api/trading/portfolio-value` | 🔒 | Total value | ✅ | None |
| GET | `/api/trading/trades` | 🔒 | Trade history | ✅ | None |
| POST | `/api/trading/close-all` | 🔒 | Emergency close | ✅ | None |

---

## PORTFOLIO ENDPOINTS (6)

| Method | Path | Auth | Purpose | Status | Issues |
|--------|------|------|---------|--------|--------|
| GET | `/api/portfolio/summary` | 🔒 | Portfolio summary | ✅ | ⚠️ today_pnl=0 |
| GET | `/api/portfolio/positions` | 🔒 | All positions | ✅ | None |
| GET | `/api/portfolio/position/{symbol}` | 🔒 | Single position | ✅ | None |
| GET | `/api/portfolio/history` | 🔒 | Trade history | ✅ | None |
| GET | `/api/portfolio/performance` | 🔒 | Metrics | ✅ | ⚠️ Simplified Sharpe/drawdown |
| GET | `/api/portfolio/pnl-chart` | 🔒 | P&L chart data | ✅ | None |

---

## STRATEGY ENDPOINTS (9)

| Method | Path | Auth | Purpose | Status | Issues |
|--------|------|------|---------|--------|--------|
| GET | `/api/strategy/list` | 🔒 | List strategies | ✅ | None |
| GET | `/api/strategy/{name}` | 🔒 | Get strategy | ✅ | None |
| POST | `/api/strategy/` | 🔒 | Create/update | ✅ | None |
| PUT | `/api/strategy/{name}/toggle` | 🔒 | Enable/disable | ✅ | None |
| DELETE | `/api/strategy/{name}` | 🔒 | Delete (soft) | ✅ | None |
| POST | `/api/strategy/backtest` | 🔒 | Run backtest | ✅ | ⚠️ Long-only, single symbol |
| GET | `/api/strategy/backtest/results` | 🔒 | List backtests | ✅ | None |
| GET | `/api/strategy/backtest/{id}` | 🔒 | Backtest details | ✅ | None |

---

## SETTINGS ENDPOINTS (3)

| Method | Path | Auth | Purpose | Status | Issues |
|--------|------|------|---------|--------|--------|
| GET | `/api/settings/` | 🔒 | Get settings | ✅ | ❌ Global, not per-user |
| PUT | `/api/settings/` | 🔒 | Save settings | ✅ | ❌ Plaintext API keys |
| POST | `/api/settings/reset` | 🔒 | Reset to defaults | ✅ | ❌ Global impact |

---

## MARKET DATA ENDPOINTS (7) - PUBLIC

| Method | Path | Auth | Purpose | Status |
|--------|------|------|---------|--------|
| GET | `/api/market/overview` | 🌐 | Market stats | ✅ |
| GET | `/api/market/prices` | 🌐 | Multiple prices | ✅ |
| GET | `/api/market/price/{symbol}` | 🌐 | Single price | ✅ |
| GET | `/api/market/candles/{symbol}` | 🌐 | OHLCV data | ✅ |
| GET | `/api/market/indicators/{symbol}` | 🌐 | Technical indicators | ✅ |
| GET | `/api/market/trending` | 🌐 | Trending coins | ✅ |
| GET | `/api/market/gainers-losers` | 🌐 | Top movers | ✅ |

---

## SENTIMENT ENDPOINTS (4) - PUBLIC

| Method | Path | Auth | Purpose | Status | Issues |
|--------|------|------|---------|--------|--------|
| GET | `/api/sentiment/fear-greed` | 🌐 | F&G Index | ✅ | None |
| GET | `/api/sentiment/social/{symbol}` | 🌐 | Social sentiment | ⚠️ | External API dependency |
| GET | `/api/sentiment/analysis` | 🌐 | Comprehensive | ⚠️ | Partial implementation |
| GET | `/api/sentiment/trending-topics` | 🌐 | Trending | 📝 | Returns mock data |

---

## ERROR CODE STANDARDS

All endpoints follow standard HTTP error codes:

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | Success | Successful GET/PUT |
| 201 | Created | Successful POST (create) |
| 400 | Bad Request | Invalid input, validation failure |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Pydantic validation error |
| 500 | Internal Server Error | Server/service error |

---

## IDEMPOTENCY

| Endpoint | Idempotent | Notes |
|----------|------------|-------|
| GET (all) | ✅ Yes | Safe, no side effects |
| POST /order | ❌ No | Each call creates new order |
| POST /backtest | ❌ No | Each call creates new backtest |
| PUT /strategy | ✅ Yes | Updates to same state |
| DELETE /strategy | ✅ Yes | Soft delete, repeatable |

**Missing Idempotency Keys:**
- Order creation should accept idempotency key to prevent duplicate orders on retry
- **Recommendation:** Add `X-Idempotency-Key` header support for POST endpoints

---

## WEBHOOKS

**Status:** ❌ NOT IMPLEMENTED

No webhook endpoints exist. Planned for v1.2:
- POST /webhooks/register
- DELETE /webhooks/{id}
- GET /webhooks/list

---

## RATE LIMITING

**Status:** ❌ NOT IMPLEMENTED

**Critical Issue:** No rate limiting on any endpoint

**Recommendation:** Implement rate limiting:
- Auth endpoints: 5 req/min per IP
- Trading endpoints: 10 req/sec per user
- Public endpoints: 100 req/min per IP

---

## CRITICAL ISSUES SUMMARY

### P0 (Blocking):
1. Trading signals publicly accessible (no auth)
2. Settings are global (security risk)
3. No rate limiting (DoS vulnerability)

### P1 (High):
4. No server-side token revocation
5. No idempotency keys for orders
6. Plaintext API key storage

### P2 (Medium):
7. Simplified performance metrics
8. No webhook support
9. No admin endpoints

---

**End of API Contracts Registry**
