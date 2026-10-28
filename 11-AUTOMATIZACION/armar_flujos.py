# -*- coding: utf-8 -*-
"""Arma los flujos de n8n de 11-AUTOMATIZACION/n8n a partir de los prompts.

Los textos que guian a cada agente viven en prompts/*.md. Si Martin edita uno,
corre este archivo y los JSON quedan al dia:

    python3 11-AUTOMATIZACION/armar_flujos.py

Despues, en n8n, se reimporta el flujo que cambio.
"""
import json, os, uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, "n8n")
# Modelos de la API de Claude (decisión de Martin, 27/10/2026): Haiku para lo
# simple y de mucho volumen (auditar webs, clasificar respuestas), Sonnet para
# lo que lee el cliente (mails, seguimientos, WhatsApp).
MODELO_RAPIDO = "claude-haiku-5-5"
MODELO_ESCRITURA = "claude-sonnet-5-5"


def prompt(nombre):
    with open(os.path.join(AQUI, "prompts", nombre + ".md"), encoding="utf-8") as f:
        return f.read().strip()


# ------------------------------------------------------------------ JS comun
JS_CLAUDE = r"""
function cuerpoClaude(system, user, maxTokens, effort, modelo) {
  const b = {
    model: modelo || '%s',
    max_tokens: maxTokens,
    system: system,
    messages: [{ role: 'user', content: user }],
    output_config: { effort: effort },
  };
  // Si un filtro de seguridad rechaza el pedido, Sonnet y Opus lo reintentan
  // solos con otro modelo; Haiku no tiene ese respaldo.
  if (!/haiku/.test(b.model)) b.fallbacks = 'default';
  return b;
}
const RAPIDO = '%s';
""" % (MODELO_ESCRITURA, MODELO_RAPIDO)

JS_LEER = r"""
// Lee la respuesta de Claude. Antes de tocar content mira stop_reason:
// un rechazo o un corte por max_tokens no se trata como respuesta valida.
// temporal = falla de red o de la API (429, 529, caída): se reintenta otro día.
function leerClaude(r) {
  if (!r || r.error) return { ok: false, temporal: true, motivo: 'error_http: ' + JSON.stringify(r && r.error || '').slice(0, 300) };
  if (r.stop_reason === 'refusal') return { ok: false, motivo: 'refusal' };
  if (r.stop_reason === 'max_tokens') return { ok: false, motivo: 'max_tokens' };
  const texto = (r.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
  const limpio = texto.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '');
  const i = limpio.indexOf('{'), j = limpio.lastIndexOf('}');
  if (i < 0 || j <= i) return { ok: false, motivo: 'sin_json' };
  try { return { ok: true, data: JSON.parse(limpio.slice(i, j + 1)) }; }
  catch (e) { return { ok: false, motivo: 'json_invalido' }; }
}
"""

# El idioma del destinatario manda en todo lo que le llega: el mail, la oferta,
# la firma, la línea de baja y la página de la propuesta (Martin, 28/10/2026).
JS_IDIOMA = r"""
const IDIOMA_PAIS = { 'Brasil': 'pt', 'Portugal': 'pt', 'Estados Unidos': 'en', 'Reino Unido': 'en',
  'Canadá': 'en', 'Australia': 'en', 'Irlanda': 'en', 'Países Bajos': 'en', 'Malta': 'en' };
const idiomaDe = l => { const i = String(l.idioma || '').trim().slice(0, 2).toLowerCase();
  return ['es', 'en', 'pt'].includes(i) ? i : (IDIOMA_PAIS[String(l.pais || '').trim()] || 'es'); };
const NOMBRE_IDIOMA = { es: 'español', en: 'inglés', pt: 'portugués' };
// la propuesta se abre en su idioma (propuesta.js lee ?lang=)
const linkPropuesta = i => 'https://apardianstudio.com/propuesta.html' + (i === 'es' ? '' : '?lang=' + i);
const lineaIdioma = l => { const i = idiomaDe(l);
  return '\nIDIOMA: ' + NOMBRE_IDIOMA[i] + ' (' + i + '). Todo lo que escribas va en este idioma, aunque los datos estén en español.' +
    '\nLINK DE LA PROPUESTA (usalo tal cual): ' + linkPropuesta(i); };
"""

# Una "web" que en realidad es Instagram, Facebook, Linktree o WhatsApp: no tiene web.
JS_REDES = r"""
const esRed = u => /(^|\/\/|\.)(instagram\.com|facebook\.com|fb\.com|fb\.me|linktr\.ee|wa\.me|api\.whatsapp\.com|tiktok\.com)(\/|$)/i.test(String(u || '').trim());
"""

JS_HTML = r"""
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
// La clave de Radar: tiene que estar cambiada (no la de ejemplo) y ser larga.
const claveOk = (t, clave) => !!t && !!clave && String(clave).length >= 24 && !/^CAMBIAR/.test(String(clave)) && String(t) === String(clave);
"""

JS_FECHA = r"""
// Fechas en Montevideo (AAAA-MM-DD), no en UTC.
const hoy = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Montevideo' }).format(new Date());
// Acepta AAAA-MM-DD y también DD/MM/AAAA (si alguien escribe una fecha a mano).
const aISO = f => { const t = String(f || '').trim(), m = t.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  return m ? m[3] + '-' + m[2].padStart(2, '0') + '-' + m[1].padStart(2, '0') : t.slice(0, 10); };
// Días enteros entre esa fecha y hoy. Sin fecha o ilegible: -1.
const diasDesde = f => { const d = Date.parse(aISO(f)); return f && !isNaN(d) ? Math.round((Date.parse(hoy()) - d) / 864e5) : -1; };
// FECHA_FIN (AAAA-MM-DD): último día de la prueba. Vacía = sin fin.
const terminoPrueba = c => /^\d{4}-\d{2}-\d{2}$/.test(String(c.FECHA_FIN || '')) && hoy() > c.FECHA_FIN;
"""


# ------------------------------------------------------------------ nodos
class Flujo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.nodos, self.con = [], {}
        self.x = 0

    def _id(self, nombre):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, "apardian/" + self.nombre + "/" + nombre))

    def nodo(self, nombre, tipo, version, params, pos=None, extra=None):
        assert nombre not in [n["name"] for n in self.nodos], nombre
        if pos is None:
            pos = (self.x, 0)
            self.x += 240
        n = {"parameters": params, "id": self._id(nombre), "name": nombre,
             "type": tipo, "typeVersion": version, "position": list(pos)}
        if extra:
            n.update(extra)
        self.nodos.append(n)
        return nombre

    def unir(self, a, b, salida=0):
        m = self.con.setdefault(a, {"main": []})["main"]
        while len(m) <= salida:
            m.append([])
        m[salida].append({"node": b, "type": "main", "index": 0})

    def cadena(self, *ns):
        for a, b in zip(ns, ns[1:]):
            self.unir(a, b)

    def json(self):
        return {"name": self.nombre, "nodes": self.nodos, "connections": self.con,
                "active": False, "pinData": {},
                "settings": {"executionOrder": "v1", "timezone": "America/Montevideo"},
                "meta": {"templateCredsSetupCompleted": False},
                "tags": []}

    def guardar(self, archivo):
        ruta = os.path.join(DEST, archivo)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.json(), f, ensure_ascii=False, indent=2)
        return ruta


def cred(tipo, nombre):
    return {tipo: {"id": "REEMPLAZAR", "name": nombre}}


# ---- constructores de nodos usados en todos los flujos
def config(fl, nombre, valores, pos=None):
    asig = []
    for k, (v, t) in valores.items():
        asig.append({"id": str(uuid.uuid5(uuid.NAMESPACE_URL, fl.nombre + nombre + k)),
                     "name": k, "value": v, "type": t})
    return fl.nodo(nombre, "n8n-nodes-base.set", 3.4,
                   {"assignments": {"assignments": asig}, "options": {}}, pos)


CONFIG_BASE = {
    "SHEET_ID": ("PEGAR_ID_DE_LA_PLANILLA", "string"),
    "TELEGRAM_CHAT_ID": ("PEGAR_CHAT_ID", "string"),
}


def codigo(fl, nombre, js, por_item=False, pos=None, extra=None):
    p = {"jsCode": js.strip() + "\n"}
    if por_item:
        p["mode"] = "runOnceForEachItem"
    return fl.nodo(nombre, "n8n-nodes-base.code", 2, p, pos, extra)


def hoja(cfg):
    return {"__rl": True, "value": "={{ $('%s').first().json.SHEET_ID }}" % cfg, "mode": "id"}


def leer_hoja(fl, nombre, cfg, pestana, pos=None):
    return fl.nodo(nombre, "n8n-nodes-base.googleSheets", 4.5, {
        "operation": "read",
        "documentId": hoja(cfg),
        "sheetName": {"__rl": True, "value": pestana, "mode": "name"},
        "options": {},
    }, pos, {"credentials": cred("googleSheetsOAuth2Api", "Google Sheets"),
             "executeOnce": True, "alwaysOutputData": True})


def escribir_hoja(fl, nombre, cfg, pestana, operacion="update", pos=None, clave="id"):
    p = {
        "operation": operacion,
        "documentId": hoja(cfg),
        "sheetName": {"__rl": True, "value": pestana, "mode": "name"},
        "columns": {"mappingMode": "autoMapInputData", "value": {},
                    "matchingColumns": [clave] if operacion in ("update", "appendOrUpdate") else [],
                    "schema": []},
        # RAW: lo que se escribe queda tal cual. Con USER_ENTERED, un teléfono
        # "+598 99…" se toma como fórmula (#ERROR!) y las fechas cambian de formato.
        "options": {"cellFormat": "RAW"},
    }
    extra = {"credentials": cred("googleSheetsOAuth2Api", "Google Sheets")}
    if operacion != "append":
        # actualizar por id se puede repetir sin duplicar nada
        extra.update({"retryOnFail": True, "maxTries": 4, "waitBetweenTries": 5000})
    return fl.nodo(nombre, "n8n-nodes-base.googleSheets", 4.5, p, pos, extra)


def claude(fl, nombre, pos=None):
    return fl.nodo(nombre, "n8n-nodes-base.httpRequest", 4.2, {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "anthropic-version", "value": "2023-06-01"},
            {"name": "anthropic-beta", "value": "server-side-fallback-2026-07-01"},
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.claude_body) }}",
        # de a 3 cada 5 s (unos 36 por minuto): sin esto salen todos juntos y
        # la API corta con 429 a la mitad
        "options": {"timeout": 180000,
                    "batching": {"batch": {"batchSize": 3, "batchInterval": 5000}}},
    }, pos, {"credentials": cred("httpHeaderAuth", "Anthropic API"),
             "onError": "continueRegularOutput", "retryOnFail": True,
             "maxTries": 3, "waitBetweenTries": 5000})


def enviar_mail(fl, nombre, cfg, pos=None):
    """Manda un mail de texto plano por el SMTP de Hostinger (contacto@).
    Espera en el item: para, asunto, cuerpo."""
    return fl.nodo(nombre, "n8n-nodes-base.emailSend", 2.1, {
        "fromEmail": "={{ $('%s').first().json.MI_EMAIL }}" % cfg,
        "toEmail": "={{ $json.para }}",
        "subject": "={{ $json.asunto }}",
        "emailFormat": "text",
        "text": "={{ $json.cuerpo }}",
        "options": {"appendAttribution": False},
    }, pos, {"credentials": cred("smtp", "Hostinger SMTP (contacto@)"),
             "onError": "continueRegularOutput"})


def telegram(fl, nombre, cfg, pos=None, texto="$json.telegram_text"):
    return fl.nodo(nombre, "n8n-nodes-base.telegram", 1.2, {
        "chatId": "={{ $('%s').first().json.TELEGRAM_CHAT_ID }}" % cfg,
        "text": "={{ %s }}" % texto,
        "additionalFields": {"appendAttribution": False, "parse_mode": "HTML",
                             "disable_web_page_preview": True},
    }, pos, {"credentials": cred("telegramApi", "Telegram Apardian")})


def si(fl, nombre, expr, pos=None):
    """IF de n8n v2 sobre una expresion booleana."""
    return fl.nodo(nombre, "n8n-nodes-base.if", 2, {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
            "conditions": [{
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, fl.nombre + nombre)),
                "leftValue": "={{ %s }}" % expr, "rightValue": "",
                "operator": {"type": "boolean", "operation": "true", "singleValue": True},
            }],
            "combinator": "and",
        },
        "options": {},
    }, pos)


def programado(fl, nombre, regla, pos=None):
    return fl.nodo(nombre, "n8n-nodes-base.scheduleTrigger", 1.2,
                   {"rule": {"interval": [regla]}}, pos)


def manual(fl, nombre, pos):
    return fl.nodo(nombre, "n8n-nodes-base.manualTrigger", 1, {}, pos)


def webhook(fl, nombre, ruta, metodo="GET", pos=None):
    return fl.nodo(nombre, "n8n-nodes-base.webhook", 2,
                   {"httpMethod": metodo, "path": ruta, "responseMode": "onReceived",
                    "options": {}}, pos,
                   {"webhookId": str(uuid.uuid5(uuid.NAMESPACE_URL, "apardian-wh/" + ruta))})


def disparadores(fl, regla):
    """Programado + manual (para probar), los dos entran al nodo Config."""
    a = programado(fl, "Programado", regla, (0, -100))
    b = manual(fl, "Probar a mano", (0, 100))
    fl.x = 240
    return a, b


# ================================================================== 01
def f01():
    fl = Flujo("APARDIAN 01 · Prospector (Radar)")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 7})
    v = dict(CONFIG_BASE)
    v.update({
        "BUSQUEDAS_POR_DIA": (12, "number"),
        # Solo negocios con buena reputación en Google: son los que más pierden
        # con una web floja o sin web (decisión de Martin, 25/10/2026).
        "RATING_MINIMO": (4.5, "number"),
        "RESENAS_MINIMAS": (15, "number"),
        # Prueba de un mes: después de esta fecha no busca más negocios.
        "FECHA_FIN": ("", "string"),
    })
    cfg = config(fl, "Config", v)
    busq = leer_hoja(fl, "Leer Búsquedas", cfg, "Busquedas")
    elegir = codigo(fl, "Elegir búsquedas", JS_FECHA + r"""
// La hoja "Busquedas" es el plan de Radar: país, idioma, rubro, búsqueda en
// Google Maps y servicio que se le ofrece. Cada día toma las que hace más
// tiempo que no corren (las nunca usadas primero). Cada búsqueda trae hasta 20
// negocios: 12 por día alcanzan para sostener 50 mails diarios.
const n = Number($('Config').first().json.BUSQUEDAS_POR_DIA) || 12;
if (terminoPrueba($('Config').first().json)) return [];
return $input.all().map(r => r.json)
  .filter(b => b.id && String(b.activo || '').trim().toLowerCase() === 'si' && b.query)
  .sort((x, y) => String(x.ultima_vez || '').localeCompare(String(y.ultima_vez || '')))
  .slice(0, n)
  .map(b => ({ json: b }));
""")
    places = fl.nodo("Google Places", "n8n-nodes-base.httpRequest", 4.2, {
        "method": "POST",
        "url": "https://places.googleapis.com/v1/places:searchText",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [{
            "name": "X-Goog-FieldMask",
            "value": "places.id,places.displayName,places.websiteUri,places.formattedAddress,"
                     "places.rating,places.userRatingCount,places.nationalPhoneNumber,places.internationalPhoneNumber,places.googleMapsUri",
        }]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ textQuery: $json.query, languageCode: $json.idioma || 'es', regionCode: $json.region || 'UY', pageSize: 20 }) }}",
        "options": {"timeout": 30000},
    }, None, {"credentials": cred("httpHeaderAuth", "Google Places API"),
              "onError": "continueRegularOutput"})
    plano = codigo(fl, "Aplanar", r"""
// Una fila por negocio, con el país, idioma, mercado y zona horaria de su búsqueda.
const busq = $('Elegir búsquedas').all();
const out = [];
$input.all().forEach((it, i) => {
  const b = busq[i] ? busq[i].json : {};
  for (const p of (it.json.places || [])) {
    out.push({ json: {
      id: p.id,
      nombre: (p.displayName && p.displayName.text) || '',
      web: p.websiteUri || '',
      telefono: p.internationalPhoneNumber || p.nationalPhoneNumber || '',
      direccion: p.formattedAddress || '',
      rating: p.rating || '',
      reseñas: p.userRatingCount || 0,
      maps: p.googleMapsUri || '',
      rubro: b.rubro, ciudad: b.query, pais: b.pais || 'Uruguay', idioma: b.idioma || 'es',
      mercado: b.mercado || 'uy', zona: b.zona || 'America/Montevideo', servicio_objetivo: b.servicio_objetivo || '',
    } });
  }
});
return out;
""")
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    dedupe = codigo(fl, "Solo nuevos", JS_FECHA + JS_REDES + r"""
// Saca los que ya están en la planilla (por id de Google o por web) y los que
// no tienen buena reputación: rating y cantidad de reseñas mínimos (Config).
const c = $('Config').first().json;
const rMin = Number(c.RATING_MINIMO) || 0, nMin = Number(c.RESENAS_MINIMAS) || 0;
// La web se compara sin protocolo, www, parámetros (?utm…) ni barra final:
// varias sucursales con la misma web son un solo lead.
const limpiar = u => String(u || '').toLowerCase().replace(/^https?:\/\/(www\.)?/, '').replace(/[?#].*$/, '').replace(/\/+$/, '');
const ya = new Set(), webs = new Set();
for (const r of $('Leer Leads').all()) {
  if (r.json.id) ya.add(String(r.json.id));
  if (r.json.web) webs.add(limpiar(r.json.web));
}
const vistos = new Set(), out = [];
for (const it of $('Aplanar').all()) {
  const p = it.json;
  const w = limpiar(p.web);
  if (!p.id || ya.has(p.id) || vistos.has(p.id) || (w && webs.has(w))) continue;
  if ((Number(p.rating) || 0) < rMin || (Number(p['reseñas']) || 0) < nMin) continue;
  vistos.add(p.id);
  if (w) webs.add(w);
  // Si en Google su "web" es Instagram o Facebook, no tiene web: el mejor prospecto.
  const red = esRed(p.web);
  out.push({ json: {
    id: p.id, fecha: hoy(), rubro: p.rubro, nombre: p.nombre, web: red ? '' : p.web,
    instagram: /instagram\.com/i.test(p.web) ? p.web : '', email: '', telefono: p.telefono, ciudad: p.ciudad,
    fuente: 'google_places', score: '', servicio: p.servicio_objetivo, problemas: '',
    estado: p.web && !red ? 'nuevo' : 'sin_web', asunto: '', borrador: '', fecha_envio: '',
    seguimientos: 0, respuesta: '',
    notas: [p.direccion, p.rating ? ('rating ' + p.rating + ' (' + p['reseñas'] + ' reseñas)') : '', p.maps, red ? 'en Google su web es ' + p.web : ''].filter(Boolean).join(' · '),
    pais: p.pais, idioma: p.idioma, mercado: p.mercado, zona: p.zona, oferta_id: '',
    ultimo_envio: '', seg_asunto: '', seg_cuerpo: '',
    rating: p.rating, resenas: p['reseñas'], wa_mensaje: '',
  } });
}
return out;
""")
    guardar = escribir_hoja(fl, "Agregar a Leads", cfg, "Leads", "append")
    # Solo se marcan las búsquedas que Google contestó bien; si fallan todas
    # (clave vencida, sin facturación) avisa a Martin en vez de gastarlas.
    marca = codigo(fl, "Marcar búsquedas", JS_FECHA + r"""
const busq = $('Elegir búsquedas').all();
return $('Google Places').all()
  .map((it, i) => ({ ok: !it.json.error, id: busq[i] && busq[i].json.id }))
  .filter(x => x.ok && x.id)
  .map(x => ({ json: { id: x.id, ultima_vez: hoy() } }));
""", pos=(fl.x - 1200, 240))
    g_marca = escribir_hoja(fl, "Guardar búsquedas", cfg, "Busquedas", pos=(fl.x - 960, 240))
    falla = codigo(fl, "¿Falló Google?", JS_HTML + r"""
const r = $('Google Places').all();
if (!r.length || r.some(it => !it.json.error)) return [];
const e = JSON.stringify(r[0].json.error || '').slice(0, 300);
return [{ json: { telegram_text: '<b>Radar · Google Places no contesta</b>\nNinguna de las ' + r.length +
  ' búsquedas de hoy funcionó, así que no se marcaron. Revisá la clave y la facturación en Google Cloud.\n<i>' + esc(e) + '</i>' } }];
""", pos=(fl.x - 1200, 440))
    tg_falla = telegram(fl, "Avisar falla", cfg, pos=(fl.x - 960, 440))
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, busq, elegir, places, plano, leads, dedupe, guardar)
    fl.cadena(places, marca, g_marca)
    fl.cadena(places, falla, tg_falla)
    return fl


# ================================================================== 02
def f02():
    fl = Flujo("APARDIAN 02 · Auditor")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 9})
    # para sostener 50 mails por día hacen falta ~90 auditorías: la mitad no
    # publica mail o no tiene una oportunidad clara
    v = dict(CONFIG_BASE); v["LIMITE_DIARIO"] = (90, "number")
    # borradores de WhatsApp por día para los que no tienen web o mail
    v["LIMITE_WHATSAPP"] = (15, "number")
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    elegir = codigo(fl, "Elegir nuevos", JS_REDES + r"""
const lim = $('Config').first().json.LIMITE_DIARIO || 90;
return $input.all()
  .filter(r => r.json.estado === 'nuevo' && r.json.web && !esRed(r.json.web))
  .slice(0, lim)
  .map(r => {
    // Se pide siempre por https: muchas fichas de Google guardan http:// y el
    // sitio igual redirige a https.
    let web = String(r.json.web).trim().replace(/^http:\/\//i, 'https://');
    if (!/^https?:\/\//i.test(web)) web = 'https://' + web;
    return { json: { ...r.json, web } };
  });
""")
    bajar = fl.nodo("Bajar web", "n8n-nodes-base.httpRequest", 4.2, {
        "url": "={{ $json.web }}",
        "options": {
            "timeout": 20000,
            "redirect": {"redirect": {"followRedirects": True, "maxRedirects": 5}},
            "response": {"response": {"responseFormat": "text", "outputPropertyName": "html"}},
        },
    }, None, {"onError": "continueRegularOutput"})
    senales = codigo(fl, "Señales de la web", r"""
// Mide cosas concretas de la web. El auditor solo puede hablar de lo que está acá.
const lead = $('Elegir nuevos').item.json;
const html = typeof $json.html === 'string' ? $json.html : '';
const falla = !html ? ($json.error ? (JSON.stringify($json.error).slice(0, 200)) : 'sin_respuesta') : '';
const m = re => { const x = html.match(re); return x ? x[1].trim() : ''; };
const cuenta = re => (html.match(re) || []).length;
const texto = html
  .replace(/<script[\s\S]*?<\/script>/gi, ' ').replace(/<style[\s\S]*?<\/style>/gi, ' ')
  .replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
  .replace(/\s+/g, ' ').trim();
const imgs = [...html.matchAll(/<img[^>]*>/gi)].map(x => x[0]);
const altVacios = imgs.filter(t => !/alt\s*=\s*["'][^"']+["']/i.test(t)).length;
// Mails publicados: los mailto y los que aparecen escritos en la página
// (sin los de imágenes, servicios del constructor ni ejemplos).
const ruido = /\.(png|jpe?g|gif|webp|svg)$|sentry|wixpress|example\.|@2x|godaddy|domain\.com|tudominio|yourdomain/i;
const mails = [...new Set([
  ...[...html.matchAll(/mailto:([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/gi)].map(x => x[1]),
  ...[...texto.matchAll(/\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b/gi)].map(x => x[1]),
].map(x => x.toLowerCase()).filter(x => !ruido.test(x)))];
const ig = m(/href=["'](https?:\/\/(?:www\.)?instagram\.com\/[^"'?#]+)/i);
const s = {
  url: lead.web,
  carga: falla ? ('no cargó: ' + falla) : 'ok',
  // si la web cargó, cargó por https (se pide así); si no cargó, no se sabe
  https: falla ? 'sin_medir' : true,
  titulo: m(/<title[^>]*>([\s\S]*?)<\/title>/i).slice(0, 160),
  meta_descripcion: m(/<meta[^>]+name=["']description["'][^>]*content=["']([^"']*)/i).slice(0, 300),
  tiene_viewport_celular: /<meta[^>]+name=["']viewport["']/i.test(html),
  peso_html_kb: Math.round(html.length / 1024),
  imagenes: imgs.length,
  imagenes_sin_alt: altVacios,
  usa_webp_o_avif: /\.(webp|avif)/i.test(html),
  palabras: texto ? texto.split(' ').length : 0,
  link_whatsapp: /wa\.me\/|api\.whatsapp\.com|whatsapp:\/\//i.test(html),
  link_instagram: ig || '',
  formulario: cuenta(/<form/gi) > 0,
  constructor: /wix\.com|wixstatic/i.test(html) ? 'Wix' : /wp-content/i.test(html) ? 'WordPress'
    : /squarespace/i.test(html) ? 'Squarespace' : /shopify/i.test(html) ? 'Shopify' : '',
  mails_publicados: mails,
};
const usuario = 'MERCADO: ' + (lead.mercado || 'uy') + ' (país: ' + (lead.pais || 'Uruguay') + ')' +
  '\nNegocio: ' + lead.nombre + '\nRubro: ' + lead.rubro + '\nBúsqueda: ' + lead.ciudad +
  (lead.servicio ? '\nServicio que buscábamos ofrecerle: ' + lead.servicio : '') +
  '\nFicha de Google: ' + (lead.notas || '') +
  '\n\nSeñales medidas en la web:\n' + JSON.stringify(s, null, 2) +
  '\n\nTexto visible de la portada (extracto):\n' + texto.slice(0, 6000);
return { json: { lead, senales: s, usuario } };
""", por_item=True)
    prep = codigo(fl, "Prompt auditor", JS_CLAUDE + r"""
const SYSTEM = %s;
return { json: { ...$json, claude_body: cuerpoClaude(SYSTEM, $json.usuario, 8000, 'medium', RAPIDO) } };
""" % json.dumps(prompt("auditor"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · auditor")
    leer = codigo(fl, "Leer auditoría", JS_LEER + r"""
const base = $('Prompt auditor').item.json;
const lead = base.lead, s = base.senales;
const r = leerClaude($json);
// Falla de la API: queda 'nuevo' y se audita mañana. Respuesta inservible: error_auditoria.
if (!r.ok) return { json: { id: lead.id, estado: r.temporal ? 'nuevo' : 'error_auditoria', respuesta: 'auditor: ' + r.motivo.slice(0, 200) } };
const a = r.data || {};
const email = (s.mails_publicados || [])[0] || '';
const score = Number(a.score_oportunidad) || 0;
let estado = 'auditado';
if (score < 60) estado = 'descartado';
else if (!email) estado = 'sin_email';
const lista = Array.isArray(a.problemas) ? a.problemas : [];
const problemas = lista.filter(p => p && typeof p === 'object')
  .map(p => '• ' + String(p.problema || '') + ' — ' + String(p.evidencia || '') + ' (' + String(p.impacto || '') + ')').join('\n');
return { json: {
  id: lead.id, instagram: s.link_instagram || '', email, score,
  servicio: a.servicio_principal || '', problemas, estado,
  idioma: a.idioma || lead.idioma || 'es', mercado: lead.mercado || 'uy',
  notas: JSON.stringify({ auditoria: a, ficha: lead.notas || '' }),
} };
""", por_item=True)
    guardar = escribir_hoja(fl, "Guardar auditoría", cfg, "Leads")

    # ---- sin web o sin mail publicado: un WhatsApp para que Martin lo mande a mano
    y = 400
    elegir_wa = codigo(fl, "Elegir para WhatsApp", JS_WA + r"""
const lim = Number($('Config').first().json.LIMITE_WHATSAPP) || 15;
return $('Leer Leads').all().map(r => r.json)
  .filter(l => l.id && (l.estado === 'sin_web' || (l.estado === 'sin_email' && Number(l.score) >= 60)))
  .filter(l => celular(l.telefono, l.pais))
  // la planilla puede devolver el rating con coma ("4,5")
  .sort((x, y) => { const n = v => Number(String(v == null ? '' : v).replace(',', '.')) || 0;
    return n(y.rating) * Math.log10(10 + n(y.resenas)) - n(x.rating) * Math.log10(10 + n(x.resenas)); })
  .slice(0, lim)
  .map(l => ({ json: l }));
""", pos=(480, y))
    prep_wa = codigo(fl, "Prompt WhatsApp", JS_CLAUDE + JS_IDIOMA + r"""
const SYSTEM = %s;
const l = $json;
// sin_web trae la ficha de Google en notas; sin_email, el JSON de la auditoría
let audit = null, ficha = l.notas || '';
try { const n = JSON.parse(l.notas || '{}'); audit = n.auditoria || null; ficha = n.ficha || ''; } catch (e) {}
const usuario = 'MERCADO: ' + (l.mercado || 'uy') + '\nPaís: ' + (l.pais || 'Uruguay') + lineaIdioma(l) +
  '\nNegocio: ' + l.nombre + '\nRubro: ' + l.rubro + '\nBúsqueda: ' + l.ciudad +
  '\nRating en Google: ' + (l.rating || 'sin dato') + ' (' + (l.resenas || 0) + ' reseñas)' +
  '\nWeb: ' + (l.web || 'NO TIENE WEB') + (l.instagram ? '\nInstagram: ' + l.instagram : '') +
  '\nFicha de Google: ' + ficha +
  (audit ? '\n\nAuditoría de su web:\n' + JSON.stringify(audit, null, 2) : '');
return { json: { lead: l, claude_body: cuerpoClaude(SYSTEM, usuario, 6000, 'medium') } };
""" % json.dumps(prompt("whatsapp"), ensure_ascii=False), por_item=True, pos=(720, y))
    cl_wa = claude(fl, "Claude · WhatsApp", pos=(960, y))
    leer_wa = codigo(fl, "Leer WhatsApp", JS_LEER + r"""
const l = $('Prompt WhatsApp').item.json.lead;
const r = leerClaude($json);
// Falla de la API: se reintenta mañana. Respuesta inservible: no se insiste.
if (!r.ok) return { json: { id: l.id, estado: r.temporal ? l.estado : 'sin_contacto', respuesta: 'whatsapp: ' + r.motivo.slice(0, 200) } };
if (r.data.omitir || !r.data.mensaje) return { json: { id: l.id, estado: 'sin_contacto' } };
return { json: { id: l.id, estado: 'wa_borrador', wa_mensaje: String(r.data.mensaje).slice(0, 1500) } };
""", por_item=True, pos=(1200, y))
    g_wa = escribir_hoja(fl, "Guardar WhatsApp", cfg, "Leads", pos=(1440, y))
    # ---- "webs" que son Instagram o Facebook: no se auditan, pasan a sin_web
    redes = codigo(fl, "Webs que son redes", JS_REDES + r"""
return $('Leer Leads').all().map(r => r.json)
  .filter(l => l.id && l.estado === 'nuevo' && esRed(l.web))
  .map(l => ({ json: { id: l.id, estado: 'sin_web', web: '',
    instagram: l.instagram || (/instagram\.com/i.test(l.web) ? l.web : ''),
    notas: [l.notas, 'en Google su web es ' + l.web].filter(Boolean).join(' · ') } }));
""", pos=(480, y + 220))
    g_redes = escribir_hoja(fl, "Guardar sin web", cfg, "Leads", pos=(720, y + 220))
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, elegir, bajar, senales, prep, cl, leer, guardar)
    fl.unir(leads, elegir_wa)
    fl.cadena(leads, redes, g_redes)
    fl.cadena(elegir_wa, prep_wa, cl_wa, leer_wa, g_wa)
    return fl


# ================================================================== Radar
JS_RADAR = r"""
// Hora y día en la zona horaria del destinatario (Intl viene con Node).
// Una zona mal escrita da -1 / 'Sun': ese lead no sale hasta corregirla.
const horaEn = z => { try { return Number(new Intl.DateTimeFormat('en-US', { timeZone: String(z).trim(), hour: 'numeric', hourCycle: 'h23' }).format(new Date())); } catch (e) { return -1; } };
const diaEn = z => { try { return new Intl.DateTimeFormat('en-US', { timeZone: String(z).trim(), weekday: 'short' }).format(new Date()); } catch (e) { return 'Sun'; } };
const horarioDeOficina = z => { const h = horaEn(z), d = diaEn(z); return d !== 'Sat' && d !== 'Sun' && h >= 9 && h < 17; };
const hoyUY = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Montevideo' }).format(new Date());
// Cuántos mails salieron hoy desde la casilla (primeros y seguimientos): cada
// lead recibe como mucho uno por día, así que alcanza con contar ultimo_envio.
const mailsHoy = leads => leads.filter(l => String(l.ultimo_envio || '') === hoyUY()).length;
// Casillas de correo gratis o de proveedores: no identifican a una empresa,
// así que nunca se comparan ni se bloquean por dominio.
const genericos = /^(gmail|googlemail|hotmail|outlook|live|msn|yahoo|ymail|icloud|me|mac|aol|proton|protonmail|gmx|zoho|yandex|mail|adinet|vera|montevideo|internet|netgate|fibertel|arnet|speedy|ciudad|uol|bol|terra|telefonica|movistar|prodigy|infinitummail)\./i;
const dominioDe = mail => String(mail || '').toLowerCase().split('@')[1] || '';
const dominioPropio = mail => { const d = dominioDe(mail); return d && !genericos.test(d) ? d : ''; };
"""


JS_WA = r"""
// ¿El teléfono parece un celular con WhatsApp? Uruguay: +598 9…; Argentina:
// +54 9…; el resto se deja pasar (Martin lo ve antes de mandarlo).
const digitos = t => String(t || '').replace(/[^\d]/g, '');
const celular = (t, pais) => {
  const d = digitos(t);
  if (d.length < 8) return false;
  if (d.startsWith('598')) return d[3] === '9';
  if (d.startsWith('54')) return d[2] === '9';
  if (!String(t).trim().startsWith('+')) return String(pais || 'Uruguay') === 'Uruguay' && /^09/.test(d);
  return true;
};
const waNumero = (t, pais) => { let d = digitos(t); if (/^09/.test(d) && String(pais || 'Uruguay') === 'Uruguay') d = '598' + d.slice(1); return d; };
"""

# ================================================================== 03
def f03():
    """Escribe los primeros mails y los deja como borrador. No manda nada:
    Martin los aprueba (o edita) en la bandeja (flujo 11) y sale el 12."""
    fl = Flujo("APARDIAN 03 · Radar: redactor")
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "0 8 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({
        "SCORE_MINIMO": (60, "number"),
        # Calentamiento: borradores nuevos por día según la semana desde
        # FECHA_INICIO (AAAA-MM-DD). Con el tope de 90 mails por día de la
        # casilla, 30 nuevos dejan lugar para sus dos seguimientos.
        "FECHA_INICIO": ("PEGAR_FECHA_DE_ARRANQUE", "string"),
        "CUPOS_POR_SEMANA": ("10,20,30", "string"),
        # Prueba de un mes: después de esta fecha no escribe primeros mails
        # (los seguimientos y las respuestas siguen hasta que se apaguen).
        "FECHA_FIN": ("", "string"),
        # Si en la bandeja ya hay esta cantidad esperando, no escribe más.
        "MAX_PENDIENTES": (60, "number"),
        # Obligatoria para escribir a EE.UU. (ley CAN-SPAM). Sin ella, Radar no les escribe.
        "DIRECCION_POSTAL": ("", "string"),
        "URL_BANDEJA": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-bandeja", "string"),
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA-DE-RADAR", "string"),
    })
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    bajas = leer_hoja(fl, "Leer Bajas", cfg, "Bajas")
    ofertas = leer_hoja(fl, "Leer Ofertas", cfg, "Ofertas")
    entren = leer_hoja(fl, "Leer Entrenamiento", cfg, "Entrenamiento")
    elegir = codigo(fl, "Elegir auditados", JS_FECHA + JS_RADAR + r"""
const c = $('Config').first().json;
const bm = new Set(), bd = new Set();
for (const r of $('Leer Bajas').all()) {
  if (r.json.email) bm.add(String(r.json.email).toLowerCase());
  if (r.json.dominio) bd.add(String(r.json.dominio).toLowerCase());
}
const todos = $('Leer Leads').all().map(r => r.json).filter(l => l.id);
// Una casilla (o una empresa con dominio propio) recibe un solo primer mail:
// si otra sucursal ya está en curso, esta no se escribe.
const libres = ['nuevo', 'sin_web', 'sin_email', 'auditado', 'descartado', 'error_auditoria', 'error_redaccion'];
const usados = new Set();
for (const l of todos) if (l.email && !libres.includes(l.estado)) {
  usados.add(String(l.email).toLowerCase()); const d = dominioPropio(l.email); if (d) usados.add('@' + d);
}
const repetido = l => { const e = String(l.email).toLowerCase(), d = dominioPropio(e);
  if (usados.has(e) || (d && usados.has('@' + d))) return true;
  usados.add(e); if (d) usados.add('@' + d); return false; };
const cupos = String(c.CUPOS_POR_SEMANA || '10,20,30').split(',').map(Number).filter(n => n > 0);
const ini = /^\d{4}-\d{2}-\d{2}$/.test(String(c.FECHA_INICIO || '')) ? c.FECHA_INICIO : '';
const semana = ini ? Math.max(0, Math.floor(diasDesde(ini) / 7)) : 0;
const cupo = cupos[Math.min(semana, cupos.length - 1)] || 10;
const pendientes = todos.filter(l => ['borrador', 'aprobado'].includes(l.estado)).length;
const n = terminoPrueba(c) ? 0 : Math.max(0, Math.min(cupo, (Number(c.MAX_PENDIENTES) || 60) - pendientes));
// la planilla puede devolver el rating con coma ("4,5")
const num = v => Number(String(v == null ? '' : v).replace(',', '.')) || 0;
const rep = l => num(l.rating) * Math.log10(10 + num(l.resenas));
const elegidos = todos
  .filter(l => l.estado === 'auditado' && Number(l.score) >= (c.SCORE_MINIMO || 60) && l.email)
  .filter(l => { const e = String(l.email).toLowerCase(); return !bm.has(e) && !bd.has(dominioPropio(e)); })
  // a EE.UU. solo con dirección postal en la firma (CAN-SPAM)
  .filter(l => String(l.pais || '') !== 'Estados Unidos' || String(c.DIRECCION_POSTAL || '').trim())
  .sort((x, y) => (Number(y.score) - Number(x.score)) || (rep(y) - rep(x)))
  .filter(l => !repetido(l))
  .slice(0, n)
  .map(l => ({ json: l }));
// Sin nada para escribir igual sigue, para el aviso de las 8 (seguimientos, WhatsApp).
return elegidos.length ? elegidos : [{ json: { _vacio: true } }];
""")
    hay = si(fl, "¿Hay para escribir?", "!$json._vacio")
    prep = codigo(fl, "Prompt redactor", JS_CLAUDE + JS_FECHA + JS_IDIOMA + r"""
const SYSTEM = %s;
const c = $('Config').first().json;
let audit = {};
try { audit = JSON.parse($json.notas || '{}').auditoria || {}; } catch (e) {}
const mercado = $json.mercado || 'uy';
// Solo las ofertas que Martin aprobó en el Centro, vigentes y de este mercado.
const ofertas = $('Leer Ofertas').all().map(r => r.json)
  .filter(o => o.id && String(o.estado || '') === 'activa')
  .filter(o => !o.vigencia_hasta || String(o.vigencia_hasta) >= hoy())
  .filter(o => !o.mercado || o.mercado === 'todos' || o.mercado === mercado)
  .map(o => ({ id: o.id, servicio: o.servicio, nombre: o.nombre, para_quien: o.para_quien, que_incluye: o.que_incluye,
               plazo: o.plazo, precio_desde: o.precio_desde, moneda: o.moneda, vigencia_hasta: o.vigencia_hasta, angulo: o.angulo }));
const entrenamiento = $('Leer Entrenamiento').all().map(r => r.json)
  .filter(e => e.clave && String(e.respuesta || '').trim())
  .map(e => '- ' + (e.pregunta || e.clave) + '\n  ' + e.respuesta).join('\n');
const usuario = 'MERCADO: ' + mercado + '\nPaís: ' + ($json.pais || 'Uruguay') + lineaIdioma($json) +
  '\nNegocio: ' + $json.nombre + '\nRubro: ' + $json.rubro + '\nBúsqueda: ' + $json.ciudad +
  '\nWeb: ' + $json.web + ($json.instagram ? '\nInstagram: ' + $json.instagram : '') +
  ($json.rating ? '\nRating en Google: ' + $json.rating + ' (' + ($json.resenas || 0) + ' reseñas)' : '') +
  (String($json.pais || '') === 'Estados Unidos' ? '\nDIRECCION_POSTAL (va en la firma): ' + c.DIRECCION_POSTAL : '') +
  '\n\nAuditoría:\n' + JSON.stringify(audit, null, 2) +
  '\n\nOfertas aprobadas por Martin para este mercado:\n' + (ofertas.length ? JSON.stringify(ofertas, null, 2) : '(ninguna: no menciones ofertas ni precios)') +
  '\n\nLo que Martin te enseñó:\n' + (entrenamiento || '(todavía nada)');
return { json: { lead: $json, claude_body: cuerpoClaude(SYSTEM, usuario, 6000, 'medium') } };
""" % json.dumps(prompt("redactor"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · redactor")
    leer = codigo(fl, "Leer mail", JS_LEER + r"""
const lead = $('Prompt redactor').item.json.lead;
const r = leerClaude($json);
// Falla de la API: sigue 'auditado' y se escribe mañana.
if (!r.ok) return { json: { id: lead.id, estado: r.temporal ? 'auditado' : 'error_redaccion', respuesta: 'redactor: ' + r.motivo.slice(0, 200) } };
if (r.data.omitir) return { json: { id: lead.id, estado: 'descartado' } };
const m = r.data;
if (!String(m.asunto || '').trim() || !String(m.cuerpo || '').trim())
  return { json: { id: lead.id, estado: 'error_redaccion', respuesta: 'redactor: mail sin asunto o sin cuerpo' } };
return { json: { id: lead.id, estado: 'borrador', asunto: String(m.asunto || '').slice(0, 200),
  borrador: String(m.cuerpo || ''), oferta_id: m.oferta_id || '' } };
""", por_item=True)
    g = escribir_hoja(fl, "Guardar borrador", cfg, "Leads")
    aviso = codigo(fl, "Aviso de la bandeja", JS_HTML + r"""
const c = $('Config').first().json;
let nuevos = 0;
try { nuevos = $('Leer mail').all().filter(r => r.json.estado === 'borrador').length; } catch (e) {}  // hoy no escribió
const L = $('Leer Leads').all().map(r => r.json);
const segs = L.filter(l => /^borrador_seg/.test(l.estado || '')).length;
const was = L.filter(l => l.estado === 'wa_borrador').length;
const antes = L.filter(l => l.estado === 'borrador').length;
const link = c.URL_BANDEJA + '?t=' + encodeURIComponent(c.TOKEN);
if (!(nuevos + antes + segs + was)) return [];
return [{ json: { telegram_text: '<b>Radar · para aprobar</b>\n' +
  (nuevos + antes) + ' mails nuevos · ' + segs + ' seguimientos · ' + was + ' WhatsApp\n' +
  'Nada sale sin tu OK. <a href="' + esc(link) + '">Abrir la bandeja</a> (también desde el Centro → Radar).' } }];
""")
    tg = telegram(fl, "Avisar a Martin", cfg)
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, ofertas, entren, elegir, hay)
    fl.unir(hay, prep, 0)
    fl.cadena(prep, cl, leer, g, aviso, tg)
    fl.unir(hay, aviso, 1)
    return fl


# ================================================================== 04
def f04():
    """Escribe los seguimientos (día 4 y día 9 desde el primer mail) como borrador para la bandeja
    y cierra a quien no respondió en 14 días. No manda nada."""
    fl = Flujo("APARDIAN 04 · Radar: seguimiento")
    # 7:45, antes del redactor: el aviso de las 8 ya los cuenta
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "45 7 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({
        "MAX_POR_DIA": (40, "number"),
        "DIRECCION_POSTAL": ("", "string"),
    })
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    bajas = leer_hoja(fl, "Leer Bajas", cfg, "Bajas")
    toca = codigo(fl, "¿A quién le toca?", JS_FECHA + JS_RADAR + r"""
// Día 4 sin respuesta: seguimiento 1. Día 9: seguimiento 2 (y al menos 4 días
// después del anterior). Día 14: se cierra. Quien respondió ya cambió de
// estado (flujo 05) y no entra acá.
const c = $('Config').first().json;
const bm = new Set(), bd = new Set();
for (const r of $('Leer Bajas').all()) {
  if (r.json.email) bm.add(String(r.json.email).toLowerCase());
  if (r.json.dominio) bd.add(String(r.json.dominio).toLowerCase());
}
const enCurso = ['enviado', 'seguimiento_1', 'seguimiento_2', 'sin_seguimiento', 'borrador_seg1', 'borrador_seg2', 'aprobado_seg1', 'aprobado_seg2'];
const out = [];
let lim = Number(c.MAX_POR_DIA) || 40;
for (const l of $('Leer Leads').all().map(r => r.json).filter(x => x.id)) {
  const d = diasDesde(l.fecha_envio), u = l.ultimo_envio ? diasDesde(l.ultimo_envio) : d;
  if (!l.fecha_envio || !l.email) continue;
  const e = String(l.email).toLowerCase();
  // dado de baja (por mail o por su dominio): se cierra y no recibe más
  if (bm.has(e) || bd.has(dominioPropio(e))) { if (enCurso.includes(l.estado)) out.push({ json: { lead: l, n: 0, cerrar: true, estado: 'baja' } }); continue; }
  if (['seguimiento_2', 'sin_seguimiento'].includes(l.estado) && d >= 14) { out.push({ json: { lead: l, n: 0, cerrar: true } }); continue; }
  if (lim <= 0 || u < 4) continue;
  if (l.estado === 'enviado' && d >= 4) { out.push({ json: { lead: l, n: 1, cerrar: false } }); lim--; }
  else if (l.estado === 'seguimiento_1' && d >= 9) { out.push({ json: { lead: l, n: 2, cerrar: false } }); lim--; }
}
return out;
""")
    cerrar = si(fl, "¿Cerrar?", "$json.cerrar")
    fila_c = codigo(fl, "Fila cerrada", "return { json: { id: $json.lead.id, estado: $json.estado || 'cerrado_sin_respuesta' } };",
                    por_item=True, pos=(fl.x, -220))
    g_c = escribir_hoja(fl, "Guardar cierre", cfg, "Leads", pos=(fl.x + 240, -220))
    prep = codigo(fl, "Prompt seguimiento", JS_CLAUDE + JS_IDIOMA + r"""
const SYSTEM = %s;
const c = $('Config').first().json;
const x = $json;
let audit = {};
try { audit = JSON.parse(x.lead.notas || '{}').auditoria || {}; } catch (e) {}
const usuario = 'Seguimiento número: ' + x.n + '\nNegocio: ' + x.lead.nombre +
  '\nPaís: ' + (x.lead.pais || 'Uruguay') + lineaIdioma(x.lead) +
  (String(x.lead.pais || '') === 'Estados Unidos' ? '\nDIRECCION_POSTAL: ' + c.DIRECCION_POSTAL : '') +
  '\n\nPrimer mail (asunto): ' + x.lead.asunto + '\nPrimer mail (cuerpo):\n' + x.lead.borrador +
  '\n\nAuditoría:\n' + JSON.stringify(audit, null, 2);
return { json: { ...x, claude_body: cuerpoClaude(SYSTEM, usuario, 4000, 'medium') } };
""" % json.dumps(prompt("seguimiento"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · seguimiento")
    leer = codigo(fl, "Leer seguimiento", JS_LEER + r"""
const x = $('Prompt seguimiento').item.json;
const r = leerClaude($json);
if (!r.ok || !String(r.data.cuerpo || '').trim())
  return { json: { id: x.lead.id, _antes: x.lead.estado, estado: x.lead.estado, respuesta: 'seguimiento ' + x.n + ' sin escribir: ' + (r.ok ? 'vacío' : r.motivo).slice(0, 200) } };
return { json: { id: x.lead.id, _antes: x.lead.estado, estado: 'borrador_seg' + x.n,
  seg_asunto: String(r.data.asunto || ('Re: ' + x.lead.asunto)).slice(0, 200), seg_cuerpo: String(r.data.cuerpo || '') } };
""", por_item=True)
    # Escribir los seguimientos tarda; si mientras tanto el lead respondió
    # (flujo 05), su fila ya cambió y no se pisa.
    releer = leer_hoja(fl, "Releer Leads", cfg, "Leads")
    sigue = codigo(fl, "Solo si no respondió", r"""
const ahora = new Map($('Releer Leads').all().map(r => [String(r.json.id), String(r.json.estado || '')]));
return $('Leer seguimiento').all()
  .filter(it => ahora.get(String(it.json.id)) === String(it.json._antes))
  .map(it => { const { _antes, ...fila } = it.json; return { json: fila }; });
""")
    g = escribir_hoja(fl, "Guardar borrador seguimiento", cfg, "Leads")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, toca, cerrar)
    fl.unir(cerrar, fila_c, 0)
    fl.unir(fila_c, g_c)
    fl.unir(cerrar, prep, 1)
    fl.cadena(prep, cl, leer, releer, sigue, g)
    return fl


# ================================================================== 05
def f05():
    """Lee la bandeja de contacto@ (IMAP de Hostinger). Solo procesa mails de
    negocios a los que Radar les escribió; el resto (consultas de la web, etc.)
    queda intacto y sin marcar como leído."""
    fl = Flujo("APARDIAN 05 · Radar: respuestas")
    imap = fl.nodo("Mail nuevo en contacto@", "n8n-nodes-base.emailReadImap", 2, {
        "mailbox": "INBOX",
        "postProcessAction": "nothing",
        "format": "resolved",
        "options": {},
    }, (0, 0), {"credentials": cred("imap", "Hostinger IMAP (contacto@)")})
    fl.x = 240
    v = dict(CONFIG_BASE)
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    resp = codigo(fl, "¿Es de un lead?", JS_RADAR + r"""
// Une cada mail con el lead que lo mandó: por la dirección exacta o, si no es
// un mail genérico (gmail, hotmail…), por el dominio. Los rebotes
// (mailer-daemon) se unen por la dirección que aparece en el texto. Si el lead
// ya no está esperando respuesta, el mail se ignora: así un mismo mail no se
// procesa dos veces.
// También los que ya contestaron algo (no_ahora, respondio) o se cerraron:
// si escriben de nuevo, Martin se entera.
const abiertos = ['enviado', 'seguimiento_1', 'seguimiento_2', 'borrador_seg1', 'borrador_seg2', 'aprobado_seg1', 'aprobado_seg2',
  'enviando', 'enviando_seg1', 'enviando_seg2', 'sin_seguimiento', 'no_ahora', 'respondio', 'cerrado_sin_respuesta'];
const L = $('Leer Leads').all().map(r => r.json).filter(l => l.id && l.email && abiertos.includes(l.estado));
const porMail = new Map(L.map(l => [String(l.email).toLowerCase(), l]));
const porDominio = new Map();
for (const l of L) { const d = dominioPropio(l.email); if (d) porDominio.set(d, l); }
// Si contesta desde otra casilla, se lo reconoce por el asunto (sin Re:/RV:/Fwd:).
const limpioAsunto = a => String(a || '').replace(/^\s*((re|rv|fw|fwd|res|aw|tr)\s*:\s*)+/i, '').trim().toLowerCase();
const porAsunto = new Map();
for (const l of L) for (const a of [l.asunto, l.seg_asunto]) { const k = limpioAsunto(a); if (k.length > 12) porAsunto.set(k, l); }
const sinHtml = h => String(h || '').replace(/<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ');
// Corta el mail citado: Gmail/Apple ("El … escribió:") y Outlook ("De: … Enviado:").
const sinCita = t => String(t).split(/\r?\n(?:El .{5,120} escribió:|On .{5,120} wrote:|Em .{5,120} escreveu:|-{2,}\s*(?:Original Message|Mensaje original)|_{5,}|\s*(?:De|From)\s*:.+\r?\n\s*(?:Enviado|Sent|Fecha|Date)\s*:)/i)[0]
  .split('\n').filter(l => !l.startsWith('>')).join('\n').trim();
// Respuestas automáticas (fuera de oficina, vacaciones): no cambian nada.
const automatica = m => { const h = m.headers || {}, get = k => String(h[k] || h[k.toLowerCase()] || '');
  return /auto-(replied|generated)/i.test(get('auto-submitted')) || !!get('x-autoreply') || !!get('x-autorespond') ||
    /^(auto|automatic reply|respuesta autom|out of office|fuera de (la )?oficina|ausente|vacaciones|réponse automatique|resposta autom|abwesen)/i.test(String(m.subject || '').trim()); };
const contiene = (texto, mail) => new RegExp('(^|[^\\w.+-])' + String(mail).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^\\w.-])', 'i').test(texto);
const out = [], vistos = new Set();
for (const it of $('Mail nuevo en contacto@').all()) {
  const m = it.json;
  const de = String((m.from && m.from.value && m.from.value[0] && m.from.value[0].address) ||
    (String(m.from && m.from.text || m.from || '').match(/[\w.+-]+@[\w.-]+/) || [''])[0]).toLowerCase();
  const texto = String(m.text || m.textPlain || sinHtml(m.html || m.textHtml) || '');
  const rebote = /mailer-daemon|postmaster/i.test(de);
  if (!rebote && automatica(m)) continue;
  let lead = porMail.get(de) || porDominio.get(dominioPropio(de)) || (!rebote && porAsunto.get(limpioAsunto(m.subject)));
  if (!lead && rebote) lead = L.find(l => contiene(texto, l.email));
  if (!lead || vistos.has(lead.id)) continue;
  vistos.add(lead.id);
  out.push({ json: { lead, de, asunto: m.subject || '', rebote, texto: (rebote ? texto : sinCita(texto)).slice(0, 4000) } });
}
return out;
""")
    prep = codigo(fl, "Prompt clasificador", JS_CLAUDE + r"""
const SYSTEM = %s;
const usuario = 'De: ' + $json.de + '\nAsunto: ' + $json.asunto + '\n\nRespuesta:\n' + $json.texto;
return { json: { ...$json, claude_body: cuerpoClaude(SYSTEM, usuario, 2000, 'low', RAPIDO) } };
""" % json.dumps(prompt("clasificador"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · clasificador")
    leer = codigo(fl, "Leer clasificación", JS_LEER + JS_HTML + JS_FECHA + JS_RADAR + r"""
const x = $('Prompt clasificador').item.json;
const r = leerClaude($json);
const validas = ['interesado', 'pide_precio', 'no_ahora', 'baja', 'automatica', 'otro'];
let cat = r.ok && validas.includes(r.data.categoria) ? r.data.categoria : 'otro';
// 'rebote' solo cuando lo manda el servidor de correo
if (x.rebote) cat = 'rebote';
// fuera de oficina y otras automáticas: no cambian el estado ni avisan
if (cat === 'automatica') return { json: { fila: null, baja: null, alerta: false } };
const resumen = r.ok ? (r.data.resumen || '') : ('sin clasificar: ' + r.motivo);
const sug = r.ok ? (r.data.sugerencia_respuesta || '') : '';
const mail = String(x.lead.email || '').toLowerCase();
return { json: {
  fila: { id: x.lead.id, estado: cat === 'otro' ? 'respondio' : cat,
          respuesta: cat + ' · ' + hoy() + ' · ' + resumen },
  // el dominio solo si es propio de la empresa: una baja de un gmail no bloquea a todos los gmail
  baja: cat === 'baja' ? { email: mail, dominio: dominioPropio(mail), fecha: hoy(), motivo: resumen } : null,
  alerta: ['interesado', 'pide_precio', 'no_ahora', 'otro'].includes(cat),
  telegram_text: '<b>' + (cat === 'pide_precio' ? '💰 Pide precio' : cat === 'interesado' ? '🔥 Interesado' : cat === 'no_ahora' ? '⏳ No por ahora' : '📩 Respondió') +
    ': ' + esc(x.lead.nombre) + '</b>\n' + esc(x.lead.web) + '\n\n' + esc(resumen) +
    '\n\n<i>Respondió (está en contacto@):</i>\n' + esc(x.texto.slice(0, 700)) +
    (sug ? '\n\n<i>Sugerencia (revisala antes de mandar):</i>\n' + esc(sug) : ''),
} };
""", por_item=True)
    fila = codigo(fl, "Fila respuesta", "return $input.all().filter(i => i.json.fila).map(i => ({ json: i.json.fila }));")
    g = escribir_hoja(fl, "Guardar respuesta", cfg, "Leads")
    es_baja = si(fl, "¿Es baja?", "!!$json.baja", pos=(fl.x - 480, 220))
    fila_b = codigo(fl, "Fila baja", "return { json: $json.baja };", por_item=True, pos=(fl.x - 240, 220))
    g_b = escribir_hoja(fl, "Agregar a Bajas", cfg, "Bajas", "append", pos=(fl.x, 220))
    alerta = si(fl, "¿Avisar a Martin?", "$json.alerta", pos=(fl.x - 480, 440))
    tg = telegram(fl, "Aviso a Martin", cfg, pos=(fl.x - 240, 440))
    fl.cadena(imap, cfg, leads, resp, prep, cl, leer, fila, g)
    fl.unir(leer, es_baja)
    fl.unir(es_baja, fila_b, 0)
    fl.unir(fila_b, g_b)
    fl.unir(leer, alerta)
    fl.unir(alerta, tg, 0)
    return fl


# ================================================================== 06
def f06():
    fl = Flujo("APARDIAN 06 · Bienvenida de consultas")
    wh = webhook(fl, "Consulta entrante", "apardian-consulta", "POST", pos=(0, 0))
    fl.x = 240
    cfg = config(fl, "Config", {"TELEGRAM_CHAT_ID": CONFIG_BASE["TELEGRAM_CHAT_ID"],
                                 # el formulario o ManyChat llaman a .../apardian-consulta?t=CLAVE
                                 "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string")})
    prep = codigo(fl, "Prompt bienvenida", JS_CLAUDE + JS_HTML + r"""
// Espera un POST con { nombre, canal, telefono, mensaje } y la clave en ?t=.
// Puede venir de un formulario de la web o de ManyChat (WhatsApp Cloud API
// manda otro formato: hay que adaptarlo antes).
const SYSTEM = %s;
const w = $('Consulta entrante').first().json;
if (!claveOk((w.query || {}).t, $('Config').first().json.TOKEN)) return [];
const c = w.body || {};
const usuario = 'Canal: ' + (c.canal || 'whatsapp') + '\nNombre: ' + (c.nombre || '') +
  '\nTeléfono: ' + (c.telefono || '') + '\n\nConsulta:\n' + String(c.mensaje || '').slice(0, 3000);
return [{ json: { consulta: c, claude_body: cuerpoClaude(SYSTEM, usuario, 3000, 'low') } }];
""" % json.dumps(prompt("bienvenida"), ensure_ascii=False))
    cl = claude(fl, "Claude · bienvenida")
    leer = codigo(fl, "Armar aviso", JS_LEER + JS_HTML + r"""
const c = $('Prompt bienvenida').first().json.consulta;
const r = leerClaude($input.first().json);
const d = r.ok ? r.data : { servicio: 'otro', urgencia: 'media', resumen: 'sin clasificar: ' + r.motivo, respuesta_sugerida: '' };
const tel = String(c.telefono || '').replace(/\D/g, '');
const wa = tel ? 'https://wa.me/' + tel + '?text=' + encodeURIComponent(d.respuesta_sugerida || '') : '';
return [{ json: { telegram_text:
  (d.urgencia === 'alta' ? '🔴 ' : '') + '<b>Consulta nueva · ' + esc(d.servicio) + '</b> (' + esc(c.canal || 'whatsapp') + ')\n' +
  esc(String(c.nombre || '').slice(0, 100)) + ' ' + esc(String(c.telefono || '').slice(0, 40)) + '\n\n' + esc(String(c.mensaje || '').slice(0, 1500)) +
  '\n\n<i>Resumen:</i> ' + esc(d.resumen) +
  '\n\n<i>Respuesta sugerida (revisala):</i>\n' + esc(String(d.respuesta_sugerida || '').slice(0, 1200)) +
  (wa ? '\n\n<a href="' + esc(wa) + '">Abrir WhatsApp con la respuesta</a>' : '') } }];
""")
    tg = telegram(fl, "Aviso a Martin", cfg)
    fl.cadena(wh, cfg, prep, cl, leer, tg)
    return fl


# ------------------------------------------------------------------ Instagram
# Uruguay no tiene horario de verano desde 2015: Montevideo es UTC-3 todo el año.
JS_HORA_UY = r"""
const enUY = (fecha, hora) => new Date(fecha + 'T' + (hora || '00:00') + ':00-03:00');
const ahoraISO = () => new Date().toISOString();
"""


def webhook_respuesta(fl, nombre, ruta, pos, metodo="GET"):
    """Webhook que contesta con una pagina (el boton de Telegram o del Centro abre el navegador)."""
    return fl.nodo(nombre, "n8n-nodes-base.webhook", 2,
                   {"httpMethod": metodo, "path": ruta, "responseMode": "responseNode",
                    "options": {}}, pos,
                   {"webhookId": str(uuid.uuid5(uuid.NAMESPACE_URL, "apardian-wh/" + ruta))})


def responder(fl, nombre, expr, pos):
    return fl.nodo(nombre, "n8n-nodes-base.respondToWebhook", 1.1, {
        "respondWith": "text",
        "responseBody": "={{ %s }}" % expr,
        "options": {"responseHeaders": {"entries": [
            {"name": "Content-Type", "value": "text/html; charset=utf-8"}]}},
    }, pos)


def telegram_botones(fl, nombre, cfg, operacion, pos):
    """Mensaje o foto de Telegram con dos botones que abren el link de aprobacion."""
    p = {
        "chatId": "={{ $('%s').first().json.TELEGRAM_CHAT_ID }}" % cfg,
        "replyMarkup": "inlineKeyboard",
        "inlineKeyboard": {"rows": [{"row": {"buttons": [
            {"text": "Aprobar", "additionalFields": {"url": "={{ $json.url_aprobar }}"}},
            {"text": "No publicar", "additionalFields": {"url": "={{ $json.url_rechazar }}"}},
        ]}}]},
    }
    if operacion == "sendPhoto":
        p.update({"operation": "sendPhoto", "binaryData": False, "file": "={{ $json.foto }}",
                  "additionalFields": {"caption": "={{ $json.texto }}", "parse_mode": "HTML"}})
    else:
        p.update({"text": "={{ $json.texto }}",
                  "additionalFields": {"appendAttribution": False, "parse_mode": "HTML",
                                       "disable_web_page_preview": False}})
    return fl.nodo(nombre, "n8n-nodes-base.telegram", 1.2, p, pos,
                   {"credentials": cred("telegramApi", "Telegram Apardian")})


# ================================================================== 07
def f07():
    fl = Flujo("APARDIAN 07 · Aprobación de Instagram")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 10})
    v = dict(CONFIG_BASE)
    v.update({
        "URL_APROBAR_IG": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-ig-aprobar", "string"),
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
        "HORAS_ANTES": (36, "number"),
    })
    cfg = config(fl, "Config", v)
    cal = leer_hoja(fl, "Leer Calendario", cfg, "Calendario")
    pedir = codigo(fl, "¿Qué hay que aprobar?", JS_HTML + JS_HORA_UY + r"""
// Las publicaciones pendientes de las próximas HORAS_ANTES horas (y las que
// quedaron sin aprobar de hoy). Una por mensaje, en orden de fecha.
// Mientras sigan pendientes, se vuelven a pedir todos los días: es el recordatorio.
// Solo pasa lo que Lupa dejó en "ok" (columna revision): lo frenado no llega.
const c = $('Config').first().json;
const ahora = Date.now(), lim = ahora + Number(c.HORAS_ANTES || 36) * 3600e3;
const link = (id, acc) => c.URL_APROBAR_IG + '?id=' + encodeURIComponent(id) + '&a=' + acc + '&t=' + encodeURIComponent(c.TOKEN);
const out = [];
for (const r of $('Leer Calendario').all()) {
  const f = r.json;
  if (String(f.estado || '').trim() !== 'pendiente' || !f.id) continue;
  if (!/^ok/.test(String(f.revision || '').trim())) continue;
  const t = enUY(f.fecha, f.hora).getTime();
  if (isNaN(t) || t > lim || t < ahora - 12 * 3600e3) continue;
  const urls = String(f.urls || '').split('|').filter(Boolean);
  const foto = urls.find(u => /\.jpe?g$/i.test(u)) || '';
  const cuando = new Date(t).toLocaleString('es-UY', { timeZone: 'America/Montevideo', weekday: 'long', day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
  const pie = String(f.pie || '');
  // el pie de una foto de Telegram tiene 1024 caracteres como máximo
  const vista = pie.length > 600 ? pie.slice(0, 600) + '…' : pie;
  const nombre = { STORY: 'HISTORIA', IMAGE: 'POSTEO', CAROUSEL: 'CARRUSEL', REEL: 'REEL' }[f.tipo] || f.tipo;
  const nota = String(f.revision || '').split('nota: ')[1];
  const texto = '<b>' + esc(nombre) + ' · ' + esc(f.titulo) + '</b>\n' + esc(cuando) +
    ' · ' + urls.length + ' archivo' + (urls.length === 1 ? '' : 's') + '\n\n' + esc(vista) +
    (!foto && urls[0] ? '\n\n<a href="' + esc(urls[0]) + '">Ver el video</a>' : '') +
    '\n\n🔍 Lupa: ' + (nota ? esc(nota) : 'sin observaciones') +
    '\n\n<i>Si lo aprobás, se publica solo a esa hora.</i>';
  out.push({ json: { id: f.id, t, foto, texto, url_aprobar: link(f.id, 'aprobar'), url_rechazar: link(f.id, 'rechazar') } });
}
out.sort((x, y) => x.json.t - y.json.t);
return out;
""")
    hay_foto = si(fl, "¿Tiene imagen?", "!!$json.foto")
    tg_foto = telegram_botones(fl, "Pedir aprobación (foto)", cfg, "sendPhoto", (fl.x, -120))
    tg_txt = telegram_botones(fl, "Pedir aprobación (texto)", cfg, "sendMessage", (fl.x, 120))
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, cal, pedir, hay_foto)
    fl.unir(hay_foto, tg_foto, 0)
    fl.unir(hay_foto, tg_txt, 1)

    # ---- segunda entrada: Martin toca "Aprobar" o "No publicar"
    y = 600
    wh = webhook_respuesta(fl, "Botón de Telegram", "apardian-ig-aprobar", (0, y))
    cfg2 = config(fl, "Config aprobación", {
        "SHEET_ID": CONFIG_BASE["SHEET_ID"],
        "TELEGRAM_CHAT_ID": CONFIG_BASE["TELEGRAM_CHAT_ID"],
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
    }, pos=(240, y))
    cal2 = leer_hoja(fl, "Leer Calendario (aprobación)", cfg2, "Calendario", pos=(480, y))
    decidir = codigo(fl, "Validar y decidir", JS_HTML + JS_HORA_UY + r"""
const c = $('Config aprobación').first().json;
const q = $('Botón de Telegram').first().json.query || {};
const pagina = (titulo, txt) => '<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<body style="font-family:system-ui;background:#F8F7F6;color:#171717;padding:32px"><h2 style="margin:0 0 8px">' +
  esc(titulo) + '</h2><p>' + esc(txt) + '</p></body>';
if (!claveOk(q.t, c.TOKEN)) {
  return [{ json: { ok: false, html: pagina('Link no válido', 'El token no coincide (o todavía es el de ejemplo). No se cambió nada.') } }];
}
// Desde el Centro el link trae la pieza entera (d, base64url): así una pieza
// que Luz rehízo o reemplazó entra a la hoja aunque todavía no esté, o con sus
// archivos y su pie nuevos. Solo se aceptan archivos de apardianstudio.com/ig.
let d = null;
if (q.d) {
  try { d = JSON.parse(Buffer.from(String(q.d).replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8')); }
  catch (e) { return [{ json: { ok: false, html: pagina('Link roto', 'No pude leer la pieza que mandó el Centro. No se cambió nada.') } }]; }
  const urls = String(d.urls || '').split('|').filter(Boolean);
  if (String(d.id || '') !== String(q.id) || !['IMAGE', 'CAROUSEL', 'REEL', 'STORY'].includes(d.tipo) ||
      !urls.length || urls.some(u => !/^https:\/\/apardianstudio\.com\/ig\/[^\s"'<>]+$/.test(u)) ||
      !/^\d{4}-\d{2}-\d{2}$/.test(String(d.fecha || '')) || !/^\d{2}:\d{2}$/.test(String(d.hora || ''))) {
    return [{ json: { ok: false, html: pagina('Pieza no válida', 'Los datos que mandó el Centro no están completos. No se cambió nada.') } }];
  }
}
const f = $input.all().map(r => r.json).find(r => String(r.id) === String(q.id)) || d;
if (!f) return [{ json: { ok: false, html: pagina('No encontré esa publicación', String(q.id || '')) } }];
if (f.publicado_en) return [{ json: { ok: false, html: pagina('Ya está publicada', f.titulo + ' · ' + f.publicado_en) } }];
const aprobar = q.a === 'aprobar';
const desde = d ? 'Centro' : 'Telegram';
const fila = Object.assign(d && aprobar ? { fecha: d.fecha, hora: d.hora, tipo: d.tipo, titulo: String(d.titulo || ''),
                                 archivos: String(d.archivos || ''), urls: d.urls, pie: String(d.pie || '').slice(0, 2200),
                                 primer_comentario: String(d.primer_comentario || ''), revision: 'ok' } : {},
  { id: String(q.id), estado: aprobar ? 'aprobado' : 'rechazado',
    aprobado_por: aprobar ? 'Martin (' + desde + ')' : '', aprobado_en: aprobar ? ahoraISO() : '', error: '' });
const cuando = enUY(f.fecha, f.hora).toLocaleString('es-UY', { timeZone: 'America/Montevideo', weekday: 'long', day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
return [{ json: { ok: true, fila,
  html: pagina(aprobar ? 'Aprobado ✓' : 'No se publica', (aprobar ? f.titulo + ' sale el ' + cuando + '.' : f.titulo + ' no sale.') +
               (d ? ' Ya podés cerrar esta pestaña y volver al Centro.' : '')),
  telegram_text: (aprobar ? '✅ Aprobado: ' : '✖️ No se publica: ') + '<b>' + esc(f.titulo) + '</b>' + (aprobar ? '\nSale el ' + esc(cuando) + '.' : '') } }];
""", pos=(720, y))
    valido = si(fl, "¿Válido?", "$json.ok", pos=(960, y))
    fila = codigo(fl, "Fila aprobación", "return [{ json: $input.first().json.fila }];", pos=(1200, y - 100))
    g = escribir_hoja(fl, "Guardar aprobación", cfg2, "Calendario", "appendOrUpdate", pos=(1440, y - 100))
    tg = telegram(fl, "Confirmar en Telegram", cfg2, pos=(1680, y - 100),
                  texto="$('Validar y decidir').first().json.telegram_text")
    r_ok = responder(fl, "Página: listo", "$('Validar y decidir').first().json.html", (1920, y - 100))
    r_no = responder(fl, "Página: no válido", "$('Validar y decidir').first().json.html", (1200, y + 100))
    fl.cadena(wh, cfg2, cal2, decidir, valido)
    fl.unir(valido, fila, 0)
    fl.unir(valido, r_no, 1)
    fl.cadena(fila, g, tg, r_ok)
    return fl


# ================================================================== 08
JS_PUBLICAR = r"""
// Publica UNA fila aprobada con la API de Instagram (Graph API).
// Imagen: contenedor + media_publish. Carrusel: un contenedor por hoja
// (is_carousel_item), el contenedor padre y media_publish. Reel: contenedor
// REELS, esperar a que Instagram termine de procesar el video, y publicar.
// Historia: contenedor STORIES con la imagen o el video (sin pie ni comentario).
const c = $('Config').first().json;
const x = $input.first().json;
const f = x.fila;
const G = String(c.GRAPH_URL).replace(/\/$/, '');
const tok = c.ACCESS_TOKEN;
const dormir = ms => new Promise(r => setTimeout(r, ms));

async function api(metodo, ruta, params) {
  try {
    const r = await this.helpers.httpRequest({
      method: metodo, url: G + ruta, qs: Object.assign({ access_token: tok }, params || {}), json: true,
    });
    return typeof r === 'string' ? JSON.parse(r) : r;
  } catch (e) {
    const cuerpo = (e && e.cause && e.cause.response && e.cause.response.data) || (e && e.response && e.response.body) || null;
    const msj = cuerpo && cuerpo.error ? cuerpo.error.message + ' (código ' + cuerpo.error.code + ')' : (e.description || e.message || String(e));
    throw new Error(ruta.split('?')[0] + ': ' + msj);
  }
}
const llamar = api.bind(this);

async function esperar(id, intentos, pausa) {
  for (let i = 0; i < intentos; i++) {
    const s = await llamar('GET', '/' + id, { fields: 'status_code,status' });
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED')
      throw new Error('Instagram no pudo procesar el archivo: ' + (s.status || s.status_code));
    await dormir(pausa);
  }
  throw new Error('Instagram sigue procesando el archivo; se reintenta en la próxima vuelta');
}

const urls = String(f.urls || '').split('|').filter(Boolean);
const user = '/' + c.IG_USER_ID;
let creacion;
try {
  if (f.tipo === 'IMAGE') {
    creacion = (await llamar('POST', user + '/media', { image_url: urls[0], caption: f.pie })).id;
    await esperar(creacion, 6, 5000);
  } else if (f.tipo === 'CAROUSEL') {
    if (urls.length < 2 || urls.length > 10) throw new Error('un carrusel lleva de 2 a 10 archivos, este tiene ' + urls.length);
    const hijos = [];
    for (const u of urls) {
      const p = /\.mp4$/i.test(u) ? { media_type: 'VIDEO', video_url: u, is_carousel_item: true }
                                  : { image_url: u, is_carousel_item: true };
      hijos.push((await llamar('POST', user + '/media', p)).id);
    }
    for (const h of hijos) await esperar(h, 12, 5000);
    creacion = (await llamar('POST', user + '/media', { media_type: 'CAROUSEL', children: hijos.join(','), caption: f.pie })).id;
    await esperar(creacion, 6, 5000);
  } else if (f.tipo === 'REEL') {
    const video = urls.find(u => /\.mp4$/i.test(u));
    const tapa = urls.find(u => /\.jpe?g$/i.test(u));
    const p = { media_type: 'REELS', video_url: video, caption: f.pie, share_to_feed: true };
    if (tapa) p.cover_url = tapa;
    creacion = (await llamar('POST', user + '/media', p)).id;
    await esperar(creacion, 10, 20000);       // hasta ~3 minutos y medio
  } else if (f.tipo === 'STORY') {
    const u = urls[0];
    const esVideo = /\.mp4$/i.test(u);
    const p = esVideo ? { media_type: 'STORIES', video_url: u } : { media_type: 'STORIES', image_url: u };
    creacion = (await llamar('POST', user + '/media', p)).id;
    await esperar(creacion, esVideo ? 10 : 6, esVideo ? 15000 : 5000);
  } else {
    throw new Error('tipo desconocido: ' + f.tipo);
  }
  const pub = await llamar('POST', user + '/media_publish', { creation_id: creacion });
  let aviso_com = '';
  if (f.primer_comentario && f.tipo !== 'STORY') {
    try { await llamar('POST', '/' + pub.id + '/comments', { message: f.primer_comentario }); }
    catch (e) { aviso_com = '\n(No se pudo dejar el primer comentario: ' + e.message + ')'; }
  }
  let link = '';
  try { link = (await llamar('GET', '/' + pub.id, { fields: 'permalink' })).permalink || ''; } catch (e) {}
  return [{ json: {
    fila: { id: f.id, estado: 'publicado', publicado_en: new Date().toISOString(), ig_media_id: pub.id, error: '' },
    telegram_text: (f.tipo === 'STORY' ? '📣 Historia arriba: <b>' : '📣 Publicado: <b>') + esc(f.titulo) + '</b>' + (link ? '\n' + esc(link) : '') + esc(aviso_com),
  } }];
} catch (e) {
  // "sigue procesando" no es un error de la fila: queda aprobada y se reintenta
  const reintentar = /sigue procesando/.test(e.message);
  return [{ json: {
    fila: { id: f.id, estado: reintentar ? 'aprobado' : 'error', error: String(e.message).slice(0, 480) },
    telegram_text: (reintentar ? '⏳ ' : '⚠️ No se pudo publicar ') + '<b>' + esc(f.titulo) + '</b>\n' + esc(e.message),
  } }];
}
"""


def f08():
    fl = Flujo("APARDIAN 08 · Publicador de Instagram")
    # Las horas del calendario son 11:00, 12:30, 13:00 y 19:30: 10 corridas por
    # día en vez de 96 (cada 15 minutos gastaba más que todo el plan de n8n).
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "0,30 11-13,19-20 * * *"})
    v = dict(CONFIG_BASE)
    v.update({
        "IG_USER_ID": ("PEGAR_IG_USER_ID", "string"),
        "ACCESS_TOKEN": ("PEGAR_TOKEN_DE_LARGA_DURACION", "string"),
        "GRAPH_URL": ("https://graph.facebook.com/v22.0", "string"),
        "VENCE_HORAS": (48, "number"),
    })
    cfg = config(fl, "Config", v)
    cal = leer_hoja(fl, "Leer Calendario", cfg, "Calendario")
    elegir = codigo(fl, "¿Qué toca publicar?", JS_HTML + JS_HORA_UY + r"""
// Solo filas "aprobado", sin publicar, cuya hora ya llegó. Una por vuelta:
// cada 15 minutos sale como mucho una publicación, nunca una ráfaga.
// Lo aprobado que quedó colgado más de VENCE_HORAS no se publica de golpe:
// se marca como error y se avisa, para que Martin decida.
const c = $('Config').first().json;
const ahora = Date.now(), vence = Number(c.VENCE_HORAS || 48) * 3600e3;
const listas = [], vencidas = [];
for (const r of $('Leer Calendario').all()) {
  const f = r.json;
  if (String(f.estado || '').trim() !== 'aprobado' || f.publicado_en || !f.id) continue;
  const t = enUY(f.fecha, f.hora).getTime();
  if (isNaN(t) || t > ahora) continue;
  (ahora - t > vence ? vencidas : listas).push({ f, t });
}
listas.sort((x, y) => x.t - y.t);
const out = [];
if (listas.length) out.push({ json: { accion: 'publicar', fila: listas[0].f } });
for (const v of vencidas)
  out.push({ json: { accion: 'vencida', fila: v.f,
    telegram_text: '⚠️ Quedó aprobada pero sin publicar más de ' + c.VENCE_HORAS + ' h: <b>' + esc(v.f.titulo) +
                   '</b>. La marqué como error; si querés que salga, cambiá la fecha y volvé a poner "aprobado".' } });
return out;
""")
    hay = si(fl, "¿Publicar?", "$json.accion === 'publicar'")
    limite = fl.nodo("Cupo del día", "n8n-nodes-base.httpRequest", 4.2, {
        "method": "GET",
        "url": "={{ $('Config').first().json.GRAPH_URL }}/{{ $('Config').first().json.IG_USER_ID }}/content_publishing_limit",
        "sendQuery": True,
        "queryParameters": {"parameters": [
            {"name": "fields", "value": "config,quota_usage"},
            {"name": "access_token", "value": "={{ $('Config').first().json.ACCESS_TOKEN }}"},
        ]},
        "options": {"timeout": 30000},
    }, None, {"onError": "continueRegularOutput"})
    cupo = codigo(fl, "¿Hay cupo?", JS_HTML + r"""
// Instagram deja publicar una cantidad fija por 24 h (hoy 50 por cuenta).
const d = (($json.data || [])[0]) || {};
const usado = Number(d.quota_usage || 0), total = Number((d.config || {}).quota_total || 50);
const f = $('¿Publicar?').first().json.fila;
if ($json.error) return [{ json: { seguir: false, fila: f, telegram_text: '⚠️ No pude consultar el cupo de Instagram: ' + esc(JSON.stringify($json.error).slice(0, 300)) + '. Revisá el token.' } }];
if (usado >= total - 1) return [{ json: { seguir: false, fila: f, telegram_text: '⏸️ Cupo de Instagram casi lleno (' + usado + '/' + total + '). ' + esc(f.titulo) + ' sale en la próxima vuelta con cupo.' } }];
return [{ json: { seguir: true, fila: f } }];
""")
    sigue = si(fl, "¿Sigue?", "$json.seguir")
    publicar = codigo(fl, "Publicar en Instagram", JS_HTML + JS_PUBLICAR)
    fila = codigo(fl, "Fila resultado", "return [{ json: $input.first().json.fila }];")
    g = escribir_hoja(fl, "Guardar resultado", cfg, "Calendario")
    tg = telegram(fl, "Avisar a Martin", cfg, texto="$('Publicar en Instagram').first().json.telegram_text")
    tg_cupo = telegram(fl, "Avisar cupo/token", cfg, pos=(fl.x - 960, 240),
                       texto="$json.telegram_text")
    # vencidas
    fila_v = codigo(fl, "Fila vencida", "return { json: { id: $json.fila.id, estado: 'error', error: 'vencida sin publicar' } };",
                    por_item=True, pos=(960, 360))
    g_v = escribir_hoja(fl, "Guardar vencida", cfg, "Calendario", pos=(1200, 360))
    tg_v = telegram(fl, "Avisar vencida", cfg, pos=(1440, 360),
                    texto="$('¿Publicar?').item.json.telegram_text")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, cal, elegir, hay)
    fl.unir(hay, limite, 0)
    fl.unir(hay, fila_v, 1)
    fl.cadena(limite, cupo, sigue)
    fl.unir(sigue, publicar, 0)
    fl.unir(sigue, tg_cupo, 1)
    fl.cadena(publicar, fila, g, tg)
    fl.cadena(fila_v, g_v, tg_v)
    return fl


# ================================================================== 09
def f09():
    """Lo que Martin aprueba en el Centro (ofertas y entrenamiento de Radar)
    llega acá: el botón de la app abre este link con los datos y la clave."""
    fl = Flujo("APARDIAN 09 · Radar: conexión con el Centro")
    wh = webhook_respuesta(fl, "Link del Centro", "apardian-radar", (0, 0))
    fl.x = 240
    cfg = config(fl, "Config", {
        "SHEET_ID": CONFIG_BASE["SHEET_ID"],
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA-DE-RADAR", "string"),
    })
    validar = codigo(fl, "Validar", JS_HTML + JS_RADAR + r"""
const c = $('Config').first().json;
const q = $('Link del Centro').first().json.query || {};
const pagina = (titulo, txt) => '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<body style="font-family:system-ui;background:#0B0B0B;color:#F8F7F6;padding:40px"><p style="letter-spacing:.2em;font-size:11px;color:#FF0033">APARDIAN · RADAR</p>' +
  '<h2 style="margin:8px 0">' + esc(titulo) + '</h2><p style="color:#9A9592">' + esc(txt) + '</p></body>';
if (!claveOk(q.t, c.TOKEN)) return [{ json: { ok: false, html: pagina('Link no válido', 'La clave no coincide con la de n8n (o todavía es la de ejemplo). Revisala en el Centro → Radar → Conexión.') } }];
let d;
try { d = JSON.parse(Buffer.from(String(q.d || '').replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8')); }
catch (e) { return [{ json: { ok: false, html: pagina('No pude leer los datos', 'Volvé a tocar el botón en el Centro.') } }]; }
const ahora = new Date().toISOString();
if (q.tipo === 'oferta') {
  const campos = ['id','estado','mercado','servicio','nombre','para_quien','que_incluye','plazo','precio_desde','moneda','vigencia_hasta','angulo'];
  const f = {}; for (const k of campos) f[k] = String(d[k] == null ? '' : d[k]).slice(0, 1500);
  if (!f.id || !['activa','pausada'].includes(f.estado)) return [{ json: { ok: false, html: pagina('Oferta incompleta', 'Falta el id o el estado.') } }];
  f.actualizado = ahora;
  return [{ json: { ok: true, tipo: 'oferta', filas: [f], html: pagina(f.estado === 'activa' ? 'Oferta activada ✓' : 'Oferta pausada',
    f.nombre + (f.estado === 'activa' ? ': Radar ya la puede usar en los mails.' : ': Radar deja de usarla.') + ' Podés cerrar esta pestaña.') } }];
}
if (q.tipo === 'entrenamiento') {
  const filas = (Array.isArray(d) ? d : []).filter(x => x && x.clave)
    .map(x => ({ clave: String(x.clave).slice(0, 60), pregunta: String(x.pregunta || '').slice(0, 300), respuesta: String(x.respuesta || '').slice(0, 2000), actualizado: ahora }));
  if (!filas.length) return [{ json: { ok: false, html: pagina('Nada para guardar', 'No llegaron respuestas.') } }];
  return [{ json: { ok: true, tipo: 'entrenamiento', filas, html: pagina('Radar aprendió ✓', filas.length + ' respuestas guardadas. Desde el próximo mail las usa. Podés cerrar esta pestaña.') } }];
}
return [{ json: { ok: false, html: pagina('Pedido desconocido', String(q.tipo || '')) } }];
""")
    valido = si(fl, "¿Válido?", "$json.ok")
    tipo = si(fl, "¿Es oferta?", "$json.tipo === 'oferta'", pos=(fl.x, -120))
    filas_o = codigo(fl, "Filas oferta", "return $('Validar').first().json.filas.map(f => ({ json: f }));", pos=(fl.x, -240))
    g_o = escribir_hoja(fl, "Guardar oferta", cfg, "Ofertas", "appendOrUpdate", pos=(fl.x + 240, -240))
    filas_e = codigo(fl, "Filas entrenamiento", "return $('Validar').first().json.filas.map(f => ({ json: f }));", pos=(fl.x, 0))
    g_e = escribir_hoja(fl, "Guardar entrenamiento", cfg, "Entrenamiento", "appendOrUpdate", pos=(fl.x + 240, 0), clave="clave")
    r_o = responder(fl, "Página: oferta", "$('Validar').first().json.html", (fl.x + 480, -240))
    r_e = responder(fl, "Página: entrenamiento", "$('Validar').first().json.html", (fl.x + 480, 0))
    r_no = responder(fl, "Página: no válido", "$('Validar').first().json.html", (fl.x - 240, 240))
    fl.cadena(wh, cfg, validar, valido)
    fl.unir(valido, tipo, 0)
    fl.unir(valido, r_no, 1)
    fl.unir(tipo, filas_o, 0)
    fl.unir(tipo, filas_e, 1)
    fl.cadena(filas_o, g_o, r_o)
    fl.cadena(filas_e, g_e, r_e)
    return fl


# ================================================================== 11
JS_PAGINA = r"""
// Página con la estética del Centro. n8n la sirve dentro de un sandbox: los
// links externos van con target="_blank" (abre otra pestaña y no se pierde lo
// que no se guardó), "Volver" con target="_top" y el formulario con dirección absoluta.
const pagina = (titulo, cuerpo) => '<!doctype html><html lang="es"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(titulo) + '</title>' +
  '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Work+Sans:wght@400;500;600&display=swap">' +
  '<style>:root{--bg:#0B0B0B;--panel:#141414;--panel-2:#1C1C1C;--fg:#F8F7F6;--muted:#9A9592;--line:rgba(248,247,246,.12);' +
  '--red:#FF0033;--ok:#3DDC84;--display:"Anton",Impact,sans-serif;--body:"Work Sans",-apple-system,Arial,sans-serif}' +
  '*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 var(--body)}' +
  'main{max-width:860px;margin:0 auto;padding:28px 16px 120px}.eye{letter-spacing:.2em;font-size:11px;color:var(--red);text-transform:uppercase}' +
  'h1{font:400 clamp(34px,7vw,56px)/1 var(--display);text-transform:uppercase;margin:6px 0 10px}h2{font:400 26px/1.1 var(--display);text-transform:uppercase;margin:36px 0 12px}' +
  'p,.muted{color:var(--muted)}a{color:var(--fg)}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0 0 14px}' +
  '.meta{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:baseline}.meta b{font-size:17px}.meta span{color:var(--muted);font-size:13px}.meta .rep{color:var(--fg)}' +
  '.tag{display:inline-block;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--red);margin-bottom:4px}' +
  '.links{font-size:13px;color:var(--muted);margin:4px 0 8px;word-break:break-word}details{margin:6px 0 10px;font-size:13px;color:var(--muted)}summary{cursor:pointer}' +
  'label.lbl{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:10px 0 4px}' +
  'input[type=text],textarea{width:100%;background:var(--panel-2);color:var(--fg);border:1px solid var(--line);border-radius:10px;padding:10px;font:15px/1.5 var(--body);margin-top:4px}' +
  'textarea{min-height:200px;resize:vertical}.dec{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}' +
  '.dec label{display:flex;gap:8px;align-items:center;border:1px solid var(--line);border-radius:999px;padding:8px 14px;cursor:pointer}' +
  '.dec label:has(input:checked){border-color:var(--fg);background:var(--panel-2)}.dec input{accent-color:var(--red)}' +
  '.btn{display:inline-block;border:1px solid var(--fg);background:none;color:var(--fg);border-radius:999px;padding:10px 18px;font:600 14px var(--body);cursor:pointer;text-decoration:none}' +
  '.btn.rojo{background:var(--red);border-color:var(--red);color:#fff}.barra{position:fixed;left:0;right:0;bottom:0;background:rgba(11,11,11,.94);border-top:1px solid var(--line);padding:12px 16px}' +
  '.barra div{max-width:860px;margin:0 auto;display:flex;gap:10px;align-items:center;justify-content:space-between}.barra .btn{padding:10px 14px;white-space:nowrap}.ok{color:var(--ok)}' +
  '</style></head><body><main>' + cuerpo + '</main></body></html>';
"""


def f11():
    """La bandeja: Martin ve cada mail, seguimiento y WhatsApp que escribió
    Radar, lo edita si quiere y lo aprueba o lo descarta. Se abre desde el
    Centro (Radar → Bandeja) o desde el aviso de Telegram."""
    fl = Flujo("APARDIAN 11 · Radar: bandeja de aprobación")
    wh = webhook_respuesta(fl, "Abrir bandeja", "apardian-bandeja", (0, 0))
    fl.x = 240
    cfg = config(fl, "Config", {
        "SHEET_ID": CONFIG_BASE["SHEET_ID"],
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA-DE-RADAR", "string"),
        # Vacío: se arma solo con la dirección de esta misma instancia.
        "URL_GUARDAR": ("", "string"),
        "MAX_EN_PANTALLA": (60, "number"),
    })
    clave = codigo(fl, "Clave", JS_HTML + JS_PAGINA + r"""
const q = $('Abrir bandeja').first().json.query || {};
return [{ json: { ok: claveOk(q.t, $('Config').first().json.TOKEN),
  html: pagina('Link no válido', '<p class="eye">APARDIAN · Radar</p><h1>Link no válido</h1><p>La clave no coincide con la de n8n. Abrí la bandeja desde el Centro → Radar.</p>') } }];
""")
    clave_ok = si(fl, "¿Clave válida?", "$json.ok")
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    armar = codigo(fl, "Armar bandeja", JS_HTML + JS_WA + JS_PAGINA + r"""
const c = $('Config').first().json;
const w = $('Abrir bandeja').first().json;
const q = w.query || {};
const h = w.headers || {};
const guardar = c.URL_GUARDAR || ('https://' + (h['x-forwarded-host'] || h.host) + '/webhook/apardian-bandeja-guardar');
const L = $('Leer Leads').all().map(r => r.json).filter(l => l.id);
const max = Number(c.MAX_EN_PANTALLA) || 60;
const mails = L.filter(l => l.estado === 'borrador');
const segs = L.filter(l => /^borrador_seg[12]$/.test(l.estado || ''));
const was = L.filter(l => l.estado === 'wa_borrador');
const enCola = L.filter(l => /^aprobado/.test(l.estado || '')).length;
const url = x => /^https?:\/\//.test(x) ? x : 'https://' + x;
const rep = l => l.rating ? '★ ' + String(l.rating).replace('.', ',') + (l.resenas ? ' · ' + l.resenas + ' reseñas' : '') : '';
const ficha = l => '<div class="meta"><b>' + esc(l.nombre) + '</b><span>' + esc([l.rubro, l.pais || 'Uruguay'].filter(Boolean).join(' · ')) + '</span>' +
  (rep(l) ? '<span class="rep">' + esc(rep(l)) + '</span>' : '') + (l.score ? '<span>score ' + esc(l.score) + '</span>' : '') + '</div>' +
  '<div class="links">' + (l.web ? '<a target="_blank" rel="noopener" href="' + esc(url(l.web)) + '">' + esc(String(l.web).replace(/^https?:\/\/(www\.)?/, '')) + '</a>' : 'sin web') +
  (l.instagram ? ' · <a target="_blank" rel="noopener" href="' + esc(url(l.instagram)) + '">Instagram</a>' : '') +
  (l.email ? ' · ' + esc(l.email) : '') + (l.telefono ? ' · ' + esc(l.telefono) : '') + '</div>' +
  (l.problemas ? '<details><summary>Qué vio Radar</summary><p>' + esc(l.problemas).replace(/\n/g, '<br>') + '</p></details>' : '');
const decision = (id, ops) => '<div class="dec">' + ops.map(([v, t]) =>
  '<label><input type="radio" name="d_' + esc(id) + '" value="' + v + '"> ' + t + '</label>').join('') + '</div>';
const tarjeta = (tipo, l, tag, asunto, cuerpo) => '<article class="card" data-tipo="' + tipo + '"><span class="tag">' + tag + '</span>' + ficha(l) +
  (tipo === 'seg' ? '<details><summary>Primer mail: ' + esc(l.asunto) + '</summary><p>' + esc(l.borrador).replace(/\n/g, '<br>') + '</p></details>' : '') +
  '<label class="lbl">Asunto<input type="text" name="a_' + esc(l.id) + '" value="' + esc(asunto) + '" maxlength="200"></label>' +
  '<label class="lbl">Mail (para ' + esc(l.email) + ')<textarea name="c_' + esc(l.id) + '">' + esc(cuerpo) + '</textarea></label>' +
  decision(l.id, [['aprobar', 'Aprobar'], ['descartar', 'Descartar']]) + '</article>';
const tarjetaWa = l => { const n = waNumero(l.telefono, l.pais);
  return '<article class="card" data-tipo="wa"><span class="tag">WhatsApp · lo mandás vos</span>' + ficha(l) +
  '<label class="lbl">Mensaje<textarea data-wa="' + esc(l.id) + '" name="w_' + esc(l.id) + '">' + esc(l.wa_mensaje) + '</textarea></label>' +
  '<p><a class="btn" target="_blank" rel="noopener" id="wa_' + esc(l.id) + '" data-tel="' + esc(n) + '" href="https://wa.me/' + esc(n) + '?text=' + encodeURIComponent(l.wa_mensaje || '') + '">Abrir en WhatsApp</a></p>' +
  '<p class="muted">WhatsApp se abre aparte; después marcá "Ya lo mandé" y guardá.</p>' +
  decision(l.id, [['mandado', 'Ya lo mandé'], ['descartar', 'Descartar']]) + '</article>'; };
const seccion = (titulo, lista, f) => lista.length ? '<h2>' + titulo + ' · ' + lista.length + '</h2>' +
  (lista.length > max ? '<p>Se muestran ' + max + '. Guardá y volvé a abrir para ver el resto.</p>' : '') + lista.slice(0, max).map(f).join('') : '';
const total = mails.length + segs.length + was.length;
const cuerpo = '<p class="eye">APARDIAN · Radar</p><h1>Bandeja</h1>' +
  '<p>Nada sale sin tu OK. Lo que aprobás sale desde contacto@ en el horario de oficina de cada país, hasta 90 por día. ' +
  'Lo que no marques queda para después; los cambios en un texto se guardan al aprobarlo.</p>' +
  (enCola ? '<p class="ok">' + (enCola === 1 ? '1 aprobado espera' : enCola + ' aprobados esperan') + ' su horario.</p>' : '') +
  (total ? '' : '<div class="card"><p>No hay nada para aprobar. Radar escribe de lunes a viernes a las 8.</p></div>') +
  '<form method="post" action="' + esc(guardar) + '" accept-charset="utf-8">' +
  '<input type="hidden" name="t" value="' + esc(c.TOKEN) + '">' +
  seccion('Mails nuevos', mails, l => tarjeta('mail', l, 'Primer mail', l.asunto, l.borrador)) +
  seccion('Seguimientos', segs, l => tarjeta('seg', l, 'Seguimiento ' + String(l.estado).slice(-1), l.seg_asunto, l.seg_cuerpo)) +
  seccion('WhatsApp a mano', was, tarjetaWa) +
  (total ? '<div class="barra"><div><button type="button" class="btn" id="todos">Aprobar los que faltan</button>' +
    '<button type="submit" class="btn rojo" id="guardar">Guardar</button></div></div>' : '') +
  '</form><script>' +
  'document.querySelectorAll("textarea[data-wa]").forEach(function(t){t.addEventListener("input",function(){var a=document.getElementById("wa_"+t.dataset.wa);a.href="https://wa.me/"+a.dataset.tel+"?text="+encodeURIComponent(t.value);});});' +
  'var b=document.getElementById("todos");if(b)b.onclick=function(){document.querySelectorAll("[data-tipo=mail],[data-tipo=seg]").forEach(function(c){if(!c.querySelector(".dec input:checked"))c.querySelector("input[value=aprobar]").checked=true;});cuenta();};' +
  'function cuenta(){var n=document.querySelectorAll(".dec input:checked").length,g=document.getElementById("guardar");if(g)g.textContent=n?"Guardar "+n+(n===1?" decisión":" decisiones"):"Guardar";}' +
  'document.addEventListener("change",cuenta);' +
  '</script>';
return [{ json: { html: pagina('Bandeja · Radar', cuerpo) } }];
""")
    r = responder(fl, "Mostrar bandeja", "$json.html", None)
    r_mal = responder(fl, "Página: clave mal", "$('Clave').first().json.html", (fl.x - 960, 200))
    fl.cadena(wh, cfg, clave, clave_ok)
    fl.unir(clave_ok, leads, 0)
    fl.unir(clave_ok, r_mal, 1)
    fl.cadena(leads, armar, r)

    # ---- segunda entrada: el botón Guardar de la bandeja
    y = 500
    wh2 = webhook_respuesta(fl, "Guardar bandeja", "apardian-bandeja-guardar", (0, y), metodo="POST")
    cfg2 = config(fl, "Config guardar", {
        "SHEET_ID": CONFIG_BASE["SHEET_ID"],
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA-DE-RADAR", "string"),
    }, pos=(240, y))
    clave2 = codigo(fl, "Clave guardar", JS_HTML + JS_PAGINA + r"""
const b = $('Guardar bandeja').first().json.body || {};
return [{ json: { ok: claveOk(b.t, $('Config guardar').first().json.TOKEN),
  html: pagina('Clave incorrecta', '<p class="eye">APARDIAN · Radar</p><h1>No se guardó</h1><p>La clave no coincide. Abrí la bandeja desde el Centro.</p>') } }];
""", pos=(480, y + 220))
    clave2_ok = si(fl, "¿Clave válida? (guardar)", "$json.ok", pos=(720, y + 220))
    r2_mal = responder(fl, "Página: clave mal (guardar)", "$('Clave guardar').first().json.html", (960, y + 320))
    leads2 = leer_hoja(fl, "Leer Leads (guardar)", cfg2, "Leads", pos=(480, y))
    aplicar = codigo(fl, "Aplicar decisiones", JS_HTML + JS_PAGINA + JS_RADAR + r"""
// Solo cambia lo que sigue esperando aprobación: si un lead respondió o ya se
// decidió en otra pestaña, se deja como está.
const c = $('Config guardar').first().json;
const b = $('Guardar bandeja').first().json.body || {};
const h = $('Guardar bandeja').first().json.headers || {};
const volver = '<p><a class="btn" target="_top" href="' + esc('https://' + (h['x-forwarded-host'] || h.host) +
  '/webhook/apardian-bandeja?t=' + encodeURIComponent(c.TOKEN)) + '">Volver a la bandeja</a></p>';
if (!claveOk(b.t, c.TOKEN)) return [{ json: { filas: [], html: pagina('Clave incorrecta', '<p class="eye">APARDIAN · Radar</p><h1>No se guardó</h1><p>La clave no coincide. Abrí la bandeja desde el Centro.</p>') } }];
const L = new Map($('Leer Leads (guardar)').all().map(r => [String(r.json.id), r.json]));
const txt = (x, max) => String(x == null ? '' : x).replace(/\r\n/g, '\n').trim().slice(0, max);
const filas = [], cuenta = { aprobados: 0, descartados: 0, whatsapp: 0, saltados: 0 };
for (const k of Object.keys(b)) {
  if (!k.startsWith('d_')) continue;
  const id = k.slice(2), d = b[k], l = L.get(id);
  if (!l) { cuenta.saltados++; continue; }
  const e = String(l.estado || '');
  if (e === 'borrador' && d === 'aprobar') {
    filas.push({ id, estado: 'aprobado', asunto: txt(b['a_' + id], 200) || l.asunto, borrador: txt(b['c_' + id], 6000) || l.borrador }); cuenta.aprobados++;
  } else if (e === 'borrador' && d === 'descartar') {
    filas.push({ id, estado: 'descartado' }); cuenta.descartados++;
  } else if (/^borrador_seg[12]$/.test(e) && d === 'aprobar') {
    filas.push({ id, estado: 'aprobado_seg' + e.slice(-1), seg_asunto: txt(b['a_' + id], 200) || l.seg_asunto, seg_cuerpo: txt(b['c_' + id], 6000) || l.seg_cuerpo }); cuenta.aprobados++;
  } else if (/^borrador_seg[12]$/.test(e) && d === 'descartar') {
    // sin más seguimientos, pero si responde igual se lo atiende
    filas.push({ id, estado: 'sin_seguimiento', seg_asunto: '', seg_cuerpo: '' }); cuenta.descartados++;
  } else if (e === 'wa_borrador' && d === 'mandado') {
    filas.push({ id, estado: 'wa_enviado', wa_mensaje: txt(b['w_' + id], 1500) || l.wa_mensaje, respuesta: 'WhatsApp mandado a mano · ' + hoyUY() }); cuenta.whatsapp++;
  } else if (e === 'wa_borrador' && d === 'descartar') {
    filas.push({ id, estado: 'descartado' }); cuenta.descartados++;
  } else cuenta.saltados++;
}
const html = pagina('Guardado · Radar', '<p class="eye">APARDIAN · Radar</p><h1>Guardado</h1>' +
  '<div class="card"><p class="ok">' + cuenta.aprobados + (cuenta.aprobados === 1 ? ' aprobado' : ' aprobados') + '</p><p>Salen desde contacto@ en el horario de oficina de cada país, hasta 90 por día.</p>' +
  '<p>' + cuenta.descartados + (cuenta.descartados === 1 ? ' descartado · ' : ' descartados · ') + cuenta.whatsapp + ' WhatsApp marcados como mandados' +
  (cuenta.saltados ? ' · ' + cuenta.saltados + ' sin cambios (ya no estaban esperando)' : '') + '</p></div>' + volver);
return [{ json: { filas, html } }];
""", pos=(720, y))
    hay = si(fl, "¿Hay cambios?", "$json.filas.length > 0", pos=(960, y))
    filas = codigo(fl, "Filas", "return $input.first().json.filas.map(f => ({ json: f }));", pos=(1200, y - 100))
    g = escribir_hoja(fl, "Guardar decisiones", cfg2, "Leads", pos=(1440, y - 100))
    r1 = responder(fl, "Página: guardado", "$('Aplicar decisiones').first().json.html", (1680, y - 100))
    r2 = responder(fl, "Página: sin cambios", "$('Aplicar decisiones').first().json.html", (1200, y + 100))
    fl.cadena(wh2, cfg2, clave2, clave2_ok)
    fl.unir(clave2_ok, leads2, 0)
    fl.unir(clave2_ok, r2_mal, 1)
    fl.cadena(leads2, aplicar, hay)
    fl.unir(hay, filas, 0)
    fl.unir(hay, r2, 1)
    fl.cadena(filas, g, r1)
    return fl


# ================================================================== 12
def f12():
    """Manda lo que Martin aprobó en la bandeja: cada hora de 9 a 17, en el
    horario de oficina del destinatario y nunca por encima del tope diario."""
    fl = Flujo("APARDIAN 12 · Radar: envío de lo aprobado")
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "0 9-17 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({
        # Desde contacto@apardianstudio.com por el SMTP de Hostinger (25/10/2026).
        "MI_EMAIL": ("Martin Apardian <contacto@apardianstudio.com>", "string"),
        # Correo gratis de Hostinger: 100 por día por casilla. 90 deja lugar
        # para lo que Martin conteste a mano desde contacto@.
        "LIMITE_TOTAL_DIA": (90, "number"),
        "DIRECCION_POSTAL": ("", "string"),
    })
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    bajas = leer_hoja(fl, "Leer Bajas", cfg, "Bajas")
    elegir = codigo(fl, "Elegir aprobados", JS_RADAR + JS_IDIOMA + r"""
const c = $('Config').first().json;
const bm = new Set(), bd = new Set();
for (const r of $('Leer Bajas').all()) {
  if (r.json.email) bm.add(String(r.json.email).toLowerCase());
  if (r.json.dominio) bd.add(String(r.json.dominio).toLowerCase());
}
const todos = $('Leer Leads').all().map(r => r.json).filter(l => l.id);
const libre = Math.max(0, (Number(c.LIMITE_TOTAL_DIA) || 90) - mailsHoy(todos));
// Una casilla recibe como mucho un mail por día, aunque sean dos sucursales.
const yaHoy = new Set(todos.filter(l => String(l.ultimo_envio || '') === hoyUY()).map(l => String(l.email || '').toLowerCase()));
const unaPorCasilla = l => { const e = String(l.email).toLowerCase(); if (yaHoy.has(e)) return false; yaHoy.add(e); return true; };
// La línea para darse de baja (Ley 18.331 / CAN-SPAM) va siempre, aunque se haya borrado al editar.
const BAJA = { es: "Si no te interesa, respondé 'no' y no te escribo más.",
  en: "If this isn't for you, just reply 'no' and I won't write again.",
  pt: "Se não tiver interesse, responda 'não' e não escrevo mais." };
const tieneBaja = t => /no te escribo m[aá]s|no le escribo m[aá]s|no vuelvo a escribir|won'?t (write|email)|n[aã]o (te |lhe )?escrevo mais|n[aã]o volto a escrever/i.test(t);
const completar = (l, cuerpo) => {
  let t = String(cuerpo || '').trim();
  const dir = String(c.DIRECCION_POSTAL || '').trim();
  if (String(l.pais || '') === 'Estados Unidos' && dir && !t.includes(dir.slice(0, 15))) t += '\n\n' + dir;
  if (!tieneBaja(t)) t += '\n\n' + BAJA[idiomaDe(l)];
  return t;
};
const horas = Math.max(1, 18 - horaEn('America/Montevideo'));
const tanda = Math.ceil(libre / horas);
if (!tanda) return [];
const orden = e => e === 'aprobado' ? 1 : 0;   // los seguimientos primero
return todos
  .filter(l => /^aprobado(_seg[12])?$/.test(l.estado || '') && l.email)
  .filter(l => { const e = String(l.email).toLowerCase(); return !bm.has(e) && !bd.has(dominioPropio(e)); })
  .filter(l => String(l.pais || '') !== 'Estados Unidos' || String(c.DIRECCION_POSTAL || '').trim())
  .filter(l => horarioDeOficina(l.zona || 'America/Montevideo') && String(l.ultimo_envio || '') !== hoyUY())
  .filter(l => { const seg = l.estado !== 'aprobado';
    return String((seg ? l.seg_asunto : l.asunto) || '').trim() && String((seg ? l.seg_cuerpo : l.borrador) || '').trim(); })
  .sort((x, y) => orden(x.estado) - orden(y.estado) || Number(y.score) - Number(x.score))
  .filter(unaPorCasilla)
  .slice(0, tanda)
  .map(l => { const seg = l.estado !== 'aprobado';
    return { json: { lead: l, n: seg ? Number(l.estado.slice(-1)) : 0, para: l.email,
      asunto: String(seg ? l.seg_asunto : l.asunto).trim(), cuerpo: completar(l, seg ? l.seg_cuerpo : l.borrador) } }; });
""")
    # Antes de mandar se marca "enviando" con la fecha de hoy: si después falla
    # la planilla o se corta la ejecución, ese mail no vuelve a salir y cuenta
    # para el tope del día.
    marcar = codigo(fl, "Marcar enviando", JS_RADAR + r"""
return $input.all().map(it => ({ json: { id: it.json.lead.id,
  estado: it.json.n ? 'enviando_seg' + it.json.n : 'enviando', ultimo_envio: hoyUY() } }));
""")
    g_marca = escribir_hoja(fl, "Guardar enviando", cfg, "Leads")
    tanda_n = codigo(fl, "Tanda", "return $('Elegir aprobados').all().map((it, i) => ({ json: it.json, pairedItem: { item: i } }));")
    env = enviar_mail(fl, "Enviar (contacto@)", "Config")
    fila = codigo(fl, "Fila enviada", JS_RADAR + r"""
const x = $('Tanda').item.json;
const rechazado = Array.isArray($json.rejected) && $json.rejected.length;
// El servidor rechazó la dirección: no existe, no se reintenta.
if (rechazado) return { json: { id: x.lead.id, estado: 'rebote', respuesta: 'rebote · ' + hoyUY() + ' · el servidor rechazó la dirección' } };
// Falla de conexión o de la casilla: vuelve a aprobado y se reintenta en la próxima hora.
if ($json.error) return { json: { id: x.lead.id, estado: x.lead.estado, ultimo_envio: x.lead.ultimo_envio || '',
  respuesta: 'envío falló · ' + hoyUY() + ' · ' + String($json.error.message || JSON.stringify($json.error)).slice(0, 200) } };
if (!x.n) return { json: { id: x.lead.id, estado: 'enviado', fecha_envio: hoyUY(), ultimo_envio: hoyUY(), seguimientos: 0 } };
return { json: { id: x.lead.id, estado: 'seguimiento_' + x.n, seguimientos: x.n, ultimo_envio: hoyUY() } };
""", por_item=True)
    g = escribir_hoja(fl, "Guardar envío", cfg, "Leads")
    fallo = codigo(fl, "¿Falló algo?", JS_HTML + r"""
const f = $('Fila enviada').all().map(i => i.json).filter(x => /^envío falló/.test(x.respuesta || ''));
if (!f.length) return [];
return [{ json: { telegram_text: '<b>Radar · no salieron ' + f.length + ' mails</b>\nQuedan aprobados y se reintenta en la próxima hora. ' +
  'Si se repite, revisá la contraseña de contacto@ en n8n (credencial SMTP).\n<i>' + esc(f[0].respuesta) + '</i>' } }];
""")
    tg = telegram(fl, "Avisar falla", cfg)
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, elegir, marcar, g_marca, tanda_n, env, fila, g, fallo, tg)
    return fl


# ================================================================== 10
def f10():
    fl = Flujo("APARDIAN 10 · Radar: reporte del día")
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "0 18 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({"FECHA_INICIO": ("PEGAR_FECHA_DE_ARRANQUE", "string"),
              "FECHA_FIN": ("", "string"),
              "CUPOS_POR_SEMANA": ("10,20,30", "string"),
              "URL_BANDEJA": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-bandeja", "string"),
              "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA-DE-RADAR", "string")})
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    resumen = codigo(fl, "Resumen", JS_HTML + JS_FECHA + JS_RADAR + r"""
// Lo que hizo Radar hoy y si hay algo para mirar. Nada de esto manda mails.
const c = $('Config').first().json;
const L = $('Leer Leads').all().map(r => r.json).filter(l => l.id);
const h = hoyUY();
const n = f => L.filter(f).length;
const cupos = String(c.CUPOS_POR_SEMANA || '10,20,30').split(',').map(Number).filter(x => x > 0);
const ini = /^\d{4}-\d{2}-\d{2}$/.test(String(c.FECHA_INICIO || '')) ? c.FECHA_INICIO : '';
const semana = ini ? Math.max(0, Math.floor((diasDesde(ini) + 1) / 7)) : 0;
const cupoManana = cupos[Math.min(semana, cupos.length - 1)] || 10;
const hoyEnv = L.filter(l => String(l.fecha_envio || '') === h);
const enviados = n(l => l.fecha_envio);
const interes = L.filter(l => ['interesado', 'pide_precio'].includes(l.estado));
const fin = /^\d{4}-\d{2}-\d{2}$/.test(String(c.FECHA_FIN || '')) ? c.FECHA_FIN : '';
const terminada = fin && h >= fin, antesDeArrancar = ini && diasDesde(ini) < 0;
const rebotes = n(l => l.estado === 'rebote');
const stock = n(l => l.estado === 'auditado' && l.email);
const porPais = {};
for (const l of hoyEnv) porPais[l.pais || 'Uruguay'] = (porPais[l.pais || 'Uruguay'] || 0) + 1;
const avisos = [];
if (enviados >= 40 && rebotes / enviados > 0.05) avisos.push('⚠️ Rebotan ' + Math.round(100 * rebotes / enviados) + '% de los mails. Pausá el envío (apagá el flujo 12) y revisá las direcciones: un dominio con muchos rebotes termina en spam.');
if (!terminada && stock < cupoManana * 2) avisos.push('Quedan ' + stock + ' leads listos para escribir. Subí BUSQUEDAS_POR_DIA en el flujo 01 o agregá búsquedas en la hoja Busquedas.');
if (!ini) avisos.push('Falta FECHA_INICIO en los flujos 03 y 10: Radar está en el cupo de la semana 1.');
if (fin && h === fin) avisos.push('Hoy termina la prueba. Desde mañana Radar no busca ni escribe mails nuevos; los seguimientos y las respuestas siguen mientras los flujos estén prendidos.');
else if (terminoPrueba(c)) avisos.push('La prueba terminó el ' + fin + ': no hay mails nuevos. Cuando no queden seguimientos, apagá los flujos o poné otra FECHA_FIN.');
const pend = n(l => l.estado === 'borrador' || /^borrador_seg/.test(l.estado || '')), was = n(l => l.estado === 'wa_borrador');
const cola = n(l => /^aprobado/.test(l.estado || ''));
const lineas = [
  '<b>Radar · ' + esc(h) + '</b>' + (antesDeArrancar ? ' · arranca el ' + esc(ini)
    : ini && fin && !terminoPrueba(c) ? ' · prueba: día ' + (diasDesde(ini) + 1) + ' de ' + (diasDesde(ini) - diasDesde(fin) + 1) : ''),
  'Mails nuevos hoy: <b>' + hoyEnv.length + '</b>' + (Object.keys(porPais).length ? ' (' + Object.entries(porPais).map(([p, k]) => esc(p) + ' ' + k).join(', ') + ')' : ''),
  'En total: ' + enviados + ' enviados · ' + interes.length + ' con interés · ' + n(l => l.estado === 'baja') + ' bajas · ' + rebotes + ' rebotes',
  terminada ? 'Prueba terminada: no se escriben mails nuevos.' : 'Mañana: cupo de ' + cupoManana + ' · ' + stock + ' leads listos · ' + n(l => l.estado === 'nuevo') + ' por auditar',
  'Para aprobar: ' + pend + ' mails · ' + was + ' WhatsApp · ' + cola + ' aprobados esperando horario',
  '<a href="' + esc(c.URL_BANDEJA + '?t=' + encodeURIComponent(c.TOKEN)) + '">Abrir la bandeja</a>',
];
// solo los que contestaron hoy (f05 escribe 'categoria · fecha · resumen')
const nuevosInteres = interes.filter(l => String(l.respuesta || '').includes(' · ' + h + ' · ')).slice(-8).map(l => '• ' + esc(l.nombre) + ' (' + esc(l.pais || 'Uruguay') + ', ' + esc(l.servicio || '') + '): ' + esc(String(l.respuesta || '').slice(0, 120)));
if (nuevosInteres.length) lineas.push('', '<b>Para contestar vos</b>', ...nuevosInteres);
const errores = { 'no se pudieron auditar': n(l => l.estado === 'error_auditoria'), 'sin mail escrito': n(l => l.estado === 'error_redaccion'),
  'fallaron al enviarse': n(l => l.estado === 'error_envio'), 'quedaron a medio enviar (revisalos en contacto@ → Enviados)': n(l => /^enviando/.test(l.estado || '') && String(l.ultimo_envio || '') < h) };
const lineasErr = Object.entries(errores).filter(([, k]) => k).map(([t, k]) => '• ' + k + ' ' + t);
if (lineasErr.length) lineas.push('', '<b>Para revisar</b>', ...lineasErr);
if (avisos.length) lineas.push('', ...avisos.map(esc));
return [{ json: { telegram_text: lineas.join('\n') } }];
""")
    tg = telegram(fl, "Mandar reporte", cfg)
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, resumen, tg)
    return fl


# ================================================================== 13
def f13():
    """Cómo le fue a cada publicación (Martin, 28/10/2026: que los agentes
    aprendan qué contenido vende). Todos los días anota en la hoja Metricas el
    alcance, los guardados, los compartidos, las visitas al perfil y los
    seguidores que trajo cada pieza de los últimos 30 días. Luz lee esa hoja
    cada semana para decidir qué se repite y qué se deja. Solo lee: no publica
    ni cambia nada en Instagram."""
    fl = Flujo("APARDIAN 13 · Instagram: métricas")
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "30 7 * * *"})
    v = dict(CONFIG_BASE)
    v.update({
        "IG_USER_ID": ("PEGAR_IG_USER_ID", "string"),
        "ACCESS_TOKEN": ("PEGAR_TOKEN_DE_LARGA_DURACION", "string"),
        "GRAPH_URL": ("https://graph.facebook.com/v22.0", "string"),
        "DIAS": (30, "number"),
    })
    cfg = config(fl, "Config", v)
    cal = leer_hoja(fl, "Leer Calendario", cfg, "Calendario")
    traer = codigo(fl, "Traer métricas", JS_HTML + r"""
const c = $('Config').first().json;
const G = String(c.GRAPH_URL).replace(/\/$/, ''), tok = c.ACCESS_TOKEN;
async function api(ruta, params) {
  const r = await this.helpers.httpRequest({ method: 'GET', url: G + ruta,
    qs: Object.assign({ access_token: tok }, params || {}), json: true });
  return typeof r === 'string' ? JSON.parse(r) : r;
}
const llamar = api.bind(this);
// La pieza del calendario que corresponde a cada publicación (el flujo 08 guarda ig_media_id)
const porMedia = {};
for (const r of $('Leer Calendario').all()) if (r.json.ig_media_id) porMedia[String(r.json.ig_media_id)] = r.json;
const desde = Date.now() - Number(c.DIAS || 30) * 864e5;
let lista;
try {
  lista = (await llamar('/' + c.IG_USER_ID + '/media', { limit: 60,
    fields: 'id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count' })).data || [];
} catch (e) {
  return [{ json: { _error: 'No pude leer las publicaciones: ' + String(e.message || e).slice(0, 300) } }];
}
// Instagram cambia qué métricas da según el tipo: se pide de más y, si rechaza, de menos.
const JUEGOS = ['reach,saved,shares,total_interactions,views,profile_visits,follows',
                'reach,saved,shares,total_interactions,views', 'reach,saved,shares,total_interactions', 'reach'];
const hoy = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Montevideo' }).format(new Date());
const out = [];
for (const m of lista) {
  if (Date.parse(m.timestamp) < desde) continue;
  const met = {};
  for (const juego of JUEGOS) {
    try {
      const r = await llamar('/' + m.id + '/insights', { metric: juego });
      for (const x of (r.data || [])) met[x.name] = (x.values && x.values[0] ? x.values[0].value : x.total_value && x.total_value.value) || 0;
      break;
    } catch (e) { /* prueba con menos métricas */ }
  }
  const p = porMedia[String(m.id)] || {};
  out.push({ json: {
    media_id: String(m.id), fecha: String(m.timestamp || '').slice(0, 10),
    tipo: m.media_product_type === 'REELS' ? 'REEL' : m.media_product_type === 'STORY' ? 'STORY' : m.media_type,
    pieza: p.id || '', titulo: p.titulo || String(m.caption || '').split('\n')[0].slice(0, 80),
    link: m.permalink || '', likes: m.like_count || 0, comentarios: m.comments_count || 0,
    alcance: met.reach || 0, guardados: met.saved || 0, compartidos: met.shares || 0,
    interacciones: met.total_interactions || 0, vistas: met.views || 0,
    visitas_perfil: met.profile_visits || 0, seguidores: met.follows || 0, actualizado: hoy,
  } });
}
return out.length ? out : [{ json: { _vacio: true } }];
""")
    ok = si(fl, "¿Hay datos?", "!$json._error && !$json._vacio")
    g = escribir_hoja(fl, "Guardar métricas", cfg, "Metricas", "appendOrUpdate", clave="media_id")
    error = codigo(fl, "¿Falló?", JS_HTML + r"""
const e = $input.first().json._error;
return e ? [{ json: { telegram_text: '<b>Métricas de Instagram</b>\n' + esc(e) + '\nRevisá el token del flujo 13 (tiene que tener instagram_manage_insights).' } }] : [];
""", pos=(fl.x - 240, 220))
    tg = telegram(fl, "Avisar falla", cfg, pos=(fl.x, 220))
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, cal, traer, ok, g)
    fl.unir(ok, error, 1)
    fl.unir(error, tg)
    return fl


if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for f, archivo in ((f01, "01_prospector.json"), (f02, "02_auditor.json"),
                       (f03, "03_redactor.json"), (f04, "04_seguimiento.json"),
                       (f05, "05_respuestas.json"), (f06, "06_bienvenida_whatsapp.json"),
                       (f07, "07_aprobacion_instagram.json"), (f08, "08_publicador_instagram.json"),
                       (f09, "09_radar_conexion_centro.json"), (f10, "10_radar_reporte.json"),
                       (f11, "11_radar_bandeja.json"), (f12, "12_radar_envio.json"), (f13, "13_instagram_metricas.json")):
        fl = f()
        nombres = {n["name"] for n in fl.nodos}
        for a, salidas in fl.con.items():
            assert a in nombres, a
            for s in salidas["main"]:
                for c in s:
                    assert c["node"] in nombres, c["node"]
        print(fl.guardar(archivo), len(fl.nodos), "nodos")
