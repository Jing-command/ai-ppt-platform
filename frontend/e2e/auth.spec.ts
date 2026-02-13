import { test, expect } from '@playwright/test';

/**
 * E2E Test: User Authentication Flow
 * Tests user login and logout functionality
 */

test.describe('User Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page before each test
    await page.goto('/login');
  });

  test('should display login form correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/登录|Login/);
    
    // Check form elements exist
    await expect(page.getByLabel(/邮箱|Email/)).toBeVisible();
    await expect(page.getByLabel(/密码|Password/)).toBeVisible();
    await expect(page.getByRole('button', { name: /登录|Sign In/ })).toBeVisible();
    
    // Check register link
    await expect(page.getByRole('link', { name: /注册|Register/ })).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    // Click login without filling fields
    await page.getByRole('button', { name: /登录|Sign In/ }).click();
    
    // Check for validation messages
    await expect(page.getByText(/请输入邮箱|email is required/i)).toBeVisible();
    await expect(page.getByText(/请输入密码|password is required/i)).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in invalid credentials
    await page.getByLabel(/邮箱|Email/).fill('invalid@example.com');
    await page.getByLabel(/密码|Password/).fill('wrongpassword');
    
    // Click login
    await page.getByRole('button', { name: /登录|Sign In/ }).click();
    
    // Check for error message
    await expect(page.getByText(/邮箱或密码错误|invalid credentials/i)).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill in valid credentials (test account)
    await page.getByLabel(/邮箱|Email/).fill('test@example.com');
    await page.getByLabel(/密码|Password/).fill('password123');
    
    // Click login
    await page.getByRole('button', { name: /登录|Sign In/ }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    
    // Check dashboard elements
    await expect(page.getByText(/欢迎|Welcome/)).toBeVisible();
    await expect(page.getByRole('heading', { name: /仪表板|Dashboard/ })).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    // Click register link
    await page.getByRole('link', { name: /注册|Register/ }).click();
    
    // Should navigate to register page
    await expect(page).toHaveURL(/\/register/);
    
    // Check register form elements
    await expect(page.getByLabel(/用户名|Name/)).toBeVisible();
    await expect(page.getByRole('button', { name: /注册|Sign Up/ })).toBeVisible();
  });
});
