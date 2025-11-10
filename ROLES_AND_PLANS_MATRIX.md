# ROLES & PLANS ACCESS MATRIX

**Project:** AutoCbot MVP
**Date:** 2025-11-10

---

## CURRENT ROLE STRUCTURE

The system implements a **basic 2-tier role model**:

| Role | Database Field | Description |
|------|---------------|-------------|
| **Regular User** | `is_superuser=false` | Standard authenticated user |
| **Superuser** | `is_superuser=true` | Admin with elevated privileges |

**Current Implementation Status:**
- ⚠️ **Role checking implemented but NOT USED** in endpoints
- ✅ Helper function exists: `get_current_active_superuser()`
- ❌ **No endpoints actually enforce superuser requirement**
- ❌ **No premium/paid plan structure** implemented

---

## ACCESS MATRIX BY ROLE

### Anonymous (Not Logged In)

| Feature | Access | Notes |
|---------|--------|-------|
| Market Overview | ✅ Full | Public API |
| Live Prices | ✅ Full | Public API |
| Fear & Greed Index | ✅ Full | Public API |
| Trading Signals | ✅ Full | ⚠️ **SHOULD BE BLOCKED** |
| Register | ✅ Full | - |
| Login | ✅ Full | - |
| All Other Features | ❌ Blocked | 401 Unauthorized |

**Critical Issue:** Trading signals should require authentication!

---

### Regular User (Authenticated)

| Feature Category | Access | Restrictions |
|-----------------|--------|--------------|
| **Authentication** | ✅ Full | Login, logout, refresh, change password |
| **Dashboard** | ✅ Full | View all widgets |
| **Trading** | ✅ Full | Create orders, cancel, view positions |
| **Portfolio** | ✅ Full | View summary, positions, history |
| **Analytics** | ✅ Full | Performance metrics, charts |
| **Strategies** | ✅ Full | CRUD operations, backtest |
| **Settings** | ✅ Full | ⚠️ Global settings (affects all users!) |
| **Market Data** | ✅ Full | All public market data |

**Issues:**
- Settings are GLOBAL, not per-user
- No user-specific data isolation (strategies/trades accessible by all)

---

### Superuser/Admin

| Feature Category | Access | Additional Privileges |
|-----------------|--------|----------------------|
| All Regular Features | ✅ Full | Same as regular user |
| Admin Features | ❌ None | **NOT IMPLEMENTED** |

**Observations:**
- Superuser role exists in database
- Helper function `get_current_active_superuser()` implemented
- **NO ENDPOINTS use this function**
- **NO ADMIN-ONLY FEATURES** exist

**Missing Admin Features (Expected but Not Implemented):**
- User management (view/edit/delete users)
- System-wide statistics
- Audit logs
- Feature flag management UI
- Global settings management
- User activity monitoring

---

## PREMIUM/PAID PLANS

### Current State: ❌ NOT IMPLEMENTED

**No plan structure exists:**
- No `plan` or `subscription` field in User model
- No plan checking in any endpoint
- No feature gating by plan
- No payment integration

### Recommended Plan Structure (If Implementing)

```
FREE PLAN:
- Paper trading only
- 2 strategies max
- 30-day history
- Basic indicators

PREMIUM PLAN:
- Live trading enabled
- Unlimited strategies
- Full history
- Advanced indicators
- Backtesting
- ML predictions

ENTERPRISE PLAN:
- All Premium features
- API access
- Custom strategies
- Priority support
- Webhooks/notifications
```

---

## FEATURE FLAGS BY ROLE

Current feature flags are GLOBAL (not role-specific):

| Feature Flag | Default | Purpose |
|--------------|---------|---------|
| `ENABLE_ML_PREDICTIONS` | false | ML-based signal generation |
| `ENABLE_BACKTESTING` | false | Strategy backtesting |
| `ENABLE_PAPER_TRADING` | true | Paper trading mode |
| `ENABLE_LIVE_TRADING` | false | Real money trading |
| `ENABLE_ADVANCED_METRICS` | false | Advanced analytics |
| `ENABLE_TELEGRAM` | false | Telegram notifications |
| `ENABLE_EMAIL_NOTIFICATIONS` | false | Email alerts |
| `ENABLE_WEBHOOKS` | false | Webhook integrations |

**Issue:** Flags are system-wide, not user-specific or plan-specific

---

## DATA ISOLATION ISSUES

### Critical: Insufficient User Data Isolation

| Entity | Current Behavior | Risk Level |
|--------|------------------|------------|
| **Strategies** | `user_id` nullable, no filtering | 🔴 HIGH |
| **Trades** | No user association | 🔴 HIGH |
| **Orders** | No user association | 🔴 HIGH |
| **Positions** | No user association | 🔴 HIGH |
| **Settings** | Global JSON file | 🔴 CRITICAL |

**Consequences:**
- All users can potentially see/modify each other's strategies
- All users share same settings (API keys, risk params)
- No privacy or data separation

**Required Actions:**
1. Add `user_id` to all relevant tables
2. Filter all queries by `current_user.id`
3. Move settings to database with per-user records
4. Add database-level foreign key constraints

---

## AUTHORIZATION VERIFICATION

### Endpoints WITHOUT Proper User Filtering

Even though these endpoints require authentication, they don't filter by user_id:

```python
# Examples of insufficient filtering:
GET /api/strategy/list
  → Returns ALL strategies (should filter by user_id)

GET /api/portfolio/positions
  → Returns ALL positions (should filter by user_id)

GET /api/trading/orders
  → Returns ALL orders (should filter by user_id)
```

**Impact:** Users can access data from other users if they know the IDs

---

## RECOMMENDATIONS

### Immediate (P0):
1. Add `user_id` filtering to all strategy/portfolio/trading queries
2. Make settings per-user (database migration)
3. Remove Trading Signals from public API OR add auth

### High Priority (P1):
4. Implement admin-only endpoints using `get_current_active_superuser()`
5. Add user management features for superusers
6. Implement audit logging

### Future (P2):
7. Design and implement plan/subscription structure
8. Add per-plan feature gating
9. Implement payment integration
10. Add usage limits/rate limiting per plan

---

## SECURITY VERDICT

**Status:** 🔴 **NOT PRODUCTION READY** (Authorization Issues)

**Critical Gaps:**
- Insufficient user data isolation
- No admin features despite role structure
- Global settings (security risk)
- Public access to trading signals

**Must Fix Before Production:**
- User-specific data filtering
- Per-user settings
- Proper authorization checks

---

**End of Roles & Plans Matrix**
