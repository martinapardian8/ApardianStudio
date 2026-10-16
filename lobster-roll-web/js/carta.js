/* Carta digital (carta.html): carga data/carta.json, data/restaurante.json y data/i18n/*.json.
   Independiente de main.js para poder vender la carta sola. */
(() => {
  'use strict';
  const IDIOMAS = ['es', 'ca', 'en'];
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const estado = { lang: 'es', t: null, carta: null, rest: null };
  const get = (o, r) => r.split('.').reduce((a, k) => (a == null ? undefined : a[k]), o);
  const fmt = (s, v) => s.replace(/\{(\w+)\}/g, (_, k) => v[k] ?? '');
  const txt = (o) => (typeof o === 'string' ? o : (o?.[estado.lang] ?? o?.es ?? ''));
  const precio = (n) => new Intl.NumberFormat(get(estado.t, 'precio.locale') || 'es-ES', { style: 'currency', currency: estado.carta?.moneda || 'EUR', minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }).format(n);
  const cargar = async (r) => { const x = await fetch(r, { cache: 'no-cache' }); if (!x.ok) throw new Error(r); return x.json(); };

  function detectarIdioma() {
    const q = new URLSearchParams(location.search).get('lang'); if (IDIOMAS.includes(q)) return q;
    try { const g = localStorage.getItem('lr-lang'); if (IDIOMAS.includes(g)) return g; } catch (e) { /* sin storage */ }
    return 'es';
  }
  function aplicarI18n() {
    document.documentElement.lang = estado.lang;
    $$('[data-i18n]').forEach((el) => { const v = get(estado.t, el.dataset.i18n); if (typeof v === 'string') el.textContent = v; });
    $$('[data-i18n-attr]').forEach((el) => el.dataset.i18nAttr.split(';').forEach((p) => { const [a, k] = p.split(':').map((s) => s.trim()); const v = get(estado.t, k); if (typeof v === 'string') el.setAttribute(a, v); }));
    $$('.idiomas button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === estado.lang)));
  }
  function aplicarDatos() {
    const r = estado.rest;
    $$('[data-dato]').forEach((el) => { const v = get(r, el.dataset.dato); if (v != null) el.textContent = v; });
    $$('[data-reservas]').forEach((a) => { a.href = r.reservas; });
    $$('[data-tel]').forEach((a) => { a.href = `tel:${r.telefono_tel}`; });
  }
  function pintarCarta() {
    const destacado = get(estado.t, 'carta.especialidad') || '';
    estado.carta.categorias.forEach((cat) => {
      const ul = $(`.items[data-categoria="${cat.id}"]`); if (!ul) return;
      const rolls = estado.carta.categorias.find((x) => x.id === 'rolls')?.items || [];
      ul.innerHTML = cat.items.map((it) => {
        const desc = txt(it.descripcion) || (it.roll ? (rolls.find((r) => r.id === it.roll)?.nombre || '') : '');
        return `<li class="item${it.destacado ? ' item--destacado' : ''}">${it.destacado ? `<span class="item__tag">${destacado}</span>` : ''}<span class="item__nombre">${it.nombre}</span><span class="item__precio num">${precio(it.precio)}</span>${desc ? `<span class="item__desc">${desc}</span>` : ''}</li>`;
      }).join('');
    });
  }
  function ahoraEn(zona) {
    const p = new Intl.DateTimeFormat('en-GB', { timeZone: zona, weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    const o = Object.fromEntries(p.filter((x) => x.type !== 'literal').map((x) => [x.type, x.value]));
    return { dia: { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[o.weekday], min: (+o.hour % 24) * 60 + (+o.minute) };
  }
  const aMin = (h) => { const [a, b] = h.split(':').map(Number); return a * 60 + b; };
  function pintarEstado() {
    const el = $('#estado'); const h = estado.rest.horario; const t = estado.t.estado; const { dia, min } = ahoraEn(h.zona);
    const hoy = h.dias[String(dia)] || []; let abierto = false; let detalle = '';
    for (const [a, b] of hoy) if (min >= aMin(a) && min < aMin(b)) { abierto = true; detalle = fmt(t.cierra, { hora: b }); break; }
    if (!abierto) {
      const prox = hoy.find(([a]) => min < aMin(a));
      if (prox) detalle = fmt(t.abre_hoy, { hora: prox[0] });
      else for (let i = 1; i <= 7; i++) { const d = (dia + i) % 7; const tr = h.dias[String(d)] || []; if (tr.length) { detalle = fmt(t.abre_dia, { dia: get(estado.t, 'localizacion.dias')[d], hora: tr[0][0] }); break; } }
    }
    el.classList.toggle('is-abierto', abierto); el.classList.toggle('is-cerrado', !abierto);
    $('.estado__txt', el).textContent = abierto ? t.abierto : t.cerrado; $('.estado__detalle', el).textContent = detalle ? ` · ${detalle}` : '';
    // resumen de horario en el pie: agrupa días iguales
    const dc = get(estado.t, 'localizacion.dias_corto'); const cerrado = get(estado.t, 'localizacion.cerrado');
    const orden = [1, 2, 3, 4, 5, 6, 0]; const partes = []; let ini = 0;
    const clave = (d) => JSON.stringify(h.dias[String(d)] || []);
    for (let i = 1; i <= orden.length; i++) {
      if (i === orden.length || clave(orden[i]) !== clave(orden[ini])) {
        const tr = h.dias[String(orden[ini])] || []; const dias = ini === i - 1 ? dc[orden[ini]] : `${dc[orden[ini]]}–${dc[orden[i - 1]]}`;
        partes.push(`${dias} ${tr.length ? tr.map(([a, b]) => `${a}–${b}`).join(', ') : cerrado.toLowerCase()}`); ini = i;
      }
    }
    $('#cd-horario').textContent = partes.join(' · ');
  }
  function initTabs() {
    const tabs = $$('[role="tab"]');
    const activar = (tab, foco = true) => { tabs.forEach((t) => { const on = t === tab; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; const p = document.getElementById(t.getAttribute('aria-controls')); if (p) p.hidden = !on; }); if (foco) tab.focus(); };
    tabs.forEach((tab, i) => { tab.addEventListener('click', () => activar(tab, false)); tab.addEventListener('keydown', (e) => { const m = { ArrowRight: 1, ArrowLeft: -1, Home: -i, End: tabs.length - 1 - i }; if (e.key in m) { e.preventDefault(); activar(tabs[(i + m[e.key] + tabs.length) % tabs.length]); } }); });
    if (location.hash === '#combos') activar(tabs[1], false);
  }
  async function cambiarIdioma(lang) {
    if (!IDIOMAS.includes(lang)) return; estado.lang = lang; estado.t = await cargar(`data/i18n/${lang}.json`);
    try { localStorage.setItem('lr-lang', lang); } catch (e) { /* sin storage */ }
    const u = new URL(location.href); u.searchParams.set('lang', lang); history.replaceState(null, '', u);
    aplicarI18n(); pintarCarta(); pintarEstado();
  }
  async function init() {
    estado.lang = detectarIdioma();
    const [t, carta, rest] = await Promise.all([cargar(`data/i18n/${estado.lang}.json`), cargar('data/carta.json'), cargar('data/restaurante.json')]);
    Object.assign(estado, { t, carta, rest });
    aplicarDatos(); aplicarI18n(); pintarCarta(); pintarEstado(); setInterval(pintarEstado, 60000); initTabs();
    $$('.idiomas button').forEach((b) => b.addEventListener('click', () => cambiarIdioma(b.dataset.lang)));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
