import { test, expect } from '@playwright/test';
import { navigateAndWait } from '../helpers/common';

/**
 * Dead Button Detection Test Suite
 *
 * This test suite clicks every interactive element on every page
 * and verifies that SOMETHING happens (navigation, state change, modal, toast, etc.)
 *
 * Any element that does nothing is a "dead button" and needs fixing.
 */

test.describe('Dead Button Detection', () => {
  const pages = [
    { name: 'Dashboard', path: '/' },
    { name: 'Trading', path: '/trading' },
    { name: 'Portfolio', path: '/portfolio' },
    { name: 'Analytics', path: '/analytics' },
    { name: 'Strategies', path: '/strategies' },
    { name: 'Settings', path: '/settings' },
  ];

  test('Sidebar Navigation: All links should navigate', async ({ page }) => {
    await navigateAndWait(page, '/');

    const navLinks = [
      { text: 'Dashboard', expectedPath: '/' },
      { text: 'Trading', expectedPath: '/trading' },
      { text: 'Portfolio', expectedPath: '/portfolio' },
      { text: 'Analytics', expectedPath: '/analytics' },
      { text: 'Strategies', expectedPath: '/strategies' },
      { text: 'Settings', expectedPath: '/settings' },
    ];

    for (const link of navLinks) {
      await page.locator('aside').locator(`text=${link.text}`).click();
      await page.waitForLoadState('networkidle');

      // Verify URL changed
      expect(page.url()).toContain(link.expectedPath);

      // Verify active state is applied
      const activeLink = page.locator('aside').locator(`text=${link.text}`).locator('..');
      await expect(activeLink).toHaveClass(/bg-primary/);
    }
  });

  test('Mobile: Hamburger menu should open sidebar', async ({ page }) => {
    // Use mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await navigateAndWait(page, '/');

    // Sidebar should be hidden initially
    const sidebar = page.locator('aside');
    await expect(sidebar).toHaveClass(/-translate-x-full/);

    // Click hamburger menu
    const menuButton = page.locator('button').filter({ has: page.locator('svg') }).first();
    await menuButton.click();

    // Sidebar should be visible
    await expect(sidebar).toHaveClass(/translate-x-0/);

    // Backdrop should be visible
    const backdrop = page.locator('.fixed.inset-0.bg-black\\/50');
    await expect(backdrop).toBeVisible();

    // Click backdrop should close sidebar
    await backdrop.click();
    await expect(sidebar).toHaveClass(/-translate-x-full/);
  });

  test('Dashboard: All interactive elements do something', async ({ page }) => {
    await navigateAndWait(page, '/');

    // Note: Dashboard is mostly read-only with auto-refresh
    // Main interactions are navigation (tested above)

    // Verify page loaded successfully
    await expect(page.locator('h1:has-text("Dashboard")')).toBeVisible();
    await expect(page.locator('text=Market Overview')).toBeVisible();
    await expect(page.locator('text=Live Prices')).toBeVisible();
  });

  test('Trading Page: All buttons do something', async ({ page }) => {
    await navigateAndWait(page, '/trading');

    // Test "New Order" button
    await page.click('button:has-text("New Order")');
    await expect(page.locator('text=Place Order')).toBeVisible(); // Modal opened
    await page.keyboard.press('Escape'); // Try to close (will fail currently)
    await page.click('button:has-text("Cancel")'); // Close via button

    // Test "Quick Buy" button
    await page.click('button:has-text("Market Buy")');
    await expect(page.locator('text=Place Order')).toBeVisible();
    await page.click('button:has-text("Cancel")');

    // Test "Quick Sell" button
    await page.click('button:has-text("Market Sell")');
    await expect(page.locator('text=Place Order')).toBeVisible();
    await page.click('button:has-text("Cancel")');

    // Test "Limit Order" button
    await page.click('button:has-text("Limit Order")');
    await expect(page.locator('text=Place Order')).toBeVisible();
    await page.click('button:has-text("Cancel")');

    // Test "Close All Positions" button
    page.once('dialog', dialog => dialog.dismiss());
    await page.click('button:has-text("Close All Positions")');
    // Confirmation dialog should appear (handled above)
  });

  test('Trading Page: Empty state CTA works', async ({ page }) => {
    await navigateAndWait(page, '/trading');

    // If empty state is visible
    const emptyCTA = page.locator('button:has-text("Place Your First Order")');
    if (await emptyCTA.isVisible()) {
      await emptyCTA.click();
      await expect(page.locator('text=Place Order')).toBeVisible(); // Modal opened
    }
  });

  test('Settings Page: Save button works', async ({ page }) => {
    await navigateAndWait(page, '/settings');

    // Change a setting
    await page.locator('label:has-text("Binance API Key")').locator('..').locator('input').fill('test');

    // Click save
    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    // Should show loading or success state
    await expect(saveButton).toHaveText(/Saving|Saved/);
  });

  test('Settings Page: All toggles work', async ({ page }) => {
    await navigateAndWait(page, '/settings');

    const toggles = [
      'ML Predictions',
      'Paper Trading',
      'Dry Run',
    ];

    for (const toggleName of toggles) {
      const toggle = page.locator(`text=${toggleName}`).locator('..').locator('input[type="checkbox"]');
      const initialState = await toggle.isChecked();

      // Click toggle
      await toggle.click({ force: true });

      // State should change
      const newState = await toggle.isChecked();
      expect(newState).toBe(!initialState);
    }
  });

  test('Strategies Page: All action buttons work', async ({ page }) => {
    await navigateAndWait(page, '/strategies');

    // Test "Create New Strategy" button
    const createButton = page.locator('button:has-text("Create New Strategy")').first();
    if (await createButton.isVisible()) {
      await createButton.click();
      // Modal should open (even if placeholder)
      await page.waitForTimeout(500); // Wait for modal animation
      // TODO: Verify modal opened
    }

    // Test strategy action buttons (if strategies exist)
    const toggleButtons = page.locator('button').filter({ hasText: /Enable|Disable/ });
    const toggleCount = await toggleButtons.count();

    if (toggleCount > 0) {
      // Click first toggle
      const firstToggle = toggleButtons.first();
      await firstToggle.click();
      // TODO: Should see loading state or toast
      await page.waitForTimeout(500);
    }

    // Test backtest button
    const backtestButtons = page.locator('button:has-text("Backtest")');
    const backtestCount = await backtestButtons.count();

    if (backtestCount > 0) {
      const firstBacktest = backtestButtons.first();
      await firstBacktest.click();
      // TODO: Should open backtest modal
      await page.waitForTimeout(500);
    }

    // Test delete button
    const deleteButtons = page.locator('button').filter({ has: page.locator('svg') }).filter({ hasText: '' });
    const deleteCount = await deleteButtons.count();

    if (deleteCount > 0) {
      page.once('dialog', dialog => dialog.dismiss());
      await deleteButtons.first().click();
      // Confirmation should appear (handled above)
    }
  });

  test('Portfolio Page: Time range filters work', async ({ page }) => {
    await navigateAndWait(page, '/portfolio');

    const timeRanges = ['7D', '30D', '90D'];

    for (const range of timeRanges) {
      const button = page.locator(`button:has-text("${range}")`);
      if (await button.isVisible()) {
        const beforeClick = await button.getAttribute('class');

        await button.click();

        // Should show active state
        const afterClick = await button.getAttribute('class');
        expect(afterClick).not.toBe(beforeClick);

        // TODO: Should trigger data refresh (currently doesn't)
      }
    }
  });

  test('Analytics Page: Time range filters work', async ({ page }) => {
    await navigateAndWait(page, '/analytics');

    const timeRanges = ['7D', '30D', '90D', '1Y'];

    for (const range of timeRanges) {
      const button = page.locator(`button:has-text("${range}")`);
      if (await button.isVisible()) {
        await button.click();

        // Should show active state
        await expect(button).toHaveClass(/bg-primary|bg-accent/);

        // TODO: Should trigger data refresh (currently doesn't)
      }
    }
  });

  test('All Pages: Should have no console errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    for (const pageInfo of pages) {
      await navigateAndWait(page, pageInfo.path);
      await page.waitForTimeout(1000); // Let page settle
    }

    // Report any console errors
    if (errors.length > 0) {
      console.log('Console errors found:', errors);
    }

    // Strict check: no errors allowed
    expect(errors.length).toBe(0);
  });

  test('[DETECTION] Find all buttons without click handlers', async ({ page }) => {
    await navigateAndWait(page, '/');

    // Get all buttons
    const allButtons = await page.locator('button').all();

    console.log(`Found ${allButtons.length} buttons on Dashboard`);

    // Check each button has an onClick handler
    for (let i = 0; i < allButtons.length; i++) {
      const button = allButtons[i];
      const text = await button.textContent();
      const hasOnClick = await button.evaluate(el => {
        // Check if element or any parent has click event listener
        return (el as HTMLElement).onclick !== null;
      });

      if (!hasOnClick) {
        console.log(`⚠️  Button without click handler: "${text}"`);
      }
    }

    // TODO: This is just detection, not an assertion
    // Manual review needed for each flagged button
  });

  test('[DETECTION] Find all links without href', async ({ page }) => {
    await navigateAndWait(page, '/');

    // Get all links
    const allLinks = await page.locator('a').all();

    for (const link of allLinks) {
      const href = await link.getAttribute('href');
      const text = await link.textContent();

      if (!href || href === '#' || href === 'javascript:void(0)') {
        console.log(`⚠️  Link without valid href: "${text}" (href="${href}")`);
      }
    }
  });

  test('[DETECTION] Find all forms without onSubmit', async ({ page }) => {
    const allPages = ['/', '/trading', '/settings', '/strategies'];

    for (const path of allPages) {
      await navigateAndWait(page, path);

      const forms = await page.locator('form').all();

      if (forms.length > 0) {
        console.log(`Page ${path}: Found ${forms.length} forms`);

        for (const form of forms) {
          const hasSubmit = await form.evaluate(el => {
            return (el as HTMLFormElement).onsubmit !== null;
          });

          if (!hasSubmit) {
            console.log(`⚠️  Form without submit handler on ${path}`);
          }
        }
      }
    }
  });
});
