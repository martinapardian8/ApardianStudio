/* =========================================================
   EDITOR VISUAL — Apardian Studio
   Textos, bloques arrastrables, redimensionado, reemplazo de
   imágenes con previsualización, estilo y exportación.
   Se activa agregando ?edit=1 a la dirección.
   ========================================================= */
(function () {
  'use strict';

  var KEY = 'apardian.overrides.v1';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------- almacén ---------------- */
  var OV = load();
  function blank() { return { text: {}, img: {}, order: {}, size: {}, hidden: {}, style: {}, pos: {}, add: {} }; }
  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return blank();
      var o = JSON.parse(raw), b = blank();
      Object.keys(b).forEach(function (k) { if (o[k] && typeof o[k] === 'object') b[k] = o[k]; });
      return b;
    } catch (e) { return blank(); }
  }
  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(OV)); return true; }
    catch (e) { return false; }
  }

  /* ---------------- historial ---------------- */
  var past = [], future = [];
  function snapshot() { past.push(JSON.stringify(OV)); if (past.length > 60) past.shift(); future.length = 0; refreshBar(); }
  function undo() { if (!past.length) return; future.push(JSON.stringify(OV)); OV = JSON.parse(past.pop()); afterChange(); }
  function redo() { if (!future.length) return; past.push(JSON.stringify(OV)); OV = JSON.parse(future.pop()); afterChange(); }
  function afterChange() { applyAll(); persist(); refreshBar(); flag('Cambios guardados', true); }

  /* ---------------- aplicar overrides ---------------- */
  function stampOriginals(root) {
    $$('img[src], video[src]', root || document).forEach(function (el) {
      if (!el.dataset.orig) el.dataset.orig = el.getAttribute('src') || '';
    });
  }

  function applyText() {
    $$('[data-ed]').forEach(function (el) {
      var k = el.dataset.ed;
      if (!el.dataset.base) el.dataset.base = el.innerHTML;
      el.innerHTML = (k in OV.text) ? OV.text[k] : el.dataset.base;
    });
  }

  function applyImg(root) {
    stampOriginals(root);
    $$('img[data-orig], video[data-orig]', root || document).forEach(function (el) {
      var o = el.dataset.orig;
      if (!o) return;
      var want = OV.img[o];
      var cur = el.getAttribute('src');
      if (want && cur !== want) el.setAttribute('src', want);
      else if (!want && cur !== o) el.setAttribute('src', o);
    });
  }

  function applySize(root) {
    $$('#galgrid figure', root || document).forEach(function (f) {
      var im = f.querySelector('img,video');
      var k = im && im.dataset.orig;
      if (!k) return;
      var want = OV.size[k];
      f.classList.remove('wide', 'tall');
      if (want === 'wide' || want === 'tall') f.classList.add(want);
      else if (want !== 'normal' && f.dataset.baseShape) f.classList.add(f.dataset.baseShape);
    });
  }

  function applyOrderSections() {
    var order = OV.order.sections;
    if (!order || !order.length) return;
    var map = {};
    $$('[data-sec]').forEach(function (s) { map[s.dataset.sec] = s; });
    var first = $$('[data-sec]')[0];
    if (!first) return;
    var parent = first.parentNode, anchor = first;
    order.forEach(function (id) {
      var el = map[id];
      if (el) { parent.insertBefore(el, anchor); anchor = el.nextSibling; }
    });
  }

  function applyHidden() {
    $$('[data-sec]').forEach(function (s) {
      s.classList.toggle('ed-hidden', !!OV.hidden[s.dataset.sec]);
      if (!EDIT) s.style.display = OV.hidden[s.dataset.sec] ? 'none' : '';
    });
  }

  function applyOrderGrid() {
    var grid = $('#galgrid'); if (!grid) return;
    var cat = currentCat(); if (!cat) return;
    var order = OV.order['gal:' + cat];
    if (!order || !order.length) return;
    var figs = $$('#galgrid figure');
    var map = {};
    figs.forEach(function (f) { var im = f.querySelector('img,video'); if (im && im.dataset.orig) map[im.dataset.orig] = f; });
    order.forEach(function (k) { if (map[k]) grid.appendChild(map[k]); });
    figs.forEach(function (f) { if (f.parentNode === grid) grid.appendChild(f); });
  }

  function applyPos() {
    $$('[data-ed]').forEach(function (el) {
      var p = OV.pos[el.dataset.ed];
      if (!p) {
        el.style.transform = ''; el.style.width = ''; el.style.fontSize = '';
        el.classList.remove('ed-moved');
        return;
      }
      el.style.transform = 'translate(' + (p.x || 0) + 'px,' + (p.y || 0) + 'px)';
      if (p.w) el.style.width = p.w + 'px';
      if (p.s && p.s !== 1) {
        if (!el.dataset.baseFs) {
          el.dataset.baseFs = parseFloat(getComputedStyle(el).fontSize) || 16;
        }
        el.style.fontSize = (parseFloat(el.dataset.baseFs) * p.s).toFixed(2) + 'px';
      }
      el.classList.add('ed-moved');
    });
  }

  function applyStyle() {
    var r = document.documentElement;
    if (OV.style.accent) r.style.setProperty('--red', OV.style.accent);
    else r.style.removeProperty('--red');
    if (OV.style.fs) document.body.style.fontSize = OV.style.fs + 'px';
    else document.body.style.fontSize = '';
    if (OV.style.pad) r.style.setProperty('--pad', OV.style.pad + 'px');
    else r.style.removeProperty('--pad');
  }

  // fotos que sumó el usuario desde el editor
  function applyAdd() {
    var grid = $('#galgrid'); if (!grid) return;
    var cat = currentCat(); if (!cat) return;
    var extra = OV.add[cat] || [];
    $$('#galgrid figure.ed-added').forEach(function (f) { f.remove(); });
    extra.forEach(function (p, i) {
      var f = document.createElement('figure');
      f.className = 'ed-added';
      if (p.shape) f.classList.add(p.shape);
      var im = document.createElement('img');
      im.loading = 'lazy'; im.decoding = 'async';
      im.src = p.thumb; im.alt = ''; im.dataset.orig = 'add:' + cat + ':' + i;
      f.appendChild(im);
      f.addEventListener('click', function () { openLB([{ web: p.web, cap: 'Agregada' }], 0); });
      grid.appendChild(f);
    });
    if (EDIT) decorate();
  }

  function currentCat() {
    var btns = $$('#galnav button');
    for (var i = 0; i < btns.length; i++) if (btns[i].classList.contains('on')) {
      var d = window.SITE_DATA && SITE_DATA.categories[i];
      return d ? d.key : null;
    }
    return null;
  }

  function applyAll() {
    applyText(); applyImg(); applySize(); applyOrderSections();
    applyHidden(); applyOrderGrid(); applyStyle(); applyPos(); applyAdd();
    if (EDIT) decorate();
  }

  /* ---------------- modo edición ---------------- */
  var EDIT = /[?&]edit=1/.test(location.search);

  // El sitio público también respeta lo guardado
  if (!EDIT) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bootPublic);
    else bootPublic();
    return;
  }
  function bootPublic() { setTimeout(applyAll, 60); watchGrid(); }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  function boot() {
    // saltear el loader en modo edición
    var ld = $('#loader');
    if (ld) { var b = $('#enter'); if (b) b.click(); setTimeout(function () { if (ld.parentNode) ld.parentNode.removeChild(ld); }, 100); }
    document.body.classList.remove('locked');
    document.body.classList.add('ed-on');

    buildBar(); buildSide(); buildModal();
    setTimeout(function () { applyAll(); watchGrid(); }, 200);
  }

  function watchGrid() {
    var grid = $('#galgrid'); if (!grid || !window.MutationObserver) return;
    var mo = new MutationObserver(function () {
      $$('#galgrid figure').forEach(function (f) {
        if (!f.dataset.baseShape) f.dataset.baseShape = f.classList.contains('wide') ? 'wide' : (f.classList.contains('tall') ? 'tall' : '');
      });
      applyImg(grid); applySize(grid); applyOrderGrid();
      if (EDIT) decorate();
    });
    mo.observe(grid, { childList: true });
  }

  /* ---------------- barra superior ---------------- */
  var bar, statusEl, btnUndo, btnRedo;
  function buildBar() {
    bar = document.createElement('div');
    bar.className = 'ed-bar';
    bar.innerHTML =
      '<span class="brand">Apardian<i>.</i> Editor</span>' +
      '<span class="ed-sep"></span>' +
      '<button class="ed-btn" data-dev="desktop">Escritorio</button>' +
      '<button class="ed-btn" data-dev="tablet">Tablet</button>' +
      '<button class="ed-btn" data-dev="mobile">Móvil</button>' +
      '<span class="ed-sep"></span>' +
      '<button class="ed-btn" id="edModo">✥ Mover bloques</button>' +
      '<button class="ed-btn" id="edAddFoto">+ Foto</button>' +
      '<span class="ed-sep"></span>' +
      '<button class="ed-btn" id="edUndo">↶ Deshacer</button>' +
      '<button class="ed-btn" id="edRedo">↷ Rehacer</button>' +
      '<span class="ed-spacer"></span>' +
      '<span class="ed-status" id="edStatus">Listo para editar</span>' +
      '<button class="ed-btn" id="edPanel">Panel</button>' +
      '<button class="ed-btn" id="edExport">Exportar</button>' +
      '<button class="ed-btn" id="edImport">Importar</button>' +
      '<button class="ed-btn go" id="edSave">Guardar</button>' +
      '<button class="ed-btn" id="edExit">Salir</button>';
    document.body.insertBefore(bar, document.body.firstChild);
    statusEl = $('#edStatus'); btnUndo = $('#edUndo'); btnRedo = $('#edRedo');

    // Vista de dispositivo: se muestra el sitio dentro de un marco del ancho real.
    // Un iframe tiene su propio viewport, así que el diseño responde de verdad.
    var MEDIDAS = { tablet: [834, 1112, 'Tablet'], mobile: [390, 844, 'Móvil'] };
    function verEn(d) {
      var prev = $('#edPreview');
      if (prev) prev.remove();
      document.body.classList.remove('ed-preview-on');
      if (d === 'desktop') return;
      var m = MEDIDAS[d];
      var wrap = document.createElement('div');
      wrap.id = 'edPreview';
      wrap.className = 'ed-preview';
      wrap.innerHTML =
        '<div class="ed-phone" style="width:' + m[0] + 'px;height:' + m[1] + 'px">' +
          '<iframe src="index.html" title="Vista ' + m[2] + '"></iframe>' +
        '</div>' +
        '<div class="ed-preview-tip">' + m[2] + ' · ' + m[0] + ' x ' + m[1] +
          ' — la web real, en su ancho. Para editar, volvé a Escritorio.</div>';
      document.body.appendChild(wrap);
      document.body.classList.add('ed-preview-on');
    }

    $$('[data-dev]', bar).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('[data-dev]', bar).forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        verEn(b.dataset.dev);
      });
    });
    $$('[data-dev]', bar)[0].classList.add('on');

    // Modo mover: los bloques se arrastran y se estiran en vez de editarse
    var btnModo = $('#edModo');
    btnModo.addEventListener('click', function () {
      MOVER = !MOVER;
      btnModo.classList.toggle('on', MOVER);
      document.body.classList.toggle('ed-mover', MOVER);
      btnModo.textContent = MOVER ? '✥ Moviendo' : '✥ Mover bloques';
      flag(MOVER ? 'Arrastrá los bloques. La esquina los estira.' : 'Volviste a editar texto', true);
      decorate();
    });

    $('#edAddFoto').addEventListener('click', function () {
      if (!currentCat()) { flag('Abrí primero una sección de la galería'); return; }
      openImageModal(null, true);
    });

    btnUndo.addEventListener('click', undo);
    btnRedo.addEventListener('click', redo);
    $('#edPanel').addEventListener('click', function () {
      var s = $('.ed-side');
      s.classList.toggle('on');
      document.body.classList.toggle('ed-side-on', s.classList.contains('on'));
    });
    $('#edSave').addEventListener('click', function () {
      flag(persist() ? 'Guardado en este navegador' : 'No se pudo guardar', true);
    });
    $('#edExport').addEventListener('click', exportJSON);
    $('#edImport').addEventListener('click', importJSON);
    $('#edExit').addEventListener('click', function () {
      persist(); location.href = location.pathname;
    });

    document.addEventListener('keydown', function (e) {
      var mod = e.metaKey || e.ctrlKey;
      if (!mod) return;
      if (e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
      if (e.key === 'z' && e.shiftKey) { e.preventDefault(); redo(); }
      if (e.key === 's') { e.preventDefault(); persist(); flag('Guardado', true); }
    });
    refreshBar();
  }
  function refreshBar() {
    if (!btnUndo) return;
    btnUndo.disabled = !past.length;
    btnRedo.disabled = !future.length;
  }
  var flagT;
  function flag(msg, ok) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.classList.toggle('ok', !!ok);
    clearTimeout(flagT);
    flagT = setTimeout(function () { statusEl.textContent = 'Listo para editar'; statusEl.classList.remove('ok'); }, 2600);
  }

  /* ---------------- panel lateral ---------------- */
  function buildSide() {
    var side = document.createElement('aside');
    side.className = 'ed-side on';
    document.body.classList.add('ed-side-on');
    side.innerHTML =
      '<h3>Cómo se edita</h3>' +
      '<p class="hint"><b>Textos.</b> Clic encima y escribís. Se guarda solo.</p>' +
      '<p class="hint"><b>Fotos.</b> Pasá el mouse por una y aparecen tres botones: cambiarla, cambiar su tamaño, o sacarla. Arrastrándolas se reordenan. El botón <b>+ Foto</b> de arriba suma una nueva a la sección abierta, del archivo o de tu computadora.</p>' +
      '<p class="hint"><b>Mover bloques.</b> El botón <b>✥ Mover bloques</b> cambia el modo: los textos se arrastran a donde quieras y el cuadradito verde de la esquina los estira. Doble clic sobre un bloque lo devuelve a su lugar, doble clic en el cuadradito le devuelve el tamaño.</p>' +
      '<p class="hint"><b>Vistas.</b> Tablet y Móvil abren la web en el ancho real de cada pantalla.</p>' +

      '<div class="ed-group"><span class="ed-label">Secciones · arrastrá para ordenar</span>' +
      '<ul class="ed-sec-list" id="edSecs"></ul></div>' +

      '<div class="ed-group"><span class="ed-label">Color de acento</span>' +
      '<div class="ed-row"><input type="color" id="edAccent" value="#FF0033"><output id="edAccentV">#FF0033</output>' +
      '<button class="ed-btn" id="edAccentR" style="padding:5px 9px">Reset</button></div></div>' +

      '<div class="ed-group"><span class="ed-label">Tamaño de texto</span>' +
      '<div class="ed-row"><input type="range" id="edFs" min="14" max="20" step="1" value="16"><output id="edFsV">16 px</output></div></div>' +

      '<div class="ed-group"><span class="ed-label">Aire lateral</span>' +
      '<div class="ed-row"><input type="range" id="edPad" min="16" max="120" step="4" value="72"><output id="edPadV">72 px</output></div></div>' +

      '<div class="ed-group"><span class="ed-label">Volver atrás</span>' +
      '<button class="ed-btn" id="edReset" style="width:100%">Descartar todos los cambios</button></div>';
    document.body.appendChild(side);

    buildSecList();

    var ac = $('#edAccent'), acv = $('#edAccentV');
    if (OV.style.accent) { ac.value = OV.style.accent; acv.textContent = OV.style.accent; }
    ac.addEventListener('input', function () { acv.textContent = ac.value; OV.style.accent = ac.value; applyStyle(); });
    ac.addEventListener('change', function () { snapshot(); persist(); });
    $('#edAccentR').addEventListener('click', function () {
      snapshot(); delete OV.style.accent; ac.value = '#FF0033'; acv.textContent = '#FF0033'; afterChange();
    });

    bindRange('#edFs', '#edFsV', 'fs', ' px', 16);
    bindRange('#edPad', '#edPadV', 'pad', ' px', 72);

    $('#edReset').addEventListener('click', function () {
      if (!confirm('Esto borra todos los cambios que hiciste y deja la web como estaba. ¿Seguimos?')) return;
      snapshot(); OV = blank(); afterChange(); buildSecList();
    });
  }

  function bindRange(sel, outSel, key, unit, def) {
    var r = $(sel), o = $(outSel);
    if (OV.style[key]) r.value = OV.style[key];
    o.textContent = r.value + unit;
    r.addEventListener('input', function () { o.textContent = r.value + unit; OV.style[key] = +r.value; applyStyle(); });
    r.addEventListener('change', function () { snapshot(); persist(); });
  }

  function buildSecList() {
    var ul = $('#edSecs'); if (!ul) return;
    ul.innerHTML = '';
    $$('[data-sec]').forEach(function (sec) {
      var id = sec.dataset.sec;
      var li = document.createElement('li');
      li.draggable = true; li.dataset.sec = id;
      li.classList.toggle('off', !!OV.hidden[id]);
      li.innerHTML = '<span class="grip">⠿</span><span>' + sec.dataset.secName + '</span>' +
        '<button title="Mostrar u ocultar">' + (OV.hidden[id] ? '☒' : '☑') + '</button>';
      li.querySelector('button').addEventListener('click', function (e) {
        e.stopPropagation(); snapshot();
        if (OV.hidden[id]) delete OV.hidden[id]; else OV.hidden[id] = true;
        afterChange(); buildSecList();
      });
      li.addEventListener('dragstart', function () { li.classList.add('drag'); dragLi = li; });
      li.addEventListener('dragend', function () { li.classList.remove('drag'); commitSecOrder(); });
      li.addEventListener('dragover', function (e) {
        e.preventDefault();
        if (!dragLi || dragLi === li) return;
        var r = li.getBoundingClientRect();
        ul.insertBefore(dragLi, (e.clientY - r.top) / r.height > .5 ? li.nextSibling : li);
      });
      ul.appendChild(li);
    });
  }
  var dragLi = null;
  var MOVER = false;
  function commitSecOrder() {
    snapshot();
    OV.order.sections = $$('#edSecs li').map(function (li) { return li.dataset.sec; });
    afterChange();
  }

  /* ---------------- decorar piezas editables ---------------- */
  function decorate() {
    $$('[data-ed]').forEach(function (el) {
      if (!el.dataset.wired) {
        el.dataset.wired = '1';
        el.addEventListener('click', function (e) {
          if (MOVER || el.isContentEditable) return;
          e.preventDefault(); e.stopPropagation();
          startEdit(el);
        });
        armarMover(el);
      }
      // el tirador de esquina solo existe en modo mover
      var tir = el.querySelector(':scope > .ed-grip');
      if (MOVER && !tir) {
        tir = document.createElement('span');
        tir.className = 'ed-grip';
        tir.title = 'Arrastrá para estirar. Doble clic vuelve al tamaño original.';
        el.appendChild(tir);
        armarEstirar(el, tir);
      } else if (!MOVER && tir) { tir.remove(); }
    });

    $$('#galgrid figure, .rail .card').forEach(function (item) {
      if (item.dataset.wired) return;
      item.dataset.wired = '1';
      var im = item.querySelector('img,video');
      if (!im) return;
      if (!item.dataset.baseShape) item.dataset.baseShape = item.classList.contains('wide') ? 'wide' : (item.classList.contains('tall') ? 'tall' : '');

      var host = item.classList.contains('card') ? item.querySelector('.shot') : item;
      var tools = document.createElement('div');
      tools.className = 'ed-tools';
      var isGrid = !item.classList.contains('card');
      tools.innerHTML =
        '<button title="Cambiar foto">🖼</button>' +
        (isGrid ? '<button title="Cambiar tamaño">⤢</button>' : '') +
        (isGrid ? '<button title="Quitar de la galería">✕</button>' : '');
      host.appendChild(tools);

      var bs = tools.querySelectorAll('button');
      bs[0].addEventListener('click', function (e) { e.stopPropagation(); openImageModal(im); });
      if (isGrid) {
        bs[1].addEventListener('click', function (e) {
          e.stopPropagation(); snapshot();
          var k = im.dataset.orig;
          var cyc = ['normal', 'wide', 'tall'];
          var cur = OV.size[k] || (item.dataset.baseShape || 'normal');
          OV.size[k] = cyc[(cyc.indexOf(cur) + 1) % cyc.length];
          afterChange();
        });
        bs[2].addEventListener('click', function (e) {
          e.stopPropagation(); snapshot();
          OV.hidden['img:' + im.dataset.orig] = true;
          item.style.display = 'none';
          afterChange();
        });
      }

      // arrastrar para reordenar dentro de la galería
      if (isGrid) {
        item.draggable = true;
        item.addEventListener('dragstart', function () { item.classList.add('drag'); dragFig = item; });
        item.addEventListener('dragend', function () { item.classList.remove('drag'); commitGridOrder(); });
        item.addEventListener('dragover', function (e) {
          e.preventDefault();
          if (!dragFig || dragFig === item) return;
          item.classList.add('over');
          var r = item.getBoundingClientRect();
          item.parentNode.insertBefore(dragFig, (e.clientX - r.left) / r.width > .5 ? item.nextSibling : item);
        });
        item.addEventListener('dragleave', function () { item.classList.remove('over'); });
      }
    });

    // ocultar los que el usuario quitó
    $$('#galgrid figure').forEach(function (f) {
      var im = f.querySelector('img,video');
      if (im && OV.hidden['img:' + im.dataset.orig]) f.style.display = 'none';
    });

    var heroImg = $('#heroimg');
    if (heroImg && !heroImg.dataset.wiredHero) {
      heroImg.dataset.wiredHero = '1';
      heroImg.style.cursor = 'pointer';
      heroImg.addEventListener('click', function () { openImageModal(heroImg); });
    }
  }
  /* ---------------- mover y estirar bloques ---------------- */
  function posDe(k) {
    if (!OV.pos[k]) OV.pos[k] = { x: 0, y: 0, w: 0, s: 1 };
    return OV.pos[k];
  }

  function armarMover(el) {
    var arr = false, x0, y0, px, py, k = el.dataset.ed, movido;
    el.addEventListener('pointerdown', function (e) {
      if (!MOVER || e.target.classList.contains('ed-grip')) return;
      e.preventDefault();
      var p = posDe(k);
      arr = true; movido = false;
      x0 = e.clientX; y0 = e.clientY; px = p.x || 0; py = p.y || 0;
      el.setPointerCapture(e.pointerId);
      el.classList.add('ed-dragging');
    });
    el.addEventListener('pointermove', function (e) {
      if (!arr) return;
      var dx = e.clientX - x0, dy = e.clientY - y0;
      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) movido = true;
      var p = posDe(k);
      p.x = Math.round(px + dx); p.y = Math.round(py + dy);
      el.style.transform = 'translate(' + p.x + 'px,' + p.y + 'px)';
      el.classList.add('ed-moved');
    });
    function soltar() {
      if (!arr) return;
      arr = false; el.classList.remove('ed-dragging');
      if (movido) { snapshot(); persist(); refreshBar(); flag('Bloque movido', true); }
    }
    el.addEventListener('pointerup', soltar);
    el.addEventListener('pointercancel', soltar);
    // doble clic: vuelve a su lugar
    el.addEventListener('dblclick', function (e) {
      if (!MOVER) return;
      e.preventDefault(); snapshot();
      delete OV.pos[k]; afterChange();
      flag('Bloque devuelto a su lugar', true);
    });
  }

  function armarEstirar(el, tir) {
    var arr = false, x0, y0, w0, s0, k = el.dataset.ed;
    tir.addEventListener('pointerdown', function (e) {
      e.preventDefault(); e.stopPropagation();
      var p = posDe(k);
      arr = true; x0 = e.clientX; y0 = e.clientY;
      w0 = p.w || Math.round(el.getBoundingClientRect().width);
      s0 = p.s || 1;
      if (!el.dataset.baseFs) el.dataset.baseFs = parseFloat(getComputedStyle(el).fontSize) || 16;
      tir.setPointerCapture(e.pointerId);
    });
    tir.addEventListener('pointermove', function (e) {
      if (!arr) return;
      var p = posDe(k);
      p.w = Math.max(80, Math.round(w0 + (e.clientX - x0)));
      // el alto controla el cuerpo de la tipografía
      p.s = Math.max(0.4, Math.min(4, +(s0 + (e.clientY - y0) / 260).toFixed(3)));
      el.style.width = p.w + 'px';
      el.style.fontSize = (parseFloat(el.dataset.baseFs) * p.s).toFixed(2) + 'px';
      el.classList.add('ed-moved');
    });
    function soltar() {
      if (!arr) return; arr = false;
      snapshot(); persist(); refreshBar(); flag('Tamaño guardado', true);
    }
    tir.addEventListener('pointerup', soltar);
    tir.addEventListener('pointercancel', soltar);
    tir.addEventListener('dblclick', function (e) {
      e.preventDefault(); e.stopPropagation(); snapshot();
      var p = posDe(k); p.w = 0; p.s = 1;
      el.style.width = ''; el.style.fontSize = '';
      afterChange(); flag('Tamaño original', true);
    });
  }

  var dragFig = null;
  function commitGridOrder() {
    var cat = currentCat(); if (!cat) return;
    snapshot();
    OV.order['gal:' + cat] = $$('#galgrid figure').map(function (f) {
      var im = f.querySelector('img,video'); return im ? im.dataset.orig : '';
    }).filter(Boolean);
    afterChange();
  }

  /* ---------------- edición de texto ---------------- */
  function startEdit(el) {
    el.contentEditable = 'true';
    el.classList.add('editing');
    el.focus();
    var sel = window.getSelection(), rng = document.createRange();
    rng.selectNodeContents(el); sel.removeAllRanges(); sel.addRange(rng);
    var before = el.innerHTML;

    function end(save) {
      el.contentEditable = 'false';
      el.classList.remove('editing');
      el.removeEventListener('blur', onBlur);
      el.removeEventListener('keydown', onKey);
      el.removeEventListener('input', onInput);
      clearTimeout(t);
      if (save && el.innerHTML !== before) {
        snapshot();
        var k = el.dataset.ed;
        if (el.innerHTML === el.dataset.base) delete OV.text[k];
        else OV.text[k] = el.innerHTML;
        persist(); refreshBar(); flag('Texto actualizado', true);
      } else if (!save) {
        el.innerHTML = before;
      }
    }
    function onBlur() { end(true); }
    // guardado automático mientras se escribe: no depende de perder el foco
    var t;
    function onInput() {
      clearTimeout(t);
      t = setTimeout(function () {
        var k = el.dataset.ed;
        if (el.innerHTML === el.dataset.base) delete OV.text[k];
        else OV.text[k] = el.innerHTML;
        persist(); flag('Guardado', true);
      }, 400);
    }
    el.addEventListener('input', onInput);
    function onKey(e) {
      if (e.key === 'Escape') { e.preventDefault(); end(false); el.blur(); }
      if (e.key === 'Enter' && !e.shiftKey && el.tagName !== 'P') { e.preventDefault(); end(true); el.blur(); }
    }
    el.addEventListener('blur', onBlur);
    el.addEventListener('keydown', onKey);
  }

  /* ---------------- modal de imagen ---------------- */
  var modal, target = null, chosen = null, chosenThumb = null, modoAgregar = false;
  function buildModal() {
    modal = document.createElement('div');
    modal.className = 'ed-modal';
    modal.innerHTML =
      '<div class="ed-box">' +
        '<header><b>Cambiar la foto</b><button class="ai-close" id="edmX">×</button></header>' +
        '<div class="body">' +
          '<div class="ed-compare">' +
            '<figure><div class="cap">Ahora</div><div class="frame"><img id="edmOld" alt=""></div></figure>' +
            '<figure><div class="cap new">Así va a quedar</div><div class="frame" id="edmNewFrame"><span class="empty">Elegí una foto abajo</span></div></figure>' +
          '</div>' +
          '<div class="ed-tabs">' +
            '<button class="on" data-tab="lib">Del archivo</button>' +
            '<button data-tab="up">Subir del disco</button>' +
          '</div>' +
          '<div id="edmLib" class="ed-lib"></div>' +
          '<div id="edmUp" style="display:none">' +
            '<div class="ed-drop" id="edmDrop">Arrastrá una foto acá o hacé clic para buscarla en tu computadora</div>' +
            '<input type="file" id="edmFile" accept="image/*" hidden>' +
          '</div>' +
        '</div>' +
        '<footer>' +
          '<button class="ed-btn" id="edmCancel">Cancelar</button>' +
          '<button class="ed-btn go" id="edmOk" disabled>Confirmar cambio</button>' +
        '</footer>' +
      '</div>';
    document.body.appendChild(modal);

    $('#edmX', modal).addEventListener('click', closeModal);
    $('#edmCancel', modal).addEventListener('click', closeModal);
    modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });

    $$('[data-tab]', modal).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('[data-tab]', modal).forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        $('#edmLib', modal).style.display = b.dataset.tab === 'lib' ? '' : 'none';
        $('#edmUp', modal).style.display = b.dataset.tab === 'up' ? '' : 'none';
      });
    });

    var drop = $('#edmDrop', modal), file = $('#edmFile', modal);
    drop.addEventListener('click', function () { file.click(); });
    file.addEventListener('change', function () { if (file.files[0]) readFile(file.files[0]); });
    ['dragenter', 'dragover'].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('hot'); });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('hot'); });
    });
    drop.addEventListener('drop', function (e) {
      var f = e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) readFile(f);
    });

    $('#edmOk', modal).addEventListener('click', function () {
      if (!chosen) return;
      snapshot();
      if (modoAgregar) {
        var cat = currentCat();
        if (!cat) { closeModal(); return; }
        if (!OV.add[cat]) OV.add[cat] = [];
        OV.add[cat].push({ web: chosen, thumb: chosenThumb || chosen, shape: '' });
        afterChange(); closeModal();
        flag('Foto agregada a la sección', true);
      } else {
        if (!target) return;
        OV.img[target.dataset.orig] = chosen;
        afterChange(); closeModal();
        flag('Foto reemplazada', true);
      }
    });
  }

  function readFile(f) {
    if (!/^image\//.test(f.type)) { alert('Ese archivo no es una imagen.'); return; }
    if (f.size > 6 * 1024 * 1024) {
      if (!confirm('La foto pesa ' + Math.round(f.size / 1048576) + ' MB. Va a hacer la web más lenta. ¿La usamos igual?')) return;
    }
    var r = new FileReader();
    r.onload = function () { setPreview(r.result); };
    r.readAsDataURL(f);
  }

  function setPreview(src, thumb) {
    chosen = src; chosenThumb = thumb || src;
    var fr = $('#edmNewFrame', modal);
    fr.innerHTML = '';
    var im = document.createElement('img');
    im.src = src; fr.appendChild(im);
    $('#edmOk', modal).disabled = false;
  }

  function library() {
    var out = [], seen = {};
    (window.SITE_DATA ? SITE_DATA.categories : []).forEach(function (c) {
      (c.photos || []).forEach(function (p) {
        if (p.video || seen[p.thumb]) return;
        seen[p.thumb] = 1; out.push({ thumb: p.thumb, full: p.web });
      });
    });
    (window.SITE_DATA ? SITE_DATA.works : []).forEach(function (w) {
      if (seen[w.thumb]) return; seen[w.thumb] = 1; out.push({ thumb: w.thumb, full: w.web });
    });
    return out;
  }

  function openImageModal(el, agregar) {
    modoAgregar = !!agregar;
    target = el; chosen = null; chosenThumb = null;
    var cab = modal.querySelector('header b');
    var vieja = modal.querySelector('.ed-compare figure:first-child');
    if (modoAgregar) {
      cab.textContent = 'Agregar una foto';
      if (vieja) vieja.style.display = 'none';
    } else {
      cab.textContent = 'Cambiar la foto';
      if (vieja) vieja.style.display = '';
    }
    if (el) {
      if (!el.dataset.orig) el.dataset.orig = el.getAttribute('src') || '';
      $('#edmOld', modal).src = el.getAttribute('src') || '';
    }
    $('#edmNewFrame', modal).innerHTML = '<span class="empty">Elegí una foto abajo</span>';
    $('#edmOk', modal).disabled = true;

    var lib = $('#edmLib', modal);
    lib.innerHTML = '';
    library().forEach(function (p) {
      var b = document.createElement('button');
      b.innerHTML = '<img loading="lazy" src="' + p.thumb + '" alt="">';
      b.addEventListener('click', function () {
        $$('button', lib).forEach(function (x) { x.classList.remove('sel'); });
        b.classList.add('sel');
        setPreview(p.full, p.thumb);
      });
      lib.appendChild(b);
    });
    modal.classList.add('on');
  }
  function closeModal() { modal.classList.remove('on'); target = null; chosen = null; chosenThumb = null; modoAgregar = false; }

  /* ---------------- exportar / importar ---------------- */
  function exportJSON() {
    var blob = new Blob([JSON.stringify(OV, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'apardian-cambios.json';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    flag('Archivo descargado', true);
  }
  function importJSON() {
    var i = document.createElement('input');
    i.type = 'file'; i.accept = 'application/json';
    i.addEventListener('change', function () {
      var f = i.files[0]; if (!f) return;
      var r = new FileReader();
      r.onload = function () {
        try {
          var o = JSON.parse(r.result);
          snapshot();
          var b = blank();
          Object.keys(b).forEach(function (k) { if (o[k] && typeof o[k] === 'object') b[k] = o[k]; });
          OV = b; afterChange(); buildSecList();
          flag('Cambios importados', true);
        } catch (e) { alert('Ese archivo no se pudo leer.'); }
      };
      r.readAsText(f);
    });
    i.click();
  }

})();
