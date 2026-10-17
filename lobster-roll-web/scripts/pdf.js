const { chromium } = require('playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM || undefined, args:['--no-sandbox'] });
  const out = process.argv[2] || '.';
  for (const lang of ['es','ca','en','fr','it','pt','ru','todos']) {
    const page = await browser.newPage({ viewport: { width: 900, height: 1300 } });
    const errs=[]; page.on('pageerror', e => errs.push(e.message));
    await page.goto(`http://127.0.0.1:8899/carta-impresa.html?lang=${lang}`, { waitUntil: 'networkidle' });
    await page.waitForSelector('body[data-listo]'); await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(400);
    await page.pdf({ path: `${out}/carta-A4-${lang}.pdf`, format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, preferCSSPageSize: true });
    if (lang === 'es') await page.screenshot({ path: `${out}/carta-A4-es-preview.png`, fullPage: true });
    console.log(lang, 'ok', errs);
    await page.close();
  }
  await browser.close();
})();
