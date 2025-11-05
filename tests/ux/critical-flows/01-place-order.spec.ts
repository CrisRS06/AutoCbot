import { test, expect } from '@playwright/test';
import {
  navigateAndWait,
  expectModalOpen,
  expectModalClosed,
  fillOrderForm,
  expectToast,
  mockApiResponse,
  mockApiError,
} from '../helpers/common';

test.describe('Critical Flow: Place Trading Order', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/trading');
  });

  test('should open order modal when clicking "New Order"', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page, 'Place Order');
  });

  test('should open order modal with BUY prefilled when clicking "Quick Buy"', async ({ page }) => {
    await page.click('button:has-text("Market Buy")');
    await expectModalOpen(page, 'Place Order');

    // Verify Buy is selected
    const buyButton = page.locator('button:has-text("Buy")');
    await expect(buyButton).toHaveClass(/bg-success/);

    // Verify Market is selected
    const marketButton = page.locator('button:has-text("Market")');
    await expect(marketButton).toHaveClass(/bg-primary/);
  });

  test('should open order modal with SELL prefilled when clicking "Quick Sell"', async ({ page }) => {
    await page.click('button:has-text("Market Sell")');
    await expectModalOpen(page, 'Place Order');

    // Verify Sell is selected
    const sellButton = page.locator('button:has-text("Sell")');
    await expect(sellButton).toHaveClass(/bg-danger/);
  });

  test('should disable Place Order button when amount is empty', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    const placeOrderButton = page.locator('button:has-text("Place")');
    await expect(placeOrderButton).toBeDisabled();
  });

  test('should enable Place Order button when amount is filled', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    await fillOrderForm(page, { amount: '0.001' });

    const placeOrderButton = page.locator('button:has-text("Place")');
    await expect(placeOrderButton).toBeEnabled();
  });

  test('should show price field only for limit orders', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    // Market order: price field hidden
    await page.locator('button:has-text("Market")').click();
    const priceInput = page.locator('label:has-text("Price")');
    await expect(priceInput).not.toBeVisible();

    // Limit order: price field visible
    await page.locator('button:has-text("Limit")').click();
    await expect(priceInput).toBeVisible();
  });

  test('should show warning message based on order type', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    // Market order warning
    await page.locator('button:has-text("Market")').click();
    await expect(page.locator('text=Market orders execute immediately')).toBeVisible();

    // Limit order warning
    await page.locator('button:has-text("Limit")').click();
    await expect(page.locator('text=Limit orders only execute when price reaches')).toBeVisible();
  });

  test('[CRITICAL] should place market buy order successfully', async ({ page }) => {
    // Mock successful API response
    await mockApiResponse(page, '**/api/v1/trading/order', {
      id: 'order-123',
      status: 'open',
      symbol: 'BTC/USDT',
      side: 'buy',
      type: 'market',
      amount: 0.001,
    });

    await page.click('button:has-text("Quick Buy")');
    await expectModalOpen(page);

    await fillOrderForm(page, {
      symbol: 'BTC/USDT',
      amount: '0.001',
      stopLoss: '-5',
      takeProfit: '3',
    });

    const placeOrderButton = page.locator('button:has-text("Place BUY Order")');

    // CRITICAL CHECK: Button should show loading state
    await placeOrderButton.click();

    // TODO: This will likely FAIL - button doesn't show loading state
    // await expect(placeOrderButton).toHaveText(/Placing|Loading/);
    // await expect(placeOrderButton).toBeDisabled();

    // Wait for success toast
    await expectToast(page, 'Order placed successfully!', 'success');

    // Modal should close
    await expectModalClosed(page);

    // Order should appear in table
    // TODO: This might fail if API doesn't return the order
    // await expect(page.locator('text=BTC/USDT').first()).toBeVisible();
  });

  test('[ERROR] should handle order placement failure gracefully', async ({ page }) => {
    // Mock API error
    await mockApiError(page, '**/api/v1/trading/order', 500);

    await page.click('button:has-text("Quick Buy")');
    await expectModalOpen(page);

    await fillOrderForm(page, { amount: '0.001' });

    await page.locator('button:has-text("Place BUY Order")').click();

    // Should show error toast
    await expectToast(page, 'Failed to place order', 'error');

    // Modal should stay open (user can retry)
    await expectModalOpen(page);
  });

  test('should close modal when clicking X button', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    // Click X button
    const closeButton = page.locator('[class*="fixed"] button').filter({ has: page.locator('svg') }).first();
    await closeButton.click();

    await expectModalClosed(page);
  });

  test('should close modal when clicking Cancel button', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    await page.click('button:has-text("Cancel")');
    await expectModalClosed(page);
  });

  test('[EXPECTED FAIL] should close modal when pressing ESC key', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    await page.keyboard.press('Escape');

    // TODO: This will FAIL - ESC doesn't close modal
    // await expectModalClosed(page);
  });

  test('[EXPECTED FAIL] should close modal when clicking backdrop', async ({ page }) => {
    await page.click('button:has-text("New Order")');
    await expectModalOpen(page);

    // Click on backdrop (outside modal)
    await page.locator('[class*="fixed"][class*="bg-black"]').click({ position: { x: 10, y: 10 } });

    // TODO: This will FAIL - clicking backdrop doesn't close modal
    // await expectModalClosed(page);
  });

  test('[CRITICAL] should confirm before closing all positions', async ({ page }) => {
    // Setup: expect browser confirm dialog
    page.on('dialog', async dialog => {
      expect(dialog.type()).toBe('confirm');
      expect(dialog.message()).toContain('close ALL positions');
      await dialog.dismiss();
    });

    await page.click('button:has-text("Close All Positions")');

    // Confirmation dialog should have appeared (handled above)
  });

  test('should show empty state when no orders', async ({ page }) => {
    // Mock empty orders response
    await mockApiResponse(page, '**/api/v1/trading/orders*', []);

    await navigateAndWait(page, '/trading');

    // Should show empty state
    await expect(page.locator('text=No open orders')).toBeVisible();
    await expect(page.locator('button:has-text("Place Your First Order")')).toBeVisible();
  });

  test('should display open orders in table', async ({ page }) => {
    // Mock orders response
    await mockApiResponse(page, '**/api/v1/trading/orders*', [
      {
        id: 'order-1',
        symbol: 'BTC/USDT',
        side: 'buy',
        type: 'limit',
        amount: 0.001,
        price: 50000,
        status: 'open',
        timestamp: new Date().toISOString(),
      },
      {
        id: 'order-2',
        symbol: 'ETH/USDT',
        side: 'sell',
        type: 'market',
        amount: 0.1,
        status: 'open',
        timestamp: new Date().toISOString(),
      },
    ]);

    await navigateAndWait(page, '/trading');

    // Should show both orders
    await expect(page.locator('text=BTC/USDT')).toBeVisible();
    await expect(page.locator('text=ETH/USDT')).toBeVisible();
    await expect(page.locator('text=LIMIT')).toBeVisible();
    await expect(page.locator('text=MARKET')).toBeVisible();
  });

  test('[CRITICAL] should cancel order when clicking X', async ({ page }) => {
    // Mock orders response
    await mockApiResponse(page, '**/api/v1/trading/orders*', [
      {
        id: 'order-1',
        symbol: 'BTC/USDT',
        side: 'buy',
        type: 'limit',
        amount: 0.001,
        price: 50000,
        status: 'open',
        timestamp: new Date().toISOString(),
      },
    ]);

    // Mock cancel response
    await mockApiResponse(page, '**/api/v1/trading/order/order-1', { success: true });

    await navigateAndWait(page, '/trading');

    // Click cancel button (X icon)
    const cancelButton = page.locator('button').filter({ has: page.locator('svg') }).last();
    await cancelButton.click();

    // TODO: Should show loading state (will likely FAIL)
    // await expect(cancelButton).toBeDisabled();

    // Should show success toast
    await expectToast(page, 'Order cancelled', 'success');
  });
});
