// tests/admin-user-management.spec.js
import { test } from '@playwright/test';
require('dotenv').config();

const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'admin123456';

// Utilidad para generar un usuario único
function randomUsername() {
  return 'UsuarioPrueba_' + Math.floor(Math.random() * 1000000);
}

test('admin puede crear y eliminar un usuario', async ({ page }) => {
    // Login
  await page.goto('http://localhost:8000/admin/login/');
  await page.locator('input[name="username"]').fill('admin');
  await page.locator('input[name="password"]').fill('admin123456');
  // Admin login usually uses input[type="submit"]
  await page.locator('button[type="submit"]').click();

  // Crear usuario
  await page.getByRole('link', { name: 'Añadir usuario' }).click();
  const username = randomUsername();
  await page.getByRole('textbox', { name: 'Nombre de usuario:' }).fill(username);
  await page.getByRole('textbox', { name: 'Nombre:' }).fill('Usuario');
  await page.getByRole('textbox', { name: 'Apellidos:' }).fill('Prueba');
  await page.getByRole('textbox', { name: 'Dirección de correo electró' }).fill('prueba@example.com');
  await page.getByRole('textbox', { name: 'Contraseña:' }).fill('con123456!');
  await page.getByRole('textbox', { name: 'Contraseña (confirmación):' }).fill('con123456!');
  await page.getByRole('button', { name: 'Guardar', exact: true }).click();

  // Eliminar usuario
  await page.getByLabel('Barra lateral').getByRole('link', { name: 'Usuarios' }).click();
  await page.getByRole('checkbox', { name: new RegExp(`Seleccione este objeto para una acción - ${username}`) }).check();
  await page.getByLabel('Acción: --------- Eliminar').selectOption('delete_selected');
  await page.getByRole('button', { name: 'Ir' }).click();
  await page.getByRole('button', { name: 'Si, estoy seguro' }).click();
});
