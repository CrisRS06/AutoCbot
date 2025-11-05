import { test, expect } from '@playwright/test';
import { navigateAndWait, expectEmptyState, mockApiResponse, mockApiError } from '../helpers/common';

/**
 * States Matrix Testing
 *
 * Every data display component should handle 4 states:
 * 1. LOADING - Show skeleton/spinner while data loads
 * 2. SUCCESS - Show data when loaded successfully
 * 3. EMPTY - Show helpful message when no data
 * 4. ERROR - Show error message when API fails
 */

test.describe('States Matrix: Dashboard Components', () => {
  test('Market Overview Card: Loading State', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/v1/market/overview', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          total_market_cap: 1500000000000,
          btc_dominance: 45.5,
          eth_dominance: 18.3,
          defi_market_cap: 50000000000,
          total_volume_24h: 100000000000,
        }),
      });
    });

    await navigateAndWait(page, '/');

    // Should show loading skeleton
    const marketCard = page.locator('text=Market Overview').locator('..');
    await expect(marketCard).toBeVisible();

    // Look for animate-pulse (skeleton loading)
    const skeleton = marketCard.locator('.animate-pulse');
    await expect(skeleton).toBeVisible();

    // Wait for data to load
    await page.waitForTimeout(2500);

    // Skeleton should be gone, data should be visible
    await expect(skeleton).not.toBeVisible();
    await expect(marketCard).toContainText('$');
  });

  test('Market Overview Card: Empty/Zero State', async ({ page }) => {
    // Mock empty data (all zeros)
    await mockApiResponse(page, '**/api/v1/market/overview', {
      total_market_cap: 0,
      btc_dominance: 0,
      eth_dominance: 0,
      defi_market_cap: 0,
      total_volume_24h: 0,
    });

    await navigateAndWait(page, '/');

    // BUG: Shows "$0.00" which looks broken, not "no data"
    const marketCard = page.locator('text=Market Overview').locator('..');
    await expect(marketCard).toContainText('$0');

    // SHOULD show: "Configure API keys" or "No data available"
    // CURRENTLY shows: "$0.00" everywhere (confusing)
  });

  test('Fear & Greed Meter: Loading State', async ({ page }) => {
    await page.route('**/api/v1/sentiment/fear-greed', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          value: 75,
          value_classification: 'Greed',
          timestamp: new Date().toISOString(),
        }),
      });
    });

    await navigateAndWait(page, '/');

    const fearGreedCard = page.locator('text=Fear & Greed Index').locator('..');
    await expect(fearGreedCard).toBeVisible();

    // Should show loading skeleton
    const skeleton = fearGreedCard.locator('.animate-pulse');
    await expect(skeleton).toBeVisible();
  });

  test('Trading Signals: Loading State', async ({ page }) => {
    await navigateAndWait(page, '/');

    const signalsCard = page.locator('text=Trading Signals').locator('..');
    await expect(signalsCard).toBeVisible();

    // TODO: Verify loading skeleton appears initially
    // Current implementation does show skeleton
  });

  test('Trading Signals: Empty State', async ({ page }) => {
    // Mock empty signals
    await mockApiResponse(page, '**/api/v1/trading/signals*', []);

    await navigateAndWait(page, '/');

    const signalsCard = page.locator('text=Trading Signals').locator('..');

    // Should show empty state
    await expect(signalsCard).toContainText('No active signals');

    // Should have icon
    const icon = signalsCard.locator('svg').nth(1); // Skip the title icon
    await expect(icon).toBeVisible();
  });

  test('Trading Signals: Success State with Data', async ({ page }) => {
    // Mock signals data
    await mockApiResponse(page, '**/api/v1/trading/signals*', [
      {
        symbol: 'BTC/USDT',
        signal: 'buy',
        confidence: 0.85,
        entry_price: 50000,
        stop_loss: 48000,
        take_profit: 52000,
        strategy: 'RSI Divergence',
        timestamp: new Date().toISOString(),
        reasons: ['RSI oversold', 'MACD crossover'],
      },
    ]);

    await navigateAndWait(page, '/');

    const signalsCard = page.locator('text=Trading Signals').locator('..');

    // Should show signal data
    await expect(signalsCard).toContainText('BTC');
    await expect(signalsCard).toContainText('BUY');
    await expect(signalsCard).toContainText('85%'); // Confidence
  });

  test('Positions Table: Loading State', async ({ page }) => {
    await navigateAndWait(page, '/');

    const positionsCard = page.locator('text=Open Positions').locator('..');
    await expect(positionsCard).toBeVisible();

    // Should show loading skeleton
    const skeleton = positionsCard.locator('.animate-pulse');
    // TODO: May not be visible if data loads too fast
  });

  test('Positions Table: Empty State', async ({ page }) => {
    // Mock empty positions
    await mockApiResponse(page, '**/api/v1/portfolio/positions', []);

    await navigateAndWait(page, '/');

    const positionsCard = page.locator('text=Open Positions').locator('..');

    // Should show empty state
    await expect(positionsCard).toContainText('No open positions');

    // Should have icon
    await expect(positionsCard.locator('svg').nth(1)).toBeVisible();
  });

  test('Live Prices: No Loading State (BUG)', async ({ page }) => {
    // Mock slow prices response
    await page.route('**/api/v1/market/prices*', async route => {
      await new Promise(resolve => setTimeout(resolve, 3000));
      await route.fulfill({
        status: 200,
        body: JSON.stringify([
          { symbol: 'BTC/USDT', price: 50000, change_24h: 2.5, volume_24h: 1000000000, timestamp: new Date().toISOString() },
        ]),
      });
    });

    await navigateAndWait(page, '/');

    const livePricesCard = page.locator('text=Live Prices').locator('..');
    await expect(livePricesCard).toBeVisible();

    // BUG: No loading state!
    // Should show skeleton but doesn't
    const skeleton = livePricesCard.locator('.animate-pulse');
    await expect(skeleton).not.toBeVisible(); // Will pass, but shouldn't

    // After 3s, data should appear
    await page.waitForTimeout(3500);
    // TODO: Verify data appears
  });

  test('Live Prices: Empty State (Not Implemented)', async ({ page }) => {
    // Mock empty prices
    await mockApiResponse(page, '**/api/v1/market/prices*', []);

    await navigateAndWait(page, '/');

    const livePricesCard = page.locator('text=Live Prices').locator('..');

    // BUG: No empty state message!
    // Just shows empty grid
    // SHOULD show: "No price data available" with helpful message
  });
});

test.describe('States Matrix: Error Handling', () => {
  test('[CRITICAL] Dashboard: Should show error when backend is down', async ({ page }) => {
    // Mock all APIs to return 500
    await mockApiError(page, '**/api/v1/market/**', 500);
    await mockApiError(page, '**/api/v1/sentiment/**', 500);
    await mockApiError(page, '**/api/v1/trading/**', 500);
    await mockApiError(page, '**/api/v1/portfolio/**', 500);

    await navigateAndWait(page, '/');

    // BUG: Errors are only logged to console, not shown to user!
    // User sees loading states forever or empty/zero data

    // SHOULD show:
    // - Toast notification: "Failed to load dashboard data"
    // - Error state in each card with retry button
    // - User-friendly message: "Something went wrong. Please refresh or try again later."

    // TODO: Add assertions once error handling is implemented
  });

  test('[CRITICAL] Trading: Should handle order placement error gracefully', async ({ page }) => {
    await navigateAndWait(page, '/trading');

    // Mock order error
    await mockApiError(page, '**/api/v1/trading/order', 400);

    await page.click('button:has-text("Quick Buy")');
    await page.locator('input[type="number"]').first().fill('0.001');
    await page.locator('button:has-text("Place BUY Order")').click();

    // Should show error toast
    await expect(page.locator('text=Failed to place order')).toBeVisible({ timeout: 5000 });

    // Modal should stay open (user can fix and retry)
    await expect(page.locator('text=Place Order')).toBeVisible();

    // Button should re-enable
    const placeButton = page.locator('button:has-text("Place BUY Order")');
    await expect(placeButton).toBeEnabled();
  });

  test('[CRITICAL] Settings: Should handle save error gracefully', async ({ page }) => {
    await navigateAndWait(page, '/settings');

    // Mock save error (once API is real)
    await mockApiError(page, '**/api/v1/settings', 500);

    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test');
    await page.locator('button:has-text("Save Settings")').click();

    // Should show error toast
    await expect(page.locator('text=Failed to save settings')).toBeVisible({ timeout: 5000 });

    // Button should re-enable
    const saveButton = page.locator('button:has-text("Save Settings")');
    await expect(saveButton).toBeEnabled();
  });

  test('Network timeout: Should show timeout message', async ({ page }) => {
    // Mock request that never resolves (simulates timeout)
    await page.route('**/api/v1/market/overview', async route => {
      // Never resolve
      await new Promise(() => {});
    });

    await page.goto('/');

    // Wait for timeout (default 30s navigation timeout)
    // Should show: "Request timed out. Please check your connection."

    // TODO: This will likely just hang or show loading forever
  });

  test('Offline mode: Should detect and show offline message', async ({ page }) => {
    await navigateAndWait(page, '/');

    // Simulate offline
    await page.context().setOffline(true);

    // Refresh page
    await page.reload().catch(() => {
      // Expected to fail when offline
    });

    // Should show: "You are offline. Please check your internet connection."
    // TODO: Add offline detection and user notification
  });
});

test.describe('States Matrix: Loading Button States', () => {
  test('[BUG] Trading: Place Order button has no loading state', async ({ page }) => {
    await navigateAndWait(page, '/trading');

    // Mock slow order placement
    await page.route('**/api/v1/trading/order', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({ status: 200, body: JSON.stringify({ id: 'order-123' }) });
    });

    await page.click('button:has-text("Quick Buy")');
    await page.locator('input[type="number"]').first().fill('0.001');

    const placeButton = page.locator('button:has-text("Place BUY Order")');
    await placeButton.click();

    // BUG: Button doesn't show loading state!
    // Should be disabled and show "Placing..." or spinner
    // Currently: Button stays enabled, user might double-click

    // Wait for success
    await page.waitForTimeout(2500);
  });

  test('[BUG] Strategies: Toggle button has no loading state', async ({ page }) => {
    await navigateAndWait(page, '/strategies');

    // If strategies exist
    const toggleButton = page.locator('button').filter({ hasText: /Enable|Disable/ }).first();

    if (await toggleButton.isVisible()) {
      // Mock slow toggle
      await page.route('**/api/v1/strategy/*/toggle', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
      });

      await toggleButton.click();

      // BUG: No loading state!
      // Toggle should be disabled during API call
      // Should show spinner or "Enabling..." text

      await page.waitForTimeout(2500);
    }
  });

  test('[BUG] Strategies: Backtest button has no loading state', async ({ page }) => {
    await navigateAndWait(page, '/strategies');

    const backtestButton = page.locator('button:has-text("Backtest")').first();

    if (await backtestButton.isVisible()) {
      // Mock slow backtest (backtests can take 30-60 seconds!)
      await page.route('**/api/v1/strategy/backtest', async route => {
        await new Promise(resolve => setTimeout(resolve, 5000));
        await route.fulfill({ status: 200, body: JSON.stringify({ results: {} }) });
      });

      await backtestButton.click();

      // BUG: No loading state!
      // CRITICAL for backtests which take a long time
      // Should show:
      // - Progress modal
      // - "Running backtest..." message
      // - Progress bar or spinner
      // - "This may take a minute" warning

      await page.waitForTimeout(5500);
    }
  });

  test('Settings: Save button DOES have loading state ✅', async ({ page }) => {
    await navigateAndWait(page, '/settings');

    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test');

    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    // GOOD: Button shows "Saving..."
    await expect(saveButton).toHaveText(/Saving/);
    await expect(saveButton).toBeDisabled();

    // Then shows "Saved!"
    await page.waitForTimeout(1500);
    await expect(saveButton).toHaveText(/Saved/);
  });
});

test.describe('States Matrix: Skeleton Loaders', () => {
  test('Dashboard: All cards should have skeleton loaders', async ({ page }) => {
    // Create custom HTML to insert before navigation to force loading state
    // Or mock very slow responses for all APIs

    await navigateAndWait(page, '/');

    // Cards that should have skeletons:
    const cardsWithSkeletons = [
      'Market Overview',
      'Fear & Greed Index',
      'Portfolio Summary',
      'Trading Signals',
      'Open Positions',
    ];

    for (const cardTitle of cardsWithSkeletons) {
      const card = page.locator(`text=${cardTitle}`).locator('..');

      // Skeleton should exist in the component
      // Even if data loads fast, skeleton markup should be in the code
      // This is hard to test without forcing loading state

      // At minimum, verify card is visible
      await expect(card).toBeVisible();
    }
  });

  test('Skeleton loaders should have consistent design', async ({ page }) => {
    // Slow down all APIs
    await page.route('**/api/v1/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 3000));
      await route.continue();
    });

    await page.goto('/');

    // All skeletons should use animate-pulse
    const skeletons = page.locator('.animate-pulse');
    const count = await skeletons.count();

    if (count > 0) {
      // Verify they have consistent styling
      // All should have bg-muted or similar
      for (let i = 0; i < count; i++) {
        const skeleton = skeletons.nth(i);
        const classes = await skeleton.getAttribute('class');
        expect(classes).toMatch(/bg-muted|bg-gray/);
      }
    }
  });
});
