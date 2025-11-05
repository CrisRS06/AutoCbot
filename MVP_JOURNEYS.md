# AutoCbot MVP - Critical User Journeys

## Overview
This document defines the 7 critical user journeys that MUST work end-to-end for MVP launch.

---

## Journey Definitions

### J1: Backend Health Check
**User Story**: As a system operator, I want to verify all backend services are running and healthy.

**Flow**:
1. Send GET request to `/health`
2. Verify response status is 200
3. Verify all services report as running

**Acceptance Criteria**:
- ✅ Health endpoint returns 200 OK
- ✅ Response includes `status: "healthy"`
- ✅ All services (market_data, sentiment, fundamental) report `true`
- ✅ Response time < 500ms

**Priority**: CRITICAL - Must work for system to operate

---

### J2: Load Dashboard Complete
**User Story**: As a trader, I want to see a complete dashboard with all data loaded successfully.

**Flow**:
1. User navigates to frontend (http://localhost:3000)
2. Frontend makes parallel API calls:
   - GET /api/v1/market/overview
   - GET /api/v1/sentiment/fear-greed
   - GET /api/v1/trading/signals?symbols=BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT
   - GET /api/v1/portfolio/summary
   - GET /api/v1/portfolio/positions
3. All data loads successfully
4. Dashboard renders without errors

**Acceptance Criteria**:
- ✅ All 5 API calls return 200 OK
- ✅ No loading state persists > 3 seconds
- ✅ No console errors in frontend
- ✅ All cards display valid data (no null/undefined)
- ✅ Total load time < 3 seconds

**Priority**: CRITICAL - Core user experience

---

### J3: Get Trading Signals
**User Story**: As a trader, I want to get AI-generated trading signals with confidence scores.

**Flow**:
1. Request signals for multiple symbols
2. Backend generates multi-layer analysis (technical + sentiment)
3. Returns signals with confidence, entry/exit prices
4. Frontend displays signals in table

**Acceptance Criteria**:
- ✅ GET /api/v1/trading/signals returns 200
- ✅ Each signal has: symbol, signal (buy/sell/hold), confidence (0-1)
- ✅ Each signal includes entry_price, stop_loss, take_profit
- ✅ Confidence calculation is logical (not random)
- ✅ Reasons array explains the signal
- ✅ Response time < 2 seconds

**Priority**: HIGH - Core trading functionality

---

### J4: Query Market Data
**User Story**: As a trader, I want real-time market prices and overview.

**Flow**:
1. Request market overview
2. Request prices for specific symbols
3. Verify data is recent (< 60s old)
4. Display prices with 24h change

**Acceptance Criteria**:
- ✅ GET /api/v1/market/overview returns valid data
- ✅ Overview includes: total_market_cap, btc_dominance, volume_24h
- ✅ GET /api/v1/market/prices?symbols=BTC/USDT,ETH/USDT works
- ✅ Each price includes: symbol, price, change_24h, volume_24h
- ✅ Timestamps are within last 60 seconds
- ✅ Data from CoinGecko API is valid

**Priority**: CRITICAL - Foundation for all trading

---

### J5: Analyze Sentiment
**User Story**: As a trader, I want to see market sentiment (Fear & Greed Index).

**Flow**:
1. Request Fear & Greed Index from Alternative.me
2. Classify sentiment value (0-100)
3. Display with visual gauge in frontend

**Acceptance Criteria**:
- ✅ GET /api/v1/sentiment/fear-greed returns 200
- ✅ Response includes: value (0-100), value_classification, timestamp
- ✅ Classification is correct:
  - 0-24: "Extreme Fear"
  - 25-49: "Fear"
  - 50: "Neutral"
  - 51-75: "Greed"
  - 76-100: "Extreme Greed"
- ✅ Data is cached (5 min TTL)
- ✅ Response time < 1 second

**Priority**: HIGH - Key decision factor

---

### J6: Manage Portfolio
**User Story**: As a trader, I want to see my portfolio summary and open positions.

**Flow**:
1. Request portfolio summary
2. Request open positions list
3. Calculate P&L for each position
4. Display in dashboard

**Acceptance Criteria**:
- ✅ GET /api/v1/portfolio/summary returns valid data
- ✅ Summary includes: total_value, available_balance, pnl, pnl_percentage
- ✅ GET /api/v1/portfolio/positions returns array of positions
- ✅ Each position has: symbol, side, entry_price, current_price, pnl
- ✅ P&L calculations are mathematically correct
- ✅ Handles empty portfolio gracefully

**Priority**: MEDIUM-HIGH - Important for tracking

---

### J7: WebSocket Real-time Updates
**User Story**: As a trader, I want real-time price updates without refreshing.

**Flow**:
1. Frontend connects to WebSocket at /ws
2. Client subscribes to "prices" channel
3. Backend broadcasts price updates every 5 seconds
4. Frontend updates UI without full page refresh

**Acceptance Criteria**:
- ✅ WebSocket connection establishes successfully
- ✅ Client can subscribe to channels (prices, signals, portfolio)
- ✅ Client receives messages in expected format
- ✅ Connection handles disconnects gracefully
- ✅ No memory leaks from reconnections
- ✅ Latency < 100ms

**Priority**: MEDIUM - Nice to have for MVP

---

## Journey Status Matrix

| Journey | Status | Smoke Test | E2E Test | Contract Test | Blocker Issues |
|---------|--------|------------|----------|---------------|----------------|
| J1: Health Check | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |
| J2: Dashboard Load | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |
| J3: Trading Signals | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |
| J4: Market Data | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |
| J5: Sentiment | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |
| J6: Portfolio | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |
| J7: WebSocket | 🟡 Pending | ⏳ | ⏳ | ⏳ | - |

**Legend**:
- 🟢 Green: All tests passing
- 🟡 Yellow: Tests pending / in progress
- 🔴 Red: Tests failing
- ⏳ Pending: Not yet implemented

---

## Testing Strategy

### 1. Smoke Tests (Quick)
- Run before every test session
- Verify basic service availability
- Check health endpoints
- Validate environment setup
- **Time budget**: < 30 seconds total

### 2. E2E Tests (Comprehensive)
- One test per journey
- Full request-response cycle
- Includes external API calls
- **Time budget**: < 5 minutes total

### 3. Contract Tests (API Validation)
- Validate request/response schemas
- Check Pydantic models match reality
- Ensure TypeScript types are correct
- **Time budget**: < 2 minutes total

### 4. Integration Tests (External Services)
- Mock external APIs when needed
- Validate CoinGecko integration
- Validate Alternative.me integration
- Test error handling for API failures
- **Time budget**: < 3 minutes total

---

## Success Criteria for MVP Launch

All journeys must achieve:
- ✅ 100% smoke tests passing
- ✅ 100% E2E tests passing
- ✅ 100% contract tests passing
- ✅ All response times within budget
- ✅ No console errors in production mode
- ✅ Graceful error handling for edge cases

---

## Next Steps

1. ✅ Define journeys (this document)
2. ⏳ Create smoke test suite
3. ⏳ Create E2E test harness
4. ⏳ Implement contract tests
5. ⏳ Run full test suite
6. ⏳ Fix all blocking issues
7. ⏳ Re-test and verify
8. ⏳ Document results in README_MVP.md

---

**Last Updated**: 2025-11-05
**Status**: Journeys defined, tests pending implementation
