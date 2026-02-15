import {test, expect} from '@playwright/test';

/**
 * E2E Test: Outline Management Flow
 * Tests outline creation, viewing, and editing
 */

test.describe('Outline Management', () => {
  // Helper function to login before tests
  async function login(page: any) {
    await page.goto('/login');
    await page.getByLabel(/邮箱|Email/).fill('test@example.com');
    await page.getByLabel(/密码|Password/).fill('password123');
    await page.getByRole('button', {name: /登录|Sign In/}).click();
    await expect(page).toHaveURL(/\/dashboard/);
  }

  test.beforeEach(async ({page}) => {
    // Login before each test
    await login(page);
  });

  test('should navigate to outlines page', async ({page}) => {
    // Click on outlines link in navigation
    await page.getByRole('link', {name: /大纲|Outlines/}).click();

    // Should navigate to outlines page
    await expect(page).toHaveURL(/\/outlines/);

    // Check page content
    await expect(page.getByRole('heading', {name: /大纲|Outlines/})).toBeVisible();
    await expect(page.getByRole('button', {name: /新建|New/})).toBeVisible();
  });

  test('should create new outline manually', async ({page}) => {
    // Navigate to outlines page
    await page.goto('/outlines');

    // Click new outline button
    await page.getByRole('button', {name: /新建|New/}).click();

    // Should navigate to new outline page
    await expect(page).toHaveURL(/\/outlines\/new/);

    // Fill in outline details
    await page.getByLabel(/标题|Title/).fill('Test Outline');
    await page.getByLabel(/描述|Description/).fill('This is a test outline description');

    // Add a section
    await page.getByRole('button', {name: /添加章节|Add Section/}).click();
    await page.getByPlaceholder(/章节标题|Section Title/).fill('Introduction');

    // Save outline
    await page.getByRole('button', {name: /保存|Save/}).click();

    // Should redirect to outline detail or list page
    await expect(page).toHaveURL(/\/outlines/);

    // Verify outline was created
    await expect(page.getByText('Test Outline')).toBeVisible();
  });

  test('should generate outline with AI', async ({page}) => {
    // Navigate to outlines page
    await page.goto('/outlines');

    // Click new outline button
    await page.getByRole('button', {name: /新建|New/}).click();

    // Should navigate to new outline page
    await expect(page).toHaveURL(/\/outlines\/new/);

    // Switch to AI generation tab
    await page.getByRole('tab', {name: /AI生成|AI Generate/}).click();

    // Fill in prompt
    await page.getByPlaceholder(/输入提示词|Enter prompt/).fill('Create a presentation about artificial intelligence');

    // Set number of slides
    await page.getByLabel(/页数|Slides/).fill('5');

    // Select style
    await page.getByLabel(/风格|Style/).selectOption('business');

    // Click generate
    await page.getByRole('button', {name: /生成|Generate/}).click();

    // Should show loading or redirect to processing page
    await expect(page.getByText(/生成中|Generating|处理中|Processing/)).toBeVisible();

    // Wait for generation to complete or timeout
    await expect(page.getByText(/完成|Completed|成功|Success/).first()).toBeVisible({timeout: 65000});
  });

  test('should view outline details', async ({page}) => {
    // Navigate to outlines page
    await page.goto('/outlines');

    // Wait for outlines to load
    await page.waitForSelector('[data-testid="outline-item"]', {timeout: 5000}).catch(() => {
      // If no outlines, skip this test
      test.skip();
    });

    // Click on first outline
    await page.locator('[data-testid="outline-item"]').first().click();

    // Should navigate to outline detail page
    await expect(page).toHaveURL(/\/outlines\/[a-zA-Z0-9-]+/);

    // Check outline detail elements
    await expect(page.getByRole('heading')).toBeVisible();
    await expect(page.getByText(/章节|Sections|页面|Pages/)).toBeVisible();
  });

  test('should edit existing outline', async ({page}) => {
    // Navigate to outlines page
    await page.goto('/outlines');

    // Wait for outlines to load
    const outlineItem = page.locator('[data-testid="outline-item"]').first();
    await outlineItem.waitFor({timeout: 5000}).catch(() => {
      test.skip();
    });

    // Click edit button on first outline
    await outlineItem.locator('[data-testid="edit-button"]').click();

    // Should navigate to edit page
    await expect(page).toHaveURL(/\/outlines\/[a-zA-Z0-9-]+/);

    // Edit title
    const titleInput = page.getByLabel(/标题|Title/);
    await titleInput.clear();
    await titleInput.fill('Updated Outline Title');

    // Save changes
    await page.getByRole('button', {name: /保存|Save/}).click();

    // Should show success message
    await expect(page.getByText(/保存成功|Saved|更新成功|Updated/)).toBeVisible();
  });
});
