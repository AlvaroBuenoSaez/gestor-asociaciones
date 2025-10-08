// playwright-setup.js
const { spawn } = require('child_process');
const http = require('http');

const SERVER_URL = process.env.PLAYWRIGHT_SERVER_URL || 'http://localhost:8000/admin/';
const SERVER_CHECK_URL = SERVER_URL;
const SERVER_START_CMD = process.env.PLAYWRIGHT_SERVER_CMD || 'python manage.py runserver';

function checkServer(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      resolve(res.statusCode === 200 || res.statusCode === 302);
    }).on('error', () => resolve(false));
  });
}

async function ensureServer() {
  const isUp = await checkServer(SERVER_CHECK_URL);
  if (isUp) {
    console.log('Django server is already running.');
    return null;
  }
  console.log('Starting Django server...');
  const server = spawn(SERVER_START_CMD, { shell: true, stdio: 'inherit' });
  // Esperar a que levante
  for (let i = 0; i < 20; i++) {
    if (await checkServer(SERVER_CHECK_URL)) {
      console.log('Django server started.');
      return server;
    }
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error('Django server did not start in time.');
}

module.exports = { ensureServer };
