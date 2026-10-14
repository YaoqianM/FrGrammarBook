// Render build/volN.html to build/volN.pdf with headless Chromium (adapted from ../../tools/render.mjs).
import { chromium } from 'playwright-core';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const v = process.argv[2];
const label = process.argv[3] || '';
const exe = process.env.CHROMIUM_PATH ||
  ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(p => fs.existsSync(p));

const browser = await chromium.launch(exe ? { executablePath: exe } : {});
const page = await browser.newPage();
await page.goto('file://' + path.join(root, 'build', `vol${v}.html`), { waitUntil: 'networkidle', timeout: 0 });
await page.evaluate(() => document.fonts.ready);
await page.pdf({
  path: path.join(root, 'build', `vol${v}.pdf`),
  preferCSSPageSize: true,
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate: `<div style="width:100%;font-size:7px;font-family:'DejaVu Sans',sans-serif;color:#8a93a3;display:flex;justify-content:space-between;padding:0 18mm;">
    <span>${label}</span><span class="pageNumber"></span></div>`,
  outline: true,
  tagged: true,
  timeout: 0,
});
await browser.close();
console.log('wrote', `build/vol${v}.pdf`);
