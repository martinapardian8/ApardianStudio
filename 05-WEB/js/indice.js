/* =========================================================
   APARDIAN — servicios en índice y sección de música
   En PC la fila activa muestra su trabajo en el visor fijo de la
   derecha (las muestras se mudan ahí una sola vez). En celular cada
   fila es un acordeón con su muestra adentro. Sin JS, todo queda
   abierto y legible.
   ========================================================= */
(function () {
  'use strict';
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function reproducir(v) {
    if (!v || quieto) return;
    if (!v.src && v.dataset.src) {
      v.muted = true; v.defaultMuted = true; v.playsInline = true;
      // WebM (VP9) donde se pueda: pesa lo mismo y anda en todos los Chromium
      var webm = v.dataset.srcWebm;
      v.src = (webm && v.canPlayType && v.canPlayType('video/webm; codecs="vp9"')) ? webm : v.dataset.src;
      v.addEventListener('canplay', function () {
        var p = v.play(); if (p && p.then) p.then(function () { v.classList.add('on'); }).catch(function () {});
      }, { once: true });
      v.load();
    } else if (v.paused) {
      var p2 = v.play(); if (p2 && p2.then) p2.catch(function () {});
    }
  }

  /* ---------------- SERVICIOS ---------------- */
  (function indice() {
    var sec = document.getElementById('servicios');
    if (!sec) return;
    var filas = $$('.idx-fila', sec);
    var visor = sec.querySelector('.idx-visor');
    var cuenta = sec.querySelector('.idx-cuenta');
    if (!filas.length || !visor) return;
    var paneles = filas.map(function (f) { return f.querySelector('.idx-panel'); });
    var cabs = filas.map(function (f) { return f.querySelector('.idx-cab'); });
    var pc = window.matchMedia('(min-width: 901px)');
    var actual = 0, enVisor = false;

    function videos(i) {
      paneles.forEach(function (p, k) {
        var v = p.querySelector('video');
        if (!v) return;
        if (k === i) reproducir(v); else if (!v.paused) v.pause();
      });
    }

    function activar(i) {
      actual = i;
      filas.forEach(function (f, k) { f.classList.toggle('activa', k === i); });
      if (enVisor) {
        paneles.forEach(function (p, k) { p.classList.toggle('on', k === i); });
        cabs.forEach(function (c, k) { c.setAttribute('aria-expanded', k === i ? 'true' : 'false'); });
        if (cuenta) cuenta.innerHTML = '<b>' + ('0' + (i + 1)).slice(-2) + '</b> / 0' + filas.length;
      }
      videos(i);
    }

    function abrirCelular(i) {
      paneles.forEach(function (p, k) {
        var abierto = k === i;
        p.hidden = !abierto;
        cabs[k].setAttribute('aria-expanded', abierto ? 'true' : 'false');
      });
      actual = i;
      filas.forEach(function (f, k) { f.classList.toggle('activa', k === i); });
      videos(i);
    }

    function modo() {
      if (pc.matches) {
        paneles.forEach(function (p) { p.hidden = false; visor.insertBefore(p, cuenta); });
        visor.removeAttribute('aria-hidden');
        enVisor = true;
        activar(actual < 0 ? 0 : actual);
      } else {
        enVisor = false;
        visor.setAttribute('aria-hidden', 'true');
        paneles.forEach(function (p, k) { p.classList.remove('on'); filas[k].appendChild(p); });
        abrirCelular(actual);
      }
    }

    filas.forEach(function (f, k) {
      f.addEventListener('mouseenter', function () { if (enVisor && actual !== k) activar(k); });
      cabs[k].addEventListener('focus', function () { if (enVisor && actual !== k) activar(k); });
      cabs[k].addEventListener('click', function () {
        if (enVisor) { activar(k); return; }
        abrirCelular(actual === k ? -1 : k);
        if (actual === k) f.scrollIntoView({ block: 'nearest', behavior: quieto ? 'auto' : 'smooth' });
      });
    });

    if (pc.addEventListener) pc.addEventListener('change', modo); else if (pc.addListener) pc.addListener(modo);
    modo();

    // antes y después: el control es un input range, así anda con teclado
    $$('.idx-media-ba', sec).forEach(function (fig) {
      var r = fig.querySelector('.ba-rango');
      if (!r) return;
      var poner = function () { fig.style.setProperty('--x', r.value + '%'); };
      r.addEventListener('input', poner);
      poner();
    });
  })();

  /* ---------------- MÚSICA ---------------- */
  (function musica() {
    var sec = document.getElementById('musica');
    if (!sec) return;

    // el fondo en movimiento se baja recién cuando la sección se acerca
    var v = sec.querySelector('.mus-fondo video');
    if (v && !quieto) {
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (e.isIntersecting) reproducir(v);
            else if (v.src && !v.paused) v.pause();
          });
        }, { rootMargin: '400px 0px' });
        io.observe(sec);
      } else {
        reproducir(v);
      }
    }

    // Spotify se carga solo si la persona lo pide: la página no le habla a
    // un tercero hasta ese clic, y arranca más rápido.
    $$('.sp-caja', sec).forEach(function (caja) {
      var btn = caja.querySelector('.sp-poster');
      if (!btn || !caja.dataset.spotify) return;
      btn.addEventListener('click', function () {
        var f = document.createElement('iframe');
        f.src = caja.dataset.spotify;
        f.title = 'Spotify · Fugaz — Marto Apardian';
        f.setAttribute('allow', 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture');
        f.setAttribute('loading', 'lazy');
        f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
        caja.innerHTML = '';
        caja.appendChild(f);
        f.focus();
      });
    });
  })();

  /* ---------------- aria-label traducidos ---------------- */
  // i18n.js traduce el contenido; los aria-label nuevos se traducen acá.
  document.addEventListener('idioma', function (e) {
    var lang = (e.detail && e.detail.lang) || 'es';
    var dic = (window.APARDIAN_I18N || {})[lang] || {};
    $$('[data-i18n-aria]').forEach(function (el) {
      if (!el.dataset.ariaBase) el.dataset.ariaBase = el.getAttribute('aria-label') || '';
      var k = el.dataset.i18nAria;
      el.setAttribute('aria-label', lang !== 'es' && dic[k] ? dic[k] : el.dataset.ariaBase);
    });
  });
})();
