/* =========================================================
   AGENTE DE CONTACTO — Apardian Studio
   Toma el pedido, arma el brief y lo entrega por WhatsApp
   con todo escrito. Atención personalizada aparte, en el
   segundo botón del dock.
   ========================================================= */
(function () {
  'use strict';
  var WA = '59891962962';
  var $ = function (s, c) { return (c || document).querySelector(s); };

  var brief = { servicio: '', tipo: '', fecha: '', lugar: '', nombre: '' };
  var step = 0;

  var PASOS = [
    { key: 'servicio', q: '¿Qué necesitás?', chips: ['Fotografía', 'Video', 'Foto y video', 'Página web'] },
    { key: 'tipo', q: '¿De qué se trata?', chips: ['Casamiento', 'Cumpleaños', 'Evento de empresa', 'Gastronomía o producto', 'Retrato o marca personal', 'Otra cosa'] },
    { key: 'fecha', q: '¿Para cuándo?', chips: ['Este mes', 'El mes que viene', 'Más adelante', 'Todavía no sé'] },
    { key: 'lugar', q: '¿Dónde sería?', chips: ['Montevideo', 'Canelones', 'Punta del Este', 'Otro lugar del país'] },
    { key: 'nombre', q: 'Por último, ¿cómo te llamás?', chips: [] }
  ];

  var panel, log, chips, form, input;

  function build() {
    panel = document.createElement('div');
    panel.className = 'ai-panel';
    panel.innerHTML =
      '<div class="ai-head">' +
        '<div><b>Agente Apardian</b><small>Responde al toque</small></div>' +
        '<button class="ai-close" id="aiX" aria-label="Cerrar">×</button>' +
      '</div>' +
      '<div class="ai-log" id="aiLog" aria-live="polite"></div>' +
      '<div class="ai-chips" id="aiChips"></div>' +
      '<form class="ai-form" id="aiForm">' +
        '<input id="aiIn" placeholder="Escribí acá..." autocomplete="off">' +
        '<button type="submit">Enviar</button>' +
      '</form>';
    document.body.appendChild(panel);
    log = $('#aiLog'); chips = $('#aiChips'); form = $('#aiForm'); input = $('#aiIn');

    $('#aiX').addEventListener('click', close);
    form.addEventListener('submit', function (e) { e.preventDefault(); var v = input.value.trim(); if (v) { say(v, 'me'); input.value = ''; handle(v); } });

    var btn = $('#dockAi');
    if (btn) btn.addEventListener('click', function () { panel.classList.contains('on') ? close() : open(); });
  }

  function open() {
    panel.classList.add('on');
    if (!log.children.length) {
      bot('Hola. Soy el agente de Apardian Studio.');
      setTimeout(function () { bot('Te hago cuatro preguntas cortas y te armo el pedido listo para que Martin lo vea. Tarda menos de un minuto.'); setTimeout(ask, 500); }, 500);
    }
    setTimeout(function () { input.focus(); }, 250);
  }
  function close() { panel.classList.remove('on'); }

  function say(txt, who) {
    var d = document.createElement('div');
    d.className = 'ai-msg ' + (who || 'bot');
    d.textContent = txt;
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
  }
  function bot(t) { say(t, 'bot'); }

  function ask() {
    var p = PASOS[step];
    if (!p) { finish(); return; }
    bot(p.q);
    chips.innerHTML = '';
    p.chips.forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = c;
      b.addEventListener('click', function () { say(c, 'me'); handle(c); });
      chips.appendChild(b);
    });
  }

  function handle(txt) {
    var low = txt.toLowerCase();

    // preguntas sueltas que puede hacer cualquiera en cualquier momento
    if (/precio|cuesta|cuánto|cuanto|presupuesto|tarifa/.test(low)) {
      bot('Cada trabajo se cotiza a medida, porque cambia mucho según las horas, el lugar y qué material querés recibir. Terminá estas preguntas y Martin te pasa el número exacto en menos de 24 horas.');
      return setTimeout(ask, 400);
    }
    if (/cuándo|cuanto tarda|demora|entrega|plazo/.test(low)) {
      bot('La propuesta te llega dentro de las 24 horas. La entrega del material depende del trabajo y queda escrita en el presupuesto.');
      return setTimeout(ask, 400);
    }
    if (/idioma|inglés|ingles|portugu/.test(low)) {
      bot('Martin trabaja en español, inglés y portugués.');
      return setTimeout(ask, 400);
    }
    if (/persona|humano|hablar con|martin/.test(low)) {
      bot('Dale. Tocá el botón verde de WhatsApp y hablás directo con él, sin intermediarios.');
      return;
    }

    var p = PASOS[step];
    if (p) { brief[p.key] = txt; step++; setTimeout(ask, 350); }
  }

  function finish() {
    chips.innerHTML = '';
    var resumen =
      'Hola Martin, soy ' + (brief.nombre || 'una persona que entró a tu web') + '.\n' +
      'Necesito: ' + brief.servicio + '\n' +
      'Tipo: ' + brief.tipo + '\n' +
      'Fecha: ' + brief.fecha + '\n' +
      'Lugar: ' + brief.lugar;

    bot('Listo. Esto es lo que le voy a pasar a Martin:');
    say(resumen, 'bot');
    bot('Tocá el botón y se abre WhatsApp con todo escrito. Solo tenés que apretar enviar.');

    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = 'Enviar por WhatsApp →';
    b.style.cssText = 'background:#25D366;border-color:#25D366;color:#0A2E17;font-weight:600';
    b.addEventListener('click', function () {
      window.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(resumen), '_blank', 'noopener');
    });
    chips.appendChild(b);

    var r = document.createElement('button');
    r.type = 'button'; r.textContent = 'Empezar de nuevo';
    r.addEventListener('click', function () {
      brief = { servicio: '', tipo: '', fecha: '', lugar: '', nombre: '' };
      step = 0; log.innerHTML = ''; chips.innerHTML = ''; open();
    });
    chips.appendChild(r);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
