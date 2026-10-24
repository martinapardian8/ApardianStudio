/* =========================================================
   APARDIAN — formulario de la página de propuesta
   No manda nada a ningún servidor: arma el mensaje y abre WhatsApp
   con el texto listo, en el idioma que esté elegido.
   ========================================================= */
(function () {
  'use strict';
  var form = document.getElementById('prpForm');
  if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var TEXTOS = {
    es: { hola: 'Hola Martin, quiero una propuesta.', nombre: 'Soy', negocio: 'Negocio', web: 'Web o Instagram', servicio: 'Me interesa', mensaje: 'Lo que necesito' },
    en: { hola: 'Hi Martin, I would like a proposal.', nombre: 'I am', negocio: 'Business', web: 'Website or Instagram', servicio: 'Interested in', mensaje: 'What I need' },
    pt: { hola: 'Olá Martin, quero uma proposta.', nombre: 'Sou', negocio: 'Negócio', web: 'Site ou Instagram', servicio: 'Tenho interesse em', mensaje: 'O que eu preciso' }
  };
  function idioma() {
    var l = (document.documentElement.lang || 'es').slice(0, 2);
    return TEXTOS[l] ? l : 'es';
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var nombre = $('prp-nombre').value.trim(), mensaje = $('prp-mensaje').value.trim();
    var error = $('prp-error');
    if (!nombre || !mensaje) {
      error.hidden = false;
      (nombre ? $('prp-mensaje') : $('prp-nombre')).focus();
      return;
    }
    error.hidden = true;
    var t = TEXTOS[idioma()];
    var sel = $('prp-servicio');
    var servicio = sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].textContent.trim() : '';
    var lineas = [t.hola, t.nombre + ': ' + nombre];
    var negocio = $('prp-negocio').value.trim(), web = $('prp-web').value.trim();
    if (negocio) lineas.push(t.negocio + ': ' + negocio);
    if (web) lineas.push(t.web + ': ' + web);
    if (servicio) lineas.push(t.servicio + ': ' + servicio);
    lineas.push(t.mensaje + ': ' + mensaje);
    var url = 'https://wa.me/59891962962?text=' + encodeURIComponent(lineas.join('\n'));
    // un link real, abierto por el clic de la persona: no lo bloquea ningún navegador
    var a = document.createElement('a');
    a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer';
    document.body.appendChild(a); a.click(); a.remove();
  });
})();
