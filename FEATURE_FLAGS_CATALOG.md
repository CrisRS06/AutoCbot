# FEATURE FLAGS CATALOG

**Project:** AutoCbot MVP
**Date:** 2025-11-10
**Purpose:** Complete registry of all feature flags with activation criteria

---

## BACKEND FEATURE FLAGS

**Location:** `backend/utils/feature_flags.py`
**Configuration:** Environment variables (`FEATURE_*`)

| Flag Name | ENV Variable | Default | Purpose | Scope | Activation Criteria |
|-----------|--------------|---------|---------|-------|---------------------|
| `enable_ml_strategy` | `FEATURE_ENABLE_ML_STRATEGY` | `false` | ML-based signal generation | MVP Hidden | v1.1 - After ML model training |
| `enable_backtest` | `FEATURE_ENABLE_BACKTEST` | `false` | Strategy backtesting | MVP Hidden | MVP - Already works, enable for users |
| `enable_advanced_metrics` | `FEATURE_ENABLE_ADVANCED_METRICS` | `false` | Advanced analytics | MVP Hidden | v1.1 - After implementing proper Sharpe/drawdown |
| `enable_live_trading` | `FEATURE_ENABLE_LIVE_TRADING` | `false` | Real money trading | MVP Hidden | v1.2 - After extensive testing + user opt-in |
| `enable_telegram` | `FEATURE_ENABLE_TELEGRAM` | `false` | Telegram notifications | MVP Hidden | v1.1 - After implementing notification service |
| `enable_email_notifications` | `FEATURE_ENABLE_EMAIL_NOTIFICATIONS` | `false` | Email alerts | MVP Hidden | v1.1 - After implementing email service |
| `enable_webhooks` | `FEATURE_ENABLE_WEBHOOKS` | `false` | Webhook integrations | MVP Hidden | v1.2 - After webhook service implementation |
| `enable_paper_trading` | `FEATURE_ENABLE_PAPER_TRADING` | `true` | Paper trading mode | MVP Enabled | Always on for MVP |
| `enable_export` | `FEATURE_ENABLE_EXPORT` | `false` | Data export | MVP Hidden | v1.1 - After export service |
| `enable_multi_symbol_backtest` | `FEATURE_ENABLE_MULTI_SYMBOL_BACKTEST` | `false` | Multi-symbol backtesting | Not Implemented | v1.2 - After implementation |
| `enable_short_positions` | `FEATURE_ENABLE_SHORT_POSITIONS` | `false` | Short selling | Not Implemented | v1.2 - After implementation |
| `enable_strategy_automation` | `FEATURE_ENABLE_STRATEGY_AUTOMATION` | `false` | Auto-execute strategies | Not Implemented | v2.0 - Trading bot |
| `enable_social_trading` | `FEATURE_ENABLE_SOCIAL_TRADING` | `false` | Copy trading | Not Implemented | v2.0 - Future feature |

---

## FRONTEND FEATURE FLAGS

**Location:** `frontend/src/lib/featureFlags.ts`
**Configuration:** Environment variables (`NEXT_PUBLIC_FEATURE_*`)

| Flag Name | ENV Variable | Default | Purpose | UI Impact |
|-----------|--------------|---------|---------|-----------|
| `enableLiveTrading` | `NEXT_PUBLIC_FEATURE_ENABLE_LIVE_TRADING` | `false` | Show live trading toggle | Hides live trading option in settings |
| `enablePaperTrading` | `NEXT_PUBLIC_FEATURE_ENABLE_PAPER_TRADING` | `true` | Paper trading UI | Shows paper trading features |
| `enableSmartOrders` | `NEXT_PUBLIC_FEATURE_ENABLE_SMART_ORDERS` | `true` | Smart order button | Shows "Smart Order" quick action |
| `enableMLStrategy` | `NEXT_PUBLIC_FEATURE_ENABLE_ML_STRATEGY` | `false` | ML strategy option | Hides ML-based strategies |
| `enableBacktest` | `NEXT_PUBLIC_FEATURE_ENABLE_BACKTEST` | `false` | Backtest button | Hides backtest functionality |
| `enableStrategyCreation` | `NEXT_PUBLIC_FEATURE_ENABLE_STRATEGY_CREATION` | `false` | Create strategy button | Hides "New Strategy" button |
| `enableAdvancedMetrics` | `NEXT_PUBLIC_FEATURE_ENABLE_ADVANCED_METRICS` | `false` | Advanced analytics | Hides advanced metrics in analytics page |
| `enablePerformanceCharts` | `NEXT_PUBLIC_FEATURE_ENABLE_PERFORMANCE_CHARTS` | `true` | Performance charts | Shows charts in analytics |
| `enablePnLCharts` | `NEXT_PUBLIC_FEATURE_ENABLE_PNL_CHARTS` | `true` | P&L charts | Shows P&L visualization |
| `enableTelegram` | `NEXT_PUBLIC_FEATURE_ENABLE_TELEGRAM` | `false` | Telegram settings | Hides Telegram config in settings |
| `enableEmailNotifications` | `NEXT_PUBLIC_FEATURE_ENABLE_EMAIL_NOTIFICATIONS` | `false` | Email settings | Hides email config in settings |
| `enableWebhooks` | `NEXT_PUBLIC_FEATURE_ENABLE_WEBHOOKS` | `false` | Webhook settings | Hides webhook config in settings |
| `enableDarkMode` | `NEXT_PUBLIC_FEATURE_ENABLE_DARK_MODE` | `true` | Dark mode toggle | Shows dark mode switch |
| `enableExport` | `NEXT_PUBLIC_FEATURE_ENABLE_EXPORT` | `false` | Export buttons | Hides CSV/PDF export options |

---

## USAGE EXAMPLES

### Backend

```python
from utils.feature_flags import flags

if flags.enable_backtest:
    # Run backtest
    result = backtest_service.run()
else:
    raise HTTPException(403, "Backtesting not available")
```

### Frontend

```typescript
import { FeatureGate, useFeatureFlag } from '@/lib/featureFlags';

// Component-based gating
<FeatureGate feature="enableBacktest">
  <BacktestButton />
</FeatureGate>

// Hook-based gating
const canBacktest = useFeatureFlag('enableBacktest');
if (canBacktest) {
  // Show backtest UI
}
```

---

## DEPLOYMENT CONFIGURATION

### MVP Production (.env.production)
```bash
# Enabled for MVP
FEATURE_ENABLE_PAPER_TRADING=true

# Disabled for MVP (v1.1+)
FEATURE_ENABLE_ML_STRATEGY=false
FEATURE_ENABLE_BACKTEST=false  # ⚠️ Should be true - already works
FEATURE_ENABLE_ADVANCED_METRICS=false
FEATURE_ENABLE_LIVE_TRADING=false
FEATURE_ENABLE_TELEGRAM=false
FEATURE_ENABLE_EMAIL_NOTIFICATIONS=false
FEATURE_ENABLE_WEBHOOKS=false
FEATURE_ENABLE_EXPORT=false
```

### v1.1 Preview
```bash
# Newly enabled
FEATURE_ENABLE_BACKTEST=true
FEATURE_ENABLE_ADVANCED_METRICS=true
FEATURE_ENABLE_TELEGRAM=true
FEATURE_ENABLE_EMAIL_NOTIFICATIONS=true
FEATURE_ENABLE_EXPORT=true
```

### v1.2 Beta
```bash
# Newly enabled
FEATURE_ENABLE_LIVE_TRADING=true  # With user opt-in
FEATURE_ENABLE_WEBHOOKS=true
FEATURE_ENABLE_MULTI_SYMBOL_BACKTEST=true
FEATURE_ENABLE_SHORT_POSITIONS=true
```

---

## FLAG SYNCHRONIZATION

⚠️ **CRITICAL:** Backend and frontend flags must stay synchronized!

| Feature | Backend Flag | Frontend Flag | Must Match |
|---------|--------------|---------------|------------|
| Backtesting | `enable_backtest` | `enableBacktest` | ✅ Yes |
| Live Trading | `enable_live_trading` | `enableLiveTrading` | ✅ Yes |
| ML Strategy | `enable_ml_strategy` | `enableMLStrategy` | ✅ Yes |
| Telegram | `enable_telegram` | `enableTelegram` | ✅ Yes |

**Recommendation:** Create deployment script to sync both .env files

---

## ORPHANED FLAGS (Need Cleanup)

No orphaned flags detected. All flags have corresponding code checks.

---

## ZOMBI FEATURES (Code but no flag)

Features that exist but have no feature flag protection:

1. **Strategy Creation Form** - Form exists (placeholder), button should be gated
2. **Win/Loss Streak** - UI exists, backend missing, should be gated as "coming soon"

**Recommendation:** Add flags or remove placeholder code

---

## MISSING FLAGS (Should Exist)

Features that need feature flags:

1. **WebSocket Live Prices** - Always on, should have flag for fallback control
2. **Demo Data Fallback** - Portfolio/analytics fall back to demo data, should be controllable
3. **Auto-refresh Intervals** - Dashboard auto-refresh could be flagged for performance control

---

## ACTIVATION DECISION TREE

```
Is feature fully implemented? → NO → Keep disabled, add to roadmap
  ↓ YES
Is feature tested? → NO → Enable in dev/staging only
  ↓ YES
Does feature have external dependencies? → YES → Verify API keys/services available
  ↓ NO
Is feature high-risk (e.g., live trading)? → YES → Enable per-user with opt-in
  ↓ NO
Enable globally in production ✅
```

---

## RECOMMENDATIONS

### MVP (Current)
1. ✅ Enable `FEATURE_ENABLE_BACKTEST` - Already works perfectly
2. ✅ Keep paper trading enabled
3. ❌ Keep live trading disabled
4. ❌ Keep ML/advanced features disabled

### v1.1 (Next Release)
1. Enable backtesting globally
2. Enable advanced metrics after fixing Sharpe/drawdown
3. Implement and enable Telegram/email notifications
4. Enable export functionality

### v1.2 (Future)
1. Enable live trading with user opt-in and legal disclaimers
2. Enable webhooks
3. Add multi-symbol backtesting
4. Add short positions

---

**End of Feature Flags Catalog**
