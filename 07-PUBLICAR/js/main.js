/* =========================================================
   APARDIAN STUDIO — comportamiento
   ========================================================= */
document.documentElement.classList.add('js');

(function () {
  'use strict';

  var D = window.SITE_DATA || { hero: '', works: [], categories: [] };
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------- LOADER ---------------- */
  var loader = $('#loader'), barfill = $('#barfill'), pct = $('#pct'),
      enterBtn = $('#enter'), loadmsg = $('#loadmsg'), nav = $('#nav');

  var heroSrc = D.hero || (D.categories[0] && D.categories[0].photos[0] && D.categories[0].photos[0].web) || '';
  var heroImg = $('#heroimg');

  // Precarga: el hero + las primeras miniaturas de cada categoría
  var preload = [];
  if (heroSrc) preload.push(heroSrc);
  (D.works || []).slice(0, 6).forEach(function (w) { if (w.thumb) preload.push(w.thumb); });
  if (!preload.length) preload.push('');

  var loaded = 0, total = preload.length, shown = 0;

  function paint(p) {
    barfill.style.width = p + '%';
    pct.textContent = Math.round(p);
  }
  function tick() {
    loaded++;
    var real = Math.min(100, (loaded / total) * 100);
    if (real > shown) { shown = real; paint(shown); }
    if (loaded >= total) ready();
  }
  var readyDone = false;
  function ready() {
    if (readyDone) return; readyDone = true;
    paint(100);
    loadmsg.textContent = 'Archivo listo';
    enterBtn.classList.add('on');
    enterBtn.focus({ preventScroll: true });
  }

  preload.forEach(function (src) {
    if (!src) { tick(); return; }
    var i = new Image();
    i.onload = i.onerror = tick;
    i.src = src;
  });
  setTimeout(ready, 4500); // nunca dejar a nadie encerrado

  // fondo del loader: la foto entra enseguida, el reel cuando puede
  (function loaderBg() {
    var li = $('#loaderimg'), lv = $('#loadervid');
    if (li && heroSrc) {
      li.src = heroSrc;
      li.onload = function () { li.classList.add('on'); };
    }
    if (lv && D.heroVideo) {
      lv.muted = true; lv.defaultMuted = true;
      lv.setAttribute('muted', ''); lv.setAttribute('autoplay', '');
      lv.playsInline = true;
      lv.src = D.heroVideo;
      lv.load();
      var go = function () {
        if (!lv.paused) { lv.classList.add('on'); return; }
        var pr = lv.play();
        if (pr && pr.then) pr.then(function () { lv.classList.add('on'); }).catch(function () {});
      };
      lv.addEventListener('canplay', go, { once: true });
      lv.addEventListener('playing', function () { lv.classList.add('on'); });
      ['pointerdown', 'touchstart', 'keydown'].forEach(function (ev) {
        window.addEventListener(ev, go, { passive: true, once: false });
      });
      go();
    }
  })();

  document.body.classList.add('locked');
  function openSite() {
    loader.classList.add('gone');
    document.body.classList.remove('locked');
    if (heroImg && heroSrc) { heroImg.src = heroSrc; heroImg.classList.add('on'); }
    var hv = $('#herovid');
    if (hv && D.heroVideo) {
      hv.muted = true;
      hv.defaultMuted = true;
      hv.setAttribute('muted', '');
      hv.setAttribute('autoplay', '');
      hv.playsInline = true;
      hv.src = D.heroVideo;
      hv.load();

      var tries = 0;
      function tryPlay() {
        if (!hv.paused) { hv.classList.add('on'); return; }
        if (tries++ > 30) return;
        var pr = hv.play();
        if (pr && pr.then) {
          pr.then(function () { hv.classList.add('on'); })
            .catch(function () { /* la política del navegador lo frenó: reintentamos al primer gesto */ });
        } else if (!hv.paused) {
          hv.classList.add('on');
        }
      }
      var lv2 = $('#loadervid');
      if (lv2 && !lv2.paused) { try { hv.currentTime = lv2.currentTime; } catch (e) {} }
      hv.addEventListener('canplay', tryPlay, { once: true });
      hv.addEventListener('playing', function () { hv.classList.add('on'); });
      // cualquier gesto del visitante desbloquea el autoplay
      ['pointerdown', 'touchstart', 'keydown', 'scroll'].forEach(function (ev) {
        window.addEventListener(ev, tryPlay, { passive: true });
      });
      tryPlay();
    }
    setTimeout(function () { if (loader.parentNode) loader.parentNode.removeChild(loader); }, 900);
  }
  enterBtn.addEventListener('click', openSite);
  document.addEventListener('keydown', function (e) {
    if (!readyDone) return;
    if (loader.parentNode && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openSite(); }
  });

  /* ---------------- NAV (aparece al primer scroll) ---------------- */
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY || 0;
    if (y > window.innerHeight * 0.62) nav.classList.add('show');
    else nav.classList.remove('show');
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var burger = $('#burger'), links = $('#links');
  burger.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    burger.classList.toggle('x', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  $$('#links a').forEach(function (a) {
    a.addEventListener('click', function () {
      links.classList.remove('open'); burger.classList.remove('x');
      burger.setAttribute('aria-expanded', 'false');
    });
  });

  /* ---------------- REVELADO PROGRESIVO ---------------- */
  var io = null;
  if ('IntersectionObserver' in window) {
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    $$('.rv').forEach(function (el) { io.observe(el); });
  } else {
    $$('.rv').forEach(function (el) { el.classList.add('in'); });
  }
  function watch(el) { el.classList.add('rv'); if (io) io.observe(el); else el.classList.add('in'); }

  /* ---------------- TRABAJOS ---------------- */
  var rail = $('#rail');
  (D.works || []).forEach(function (w) {
    var a = document.createElement('article');
    a.className = 'card';
    a.innerHTML =
      '<div class="shot">' +
        '<span class="chip' + (w.chipDark ? ' dark' : '') + '">' + w.chip + '</span>' +
        '<img loading="lazy" decoding="async" src="' + w.thumb + '" data-full="' + w.web + '" alt="' + w.title + '">' +
      '</div>' +
      '<h3>' + w.title + '</h3>' +
      '<p>' + w.meta + '</p>';
    a.querySelector('.shot').addEventListener('click', function () { openLB([{ web: w.web, cap: w.title }], 0); });
    rail.appendChild(a);
  });

  // Arrastre con el mouse en el carrusel
  var down = false, startX = 0, startL = 0, moved = false;
  rail.addEventListener('pointerdown', function (e) {
    down = true; moved = false; startX = e.clientX; startL = rail.scrollLeft;
    rail.style.cursor = 'grabbing';
  });
  window.addEventListener('pointerup', function () { down = false; rail.style.cursor = ''; });
  rail.addEventListener('pointermove', function (e) {
    if (!down) return;
    var dx = e.clientX - startX;
    if (Math.abs(dx) > 4) moved = true;
    rail.scrollLeft = startL - dx;
  });
  rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);

  /* ---------------- GALERÍA ---------------- */
  var galnav = $('#galnav'), galgrid = $('#galgrid'), galphrase = $('#galphrase');
  var current = null;

  (D.categories || []).forEach(function (c, idx) {
    var b = document.createElement('button');
    b.type = 'button';
    b.innerHTML = '<span>' + c.name + '</span><em>' + (c.soon ? 'Pronto' : c.photos.length) + '</em>';
    b.addEventListener('click', function () { show(idx); });
    galnav.appendChild(b);
  });

  function show(idx) {
    var c = D.categories[idx];
    if (!c) return;
    current = c;
    $$('#galnav button').forEach(function (b, i) { b.classList.toggle('on', i === idx); });
    galphrase.textContent = c.phrase || '';
    var gc = $('#galcount');
    if (gc) {
      gc.textContent = (c.soon || !c.photos.length) ? ''
        : 'Selección de ' + c.photos.length + ' fotos · archivo del proyecto: ' + c.archive;
    }
    galgrid.innerHTML = '';

    if (c.soon || !c.photos.length) {
      var d = document.createElement('p');
      d.className = 'gal-empty';
      d.textContent = c.soonText || 'Estoy revelando este archivo. Vuelve pronto.';
      galgrid.appendChild(d);
      return;
    }
    c.photos.forEach(function (p, i) {
      var f = document.createElement('figure');
      if (p.shape) f.classList.add(p.shape);
      if (p.video) f.classList.add('vid');
      if (p.video) {
        var v = document.createElement('video');
        v.muted = true; v.loop = true; v.playsInline = true;
        v.setAttribute('playsinline', ''); v.preload = 'metadata';
        v.poster = p.thumb; v.src = p.video;
        f.appendChild(v);
        var tag = document.createElement('span');
        tag.className = 'tag'; tag.textContent = 'Video';
        f.appendChild(tag);
        if (io) {
          var vio = new IntersectionObserver(function (es) {
            es.forEach(function (e) {
              if (e.isIntersecting) { var q = v.play(); if (q && q.catch) q.catch(function () {}); }
              else { v.pause(); }
            });
          }, { threshold: 0.25 });
          vio.observe(f);
        }
      } else {
        var im = document.createElement('img');
        im.loading = 'lazy'; im.decoding = 'async';
        im.src = p.thumb; im.alt = c.name + ' — Apardian Studio';
        f.appendChild(im);
      }
      f.addEventListener('click', function () { openLB(c.photos, i, c.name); });
      galgrid.appendChild(f);
    });
  }
  if ((D.categories || []).length) show(0);

  /* ---------------- LIGHTBOX ---------------- */
  var lb = $('#lb'), lbimg = $('#lbimg'), lbcap = $('#lbcap');
  var set = [], at = 0, setName = '';

  function openLB(arr, i, name) {
    set = arr; at = i; setName = name || '';
    lb.classList.add('on');
    // fondo del loader: la foto entra enseguida, el reel cuando puede
  (function loaderBg() {
    var li = $('#loaderimg'), lv = $('#loadervid');
    if (li && heroSrc) {
      li.src = heroSrc;
      li.onload = function () { li.classList.add('on'); };
    }
    if (lv && D.heroVideo) {
      lv.muted = true; lv.defaultMuted = true;
      lv.setAttribute('muted', ''); lv.setAttribute('autoplay', '');
      lv.playsInline = true;
      lv.src = D.heroVideo;
      lv.load();
      var go = function () {
        if (!lv.paused) { lv.classList.add('on'); return; }
        var pr = lv.play();
        if (pr && pr.then) pr.then(function () { lv.classList.add('on'); }).catch(function () {});
      };
      lv.addEventListener('canplay', go, { once: true });
      lv.addEventListener('playing', function () { lv.classList.add('on'); });
      ['pointerdown', 'touchstart', 'keydown'].forEach(function (ev) {
        window.addEventListener(ev, go, { passive: true, once: false });
      });
      go();
    }
  })();

  document.body.classList.add('locked');
    paintLB();
  }
  function paintLB() {
    var p = set[at]; if (!p) return;
    var lv = document.getElementById('lbvid');
    if (p.video) {
      lbimg.style.display = 'none';
      if (!lv) {
        lv = document.createElement('video');
        lv.id = 'lbvid'; lv.controls = true; lv.loop = true; lv.playsInline = true;
        lv.style.maxWidth = '100%'; lv.style.maxHeight = '88vh';
        lbimg.parentNode.insertBefore(lv, lbimg);
      }
      lv.style.display = 'block';
      lv.src = p.video; lv.poster = p.thumb;
      var q = lv.play(); if (q && q.catch) q.catch(function () {});
    } else {
      if (lv) { lv.pause(); lv.style.display = 'none'; lv.removeAttribute('src'); }
      lbimg.style.display = 'block';
      lbimg.src = p.web || p.thumb;
    }
    lbimg.alt = p.cap || setName;
    lbcap.textContent = (p.cap || setName) + '  ·  ' + (at + 1) + ' / ' + set.length;
  }
  function closeLB() {
    lb.classList.remove('on');
    document.body.classList.remove('locked');
    lbimg.src = '';
    var lv = document.getElementById('lbvid');
    if (lv) { lv.pause(); lv.removeAttribute('src'); }
  }
  function step(n) { at = (at + n + set.length) % set.length; paintLB(); }

  $('#lbclose').addEventListener('click', closeLB);
  $('#lbprev').addEventListener('click', function (e) { e.stopPropagation(); step(-1); });
  $('#lbnext').addEventListener('click', function (e) { e.stopPropagation(); step(1); });
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target === lbimg) closeLB(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('on')) return;
    if (e.key === 'Escape') closeLB();
    if (e.key === 'ArrowRight') step(1);
    if (e.key === 'ArrowLeft') step(-1);
  });

  /* ---------------- FONDO ANIMADO DE SECCIÓN ---------------- */
  (function fondoSeccion() {
    var im = $('#procesoimg'), vd = $('#procesovid');
    if (!im || !vd || !D.sectionBg) return;
    im.src = D.sectionBg.poster;
    im.onload = function () { im.classList.add('on'); };
    var armado = false;
    function armar() {
      if (armado) return; armado = true;
      vd.muted = true; vd.defaultMuted = true;
      vd.setAttribute('muted', ''); vd.playsInline = true;
      vd.src = D.sectionBg.video; vd.load();
      var go = function () {
        var pr = vd.play();
        if (pr && pr.then) pr.then(function () { vd.classList.add('on'); }).catch(function () {});
      };
      vd.addEventListener('canplay', go, { once: true });
      vd.addEventListener('playing', function () { vd.classList.add('on'); });
    }
    // se carga recién cuando la sección se acerca, para no pesar la primera vista
    var sec = document.getElementById('proceso');
    if (io && sec) {
      var o = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { armar(); vd.play && vd.play().catch(function () {}); }
          else if (armado) { vd.pause(); }
        });
      }, { rootMargin: '300px' });
      o.observe(sec);
    } else { armar(); }

    // red de seguridad: si el observador no dispara (viewport raro, navegador viejo),
    // se arma igual al primer scroll o a los tres segundos
    function porScroll() {
      var r = sec.getBoundingClientRect();
      if (r.top < (window.innerHeight || 800) + 400 && r.bottom > -400) {
        armar();
        window.removeEventListener('scroll', porScroll);
      }
    }
    window.addEventListener('scroll', porScroll, { passive: true });
    setTimeout(porScroll, 1200);
    // ultimo recurso: a los tres segundos se arma si o si, aunque el viewport
    // reporte cero (pasa en vistas previas embebidas y en algunos navegadores)
    setTimeout(armar, 3000);
  })();

  /* ---------------- TIRA DE FOTOS ---------------- */
  (function tira() {
    var a = $('#marquee'), b = $('#marquee2');
    if (!a || !b) return;
    var pool = [];
    (D.categories || []).forEach(function (c) {
      (c.photos || []).forEach(function (p) { if (!p.video) pool.push(p); });
    });
    if (!pool.length) return;
    // barajado estable, para que las dos filas no muestren lo mismo
    var mezcla = pool.slice().sort(function (x, y) {
      return (x.thumb.length % 7) - (y.thumb.length % 7) || x.thumb.localeCompare(y.thumb);
    });
    function llenar(cont, lista) {
      var frag = document.createDocumentFragment();
      // dos vueltas: el bucle del carrusel necesita el contenido duplicado
      for (var vuelta = 0; vuelta < 2; vuelta++) {
        lista.forEach(function (p) {
          var f = document.createElement('figure');
          var i = document.createElement('img');
          i.loading = 'lazy'; i.decoding = 'async';
          i.src = p.thumb; i.alt = '';
          f.appendChild(i); frag.appendChild(f);
        });
      }
      cont.appendChild(frag);
    }
    llenar(a, mezcla.slice(0, 26));
    llenar(b, mezcla.slice(26, 52).length ? mezcla.slice(26, 52) : mezcla.slice(0, 26).reverse());
  })();

  /* ---------------- RELOJ MONTEVIDEO ---------------- */
  var clock = $('#clock');
  function tickClock() {
    try {
      clock.textContent = new Intl.DateTimeFormat('es-UY', {
        timeZone: 'America/Montevideo', hour: '2-digit', minute: '2-digit', hour12: false
      }).format(new Date());
    } catch (e) { clock.textContent = ''; }
  }
  tickClock(); setInterval(tickClock, 20000);

})();
