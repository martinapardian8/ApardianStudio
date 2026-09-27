/* Capturas del sitio por tramos de viewport (cosidas), para revisar el diseño.
   Uso:  node scripts/capturas.js http://127.0.0.1:8899/ capturas
   Requiere: npm i playwright-core (y un Chromium; se usa el de PLAYWRIGHT_CHROMIUM o el de Playwright). */
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright-core');

const [,, base = 'http://127.0.0.1:8899/', outDir = 'capturas'] = process.argv;
const ANCHOS = [{ w: 375, h: 812, n: 'movil-375' }, { w: 768, h: 1024, n: 'tablet-768' }, { w: 1440, h: 900, n: 'escritorio-1440' }];

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const exe = process.env.PLAYWRIGHT_CHROMIUM || undefined;
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  for (const { w, h, n } of ANCHOS) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    page.on('pageerror', (e) => console.log('PAGEERROR', e.message));
    await page.goto(base, { waitUntil: 'networkidle' });
    await page.addStyleTag({ content: '.reveal{opacity:1!important;transform:none!important} .cinta__track{animation-play-state:paused!important}' });
    await page.waitForTimeout(1800);
    // primer pantallazo: hero con barra y aviso de cookies
    await page.screenshot({ path: path.join(outDir, `${n}-hero.png`) });
    // aceptar cookies y ocultar fijos para el resto
    await page.evaluate(() => { document.querySelector('[data-cookies="rechazar"]')?.click(); });
    await page.addStyleTag({ content: '.cookies{display:none!important}' });
    const total = await page.evaluate(() => document.documentElement.scrollHeight);
    const tramos = [];
    for (let y = 0; y < total; y += h) {
      await page.evaluate((yy) => window.scrollTo(0, yy), y);
      await page.waitForTimeout(350);
      const real = await page.evaluate(() => window.scrollY);
      if (real > 0) await page.addStyleTag({ content: '.barra,.puntos{visibility:hidden!important}' });
      const file = path.join(outDir, `_${n}-${String(tramos.length).padStart(2, '0')}.png`);
      await page.screenshot({ path: file });
      tramos.push({ file, y: real });
      if (real + h >= total) break;
    }
    fs.writeFileSync(path.join(outDir, `_${n}.json`), JSON.stringify({ w, h, total, tramos }));
    await page.close();
    console.log(n, 'alto total', total, 'tramos', tramos.length);
  }
  await browser.close();
})();
