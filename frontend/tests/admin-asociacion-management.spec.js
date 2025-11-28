import { test } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:8000/admin/login/?next=/admin/auth/user/');
  await page.locator('input[name="username"]').fill('admin');
  await page.locator('input[name="password"]').fill('admin123456');
  // Admin login usually uses input[type="submit"]
  await page.locator('button[type="submit"]').click();
  await page.getByRole('link', { name: 'Añadir' }).nth(1).click();
  await page.getByRole('textbox', { name: 'Nombre de la Asociación:' }).fill('Asocaición a Eliminar');
  await page.getByRole('textbox', { name: 'Nombre de la Asociación:' }).press('Tab');
  await page.getByRole('textbox', { name: 'Número de Registro:' }).fill('00000000 ');
  await page.getByRole('textbox', { name: 'Descripción:' }).click();
  await page.getByRole('textbox', { name: 'Descripción:' }).fill('Una descripción');
  await page.getByLabel('Contacto', { exact: true }).locator('div').filter({ hasText: 'Email de contacto:' }).first().click();
  await page.getByRole('textbox', { name: 'Email de contacto:' }).fill('asoaborrar@example.com');
  await page.getByRole('textbox', { name: 'Teléfono:' }).click();
  await page.getByRole('textbox', { name: 'Teléfono:' }).fill('666666666');
  await page.getByRole('textbox', { name: 'Dirección:' }).click();
  await page.getByRole('textbox', { name: 'Distrito:' }).click();
  await page.getByRole('textbox', { name: 'Distrito:' }).fill('Madrid');
  await page.getByRole('textbox', { name: 'Distrito:' }).press('Tab');
  await page.getByRole('textbox', { name: 'Provincia:' }).fill('Madrid');
  await page.getByRole('textbox', { name: 'Provincia:' }).press('Tab');
  await page.getByRole('textbox', { name: 'Código Postal:' }).fill('280111');
  await page.getByRole('button', { name: 'Guardar', exact: true }).click();
  await page.getByRole('checkbox', { name: 'Seleccione este objeto para una acción - Asocaición a Eliminar (00000000)' }).check();
  await page.getByLabel('Acción: --------- Eliminar').selectOption('delete_selected');
  await page.getByRole('button', { name: 'Ir' }).click();
  await page.getByRole('button', { name: 'Si, estoy seguro' }).click();
});