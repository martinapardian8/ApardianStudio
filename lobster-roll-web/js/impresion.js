/* Carta impresa: arma una página A4 por idioma a partir de data/*.json. */
(() => {
  'use strict';
  const IDIOMAS = ['es', 'ca', 'en'];
  const get = (o, r) => r.split('.').reduce((a, k) => (a == null ? undefined : a[k]), o);
  const cargar = async (r) => { const x = await fetch(r, { cache: 'no-cache' }); if (!x.ok) throw new Error(r); return x.json(); };
  const txt = (o, lang) => (typeof o === 'string' ? o : (o?.[lang] ?? o?.es ?? ''));

  function pagina(lang, t, carta, rest) {
    const precio = (n) => new Intl.NumberFormat(get(t, 'precio.locale') || 'es-ES', { style: 'currency', currency: carta.moneda || 'EUR', minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }).format(n);
    const frag = document.getElementById('tpl-pagina').content.cloneNode(true);
    const sec = frag.querySelector('.pagina'); sec.lang = lang; sec.dataset.lang = lang;
    sec.querySelectorAll('[data-i18n]').forEach((el) => { const v = get(t, el.dataset.i18n); if (typeof v === 'string') el.textContent = v; });
    const datos = { ...rest, web_corta: (rest.web || '').replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '') };
    sec.querySelectorAll('[data-dato]').forEach((el) => { const v = get(datos, el.dataset.dato); if (v != null) el.textContent = v; });
    const todos = carta.categorias.flatMap((c) => c.items);
    sec.querySelectorAll('[data-precio-de]').forEach((el) => { const it = todos.find((x) => x.id === el.dataset.precioDe); if (it) el.textContent = precio(it.precio); });
    const rolls = carta.categorias.find((c) => c.id === 'rolls')?.items || [];
    carta.categorias.forEach((cat) => {
      const ul = sec.querySelector(`[data-categoria="${cat.id}"]`); if (!ul) return;
      ul.innerHTML = cat.items.map((it) => {
        const desc = txt(it.descripcion, lang) || (it.roll ? (rolls.find((r) => r.id === it.roll)?.nombre || '') : '');
        return `<li class="${it.destacado ? 'destacado' : ''}">${it.destacado ? `<span class="tag">${get(t, 'carta.especialidad')}</span>` : ''}<span class="nombre">${it.nombre}</span><span class="precio">${precio(it.precio)}</span>${desc ? `<span class="desc">${desc}</span>` : ''}</li>`;
      }).join('');
    });
    // horario resumido
    const h = rest.horario; const dc = get(t, 'localizacion.dias_corto'); const cerrado = get(t, 'localizacion.cerrado');
    const orden = [1, 2, 3, 4, 5, 6, 0]; const partes = []; let ini = 0; const clave = (d) => JSON.stringify(h.dias[String(d)] || []);
    for (let i = 1; i <= orden.length; i++) if (i === orden.length || clave(orden[i]) !== clave(orden[ini])) {
      const tr = h.dias[String(orden[ini])] || []; const dias = ini === i - 1 ? dc[orden[ini]] : `${dc[orden[ini]]}–${dc[orden[i - 1]]}`;
      partes.push(`${dias} ${tr.length ? tr.map(([a, b]) => `${a}–${b}`).join(', ') : cerrado.toLowerCase()}`); ini = i;
    }
    sec.querySelector('.pie__horario').textContent = `${get(t, 'localizacion.horario')}: ${partes.join(' · ')}`;
    return frag;
  }

  async function init() {
    const q = new URLSearchParams(location.search).get('lang') || 'es';
    const langs = q === 'todos' ? IDIOMAS : [IDIOMAS.includes(q) ? q : 'es'];
    const [carta, rest, ...ts] = await Promise.all([cargar('data/carta.json'), cargar('data/restaurante.json'), ...langs.map((l) => cargar(`data/i18n/${l}.json`))]);
    const cont = document.getElementById('paginas');
    langs.forEach((l, i) => cont.appendChild(pagina(l, ts[i], carta, rest)));
    document.documentElement.lang = langs[0];
    document.body.dataset.listo = '1';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
