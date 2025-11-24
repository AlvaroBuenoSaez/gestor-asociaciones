// tests/example.spec.js
const { test, expect } = require('@playwright/test');

test('homepage has title and links to docs', async ({ page }) => {
  await page.goto('https://playwright.dev');
  await expect(page).toHaveTitle(/Playwright/);
  const getStarted = page.getByRole('link', { name: 'Get started' });
  await expect(getStarted).toBeVisible();
});
