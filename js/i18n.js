/* =========================================================
   APARDIAN — idiomas (ES / EN / PT)
   El HTML queda en español. Cada texto traducible lleva data-i18n
   (o data-ed) y el diccionario de js/i18n_dict.js trae la versión
   en inglés y en portugués. Al cambiar de idioma se reemplaza el
   contenido y se avisa al resto (luces, cursor) con el evento "idioma".
   ========================================================= */
(function () {
  var DIC = window.APARDIAN_I18N || {};
  var GEN = window.APARDIAN_I18N_GEN || {};
  var WA  = window.APARDIAN_I18N_WA || {};
  var NOMBRES = { es: 'Español', en: 'English', pt: 'Português' };
  var LANGS = { es: 'es-UY', en: 'en', pt: 'pt-BR' };
  var idioma = 'es', base = {}, hrefs = new WeakMap(), textos = new WeakMap(), aplicando = false;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  function claveDe(el) { return el.dataset.i18n || ('ed:' + el.dataset.ed); }

  function metaSet(sel, attr, v) { var m = $(sel); if (m && v) m.setAttribute(attr, v); }

  function traducirTexto(txt) {
    if (idioma === 'es') return null;
    var g = GEN[idioma] || {};
    if (g[txt] != null) return g[txt];
    var m = txt.match(/^(\d+) fotos$/);
    if (m && g['{n} fotos']) return g['{n} fotos'].replace('{n}', m[1]);
    m = txt.match(/^Selección de (\d+) fotos · archivo del proyecto: (\d+)$/);
    if (m && g['Selección de {n} fotos · archivo del proyecto: {m}']) return g['Selección de {n} fotos · archivo del proyecto: {m}'].replace('{n}', m[1]).replace('{m}', m[2]);
    m = txt.match(/^(.*?)(\s+·\s+\d+ \/ \d+)$/);          // pie del visor: "Bodas  ·  3 / 16"
    if (m && g[m[1]] != null) return g[m[1]] + m[2];
    return null;
  }

  // Textos que arma main.js desde data.js (galería, tarjetas, visor): se
  // traducen nodo por nodo guardando el original para poder volver.
  function traducirGenerados() {
    aplicando = true;
    var raices = $$('#galnav, #galphrase, #galcount, #galgrid, #rail, #lbcap, #marquee, #marquee2');
    raices.forEach(function (raiz) {
      var it = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, null), n;
      while ((n = it.nextNode())) {
        var orig = textos.has(n) ? textos.get(n) : n.nodeValue;
        if (!orig.trim()) continue;
        if (!textos.has(n)) textos.set(n, orig);
        var t = traducirTexto(orig.trim());
        var nuevo = (idioma === 'es' || t == null) ? orig : orig.replace(orig.trim(), t);
        if (n.nodeValue !== nuevo) n.nodeValue = nuevo;
      }
    });
    // botones con aria-label
    $$('#galgrid figure, #rail .shot, .marquee figure, .grande-grilla figure, #railPrev, #railNext, #lbclose, #lbprev, #lbnext').forEach(function (el) {
      var orig = el.dataset.ariaEs || el.getAttribute('aria-label'); if (!orig) return;
      el.dataset.ariaEs = orig;
      var g = GEN[idioma] || {}, t = null;
      Object.keys(g).some(function (k) { if (orig.indexOf(k) === 0) { t = g[k] + orig.slice(k.length); return true; } return false; });
      el.setAttribute('aria-label', idioma === 'es' || !t ? orig : t);
    });
    aplicando = false;
  }

  function traducirWhatsApp() {
    $$('a[href*="wa.me"]').forEach(function (a) {
      if (!hrefs.has(a)) hrefs.set(a, a.getAttribute('href'));
      var h = hrefs.get(a), i = h.indexOf('?text=');
      if (i < 0) return;
      var es = decodeURIComponent(h.slice(i + 6));
      var t = (idioma !== 'es' && WA[idioma] && WA[idioma][es]) ? WA[idioma][es] : es;
      a.setAttribute('href', h.slice(0, i + 6) + encodeURIComponent(t));
    });
  }

  function aplicar(lang, guardar) {
    if (!NOMBRES[lang]) lang = 'es';
    idioma = lang;
    var dic = DIC[lang] || {};
    $$('[data-i18n],[data-ed]').forEach(function (el) {
      var k = claveDe(el);
      if (!(k in base)) base[k] = el.innerHTML;
      var v = (lang !== 'es' && dic[k]) ? dic[k] : base[k];
      if (el.innerHTML !== v) el.innerHTML = v;
    });
    if (!('title' in base)) { base.title = document.title; base.desc = ($('meta[name="description"]') || {}).content || ''; base.ogt = ($('meta[property="og:title"]') || {}).content || ''; base.ogd = ($('meta[property="og:description"]') || {}).content || ''; }
    document.title = (lang !== 'es' && dic.title) || base.title;
    metaSet('meta[name="description"]', 'content', (lang !== 'es' && dic.desc) || base.desc);
    metaSet('meta[property="og:title"]', 'content', (lang !== 'es' && dic.ogtitle) || base.ogt);
    metaSet('meta[property="og:description"]', 'content', (lang !== 'es' && dic.ogdesc) || base.ogd);
    document.documentElement.lang = LANGS[lang];
    traducirGenerados();
    traducirWhatsApp();
    var b = $('#langBtn'); if (b) b.textContent = lang.toUpperCase();
    $$('#langMenu [data-lang]').forEach(function (o) { o.setAttribute('aria-selected', o.dataset.lang === lang ? 'true' : 'false'); });
    if (guardar) { try { localStorage.setItem('apardian_lang', lang); } catch (e) {} }
    document.dispatchEvent(new CustomEvent('idioma', { detail: { lang: lang, gen: GEN[lang] || {} } }));
  }

  function inicial() {
    var q = (location.search.match(/[?&]lang=(es|en|pt)/) || [])[1];
    if (q) return q;
    try { var s = localStorage.getItem('apardian_lang'); if (s && NOMBRES[s]) return s; } catch (e) {}
    var nav = (navigator.language || '').slice(0, 2).toLowerCase();
    return (nav === 'en' || nav === 'pt') ? nav : 'es';
  }

  // Botón del header
  function menu() {
    var btn = $('#langBtn'), lista = $('#langMenu'); if (!btn || !lista) return;
    function cerrar() { lista.hidden = true; btn.setAttribute('aria-expanded', 'false'); }
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var abierto = !lista.hidden; lista.hidden = abierto; btn.setAttribute('aria-expanded', abierto ? 'false' : 'true');
    });
    $$('#langMenu [data-lang]').forEach(function (o) {
      o.addEventListener('click', function () { aplicar(o.dataset.lang, true); cerrar(); });
    });
    document.addEventListener('click', function (e) { if (!lista.hidden && !lista.contains(e.target)) cerrar(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrar(); });
  }

  // Después de load: el editor visual reescribe los [data-ed] al arrancar y
  // hay que pasar por encima; luces() parte las letras 60 ms más tarde.
  function arrancar() {
    menu();
    var l = inicial();
    if (l !== 'es') aplicar(l, false); else { var b = $('#langBtn'); if (b) b.textContent = 'ES'; }
    // lo que main.js regenere (cambiar de categoría, abrir el visor) se traduce solo
    if ('MutationObserver' in window) {
      var t = null;
      var mo = new MutationObserver(function () {
        if (aplicando || idioma === 'es') return;
        clearTimeout(t); t = setTimeout(function () { traducirGenerados(); }, 30);
      });
      $$('#galnav, #galphrase, #galcount, #galgrid, #rail, #lbcap').forEach(function (r) { mo.observe(r, { childList: true, subtree: true, characterData: true }); });
    }
  }
  function despues() { setTimeout(arrancar, 120); }
  if (document.readyState === 'complete') despues(); else window.addEventListener('load', despues);

  window.APARDIAN_setLang = function (l) { aplicar(l, true); };
})();
