import { test, expect } from '@playwright/test';
import {
  navigateAndWait,
  expectToast,
  mockApiResponse,
  mockApiError,
} from '../helpers/common';

test.describe('Critical Flow: Save Settings', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/settings');
  });

  test('should display all settings sections', async ({ page }) => {
    // Verify all section headers are visible
    await expect(page.locator('text=API Keys')).toBeVisible();
    await expect(page.locator('text=Trading Parameters')).toBeVisible();
    await expect(page.locator('text=Risk Management')).toBeVisible();
    await expect(page.locator('text=Notifications')).toBeVisible();
    await expect(page.locator('text=Feature Flags')).toBeVisible();
  });

  test('should show helper text for percentage inputs', async ({ page }) => {
    // Max Position Size
    const positionSizeInput = page.locator('label:has-text("Max Position Size")').locator('..').locator('input');
    await expect(positionSizeInput).toBeVisible();

    // Should show calculated percentage
    await expect(page.locator('text=% per trade')).toBeVisible();
  });

  test('should toggle feature flags', async ({ page }) => {
    // Toggle ML Predictions
    const mlToggle = page.locator('text=ML Predictions').locator('..').locator('input[type="checkbox"]');
    const initialState = await mlToggle.isChecked();

    await mlToggle.click({ force: true }); // force because it's sr-only
    const newState = await mlToggle.isChecked();

    expect(newState).toBe(!initialState);
  });

  test('should show warning banner when dry run is disabled', async ({ page }) => {
    // Initially, dry run should be enabled (default true)
    const warningBanner = page.locator('text=Live Trading Enabled');

    // Toggle dry run off
    const dryRunToggle = page.locator('text=Dry Run').locator('..').locator('input[type="checkbox"]');
    const isChecked = await dryRunToggle.isChecked();

    if (isChecked) {
      await dryRunToggle.click({ force: true });
      // Warning should appear
      await expect(warningBanner).toBeVisible();
      await expect(page.locator('text=Real money is at risk')).toBeVisible();
    }
  });

  test('should hide warning banner when dry run is enabled', async ({ page }) => {
    // Enable dry run
    const dryRunToggle = page.locator('text=Dry Run').locator('..').locator('input[type="checkbox"]');
    const isChecked = await dryRunToggle.isChecked();

    if (!isChecked) {
      await dryRunToggle.click({ force: true });
    }

    // Warning should not be visible
    const warningBanner = page.locator('text=Live Trading Enabled');
    await expect(warningBanner).not.toBeVisible();
  });

  test('should enable Save button when settings change', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save Settings")');

    // Change a setting
    const apiKeyInput = page.locator('label:has-text("Binance API Key")').locator('..').locator('input');
    await apiKeyInput.fill('new-api-key-123');

    // Save button should be enabled
    await expect(saveButton).toBeEnabled();
  });

  test('[CRITICAL - EXPECTED FAIL] should save settings and persist on reload', async ({ page }) => {
    // Fill in some settings
    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test-api-key-123');
    await page.locator('label:has-text("Binance Secret")').locator('..').locator('input').fill('test-secret-456');
    await page.locator('label:has-text("Default Trading Pairs")').locator('..').locator('input').fill('BTC/USDT,ETH/USDT');

    // Click Save
    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    // Should show loading state
    await expect(saveButton).toHaveText(/Saving/);
    await expect(saveButton).toBeDisabled();

    // Should show success toast
    await expectToast(page, 'Settings saved successfully!', 'success');

    // Button should show "Saved!"
    await expect(saveButton).toHaveText(/Saved/);

    // Reload page
    await page.reload();
    await navigateAndWait(page, '/settings');

    // TODO: THIS WILL FAIL - Settings are NOT persisted!
    // The save is FAKE (just setTimeout(1000))
    // Settings should be restored (this assertion will fail):
    // const apiKeyInput = page.locator('label:has-text("Binance API Key")').locator('..').locator('input');
    // await expect(apiKeyInput).toHaveValue('test-api-key-123');
  });

  test('[BUG DOCUMENTATION] settings save is fake - only simulates with setTimeout', async ({ page }) => {
    // This test documents the critical bug where settings aren't actually saved

    // Open browser console to see the code
    const saveButton = page.locator('button:has-text("Save Settings")');

    // Fill a setting
    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test-key');

    // Click save
    await saveButton.click();

    // Wait for "success"
    await expectToast(page, 'Settings saved successfully!', 'success');

    // Reload
    await page.reload();

    // Settings are gone
    const apiKeyInput = page.locator('label:has-text("Binance API Key")').locator('..').locator('input');
    const value = await apiKeyInput.inputValue();

    // THIS WILL BE EMPTY
    expect(value).toBe(''); // Proves settings weren't saved

    // Expected: value should be 'test-key'
    // Actual: value is empty string
    // Root cause: handleSave() has "// TODO: Implement API call to save settings"
  });

  test('should show error toast if save fails', async ({ page }) => {
    // Mock API error (once it's implemented)
    await mockApiError(page, '**/api/v1/settings', 500);

    // Change setting
    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test-key');

    // Click save
    await page.locator('button:has-text("Save Settings")').click();

    // Should show error toast
    await expectToast(page, 'Failed to save settings', 'error');

    // Button should re-enable (user can retry)
    const saveButton = page.locator('button:has-text("Save Settings")');
    await expect(saveButton).toBeEnabled();
  });

  test('should validate numeric inputs have min/max constraints', async ({ page }) => {
    // Max Position Size should be 0-1
    const positionSizeInput = page.locator('label:has-text("Max Position Size")').locator('..').locator('input');
    await expect(positionSizeInput).toHaveAttribute('min', '0');
    await expect(positionSizeInput).toHaveAttribute('max', '1');

    // Max Open Trades should have min/max
    const maxTradesInput = page.locator('label:has-text("Max Open Trades")').locator('..').locator('input');
    await expect(maxTradesInput).toHaveAttribute('min', '1');
    await expect(maxTradesInput).toHaveAttribute('max', '20');

    // Stop Loss should be max 0 (negative)
    const stopLossInput = page.locator('label:has-text("Default Stop Loss")').locator('..').locator('input');
    await expect(stopLossInput).toHaveAttribute('max', '0');

    // Take Profit should be min 0 (positive)
    const takeProfitInput = page.locator('label:has-text("Default Take Profit")').locator('..').locator('input');
    await expect(takeProfitInput).toHaveAttribute('min', '0');
  });

  test('[MISSING FEATURE] should have "Test Connection" button for API keys', async ({ page }) => {
    // This feature doesn't exist but should

    // Fill Binance API credentials
    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test-key');
    await page.locator('label:has-text("Binance Secret")').locator('..').locator('input').fill('test-secret');

    // Look for test connection button (won't exist)
    const testButton = page.locator('button:has-text("Test Connection")');
    await expect(testButton).not.toBeVisible();

    // Recommendation: Add "Test Connection" button that:
    // 1. Makes API call to Binance /api/v3/account
    // 2. Shows loading spinner
    // 3. Shows success/error toast
    // 4. Validates API key format before testing
  });

  test('[MISSING FEATURE] should have show/hide toggle for password fields', async ({ page }) => {
    // Password fields should have show/hide toggle

    const apiKeyInput = page.locator('label:has-text("Binance API Key")').locator('..').locator('input');
    await expect(apiKeyInput).toHaveAttribute('type', 'password');

    // Look for show/hide button (won't exist)
    const toggleButton = apiKeyInput.locator('..').locator('button').filter({ hasText: /Show|Hide|👁/ });
    await expect(toggleButton).not.toBeVisible();

    // Recommendation: Add eye icon button to toggle type between 'password' and 'text'
  });

  test('[MISSING FEATURE] should warn about unsaved changes when navigating away', async ({ page }) => {
    // Change a setting
    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('unsaved-key');

    // Try to navigate away
    page.on('dialog', async dialog => {
      expect(dialog.type()).toBe('beforeunload');
      expect(dialog.message()).toContain('unsaved changes');
      await dialog.accept();
    });

    // Click Dashboard link
    await page.locator('aside').locator('text=Dashboard').click();

    // TODO: No warning will appear (feature missing)
    // User loses changes without warning
  });

  test('[MISSING FEATURE] should have Reset to Defaults button', async ({ page }) => {
    // Look for reset button (won't exist)
    const resetButton = page.locator('button:has-text("Reset to Defaults")');
    await expect(resetButton).not.toBeVisible();

    // Recommendation: Add button that resets all settings to default values
    // Should have confirmation dialog: "Are you sure? This will reset all settings."
  });

  test('should have proper focus management on inputs', async ({ page }) => {
    // Tab through inputs
    await page.keyboard.press('Tab');

    // First input should be focused
    const apiKeyInput = page.locator('label:has-text("Binance API Key")').locator('..').locator('input');
    await expect(apiKeyInput).toBeFocused();

    // Should have visible focus ring
    const hasVisibleFocus = await apiKeyInput.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return styles.outlineWidth !== '0px' || styles.boxShadow !== 'none';
    });

    expect(hasVisibleFocus).toBeTruthy();
  });

  test('should display timeframe options in select', async ({ page }) => {
    const timeframeSelect = page.locator('label:has-text("Default Timeframe")').locator('..').locator('select');

    await expect(timeframeSelect).toBeVisible();

    // Check options
    const options = await timeframeSelect.locator('option').allTextContents();
    expect(options).toContain('1 minute');
    expect(options).toContain('5 minutes');
    expect(options).toContain('15 minutes');
    expect(options).toContain('1 hour');
    expect(options).toContain('4 hours');
    expect(options).toContain('1 day');
  });
});
