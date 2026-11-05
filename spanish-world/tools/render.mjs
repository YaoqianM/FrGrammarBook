// Render build/book.html to PDF with headless Chromium (CSS paged media: named pages + margin boxes).
import { chromium } from 'playwright-core';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = process.argv[2] || path.join(root, 'build', 'book.pdf');
const exe = process.env.CHROMIUM_PATH ||
  ['/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome']
    .find(p => fs.existsSync(p));

const browser = await chromium.launch(exe ? { executablePath: exe } : {});
const page = await browser.newPage();
await page.goto('file://' + path.join(root, 'build', 'book.html'), { waitUntil: 'networkidle', timeout: 300000 });
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true, outline: true, tagged: true, timeout: 0 });
await browser.close();
console.log('wrote', out);
