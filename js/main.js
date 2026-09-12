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
    if (barfill) barfill.style.width = p + '%';
    var barra = $('#barra'); if (barra) barra.setAttribute('aria-valuenow', Math.round(p));
    if (pct) pct.textContent = Math.round(p);
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
    if (loadmsg) loadmsg.textContent = 'Archivo listo';
    if (enterBtn) { enterBtn.classList.add('on'); enterBtn.focus({ preventScroll: true }); }
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

  // La web arranca directo en el hero: no hay pantalla previa ni botón "Entrar".
  function openSite() {
    if (loader) loader.classList.add('gone');
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
    setTimeout(function () { if (loader && loader.parentNode) loader.parentNode.removeChild(loader); }, 900);
  }
  if (enterBtn) enterBtn.addEventListener('click', openSite);
  else openSite();

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
        '<img loading="lazy" decoding="async" src="' + w.thumb + '" srcset="' + w.thumb + ' 420w, ' + w.web + ' 1800w" sizes="(max-width:760px) 88vw, 42vw" data-full="' + w.web + '" alt="' + w.title + '"' + (w.foco ? ' style="object-position:' + w.foco + '"' : '') + '>' +
      '</div>' +
      '<h3>' + w.title + '</h3>' +
      '<p>' + w.meta + '</p>';
    var shot = a.querySelector('.shot');
    shot.tabIndex = 0; shot.setAttribute('role', 'button'); shot.setAttribute('aria-label', 'Ver ' + w.title);
    shot.addEventListener('click', function () { openLB([{ web: w.web, cap: w.title }], 0); });
    shot.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLB([{ web: w.web, cap: w.title }], 0); }
    });
    rail.appendChild(a);
  });

  // Carrusel: flechas, y si dejás el mouse apretado las fotos van pasando solas.
  // Un clic corto en una foto la abre en grande; arrastrar sigue funcionando.
  var down = false, startX = 0, startL = 0, moved = false, sosten = null, corriendo = false;
  function anchoCard() {
    var c = rail.querySelector('.card');
    return c ? c.getBoundingClientRect().width + 18 : 400;
  }
  function paso(n) {
    var max = rail.scrollWidth - rail.clientWidth;
    var dest = rail.scrollLeft + n * anchoCard();
    if (dest > max + 4) dest = 0;                 // al final vuelve al principio
    if (dest < -4) dest = max;
    rail.scrollTo({ left: dest, behavior: 'smooth' });
  }
  var bPrev = $('#railPrev'), bNext = $('#railNext');
  if (bPrev) bPrev.addEventListener('click', function () { paso(-1); });
  if (bNext) bNext.addEventListener('click', function () { paso(1); });

  function correr() {
    if (!corriendo) return;
    var max = rail.scrollWidth - rail.clientWidth;
    rail.scrollLeft = rail.scrollLeft >= max - 1 ? 0 : rail.scrollLeft + 2.4;   // la mitad: que dé tiempo a mirar
    requestAnimationFrame(correr);
  }
  rail.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'touch') return;
    down = true; moved = false; startX = e.clientX; startL = rail.scrollLeft;
    rail.style.cursor = 'grabbing';
    clearTimeout(sosten);
    sosten = setTimeout(function () {
      if (down && !moved) { moved = true; corriendo = true; rail.classList.add('corriendo'); correr(); }
    }, 320);
  });
  window.addEventListener('pointerup', function () {
    down = false; rail.style.cursor = ''; clearTimeout(sosten);
    if (corriendo) { corriendo = false; rail.classList.remove('corriendo'); }
  });
  rail.addEventListener('pointermove', function (e) {
    if (!down || corriendo) return;
    var dx = e.clientX - startX;
    if (Math.abs(dx) > 4) moved = true;
    rail.scrollLeft = startL - dx;
  });
  rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
  rail.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); paso(1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); paso(-1); }
  });

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
        if (p.foco) im.style.objectPosition = p.foco;   // el sujeto queda a la vista en el recorte
        f.appendChild(im);
      }
      f.addEventListener('click', function () { openLB(c.photos, i, c.name); });
      // la galería también se recorre con teclado
      f.tabIndex = 0; f.setAttribute('role', 'button');
      f.setAttribute('aria-label', 'Ver foto ' + (i + 1) + ' de ' + c.name);
      f.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLB(c.photos, i, c.name); }
      });
      galgrid.appendChild(f);
    });
  }
  if ((D.categories || []).length) show(0);

  /* ---------------- LIGHTBOX ---------------- */
  var lb = $('#lb'), lbimg = $('#lbimg'), lbcap = $('#lbcap');
  var set = [], at = 0, setName = '', lbOpener = null;

  function openLB(arr, i, name) {
    set = arr; at = i; setName = name || '';
    lbOpener = document.activeElement;
    lb.classList.add('on');
    setTimeout(function () { var cx = $('#lbclose'); if (cx) cx.focus(); }, 40);
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
    if (lbOpener && lbOpener.focus) { try { lbOpener.focus(); } catch (e) {} }
    lbOpener = null;
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

  /* ---------------- FONDOS DE SECCION ---------------- */
  // Cada seccion con .sec-bg y data-src enciende su fondo cuando se acerca.
  // El video se baja recien ahi, para no cargar cuatro videos al abrir la pagina.
  (function fondos() {
    var cajas = $$('section.has-bg .sec-bg');
    if (!cajas.length) return;

    function encender(caja) {
      if (caja.dataset.on) return;
      caja.dataset.on = '1';
      var img = caja.querySelector('img'), vid = caja.querySelector('video');
      if (img && img.dataset.src && !img.src) {
        img.src = img.dataset.src;
        img.onload = function () { img.classList.add('on'); };
      }
      if (vid && vid.dataset.src && !vid.src) {
        vid.muted = true; vid.defaultMuted = true; vid.playsInline = true;
        vid.setAttribute('muted', ''); vid.setAttribute('playsinline', '');
        vid.src = vid.dataset.src;
        vid.addEventListener('canplay', function () {
          var pr = vid.play();
          if (pr && pr.then) pr.then(function () { vid.classList.add('on'); }).catch(function () {});
          else vid.classList.add('on');
        }, { once: true });
        vid.load();
      }
    }

    function revisar() {
      var vh = window.innerHeight || document.documentElement.clientHeight || 800;
      cajas.forEach(function (c) {
        var s = c.closest('section');
        if (!s) return;
        var r = s.getBoundingClientRect();
        if (r.top < vh + 500 && r.bottom > -500) encender(c);
      });
    }
    revisar();
    window.addEventListener('scroll', revisar, { passive: true });
    // si el navegador no manda scroll, igual se encienden a los tres segundos
    setTimeout(function () { cajas.forEach(encender); }, 3000);
  })();

  /* ---------------- SERVICIOS: scrollytelling ---------------- */
  (function servicios() {
    var pasos  = $$('.svc-paso');
    var medios = $$('.svc-media');
    var cuenta = $('.svc-cuenta');
    if (!pasos.length || !medios.length) return;

    var actual = -1;
    function activar(i) {
      if (i === actual) return;
      actual = i;
      pasos.forEach(function (p, k) { p.classList.toggle('activo', k === i); });
      // la imagen anterior queda debajo ("was") mientras la nueva entra en cortina
      medios.forEach(function (m, k) {
        m.classList.toggle('was', m.classList.contains('on') && k !== i);
        m.classList.toggle('on', k === i);
      });
      if (cuenta) cuenta.innerHTML = '<b>' + ('0' + (i + 1)).slice(-2) + '</b> / 0' + pasos.length;

      // el video del servicio activo se carga recién cuando le toca:
      // así la página no arranca bajando cuatro videos de golpe
      var v = medios[i] && medios[i].querySelector('video');
      if (v && !v.src && v.dataset.src) {
        v.muted = true; v.defaultMuted = true; v.playsInline = true;
        v.src = v.dataset.src;
        v.addEventListener('canplay', function () {
          v.classList.add('listo');
          var pr = v.play(); if (pr && pr.then) pr.catch(function () {});
        }, { once: true });
        v.load();
      } else if (v && v.paused) {
        var pr2 = v.play(); if (pr2 && pr2.then) pr2.catch(function () {});
      }
      medios.forEach(function (m, k) {
        if (k === i) return;
        var o = m.querySelector('video');
        if (o && !o.paused) o.pause();
      });
    }

    activar(0);

    // Se sigue la posición con el reloj de animación del navegador en vez de
    // escuchar el scroll: hay navegadores y vistas embebidas donde el evento
    // de scroll no llega, y ahí el panel se quedaba clavado en el primero.
    var seccion = $('#servicios');
    var ultimo = -1;
    function mirar() {
      var rs = seccion.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight || 800;
      // solo trabaja mientras la sección está a la vista
      if (rs.bottom > -200 && rs.top < vh + 200) {
        // paralaje: el marco pegado se mueve apenas contra el scroll
        var marco = seccion.querySelector('.svc-marco');
        if (marco) marco.style.setProperty('--par', Math.max(-1, Math.min(1, (vh * 0.5 - (rs.top + rs.height * 0.5)) / rs.height * 2)).toFixed(3));
        var linea = vh * 0.46, mejor = 0, min = Infinity;
        for (var k = 0; k < pasos.length; k++) {
          var r = pasos[k].getBoundingClientRect();
          var d = Math.abs((r.top + r.bottom) / 2 - linea);
          // el último gana desde que su borde superior cruza la línea
          if (k === pasos.length - 1 && r.top < linea) d = -1;
          if (d < min) { min = d; mejor = k; }
        }
        if (mejor !== ultimo) { ultimo = mejor; activar(mejor); }
      }
      requestAnimationFrame(mirar);
    }
    requestAnimationFrame(mirar);

    // Tres caminos por si alguno no dispara: el reloj de animación de arriba,
    // el evento de scroll y el observador. El primero que llegue manda.
    window.addEventListener('scroll', function () {
      var vh = window.innerHeight || 800, linea = vh * 0.46, mejor = 0, min = Infinity;
      for (var k = 0; k < pasos.length; k++) {
        var r = pasos[k].getBoundingClientRect();
        var d = Math.abs((r.top + r.bottom) / 2 - linea);
        if (k === pasos.length - 1 && r.top < linea) d = -1;
        if (d < min) { min = d; mejor = k; }
      }
      if (mejor !== ultimo) { ultimo = mejor; activar(mejor); }
    }, { passive: true });

    if ('IntersectionObserver' in window) {
      var ioS = new IntersectionObserver(function (es) {
        var g = null;
        es.forEach(function (e) {
          if (e.isIntersecting && (!g || e.intersectionRatio > g.intersectionRatio)) g = e;
        });
        if (g) {
          var k = pasos.indexOf(g.target);
          if (k !== ultimo) { ultimo = k; activar(k); }
        }
      }, { rootMargin: '-40% 0px -40% 0px', threshold: [0, .3, .6, 1] });
      pasos.forEach(function (p) { ioS.observe(p); });
    }
  })();

  /* ---------------- EN GRANDE ---------------- */
  (function grande() {
    var pasos   = $$('.grande-paso');
    var medios  = $$('.grande-media');
    var cuenta  = $('.grande-cuenta');
    var seccion = $('.grande-scrolly');
    if (!pasos.length || !medios.length || !seccion) return;

    var actual = -1, ultimo = -1;
    function activar(i) {
      if (i === actual) return;
      actual = i;
      pasos.forEach(function (p, k) { p.classList.toggle('activo', k === i); });
      medios.forEach(function (m, k) {
        m.classList.toggle('was', m.classList.contains('on') && k !== i);
        m.classList.toggle('on', k === i);
      });
      if (cuenta) cuenta.innerHTML = '<b>' + ('0' + (i + 1)).slice(-2) + '</b> / 0' + pasos.length;
    }

    // Cada paso mide una pantalla y lleva la tarjeta abajo. Gana el último
    // paso cuyo borde superior ya cruzó el 22% de la pantalla: en ese momento
    // su tarjeta asoma por abajo y el montaje cambia con ella.
    function elegir() {
      var vh = window.innerHeight || document.documentElement.clientHeight || 800;
      var linea = vh * 0.22, mejor = 0;
      for (var k = 0; k < pasos.length; k++) {
        if (pasos[k].getBoundingClientRect().top <= linea) mejor = k;
      }
      return mejor;
    }
    function revisar() {
      var rs = seccion.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight || 800;
      if (rs.bottom < -200 || rs.top > vh + 200) return;
      // avance 0..1 dentro del recorrido: mueve la barra roja y el paralaje de la escena
      var t = Math.max(0, Math.min(1, -rs.top / Math.max(1, rs.height - vh)));
      var escena = seccion.querySelector('.grande-escena');
      if (escena) { escena.style.setProperty('--par', t.toFixed(3)); escena.style.setProperty('--prog', t.toFixed(3)); }
      var m = elegir();
      if (m !== ultimo) { ultimo = m; activar(m); }
    }

    activar(0);
    (function mirar() { revisar(); requestAnimationFrame(mirar); })();
    window.addEventListener('scroll', revisar, { passive: true });
    window.addEventListener('resize', revisar);
    if ('IntersectionObserver' in window) {
      var ioG = new IntersectionObserver(function () { revisar(); },
        { rootMargin: '-22% 0px -70% 0px', threshold: [0, .05, .2, .5, 1] });
      pasos.forEach(function (p) { ioG.observe(p); });
    }
  })();

  /* ---------------- TITULARES CON LUZ ---------------- */
  // El efecto de la marca del footer, en el hero y en todos los títulos:
  // cada letra se enciende con relieve según lo cerca que pase el cursor.
  (function luces() {
    if (/[?&]edit=1/.test(location.search)) return;   // el editor necesita el texto entero
    var objetivos = $$('.hero h1, .sec-h2, .works h2, .contact h2, .grande-card h3, .svc-paso h3, .foot-mark');
    if (!objetivos.length) return;

    function partir(el) {
      if (el.classList.contains('lum')) return;
      var n = 0;
      function recorrer(nodo) {
        Array.prototype.slice.call(nodo.childNodes).forEach(function (nd) {
          if (nd.nodeType === 1) {
            if (nd.tagName !== 'BR' && !nd.classList.contains('l')) recorrer(nd);
            return;
          }
          if (nd.nodeType !== 3 || !nd.textContent.trim()) return;
          var frag = document.createDocumentFragment(), palabra = null;
          nd.textContent.split('').forEach(function (ch) {
            if (!ch.trim()) { palabra = null; frag.appendChild(document.createTextNode(ch)); return; }
            // las letras de una palabra van juntas para que no se parta en dos líneas
            if (!palabra) { palabra = document.createElement('span'); palabra.className = 'w'; frag.appendChild(palabra); }
            var s = document.createElement('span');
            s.className = 'l'; s.textContent = ch; s.setAttribute('data-l', ch);
            s.style.setProperty('--i', n++);
            palabra.appendChild(s);
          });
          nodo.replaceChild(frag, nd);
        });
      }
      recorrer(el);
      el.classList.add('lum');
      // texto oscuro sobre fondo claro → variante con copia negra y relieve claro
      var col = (getComputedStyle(el).color.match(/\d+/g) || [255, 255, 255]).map(Number);
      var lum = (0.2126 * col[0] + 0.7152 * col[1] + 0.0722 * col[2]) / 255;
      if (lum < 0.5) el.classList.add('lum-oscuro');
    }
    // siempre se leen del DOM: si otro script reescribe el título, las letras nuevas siguen respondiendo
    function letrasDe(el) { return Array.prototype.slice.call(el.querySelectorAll('.l')); }

    function apagar(el) {
      letrasDe(el).forEach(function (l) { l.style.setProperty('--lit', 0); });
      el._prendido = false;
    }

    function armar() {
      objetivos.forEach(partir);

      // barrido de luz cuando el título entra en pantalla (y el loader ya se fue)
      if ('IntersectionObserver' in window) {
        var iol = new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (!e.isIntersecting) return;
            var el = e.target; iol.unobserve(el);
            (function cuando() {
              if (document.body.classList.contains('locked')) { setTimeout(cuando, 250); return; }
              el.classList.add('barrido');
            })();
          });
        }, { threshold: .2 });
        objetivos.forEach(function (el) { iol.observe(el); });
      }

      if (!window.matchMedia('(hover:hover) and (pointer:fine)').matches) return;
      var px = -1e4, py = -1e4, pendiente = false;
      var vh = window.innerHeight || 800;
      function pintar() {
        pendiente = false;
        objetivos.forEach(function (el) {
          var r = el.getBoundingClientRect();
          if (r.bottom < 0 || r.top > vh) { if (el._prendido) apagar(el); return; }
          var margen = 90;
          var cerca = px > r.left - margen && px < r.right + margen && py > r.top - margen && py < r.bottom + margen;
          if (!cerca) { if (el._prendido) apagar(el); return; }
          el._prendido = true;
          var letras = letrasDe(el);
          for (var k = 0; k < letras.length; k++) {
            var b = letras[k].getBoundingClientRect();
            var cx = b.left + b.width / 2, cy = b.top + b.height / 2;
            var d = Math.hypot(px - cx, py - cy);
            var v = Math.max(0, 1 - d / (Math.max(b.width, b.height) * 1.5));
            v = v * v * (3 - 2 * v);
            letras[k].style.setProperty('--lit', v.toFixed(3));
          }
        });
      }
      document.addEventListener('pointermove', function (e) {
        if (e.pointerType && e.pointerType !== 'mouse') return;
        px = e.clientX; py = e.clientY;
        if (!pendiente) { pendiente = true; requestAnimationFrame(pintar); }
      }, { passive: true });
      document.documentElement.addEventListener('mouseleave', function () {
        px = py = -1e4; objetivos.forEach(function (el) { if (el._prendido) apagar(el); });
      });
      window.addEventListener('resize', function () { vh = window.innerHeight || 800; });
    }

    // después de load: el editor visual (editor.js) guarda el HTML base de cada
    // texto en DOMContentLoaded y tiene que verlo entero, sin las letras partidas
    function despues() { setTimeout(armar, 180); }
    if (document.readyState === 'complete') despues();
    else window.addEventListener('load', despues);
    // al cambiar de idioma el texto es otro: se parte de nuevo
    document.addEventListener('idioma', function () {
      objetivos.forEach(function (el) {
        if (!el.classList.contains('lum')) return;
        el.classList.remove('lum', 'lum-oscuro', 'barrido'); partir(el);
      });
    });
  })();

  /* ---------------- CURSOR PROPIO ---------------- */
  (function cursor() {
    if (!window.matchMedia('(hover:hover) and (pointer:fine)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (/[?&]edit=1/.test(location.search)) return;
    var root = document.documentElement;
    var dot = document.createElement('div'); dot.className = 'cur-dot';
    var ring = document.createElement('div'); ring.className = 'cur-ring';
    ring.setAttribute('data-txt', 'Ver');
    document.addEventListener('idioma', function (e) { ring.setAttribute('data-txt', (e.detail && e.detail.gen && e.detail.gen['Ver']) || 'Ver'); });
    document.body.appendChild(dot); document.body.appendChild(ring);

    var x = -100, y = -100, rx = -100, ry = -100, vivo = false, tipoActual = '';
    function tipo(el) {
      if (!el || !el.closest) return '';
      if (el.closest('input, textarea, select, [contenteditable="true"]')) return 'campo';
      if (el.closest('.grid figure, .shot, .grande-grilla figure, .marquee figure')) return 'ver';
      if (el.closest('a, button, [role="button"], label, summary')) return 'link';
      if (el.closest('h1, h2, h3, h4, p, blockquote, li, .mono, .foot-mark')) return 'text';
      return '';
    }
    function marcar(t) {
      if (t === tipoActual) return;
      tipoActual = t;
      root.classList.toggle('cur-campo', t === 'campo');
      root.classList.toggle('cur-ver', t === 'ver');
      root.classList.toggle('cur-link', t === 'link');
      root.classList.toggle('cur-text', t === 'text');
    }
    document.addEventListener('pointermove', function (e) {
      if (e.pointerType && e.pointerType !== 'mouse') return;
      x = e.clientX; y = e.clientY;
      if (!vivo) { vivo = true; rx = x; ry = y; root.classList.add('cur'); }
      root.classList.remove('cur-out');
      marcar(tipo(e.target));
    }, { passive: true });
    document.addEventListener('pointerdown', function () { root.classList.add('cur-down'); });
    document.addEventListener('pointerup', function () { root.classList.remove('cur-down'); });
    root.addEventListener('mouseleave', function () { root.classList.add('cur-out'); });
    window.addEventListener('blur', function () { root.classList.add('cur-out'); });

    (function seguir() {
      rx += (x - rx) * .18; ry += (y - ry) * .18;
      dot.style.setProperty('--x', x + 'px'); dot.style.setProperty('--y', y + 'px');
      ring.style.setProperty('--rx', rx.toFixed(1) + 'px'); ring.style.setProperty('--ry', ry.toFixed(1) + 'px');
      requestAnimationFrame(seguir);
    })();
  })();

  /* ---------------- GRILLA DE EN GRANDE: se abre en grande ---------------- */
  (function grillaGrande() {
    var figs = $$('.grande-grilla figure');
    if (!figs.length) return;
    var set = figs.map(function (f) {
      var im = f.querySelector('img'), cap = f.querySelector('figcaption');
      return { web: im ? im.getAttribute('src') : '', cap: cap ? cap.textContent : 'En grande' };
    });
    figs.forEach(function (f, k) {
      f.tabIndex = 0; f.setAttribute('role', 'button'); f.setAttribute('aria-label', 'Ver ' + set[k].cap);
      f.addEventListener('click', function () { openLB(set, k, 'En grande'); });
      f.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLB(set, k, 'En grande'); }
      });
    });
  })();

  /* ---------------- CARTEL DEL FOOTER: el video entra cuando se acerca ---------------- */
  (function cartel() {
    var caja = $('.foot-bg'); if (!caja) return;
    var v = caja.querySelector('video'); if (!v || !v.dataset.src) return;
    var hecho = false;
    function encender() {
      if (hecho) return; hecho = true;
      v.muted = true; v.defaultMuted = true; v.playsInline = true;
      var pc = window.matchMedia('(min-width:761px)').matches;
      v.src = (pc && v.dataset.srcPc) ? v.dataset.srcPc : v.dataset.src;
      v.addEventListener('canplay', function () {
        var pr = v.play();
        if (pr && pr.then) pr.then(function () { v.classList.add('on'); }).catch(function () {});
        else v.classList.add('on');
      }, { once: true });
      v.load();
    }
    if ('IntersectionObserver' in window) {
      var ioc = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { encender(); ioc.disconnect(); } });
      }, { rootMargin: '600px 0px' });
      ioc.observe(caja);
    } else { encender(); }
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
      var set = lista.map(function (p) { return { web: p.web, cap: 'Más trabajo' }; });
      for (var vuelta = 0; vuelta < 2; vuelta++) {
        lista.forEach(function (p, k) {
          var f = document.createElement('figure');
          var i = document.createElement('img');
          i.loading = 'lazy'; i.decoding = 'async';
          i.src = p.thumb; i.alt = '';
          if (p.foco) i.style.objectPosition = p.foco;
          f.appendChild(i); frag.appendChild(f);
          // "Ver": se abre en grande como en la galería
          f.tabIndex = 0; f.setAttribute('role', 'button'); f.setAttribute('aria-label', 'Ver foto');
          f.addEventListener('click', function () { openLB(set, k, 'Más trabajo'); });
          f.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLB(set, k, 'Más trabajo'); }
          });
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
