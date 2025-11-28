
export async function loginAsAdmin(page) {
  await page.goto('http://localhost:8000/admin/login/');
  await page.locator('input[name="username"]').fill('admin');
  await page.locator('input[name="password"]').fill('admin123456');
  await page.locator('input[type="submit"]').click();
  // Wait for redirect to admin dashboard or home
  await page.waitForURL('**/admin/**');
}

export async function loginAsAssociationUser(page) {
    // Assuming we have a test user for associations.
    // If not, we might need to create one or use the admin if they have association access.
    // For now, let's use the admin credentials but navigate to the main dashboard
    await page.goto('http://localhost:8000/admin/login/');
    await page.locator('input[name="username"]').fill('admin');
    await page.locator('input[name="password"]').fill('admin123456');
    // The login button in login.html is a <button type="submit">
    await page.locator('input[type="submit"]').click();
    // Wait for either admin dashboard or user dashboard
    await page.waitForURL(/\/admin\/|\/dashboard\//);
}
