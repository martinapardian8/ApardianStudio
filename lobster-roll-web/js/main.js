/* =====================================================================
   The Lobster Roll · Barcelona — main.js (vanilla, sin dependencias)
   Carga data/*.json, aplica idioma, pinta carta/combos/galería/horario,
   y maneja menú, pestañas, lightbox, estado abierto/cerrado, cookies,
   parallax y animaciones de entrada.
   ===================================================================== */
(() => {
  'use strict';

  const IDIOMAS = ['es', 'ca', 'en'];
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const estado = { lang: 'es', t: null, carta: null, fotos: null, rest: null };

  /* ---------- Utilidades ---------- */
  const get = (obj, ruta) => ruta.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
  const fmt = (txt, vars) => txt.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? ''));
  const precio = (n) => new Intl.NumberFormat(get(estado.t, 'precio.locale') || 'es-ES', {
    style: 'currency', currency: estado.carta?.moneda || 'EUR', minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2,
  }).format(n);
  const txt = (obj) => (typeof obj === 'string' ? obj : (obj?.[estado.lang] ?? obj?.es ?? ''));

  function detectarIdioma() {
    const q = new URLSearchParams(location.search).get('lang');
    if (IDIOMAS.includes(q)) return q;
    try { const g = localStorage.getItem('lr-lang'); if (IDIOMAS.includes(g)) return g; } catch (e) { /* sin storage */ }
    return 'es'; // idioma por defecto: español. (Si se quisiera detectar el del navegador: navigator.language.)
  }

  async function cargarJSON(ruta) {
    const r = await fetch(ruta, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`No se pudo cargar ${ruta}`);
    return r.json();
  }

  /* ---------- i18n ---------- */
  function aplicarI18n() {
    const t = estado.t;
    document.documentElement.lang = estado.lang;
    $$('[data-i18n]').forEach((el) => {
      const v = get(t, el.dataset.i18n);
      if (typeof v === 'string') el.textContent = v;
    });
    $$('[data-i18n-attr]').forEach((el) => {
      el.dataset.i18nAttr.split(';').forEach((par) => {
        const [attr, clave] = par.split(':').map((s) => s.trim());
        const v = get(t, clave);
        if (typeof v === 'string') el.setAttribute(attr, v);
      });
    });
    $$('.idiomas button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === estado.lang)));
    // cinta
    const cinta = $('#cinta');
    if (cinta && Array.isArray(t.cinta)) {
      const ul = `<ul>${t.cinta.map((s) => `<li>${s}</li>`).join('')}</ul>`;
      cinta.innerHTML = ul + ul;
    }
  }

  async function cambiarIdioma(lang) {
    if (!IDIOMAS.includes(lang) || lang === estado.lang && estado.t) return;
    estado.lang = lang;
    estado.t = await cargarJSON(`data/i18n/${lang}.json`);
    try { localStorage.setItem('lr-lang', lang); } catch (e) { /* sin storage */ }
    const url = new URL(location.href); url.searchParams.set('lang', lang); history.replaceState(null, '', url);
    aplicarI18n();
    envolverLetras();
    pintarCarta();
    pintarCombos();
    pintarGaleria();
    pintarHorario();
    pintarEstado();
    pintarFotos();
  }

  /* ---------- Letras sueltas en los títulos (efecto ola al pasar el mouse) ---------- */
  function envolverLetras() {
    $$('[data-letras]').forEach((el) => {
      const clon = el.cloneNode(true); clon.querySelectorAll('.sticker').forEach((x) => x.remove());
      el.setAttribute('aria-label', clon.textContent.replace(/\s+/g, ' ').trim());
      let i = 0;
      const recorrer = (nodo) => {
        Array.from(nodo.childNodes).forEach((n) => {
          if (n.nodeType === 3) {
            if (!n.textContent.trim()) return;
            const frag = document.createDocumentFragment();
            // cada palabra en un span que no se parte; cada letra adentro, con su retardo
            n.textContent.split(/(\s+)/).forEach((trozo) => {
              if (!trozo) return;
              if (/^\s+$/.test(trozo)) { frag.appendChild(document.createTextNode(' ')); return; }
              const pal = document.createElement('span'); pal.className = 'palabra'; pal.setAttribute('aria-hidden', 'true');
              for (const ch of trozo) { const sp = document.createElement('span'); sp.className = 'letra'; sp.textContent = ch; sp.style.setProperty('--i', String(i++)); pal.appendChild(sp); }
              frag.appendChild(pal);
            });
            n.replaceWith(frag);
          } else if (n.nodeType === 1 && !n.classList.contains('letra') && !n.classList.contains('palabra') && !n.classList.contains('sticker')) recorrer(n);
        });
      };
      recorrer(el);
    });
  }

  /* ---------- Cursor langosta ---------- */
  function initCursor() {
    const cur = $('#cursor'); if (!cur) return;
    if (reduceMotion || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    document.documentElement.classList.add('cursor-langosta');
    let x = -100, y = -100, cx = -100, cy = -100, visto = false;
    const mover = () => { cx += (x - cx) * .22; cy += (y - cy) * .22; cur.style.transform = `translate(${cx - cur.offsetWidth * .45}px, ${cy - cur.offsetHeight * .22}px)`; requestAnimationFrame(mover); };
    document.addEventListener('mousemove', (e) => {
      x = e.clientX; y = e.clientY;
      if (!visto) { visto = true; cx = x; cy = y; cur.classList.add('is-on'); }
      cur.classList.toggle('is-hover', !!e.target.closest('a, button, [role="tab"], [data-letras], .item, .sticker, .compara__card, .combo, .masonry button, summary'));
    }, { passive: true });
    document.addEventListener('mousedown', () => cur.classList.add('is-click'));
    document.addEventListener('mouseup', () => cur.classList.remove('is-click'));
    document.documentElement.addEventListener('mouseleave', () => cur.classList.add('is-oculto'));
    document.documentElement.addEventListener('mouseenter', () => cur.classList.remove('is-oculto'));
    requestAnimationFrame(mover);
  }

  /* ---------- Datos del restaurante ---------- */
  function aplicarDatos() {
    const r = estado.rest;
    $$('[data-dato]').forEach((el) => { const v = get(r, el.dataset.dato); if (v != null) el.textContent = v; });
    $$('[data-reservas]').forEach((a) => { a.href = r.reservas; });
    $$('[data-tel]').forEach((a) => { a.href = `tel:${r.telefono_tel}`; });
    $$('[data-mapa]').forEach((a) => { a.href = r.mapa; });
    const redes = $('#redes');
    if (redes) {
      const items = Object.entries(r.redes || {}).filter(([, url]) => url);
      if (items.length) {
        redes.innerHTML = items.map(([k, url]) => `<li><a href="${url}" target="_blank" rel="noopener">${k[0].toUpperCase()}${k.slice(1)}</a></li>`).join('');
      }
    }
    const anio = $('#anio'); if (anio) anio.textContent = String(new Date().getFullYear());
  }

  /* ---------- Fotos desde data/fotos.json ---------- */
  function pintarFotos() {
    const f = estado.fotos;
    $$('[data-foto]').forEach((img) => {
      const cfg = f[img.dataset.foto];
      if (!cfg) return;
      if (!cfg.src) { const slot = img.closest('[data-slot]'); if (slot) slot.hidden = true; return; }
      const slot = img.closest('[data-slot]'); if (slot) slot.hidden = false;
      if (img.getAttribute('src') !== cfg.src) img.src = cfg.src;
      if (cfg.srcset) img.srcset = cfg.srcset;
      if (cfg.sizes) img.sizes = cfg.sizes;
      if (cfg.ancho) img.width = cfg.ancho;
      if (cfg.alto) img.height = cfg.alto;
      if (img.alt !== '' || !img.hasAttribute('alt')) img.alt = txt(cfg.alt);
    });
  }

  /* ---------- Video del hero (data/fotos.json → hero_video) ---------- */
  function initHeroVideo() {
    const cfg = estado.fotos?.hero_video; const v = $('#hero-video'); if (!cfg || !v || !cfg.mp4) return;
    if (cfg.poster) v.poster = cfg.poster;
    const cont = v.parentElement;
    cont.classList.add('is-ready'); // el poster se ve enseguida; el video aparece encima cuando puede reproducirse
    if (reduceMotion || !cfg.mp4) return; // sin movimiento: queda el fotograma fijo
    const src = document.createElement('source'); src.src = cfg.mp4; src.type = 'video/mp4'; v.appendChild(src);
    v.preload = 'auto'; v.autoplay = true;
    v.load(); const p = v.play(); if (p && p.catch) p.catch(() => {});
  }

  /* ---------- Carta ---------- */
  function itemHTML(it, destacadoTxt) {
    const desc = txt(it.descripcion);
    return `<li class="item${it.destacado ? ' item--destacado' : ''}">
      ${it.destacado ? `<span class="item__tag">${destacadoTxt}</span>` : ''}
      <span class="item__nombre">${it.nombre}</span>
      <span class="item__precio num">${precio(it.precio)}</span>
      ${desc ? `<span class="item__desc">${desc}</span>` : ''}
    </li>`;
  }
  function pintarCarta() {
    const c = estado.carta; if (!c) return;
    const destacadoTxt = get(estado.t, 'carta.especialidad') || '';
    c.categorias.forEach((cat) => {
      const ul = $(`.items[data-categoria="${cat.id}"]`);
      if (ul) ul.innerHTML = cat.items.map((it) => itemHTML(it, destacadoTxt)).join('');
      const nota = $(`[data-nota="${cat.id}"]`);
      if (nota) nota.textContent = txt(cat.nota);
    });
    // precios referenciados fuera de la carta (bloque 50/50)
    const todos = c.categorias.flatMap((cat) => cat.items);
    $$('[data-precio-de]').forEach((el) => {
      const it = todos.find((x) => x.id === el.dataset.precioDe);
      if (it) el.textContent = precio(it.precio);
    });
  }
  function pintarCombos() {
    const c = estado.carta; const ul = $('#combos-lista'); if (!c || !ul) return;
    const combos = c.categorias.find((x) => x.id === 'combos');
    const rolls = c.categorias.find((x) => x.id === 'rolls')?.items || [];
    if (!combos) return;
    ul.innerHTML = combos.items.map((it) => {
      const roll = rolls.find((r) => r.id === it.roll);
      return `<li class="combo"><span class="combo__nombre">${it.nombre}${roll ? `<span class="combo__roll">${roll.nombre}</span>` : ''}</span><span class="combo__precio num">${precio(it.precio)}</span></li>`;
    }).join('');
  }

  /* ---------- Pestañas accesibles ---------- */
  function initTabs() {
    const tabs = $$('[role="tab"]'); if (!tabs.length) return;
    const activar = (tab, foco = true) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        const panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (foco) tab.focus();
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => activar(tab, false));
      tab.addEventListener('keydown', (e) => {
        const map = { ArrowRight: 1, ArrowLeft: -1, Home: -i, End: tabs.length - 1 - i };
        if (e.key in map) { e.preventDefault(); activar(tabs[(i + map[e.key] + tabs.length) % tabs.length]); }
      });
    });
    // enlaces #combos desde la carta abren la pestaña si hace falta
    if (location.hash === '#panel-combos') activar(tabs[1], false);
  }

  /* ---------- Galería + lightbox ---------- */
  let lbIndex = 0;
  function pintarGaleria() {
    const cont = $('#galeria'); const f = estado.fotos; if (!cont || !f?.galeria) return;
    const abrir = get(estado.t, 'fotos.abrir') || 'Ampliar';
    cont.innerHTML = f.galeria.map((foto, i) => `
      <button type="button" data-idx="${i}" aria-label="${abrir}: ${txt(foto.alt)}">
        <img src="${foto.src}" ${foto.srcset ? `srcset="${foto.srcset}"` : ''} sizes="(min-width: 768px) 30vw, 46vw" alt="${txt(foto.alt)}" width="${foto.ancho || ''}" height="${foto.alto || ''}" loading="lazy" decoding="async">
      </button>`).join('');
  }
  function initLightbox() {
    const dlg = $('#lightbox'); const img = $('#lightbox-img'); const pie = $('#lightbox-pie'); const cont = $('#galeria');
    if (!dlg || !cont) return;
    const mostrar = (i) => {
      const g = estado.fotos.galeria; lbIndex = (i + g.length) % g.length;
      img.src = g[lbIndex].src; img.alt = txt(g[lbIndex].alt);
      pie.textContent = `${lbIndex + 1} / ${g.length} · ${txt(g[lbIndex].alt)}`;
    };
    cont.addEventListener('click', (e) => {
      const b = e.target.closest('button[data-idx]'); if (!b) return;
      mostrar(+b.dataset.idx);
      if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    });
    dlg.addEventListener('click', (e) => {
      const b = e.target.closest('[data-lb]');
      if (b) { const a = b.dataset.lb; if (a === 'cerrar') dlg.close(); if (a === 'prev') mostrar(lbIndex - 1); if (a === 'next') mostrar(lbIndex + 1); return; }
      if (e.target === dlg || e.target.classList.contains('lightbox__int')) dlg.close();
    });
    dlg.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') mostrar(lbIndex - 1); if (e.key === 'ArrowRight') mostrar(lbIndex + 1); });
  }

  /* ---------- Horario y estado abierto/cerrado ---------- */
  function ahoraEn(zona) {
    const p = new Intl.DateTimeFormat('en-GB', { timeZone: zona, weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
    const o = Object.fromEntries(p.filter((x) => x.type !== 'literal').map((x) => [x.type, x.value]));
    const dias = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    return { dia: dias[o.weekday], min: (+o.hour % 24) * 60 + (+o.minute) };
  }
  const aMin = (hhmm) => { const [h, m] = hhmm.split(':').map(Number); return h * 60 + m; };

  function pintarHorario() {
    const tb = $('#horario tbody'); const h = estado.rest?.horario; if (!tb || !h) return;
    const { dia: hoy } = ahoraEn(h.zona);
    const nombres = get(estado.t, 'localizacion.dias') || [];
    const cerrado = get(estado.t, 'localizacion.cerrado') || 'Cerrado';
    const hoyTxt = get(estado.t, 'localizacion.hoy') || 'hoy';
    const orden = [1, 2, 3, 4, 5, 6, 0]; // lunes a domingo
    tb.innerHTML = orden.map((d) => {
      const tramos = h.dias[String(d)] || [];
      const esHoy = d === hoy;
      const horas = tramos.length ? tramos.map(([a, b]) => `${a}–${b}`).join(', ') : cerrado;
      return `<tr class="${esHoy ? 'is-hoy' : ''}${tramos.length ? '' : ' is-cerrado'}"${esHoy ? ' aria-current="date"' : ''}><td>${nombres[d] || d}${esHoy ? `<span class="hoy-tag">${hoyTxt}</span>` : ''}</td><td class="num">${horas}</td></tr>`;
    }).join('');
  }

  function pintarEstado() {
    const el = $('#estado'); const h = estado.rest?.horario; if (!el || !h) return;
    const t = estado.t.estado; const { dia, min } = ahoraEn(h.zona);
    const tramosHoy = h.dias[String(dia)] || [];
    let abierto = false; let detalle = '';
    for (const [a, b] of tramosHoy) {
      if (min >= aMin(a) && min < aMin(b)) { abierto = true; detalle = fmt(t.cierra, { hora: b }); break; }
    }
    if (!abierto) {
      const prox = tramosHoy.find(([a]) => min < aMin(a));
      if (prox) detalle = fmt(t.abre_hoy, { hora: prox[0] });
      else {
        for (let i = 1; i <= 7; i++) {
          const d = (dia + i) % 7; const tr = h.dias[String(d)] || [];
          if (tr.length) { detalle = fmt(t.abre_dia, { dia: (get(estado.t, 'localizacion.dias') || [])[d], hora: tr[0][0] }); break; }
        }
      }
    }
    el.classList.toggle('is-abierto', abierto); el.classList.toggle('is-cerrado', !abierto);
    $('.estado__txt', el).textContent = abierto ? t.abierto : t.cerrado;
    $('.estado__detalle', el).textContent = detalle ? ` · ${detalle}` : '';
  }

  /* ---------- Navegación ---------- */
  function initNav() {
    const barra = $('#barra'); const hamb = $('.hamb'); const menu = $('#menu-movil');
    const onScroll = () => barra.classList.toggle('is-scrolled', window.scrollY > 40);
    onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
    const setMenu = (open) => {
      hamb.setAttribute('aria-expanded', String(open));
      hamb.setAttribute('aria-label', get(estado.t, open ? 'nav.menu_cerrar' : 'nav.menu_abrir') || '');
      menu.classList.toggle('is-open', open);
      document.body.classList.toggle('menu-abierto', open);
    };
    hamb.addEventListener('click', () => setMenu(hamb.getAttribute('aria-expanded') !== 'true'));
    menu.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false); });
    $$('.idiomas button').forEach((b) => b.addEventListener('click', () => cambiarIdioma(b.dataset.lang)));

    // sección activa: links de la barra y puntos laterales
    const secciones = $$('main > section[id], main > .partido[id]');
    const puntos = $('.puntos');
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((en) => {
          if (!en.isIntersecting) return;
          const id = en.target.id;
          $$('.barra__links a').forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${id}`));
          $$('.puntos a').forEach((a) => a.classList.toggle('is-active', a.dataset.sec === id));
          if (puntos) puntos.classList.toggle('on-paper', en.target.classList.contains('sec--papel') || en.target.classList.contains('sec--papel-2'));
        });
      }, { rootMargin: '-45% 0px -45% 0px' });
      secciones.forEach((s) => io.observe(s));
    }
  }

  /* ---------- Movimiento: entrada, parallax ---------- */
  function initMovimiento() {
    const reveals = $$('.reveal');
    if (reduceMotion || !('IntersectionObserver' in window)) { reveals.forEach((r) => r.classList.add('is-in')); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -10% 0px', threshold: .12 });
    reveals.forEach((r) => io.observe(r));
    const ioT = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-ola'); setTimeout(() => en.target.classList.remove('is-ola'), 2500); ioT.unobserve(en.target); } });
    }, { threshold: .5 });
    $$('[data-letras]').forEach((t) => ioT.observe(t));

    const capas = $$('[data-parallax]');
    if (!capas.length) return;
    let ticking = false;
    const mover = () => {
      const vh = window.innerHeight;
      capas.forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        const centro = r.top + r.height / 2 - vh / 2;
        el.style.setProperty('--py', `${(-centro * parseFloat(el.dataset.parallax)).toFixed(1)}px`);
      });
      ticking = false;
    };
    window.addEventListener('scroll', () => { if (!ticking) { requestAnimationFrame(mover); ticking = true; } }, { passive: true });
    mover();
  }

  /* ---------- Cookies ---------- */
  function initCookies() {
    const caja = $('#cookies'); if (!caja) return;
    let elegido = null;
    try { elegido = localStorage.getItem('lr-cookies'); } catch (e) { /* sin storage */ }
    if (elegido) { aplicarConsentimiento(elegido); return; }
    caja.hidden = false;
    requestAnimationFrame(() => caja.classList.add('is-visible'));
    caja.addEventListener('click', (e) => {
      const b = e.target.closest('[data-cookies]'); if (!b) return;
      try { localStorage.setItem('lr-cookies', b.dataset.cookies); } catch (err) { /* sin storage */ }
      aplicarConsentimiento(b.dataset.cookies);
      caja.classList.remove('is-visible');
      setTimeout(() => { caja.hidden = true; }, 400);
    });
  }
  function aplicarConsentimiento(valor) {
    // Punto único para activar analítica u otros scripts de terceros SOLO si se aceptó.
    document.documentElement.dataset.cookies = valor;
    if (valor === 'aceptar') {
      // Ejemplo: cargar aquí Google Analytics / Meta Pixel. Hoy no hay ninguno.
    }
  }

  /* ---------- Arranque ---------- */
  async function init() {
    estado.lang = detectarIdioma();
    try {
      const [t, carta, fotos, rest] = await Promise.all([
        cargarJSON(`data/i18n/${estado.lang}.json`),
        cargarJSON('data/carta.json'),
        cargarJSON('data/fotos.json'),
        cargarJSON('data/restaurante.json'),
      ]);
      Object.assign(estado, { t, carta, fotos, rest });
    } catch (err) {
      console.error(err);
      // Si falla la carga (p. ej. abriendo el HTML desde file://), la página queda con el contenido en español ya escrito en el HTML.
      envolverLetras(); initNav(); initTabs(); initMovimiento(); initCookies(); initCursor();
      return;
    }
    aplicarDatos();
    aplicarI18n();
    envolverLetras();
    pintarFotos();
    initHeroVideo();
    pintarCarta();
    pintarCombos();
    pintarGaleria();
    pintarHorario();
    pintarEstado();
    setInterval(pintarEstado, 60 * 1000);
    initNav();
    initTabs();
    initLightbox();
    initMovimiento();
    initCookies();
    initCursor();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
