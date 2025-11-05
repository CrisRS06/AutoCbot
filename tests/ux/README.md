# 🎯 AutoCbot UX & Frontend E2E Tests

Comprehensive end-to-end test suite focused on user experience, interactive elements, and frontend quality.

---

## 📋 Test Categories

### 1. **Critical Flows** (`critical-flows/`)
Tests for user journeys that involve critical operations:
- `01-place-order.spec.ts` - Trading order placement (money at risk!)
- `02-settings-save.spec.ts` - Settings configuration (includes critical bug test)

### 2. **Dead Button Detection** (`dead-buttons/`)
Tests to ensure ALL interactive elements do something:
- `all-interactions.spec.ts` - Systematic verification of every button, link, form

### 3. **States Matrix** (`states/`)
Tests for proper state management:
- `loading-error-empty.spec.ts` - Loading, error, empty, and success states

---

## 🚀 Quick Start

### Install Dependencies
```bash
cd tests/ux
npm install
```

### Run All Tests
```bash
npm test
```

### Run Tests by Category
```bash
npm run test:critical        # Critical user flows only
npm run test:dead-buttons    # Dead button detection
npm run test:states          # States matrix
```

### Run in UI Mode (Interactive)
```bash
npm run test:ui
```

### Run in Headed Mode (See Browser)
```bash
npm run test:headed
```

### Debug Mode (Step Through)
```bash
npm run test:debug
```

### View Last Report
```bash
npm run report
```

---

## 🔍 Expected Results

### ✅ Tests Expected to Pass
- Dashboard navigation
- Modal open/close (via buttons)
- Form state management
- Empty state displays
- Some loading states (Dashboard components, Settings save button)

### ❌ Tests Expected to FAIL (Known Bugs)
1. **Settings Save Persistence** - Settings don't actually save (fake API call)
2. **Place Order Loading State** - Button doesn't show loading during submission
3. **Cancel Order Loading State** - No loading feedback
4. **Toggle Strategy Loading State** - No loading feedback
5. **Backtest Loading State** - No progress indication (critical for long operations)
6. **Modal ESC Key** - Can't close modals with Escape key
7. **Modal Backdrop Click** - Can't close modals by clicking outside
8. **Time Range Filters** - Don't trigger data refresh (Portfolio, Analytics)
9. **Live Prices Loading State** - No skeleton loader
10. **Error States** - Errors only log to console, no user-facing messages

---

## 🐛 Critical Bugs Documented

### 1. **FAKE SETTINGS SAVE** 🚨
**File:** `frontend/src/app/settings/page.tsx:59-71`

```typescript
const handleSave = async () => {
  setLoading(true)
  try {
    // TODO: Implement API call to save settings
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    toast.success('Settings saved successfully!')
    setSaved(true)
```

**Impact:**
- Users think their API keys and settings are saved
- Everything is lost on page refresh
- Could lead to trading with wrong parameters

**Fix:** Implement real backend endpoint:
```typescript
await fetch('/api/v1/settings', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(settings),
})
```

**Test:** `critical-flows/02-settings-save.spec.ts` → `should save settings and persist on reload`

---

### 2. **No Loading States on Critical Actions**
**Affected Pages:**
- Trading: Place Order, Cancel Order, Close All
- Strategies: Toggle Strategy, Run Backtest, Delete Strategy

**Impact:**
- User doesn't know if action is processing
- Might click multiple times (double orders!)
- For backtests (30-60s), user has no idea what's happening

**Fix:** Add loading state pattern:
```typescript
const [isSubmitting, setIsSubmitting] = useState(false)

const handleSubmit = async () => {
  setIsSubmitting(true)
  try {
    await api.call()
    toast.success('Done!')
  } finally {
    setIsSubmitting(false)
  }
}

// In button:
<button disabled={isSubmitting}>
  {isSubmitting ? 'Processing...' : 'Submit'}
</button>
```

**Tests:**
- `critical-flows/01-place-order.spec.ts` → Multiple tests
- `states/loading-error-empty.spec.ts` → `Loading Button States` section

---

### 3. **Modal Interaction Issues**
**Issues:**
- Can't close with ESC key
- Can't close by clicking backdrop

**Fix:** Add event handlers:
```typescript
useEffect(() => {
  const handleEsc = (e: KeyboardEvent) => {
    if (e.key === 'Escape') setShowModal(false)
  }
  window.addEventListener('keydown', handleEsc)
  return () => window.removeEventListener('keydown', handleEsc)
}, [])

// In backdrop:
<div onClick={() => setShowModal(false)} className="fixed inset-0 bg-black/50" />
```

**Tests:**
- `critical-flows/01-place-order.spec.ts` → `should close modal when pressing ESC key`
- `critical-flows/01-place-order.spec.ts` → `should close modal when clicking backdrop`

---

### 4. **No Error Handling for Users**
**Issue:** All errors only go to console.error(), user sees nothing

**Example:**
```typescript
try {
  const response = await tradingApi.getOrders('open')
  setOrders(response.data)
} catch (error) {
  console.error('Failed to load orders:', error)  // User doesn't see this!
}
```

**Fix:** Add user-facing error states:
```typescript
const [error, setError] = useState<string | null>(null)

try {
  const response = await tradingApi.getOrders('open')
  setOrders(response.data)
} catch (error) {
  setError('Failed to load orders. Please try again.')
  toast.error('Failed to load orders')
}

// In render:
{error && (
  <div className="text-center py-8">
    <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
    <p className="text-red-500">{error}</p>
    <button onClick={() => loadOrders()}>Retry</button>
  </div>
)}
```

**Tests:** `states/loading-error-empty.spec.ts` → `States Matrix: Error Handling`

---

## 📊 Test Coverage Goals

| Category | Target | Current |
|----------|--------|---------|
| Interactive elements tested | 100% | ~60% |
| Critical flows covered | 100% | 100% |
| Loading states verified | 100% | ~40% |
| Error states tested | 100% | 0% |
| Empty states tested | 100% | ~70% |
| Mobile responsiveness | 100% | 0% |

---

## 🔧 Test Configuration

**Browser:** Chromium (Desktop)
**Mobile:** Pixel 5, iPhone 12
**Viewport:** 1280x720 (desktop), 375x667 (mobile)
**Base URL:** http://localhost:3000
**Timeout:** 60s per test
**Retries:** 2 (on CI only)
**Screenshots:** On failure only
**Video:** On failure only

---

## 📝 Writing New Tests

### Basic Pattern
```typescript
import { test, expect } from '@playwright/test';
import { navigateAndWait, expectModalOpen } from '../helpers/common';

test.describe('My Feature', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/my-page');
  });

  test('should do something', async ({ page }) => {
    await page.click('button:has-text("Click Me")');
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

### Using Helpers
```typescript
// Navigate with loading wait
await navigateAndWait(page, '/trading');

// Check modal state
await expectModalOpen(page, 'Place Order');
await expectModalClosed(page);

// Check toast
await expectToast(page, 'Order placed successfully!', 'success');

// Mock API responses
await mockApiResponse(page, '**/api/v1/orders', { id: '123' });
await mockApiError(page, '**/api/v1/orders', 500);
```

---

## 🎯 CI/CD Integration

Tests run automatically on:
- Every PR
- Every commit to main
- Scheduled daily

**GitHub Actions Workflow:**
```yaml
- name: Run UX Tests
  run: |
    cd tests/ux
    npm ci
    npx playwright test
- name: Upload Report
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: tests/ux/playwright-report
```

---

## 🐞 Debugging Tips

### 1. Run Single Test
```bash
npx playwright test -g "should place order"
```

### 2. Run in Debug Mode
```bash
npx playwright test --debug
```

### 3. View Trace
```bash
npx playwright show-trace trace.zip
```

### 4. Take Screenshots
```typescript
await page.screenshot({ path: 'debug.png' });
```

### 5. Pause Execution
```typescript
await page.pause(); // Opens inspector
```

### 6. Console Logs
```typescript
page.on('console', msg => console.log(msg.text()));
```

---

## 📚 Resources

- [Playwright Docs](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Selectors Guide](https://playwright.dev/docs/selectors)
- [API Reference](https://playwright.dev/docs/api/class-test)

---

## ✅ Checklist for New Features

Before merging new frontend features:

- [ ] Add E2E test for happy path
- [ ] Add test for error case
- [ ] Add test for empty state
- [ ] Add test for loading state
- [ ] Test button disabled states
- [ ] Test form validation
- [ ] Test mobile viewport
- [ ] Test keyboard navigation
- [ ] Test with screen reader (manual)
- [ ] Check console for errors
- [ ] Verify loading states for all actions
- [ ] Ensure toasts appear for success/error
- [ ] Test ESC key for modals
- [ ] Test backdrop click for modals

---

**Last Updated:** 2025-11-05
**Test Suite Version:** 1.0.0
**Playwright Version:** 1.56.1
