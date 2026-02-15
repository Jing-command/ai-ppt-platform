import {test, expect} from '@playwright/test';

/**
 * E2E Test: Basic Navigation and UI
 * Tests basic page navigation and UI elements without backend dependency
 */

test.describe('Basic Navigation', () => {
  test('should load home page', async ({page}) => {
    await page.goto('/');

    // Check page loaded
    await expect(page).toHaveTitle(/.*/);

    // Check main content exists
    const main = page.locator('main');
    await expect(main).toBeVisible();
  });

  test('should navigate to login page', async ({page}) => {
    await page.goto('/login');

    // Check login form exists
    await expect(page.locator('form')).toBeVisible();
    await expect(page.getByRole('button', {name: /登录|Sign In/i})).toBeVisible();
  });

  test('should have proper navigation structure', async ({page}) => {
    await page.goto('/');

    // Check for navigation or header
    const header = page.locator('header, nav').first();
    await expect(header).toBeVisible();
  });
});
