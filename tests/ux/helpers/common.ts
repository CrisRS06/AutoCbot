import { Page, expect } from '@playwright/test';

/**
 * Common helper functions for UX tests
 */

/**
 * Navigate to a page and wait for it to be fully loaded
 */
export async function navigateAndWait(page: Page, path: string) {
  await page.goto(path);
  await page.waitForLoadState('networkidle');
  // Wait for dashboard layout to be visible
  await expect(page.locator('aside')).toBeVisible(); // Sidebar
}

/**
 * Check if an element is in loading state
 */
export async function expectLoadingState(page: Page, selector: string) {
  const element = page.locator(selector);
  await expect(element).toBeVisible();
  // Check for common loading indicators
  const hasLoadingText = await element.textContent().then(text =>
    text?.toLowerCase().includes('loading') ||
    text?.toLowerCase().includes('saving') ||
    text?.toLowerCase().includes('...')
  );
  const hasSpinner = await element.locator('.animate-spin').count() > 0;
  const hasDisabled = await element.isDisabled();

  expect(hasLoadingText || hasSpinner || hasDisabled).toBeTruthy();
}

/**
 * Wait for toast notification and check message
 */
export async function expectToast(page: Page, message: string, type: 'success' | 'error' = 'success') {
  const toast = page.locator('[role="status"], [role="alert"]').filter({ hasText: message });
  await expect(toast).toBeVisible({ timeout: 5000 });

  // Verify toast type by checking icon or class
  if (type === 'success') {
    // Look for green colors or success icon
    const hasSuccessIndicator = await toast.locator('[class*="green"], [class*="success"]').count() > 0;
    expect(hasSuccessIndicator).toBeTruthy();
  } else {
    // Look for red colors or error icon
    const hasErrorIndicator = await toast.locator('[class*="red"], [class*="error"], [class*="danger"]').count() > 0;
    expect(hasErrorIndicator).toBeTruthy();
  }
}

/**
 * Check if modal is open
 */
export async function expectModalOpen(page: Page, titleText?: string) {
  const modal = page.locator('[class*="fixed"][class*="inset-0"]').filter({ has: page.locator('[class*="max-w"]') });
  await expect(modal).toBeVisible();

  if (titleText) {
    await expect(modal.locator('h2, h3').filter({ hasText: titleText })).toBeVisible();
  }
}

/**
 * Check if modal is closed
 */
export async function expectModalClosed(page: Page) {
  const modal = page.locator('[class*="fixed"][class*="inset-0"]').filter({ has: page.locator('[class*="max-w"]') });
  await expect(modal).not.toBeVisible();
}

/**
 * Close modal by clicking X button
 */
export async function closeModal(page: Page) {
  // Find X button in modal
  const closeButton = page.locator('[class*="fixed"][class*="inset-0"] button').filter({ has: page.locator('svg') }).first();
  await closeButton.click();
  await expectModalClosed(page);
}

/**
 * Fill order form in trading page
 */
export async function fillOrderForm(page: Page, orderData: {
  symbol?: string;
  side?: 'buy' | 'sell';
  type?: 'market' | 'limit';
  amount: string;
  price?: string;
  stopLoss?: string;
  takeProfit?: string;
}) {
  // Select symbol
  if (orderData.symbol) {
    await page.selectOption('select', orderData.symbol);
  }

  // Select side
  if (orderData.side) {
    await page.locator(`button:has-text("${orderData.side === 'buy' ? 'Buy' : 'Sell'}")`).click();
  }

  // Select type
  if (orderData.type) {
    await page.locator(`button:has-text("${orderData.type === 'market' ? 'Market' : 'Limit'}")`).click();
  }

  // Fill amount
  await page.locator('input[type="number"]').first().fill(orderData.amount);

  // Fill price (if limit order)
  if (orderData.price) {
    await page.locator('input[type="number"]').nth(1).fill(orderData.price);
  }

  // Fill stop loss
  if (orderData.stopLoss) {
    await page.locator('label:has-text("Stop Loss")').locator('..').locator('input').fill(orderData.stopLoss);
  }

  // Fill take profit
  if (orderData.takeProfit) {
    await page.locator('label:has-text("Take Profit")').locator('..').locator('input').fill(orderData.takeProfit);
  }
}

/**
 * Check if element has empty state
 */
export async function expectEmptyState(page: Page, containerSelector: string, expectedText: string) {
  const container = page.locator(containerSelector);
  await expect(container).toBeVisible();
  await expect(container).toContainText(expectedText);

  // Should have icon and message
  const icon = container.locator('svg').first();
  await expect(icon).toBeVisible();
}

/**
 * Mock API response
 */
export async function mockApiResponse(page: Page, url: string, response: any, status: number = 200) {
  await page.route(url, route => {
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(response),
    });
  });
}

/**
 * Mock API error
 */
export async function mockApiError(page: Page, url: string, status: number = 500) {
  await page.route(url, route => {
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' }),
    });
  });
}

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page: Page, timeout: number = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Take screenshot with custom name
 */
export async function takeScreenshot(page: Page, name: string) {
  await page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
}

/**
 * Check if sidebar is visible and interactive
 */
export async function expectSidebarVisible(page: Page) {
  const sidebar = page.locator('aside');
  await expect(sidebar).toBeVisible();

  // Check all nav links are visible
  const navLinks = [
    'Dashboard',
    'Trading',
    'Portfolio',
    'Analytics',
    'Strategies',
    'Settings',
  ];

  for (const link of navLinks) {
    await expect(sidebar.locator(`text=${link}`)).toBeVisible();
  }
}

/**
 * Navigate using sidebar
 */
export async function navigateViaSidebar(page: Page, linkText: string) {
  await page.locator('aside').locator(`text=${linkText}`).click();
  await page.waitForLoadState('networkidle');
}
