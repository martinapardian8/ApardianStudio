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
MODELO = "claude-opus-5-5"


def prompt(nombre):
    with open(os.path.join(AQUI, "prompts", nombre + ".md"), encoding="utf-8") as f:
        return f.read().strip()


# ------------------------------------------------------------------ JS comun
JS_CLAUDE = r"""
function cuerpoClaude(system, user, maxTokens, effort) {
  return {
    model: '%s',
    max_tokens: maxTokens,
    system: system,
    messages: [{ role: 'user', content: user }],
    output_config: { effort: effort },
    fallbacks: 'default',
  };
}
""" % MODELO

JS_LEER = r"""
// Lee la respuesta de Claude. Antes de tocar content mira stop_reason:
// un rechazo o un corte por max_tokens no se trata como respuesta valida.
function leerClaude(r) {
  if (!r || r.error) return { ok: false, motivo: 'error_http: ' + JSON.stringify(r && r.error || '').slice(0, 300) };
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

JS_MIME = r"""
// Mail en texto plano, UTF-8, listo para la API de Gmail (base64url).
function mime({ de, para, asunto, cuerpo, enRespuestaA }) {
  const b64 = s => Buffer.from(s, 'utf8').toString('base64');
  const h = [
    'From: ' + de,
    'To: ' + para,
    'Subject: =?UTF-8?B?' + b64(asunto) + '?=',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: base64',
  ];
  if (enRespuestaA) h.push('In-Reply-To: ' + enRespuestaA, 'References: ' + enRespuestaA);
  const raw = h.join('\r\n') + '\r\n\r\n' + b64(cuerpo).replace(/(.{76})/g, '$1\r\n');
  return Buffer.from(raw, 'utf8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
"""

JS_HTML = r"""
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
"""

JS_FECHA = r"""
const hoy = () => new Date().toISOString().slice(0, 10);
const diasDesde = f => f ? Math.floor((Date.now() - new Date(f + 'T12:00:00').getTime()) / 86400000) : -1;
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


def escribir_hoja(fl, nombre, cfg, pestana, operacion="update", pos=None):
    p = {
        "operation": operacion,
        "documentId": hoja(cfg),
        "sheetName": {"__rl": True, "value": pestana, "mode": "name"},
        "columns": {"mappingMode": "autoMapInputData", "value": {},
                    "matchingColumns": ["id"] if operacion == "update" else [],
                    "schema": []},
        "options": {},
    }
    return fl.nodo(nombre, "n8n-nodes-base.googleSheets", 4.5, p, pos,
                   {"credentials": cred("googleSheetsOAuth2Api", "Google Sheets")})


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
        "options": {"timeout": 180000},
    }, pos, {"credentials": cred("httpHeaderAuth", "Anthropic API"),
             "onError": "continueRegularOutput", "retryOnFail": True,
             "maxTries": 3, "waitBetweenTries": 5000})


def gmail_api(fl, nombre, metodo, url, cuerpo=None, pos=None):
    p = {"method": metodo, "url": url,
         "authentication": "predefinedCredentialType",
         "nodeCredentialType": "gmailOAuth2", "options": {}}
    if cuerpo:
        p.update({"sendBody": True, "specifyBody": "json", "jsonBody": cuerpo})
    return fl.nodo(nombre, "n8n-nodes-base.httpRequest", 4.2, p, pos,
                   {"credentials": cred("gmailOAuth2", "Gmail Apardian"),
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
    fl = Flujo("APARDIAN 01 · Prospector")
    a, b = disparadores(fl, {"field": "weeks", "triggerAtDay": [1], "triggerAtHour": 8})
    cfg = config(fl, "Config", dict(CONFIG_BASE))
    busq = codigo(fl, "Búsquedas", r"""
// Rubro x ciudad. Agregá o sacá filas: cada una es una búsqueda en Google Maps.
// Ojo: cada búsqueda trae hasta 20 negocios y cuesta (ver README, costos).
const rubros = [
  { rubro: 'restaurante', q: 'restaurantes' },
  { rubro: 'parrilla', q: 'parrillas' },
  { rubro: 'cafe', q: 'cafeterías de especialidad' },
  { rubro: 'salon', q: 'salones de eventos' },
  { rubro: 'inmobiliaria', q: 'inmobiliarias' },
  { rubro: 'marca', q: 'tienda de productos artesanales' },
];
const ciudades = ['Pocitos, Montevideo', 'Carrasco, Montevideo', 'Ciudad Vieja, Montevideo',
                  'Punta del Este', 'Ciudad de la Costa, Canelones'];
const out = [];
for (const r of rubros) for (const c of ciudades)
  out.push({ json: { rubro: r.rubro, ciudad: c, query: r.q + ' en ' + c + ', Uruguay' } });
return out;
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
                     "places.rating,places.userRatingCount,places.nationalPhoneNumber,places.googleMapsUri",
        }]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ textQuery: $json.query, languageCode: 'es', regionCode: 'UY', pageSize: 20 }) }}",
        "options": {"timeout": 30000},
    }, None, {"credentials": cred("httpHeaderAuth", "Google Places API"),
              "onError": "continueRegularOutput"})
    plano = codigo(fl, "Aplanar", r"""
// Una fila por negocio. Places devuelve una respuesta por búsqueda, en orden.
const busq = $('Búsquedas').all();
const out = [];
$input.all().forEach((it, i) => {
  const b = busq[i] ? busq[i].json : {};
  for (const p of (it.json.places || [])) {
    out.push({ json: {
      id: p.id,
      nombre: (p.displayName && p.displayName.text) || '',
      web: p.websiteUri || '',
      telefono: p.nationalPhoneNumber || '',
      direccion: p.formattedAddress || '',
      rating: p.rating || '',
      reseñas: p.userRatingCount || 0,
      maps: p.googleMapsUri || '',
      rubro: b.rubro, ciudad: b.ciudad,
    } });
  }
});
return out;
""")
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    dedupe = codigo(fl, "Solo nuevos", JS_FECHA + r"""
// Saca los que ya están en la planilla (por id de Google o por web).
const ya = new Set(), webs = new Set();
for (const r of $('Leer Leads').all()) {
  if (r.json.id) ya.add(String(r.json.id));
  if (r.json.web) webs.add(String(r.json.web).replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''));
}
const vistos = new Set(), out = [];
for (const it of $('Aplanar').all()) {
  const p = it.json;
  const w = p.web.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '');
  if (!p.id || ya.has(p.id) || vistos.has(p.id) || (w && webs.has(w))) continue;
  vistos.add(p.id);
  out.push({ json: {
    id: p.id, fecha: hoy(), rubro: p.rubro, nombre: p.nombre, web: p.web,
    instagram: '', email: '', telefono: p.telefono, ciudad: p.ciudad,
    fuente: 'google_places', score: '', servicio: '', problemas: '',
    estado: p.web ? 'nuevo' : 'sin_web', asunto: '', borrador: '', fecha_envio: '',
    seguimientos: 0, respuesta: '',
    notas: [p.direccion, p.rating ? ('rating ' + p.rating + ' (' + p['reseñas'] + ' reseñas)') : '', p.maps].filter(Boolean).join(' · '),
    draft_id: '', thread_id: '', mensaje_id: '',
  } });
}
return out;
""")
    guardar = escribir_hoja(fl, "Agregar a Leads", cfg, "Leads", "append")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, busq, places, plano, leads, dedupe, guardar)
    return fl


# ================================================================== 02
def f02():
    fl = Flujo("APARDIAN 02 · Auditor")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 9})
    v = dict(CONFIG_BASE); v["LIMITE_DIARIO"] = (15, "number")
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    elegir = codigo(fl, "Elegir nuevos", r"""
const lim = $('Config').first().json.LIMITE_DIARIO || 15;
return $input.all()
  .filter(r => r.json.estado === 'nuevo' && r.json.web)
  .slice(0, lim)
  .map(r => {
    let web = String(r.json.web);
    if (!/^https?:\/\//.test(web)) web = 'https://' + web;
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
const mails = [...new Set([...html.matchAll(/mailto:([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/gi)].map(x => x[1].toLowerCase()))];
const ig = m(/href=["'](https?:\/\/(?:www\.)?instagram\.com\/[^"'?#]+)/i);
const s = {
  url: lead.web,
  carga: falla ? ('no cargó: ' + falla) : 'ok',
  https: lead.web.startsWith('https://'),
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
const usuario = 'Negocio: ' + lead.nombre + '\nRubro: ' + lead.rubro + '\nCiudad: ' + lead.ciudad +
  '\nFicha de Google: ' + (lead.notas || '') +
  '\n\nSeñales medidas en la web:\n' + JSON.stringify(s, null, 2) +
  '\n\nTexto visible de la portada (extracto):\n' + texto.slice(0, 6000);
return { json: { lead, senales: s, usuario } };
""", por_item=True)
    prep = codigo(fl, "Prompt auditor", JS_CLAUDE + r"""
const SYSTEM = %s;
return { json: { ...$json, claude_body: cuerpoClaude(SYSTEM, $json.usuario, 8000, 'medium') } };
""" % json.dumps(prompt("auditor"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · auditor")
    leer = codigo(fl, "Leer auditoría", JS_LEER + r"""
const base = $('Prompt auditor').item.json;
const lead = base.lead, s = base.senales;
const r = leerClaude($json);
if (!r.ok) return { json: { id: lead.id, estado: 'error_auditoria', notas: (lead.notas || '') + ' · auditor: ' + r.motivo } };
const a = r.data;
const email = (s.mails_publicados || [])[0] || '';
const score = Number(a.score_oportunidad) || 0;
let estado = 'auditado';
if (score < 60) estado = 'descartado';
else if (!email) estado = 'sin_email';
const problemas = (a.problemas || []).map(p => '• ' + p.problema + ' — ' + p.evidencia + ' (' + p.impacto + ')').join('\n');
return { json: {
  id: lead.id, instagram: s.link_instagram || '', email, score,
  servicio: a.servicio_principal || '', problemas, estado,
  notas: JSON.stringify({ auditoria: a, ficha: lead.notas || '' }),
} };
""", por_item=True)
    guardar = escribir_hoja(fl, "Guardar auditoría", cfg, "Leads")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, elegir, bajar, senales, prep, cl, leer, guardar)
    return fl


# ================================================================== 03
def f03():
    fl = Flujo("APARDIAN 03 · Redactor y envío")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 10})
    v = dict(CONFIG_BASE)
    v.update({
        "MI_EMAIL": ("Martin Apardian <martin@TU-DOMINIO-DE-ENVIO>", "string"),
        "SCORE_MINIMO": (60, "number"),
        "MAX_POR_DIA": (20, "number"),
        "AUTO_ENVIO": (False, "boolean"),
        "SCORE_AUTO": (80, "number"),
        "URL_APROBAR": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-aprobar", "string"),
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
    })
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    bajas = leer_hoja(fl, "Leer Bajas", cfg, "Bajas")
    elegir = codigo(fl, "Elegir auditados", r"""
const c = $('Config').first().json;
const bm = new Set(), bd = new Set();
for (const r of $('Leer Bajas').all()) {
  if (r.json.email) bm.add(String(r.json.email).toLowerCase());
  if (r.json.dominio) bd.add(String(r.json.dominio).toLowerCase());
}
// Corre una vez por día: MAX_POR_DIA es el tope de mails nuevos por día.
const todos = $('Leer Leads').all().map(r => r.json);
const cupo = c.MAX_POR_DIA || 20;
return todos
  .filter(l => l.estado === 'auditado' && Number(l.score) >= (c.SCORE_MINIMO || 60) && l.email)
  .filter(l => { const e = String(l.email).toLowerCase(); return !bm.has(e) && !bd.has(e.split('@')[1]); })
  .sort((x, y) => Number(y.score) - Number(x.score))
  .slice(0, cupo)
  .map(l => ({ json: l }));
""")
    prep = codigo(fl, "Prompt redactor", JS_CLAUDE + r"""
const SYSTEM = %s;
let audit = {};
try { audit = JSON.parse($json.notas || '{}').auditoria || {}; } catch (e) {}
const usuario = 'Negocio: ' + $json.nombre + '\nRubro: ' + $json.rubro + '\nCiudad: ' + $json.ciudad +
  '\nWeb: ' + $json.web + ($json.instagram ? '\nInstagram: ' + $json.instagram : '') +
  '\n\nAuditoría:\n' + JSON.stringify(audit, null, 2);
return { json: { lead: $json, claude_body: cuerpoClaude(SYSTEM, usuario, 6000, 'medium') } };
""" % json.dumps(prompt("redactor"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · redactor")
    leer = codigo(fl, "Leer mail", JS_LEER + JS_MIME + r"""
const c = $('Config').first().json;
const lead = $('Prompt redactor').item.json.lead;
const r = leerClaude($json);
if (!r.ok || r.data.omitir) {
  return { json: { omitir: true, fila: { id: lead.id, estado: r.ok ? 'descartado' : 'error_redaccion',
    notas: lead.notas } } };
}
const m = r.data;
const raw = mime({ de: c.MI_EMAIL, para: lead.email, asunto: m.asunto, cuerpo: m.cuerpo });
return { json: { omitir: false, lead, asunto: m.asunto, cuerpo: m.cuerpo,
  gmail_body: { message: { raw } },
  auto: !!c.AUTO_ENVIO && Number(lead.score) >= (c.SCORE_AUTO || 80) } };
""", por_item=True)
    hay = si(fl, "¿Hay mail?", "!$json.omitir")
    descarte = codigo(fl, "Fila descartada", "return { json: $json.fila };", por_item=True,
                      pos=(fl.x, 220))
    g_desc = escribir_hoja(fl, "Marcar descartado", cfg, "Leads", pos=(fl.x + 240, 220))
    borr = gmail_api(fl, "Crear borrador Gmail", "POST",
                     "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                     "={{ JSON.stringify($json.gmail_body) }}")
    datos = codigo(fl, "Datos del borrador", JS_HTML + r"""
const c = $('Config').first().json;
const x = $('Leer mail').item.json;
const draft = $json.id || '';
const link = acc => c.URL_APROBAR + '?id=' + encodeURIComponent(x.lead.id) + '&k=inicial&a=' + acc + '&t=' + encodeURIComponent(c.TOKEN);
return { json: {
  fila: { id: x.lead.id, estado: draft ? 'borrador' : 'error_borrador', asunto: x.asunto,
          borrador: x.cuerpo, draft_id: draft },
  draft_id: draft, auto: x.auto,
  telegram_text: '<b>Mail listo para ' + esc(x.lead.nombre) + '</b> (' + esc(x.lead.rubro) + ', score ' + esc(x.lead.score) + ')\n' +
    esc(x.lead.web) + '\n\n<b>' + esc(x.asunto) + '</b>\n' + esc(x.cuerpo) +
    '\n\nPodés editarlo en Gmail (Borradores) antes de aprobar.\n' +
    '<a href="' + esc(link('enviar')) + '">✅ Enviar</a>   <a href="' + esc(link('descartar')) + '">✖️ Descartar</a>',
} };
""", por_item=True)
    g_borr = codigo(fl, "Fila borrador", "return { json: $json.fila };", por_item=True,
                    pos=(fl.x, 220))
    g_borr2 = escribir_hoja(fl, "Guardar borrador", cfg, "Leads", pos=(fl.x + 240, 220))
    # el estado "borrador" se guarda primero; recien despues se decide si se manda solo
    auto = si(fl, "¿Auto-envío?",
              "$('Datos del borrador').item.json.auto && !!$('Datos del borrador').item.json.draft_id")
    env_auto = gmail_api(fl, "Enviar (auto)", "POST",
                         "https://gmail.googleapis.com/gmail/v1/users/me/drafts/send",
                         "={{ JSON.stringify({ id: $('Datos del borrador').item.json.draft_id }) }}")
    fila_auto = codigo(fl, "Fila enviada (auto)", JS_FECHA + r"""
const x = $('Datos del borrador').item.json;
return { json: { id: x.fila.id, estado: $json.id ? 'enviado' : 'error_envio', fecha_envio: hoy(),
  thread_id: $json.threadId || '', mensaje_id: $json.id || '', seguimientos: 0 } };
""", por_item=True)
    g_auto = escribir_hoja(fl, "Guardar envío (auto)", cfg, "Leads")
    tg = telegram(fl, "Pedir aprobación", cfg, pos=(fl.x - 720, 440),
                  texto="$('Datos del borrador').item.json.telegram_text")

    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, elegir, prep, cl, leer, hay)
    fl.unir(hay, borr, 0)
    fl.unir(hay, descarte, 1)
    fl.unir(descarte, g_desc)
    fl.cadena(borr, datos, g_borr, g_borr2, auto)
    fl.unir(auto, env_auto, 0)
    fl.unir(auto, tg, 1)
    fl.cadena(env_auto, fila_auto, g_auto)

    # ---- segunda entrada: Martin toca "Enviar" o "Descartar" en Telegram
    y = 800
    wh = webhook(fl, "Aprobación (link de Telegram)", "apardian-aprobar", pos=(0, y))
    cfg2 = config(fl, "Config aprobación", {
        "SHEET_ID": CONFIG_BASE["SHEET_ID"],
        "TELEGRAM_CHAT_ID": CONFIG_BASE["TELEGRAM_CHAT_ID"],
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
    }, pos=(240, y))
    leads2 = leer_hoja(fl, "Leer Leads (aprobación)", cfg2, "Leads", pos=(480, y))
    buscar = codigo(fl, "Buscar lead", r"""
const c = $('Config aprobación').first().json;
const q = $('Aprobación (link de Telegram)').first().json.query || {};
if (!q.t || q.t !== c.TOKEN) throw new Error('Token inválido');
const l = $input.all().map(r => r.json).find(r => String(r.id) === String(q.id));
if (!l) throw new Error('Lead no encontrado: ' + q.id);
// Solo se manda lo que todavía es borrador: si respondió entretanto, no se envía.
if (!/^borrador/.test(l.estado || '')) throw new Error('El lead ya no está en borrador: ' + l.estado);
return [{ json: { lead: l, k: q.k || 'inicial', enviar: q.a === 'enviar' } }];
""", pos=(720, y))
    decide = si(fl, "¿Enviar?", "$json.enviar", pos=(960, y))
    env = gmail_api(fl, "Enviar borrador", "POST",
                    "https://gmail.googleapis.com/gmail/v1/users/me/drafts/send",
                    "={{ JSON.stringify({ id: $json.lead.draft_id }) }}", pos=(1200, y - 100))
    fila_env = codigo(fl, "Estado enviado", JS_FECHA + JS_HTML + r"""
const x = $('Buscar lead').first().json;
const l = x.lead, ok = !!$json.id;
const f = { id: l.id };
if (!ok) f.estado = 'error_envio';
else if (x.k === 'seg1') { f.estado = 'seguimiento_1'; f.seguimientos = 1; }
else if (x.k === 'seg2') { f.estado = 'seguimiento_2'; f.seguimientos = 2; }
else { f.estado = 'enviado'; f.fecha_envio = hoy(); f.thread_id = $json.threadId || ''; f.mensaje_id = $json.id || ''; f.seguimientos = 0; }
return [{ json: { fila: f, telegram_text: (ok ? '✅ Enviado a ' : '⚠️ No se pudo enviar a ') + esc(l.nombre) } }];
""", pos=(1440, y - 100))
    f_env = codigo(fl, "Fila enviado", "return [{ json: $input.first().json.fila }];",
                   pos=(1680, y - 100))
    g_env = escribir_hoja(fl, "Guardar enviado", cfg2, "Leads", pos=(1920, y - 100))
    tg_env = telegram(fl, "Confirmar envío", cfg2, pos=(2160, y - 100),
                      texto="$('Estado enviado').first().json.telegram_text")
    borrar = gmail_api(fl, "Borrar borrador", "DELETE",
                       "=https://gmail.googleapis.com/gmail/v1/users/me/drafts/{{ $json.lead.draft_id }}",
                       pos=(1200, y + 100))
    fila_desc = codigo(fl, "Estado descartado", JS_HTML + r"""
const x = $('Buscar lead').first().json;
// Un seguimiento descartado vuelve al estado anterior; un primer mail, se descarta.
const estado = x.k === 'seg1' ? 'enviado' : x.k === 'seg2' ? 'seguimiento_1' : 'descartado';
return [{ json: { fila: { id: x.lead.id, estado, draft_id: '' }, telegram_text: '✖️ Descartado: ' + esc(x.lead.nombre) } }];
""", pos=(1440, y + 100))
    f_desc = codigo(fl, "Fila descarte", "return [{ json: $input.first().json.fila }];",
                    pos=(1680, y + 100))
    g_desc2 = escribir_hoja(fl, "Guardar descarte", cfg2, "Leads", pos=(1920, y + 100))
    tg_desc = telegram(fl, "Confirmar descarte", cfg2, pos=(2160, y + 100),
                       texto="$('Estado descartado').first().json.telegram_text")
    fl.cadena(wh, cfg2, leads2, buscar, decide)
    fl.unir(decide, env, 0)
    fl.unir(decide, borrar, 1)
    fl.cadena(env, fila_env, f_env, g_env, tg_env)
    fl.cadena(borrar, fila_desc, f_desc, g_desc2, tg_desc)
    return fl


# ================================================================== 04
def f04():
    fl = Flujo("APARDIAN 04 · Seguimiento")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 11})
    v = dict(CONFIG_BASE)
    v.update({
        "MI_EMAIL": ("Martin Apardian <martin@TU-DOMINIO-DE-ENVIO>", "string"),
        "URL_APROBAR": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-aprobar", "string"),
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
    })
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    bajas = leer_hoja(fl, "Leer Bajas", cfg, "Bajas")
    toca = codigo(fl, "¿A quién le toca?", JS_FECHA + r"""
// Día 4 sin respuesta: seguimiento 1. Día 9: seguimiento 2. Día 14: se cierra.
// Quien respondió ya cambió de estado (flujo 05) y no entra acá.
const bm = new Set($('Leer Bajas').all().map(r => String(r.json.email || '').toLowerCase()));
const out = [];
for (const r of $('Leer Leads').all()) {
  const l = r.json, d = diasDesde(l.fecha_envio);
  if (!l.thread_id || bm.has(String(l.email || '').toLowerCase())) continue;
  if (l.estado === 'enviado' && d >= 4) out.push({ json: { lead: l, n: 1, cerrar: false } });
  else if (l.estado === 'seguimiento_1' && d >= 9) out.push({ json: { lead: l, n: 2, cerrar: false } });
  else if (l.estado === 'seguimiento_2' && d >= 14) out.push({ json: { lead: l, n: 0, cerrar: true } });
}
return out;
""")
    cerrar = si(fl, "¿Cerrar?", "$json.cerrar")
    fila_c = codigo(fl, "Fila cerrada", "return { json: { id: $json.lead.id, estado: 'cerrado_sin_respuesta' } };",
                    por_item=True, pos=(fl.x, -220))
    g_c = escribir_hoja(fl, "Guardar cierre", cfg, "Leads", pos=(fl.x + 240, -220))
    msgid = gmail_api(fl, "Message-ID original", "GET",
                      "=https://gmail.googleapis.com/gmail/v1/users/me/messages/{{ $json.lead.mensaje_id }}?format=metadata&metadataHeaders=Message-ID")
    prep = codigo(fl, "Prompt seguimiento", JS_CLAUDE + r"""
const SYSTEM = %s;
const x = $('¿Cerrar?').item.json;
const hdr = (($json.payload || {}).headers || []).find(h => /^message-id$/i.test(h.name));
let audit = {};
try { audit = JSON.parse(x.lead.notas || '{}').auditoria || {}; } catch (e) {}
const usuario = 'Seguimiento número: ' + x.n + '\nNegocio: ' + x.lead.nombre +
  '\n\nPrimer mail (asunto): ' + x.lead.asunto + '\nPrimer mail (cuerpo):\n' + x.lead.borrador +
  '\n\nAuditoría:\n' + JSON.stringify(audit, null, 2);
return { json: { ...x, message_id_hdr: hdr ? hdr.value : '', claude_body: cuerpoClaude(SYSTEM, usuario, 4000, 'medium') } };
""" % json.dumps(prompt("seguimiento"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · seguimiento")
    leer = codigo(fl, "Leer seguimiento", JS_LEER + JS_MIME + r"""
const c = $('Config').first().json;
const x = $('Prompt seguimiento').item.json;
const r = leerClaude($json);
if (!r.ok) throw new Error('Seguimiento de ' + x.lead.nombre + ': ' + r.motivo);
const asunto = r.data.asunto || ('Re: ' + x.lead.asunto);
const raw = mime({ de: c.MI_EMAIL, para: x.lead.email, asunto, cuerpo: r.data.cuerpo,
                   enRespuestaA: x.message_id_hdr });
return { json: { ...x, asunto, cuerpo: r.data.cuerpo,
  gmail_body: { message: { raw, threadId: x.lead.thread_id } } } };
""", por_item=True)
    borr = gmail_api(fl, "Crear borrador en el hilo", "POST",
                     "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                     "={{ JSON.stringify($json.gmail_body) }}")
    datos = codigo(fl, "Datos del seguimiento", JS_HTML + r"""
const c = $('Config').first().json;
const x = $('Leer seguimiento').item.json;
const k = x.n === 1 ? 'seg1' : 'seg2';
const link = acc => c.URL_APROBAR + '?id=' + encodeURIComponent(x.lead.id) + '&k=' + k + '&a=' + acc + '&t=' + encodeURIComponent(c.TOKEN);
return { json: {
  fila: { id: x.lead.id, estado: $json.id ? ('borrador_seg' + x.n) : 'error_borrador', draft_id: $json.id || '' },
  telegram_text: '<b>Seguimiento ' + x.n + ' para ' + esc(x.lead.nombre) + '</b>\n\n<b>' + esc(x.asunto) + '</b>\n' +
    esc(x.cuerpo) + '\n\n<a href="' + esc(link('enviar')) + '">✅ Enviar</a>   <a href="' + esc(link('descartar')) + '">✖️ Descartar</a>',
} };
""", por_item=True)
    fila = codigo(fl, "Fila seguimiento", "return { json: $json.fila };", por_item=True)
    g = escribir_hoja(fl, "Guardar borrador seguimiento", cfg, "Leads")
    tg = telegram(fl, "Pedir aprobación", cfg,
                  texto="$('Datos del seguimiento').item.json.telegram_text")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, toca, cerrar)
    fl.unir(cerrar, fila_c, 0)
    fl.unir(fila_c, g_c)
    fl.unir(cerrar, msgid, 1)
    fl.cadena(msgid, prep, cl, leer, borr, datos, fila, g, tg)
    return fl


# ================================================================== 05
def f05():
    fl = Flujo("APARDIAN 05 · Respuestas")
    a, b = disparadores(fl, {"field": "hours", "hoursInterval": 2})
    v = dict(CONFIG_BASE)
    v["MI_DIRECCION"] = ("martin@TU-DOMINIO-DE-ENVIO", "string")
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    hilos = codigo(fl, "Con hilo abierto", r"""
const abiertos = ['enviado', 'seguimiento_1', 'seguimiento_2', 'borrador_seg1', 'borrador_seg2'];
return $input.all().filter(r => r.json.thread_id && abiertos.includes(r.json.estado))
  .map(r => ({ json: r.json }));
""")
    hilo = gmail_api(fl, "Leer hilo", "GET",
                     "=https://gmail.googleapis.com/gmail/v1/users/me/threads/{{ $json.thread_id }}?format=full")
    resp = codigo(fl, "¿Respondió?", r"""
// Busca el último mensaje del hilo que NO mandamos nosotros.
const yo = String($('Config').first().json.MI_DIRECCION || '').toLowerCase();
const leads = $('Con hilo abierto').all();
const dec = d => Buffer.from(String(d || '').replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8');
const textoPlano = p => {
  if (!p) return '';
  if (p.mimeType === 'text/plain' && p.body && p.body.data) return dec(p.body.data);
  for (const q of (p.parts || [])) { const t = textoPlano(q); if (t) return t; }
  return '';
};
const sinCita = t => t.split(/\r?\n(?:El .{5,120} escribió:|On .{5,120} wrote:|Em .{5,120} escreveu:)/)[0]
  .split('\n').filter(l => !l.startsWith('>')).join('\n').trim();
const out = [];
$input.all().forEach((it, i) => {
  const lead = leads[i] ? leads[i].json : null;
  if (!lead || it.json.error) return;
  const ajenos = (it.json.messages || []).filter(m => {
    const from = ((m.payload || {}).headers || []).find(h => /^from$/i.test(h.name));
    return from && !String(from.value).toLowerCase().includes(yo);
  });
  if (!ajenos.length) return;
  const m = ajenos[ajenos.length - 1];
  const h = n => (((m.payload || {}).headers || []).find(x => x.name.toLowerCase() === n) || {}).value || '';
  out.push({ json: { lead, de: h('from'), asunto: h('subject'),
    texto: (sinCita(textoPlano(m.payload)) || m.snippet || '').slice(0, 4000) } });
});
return out;
""")
    prep = codigo(fl, "Prompt clasificador", JS_CLAUDE + r"""
const SYSTEM = %s;
const usuario = 'De: ' + $json.de + '\nAsunto: ' + $json.asunto + '\n\nRespuesta:\n' + $json.texto;
return { json: { ...$json, claude_body: cuerpoClaude(SYSTEM, usuario, 2000, 'low') } };
""" % json.dumps(prompt("clasificador"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · clasificador")
    leer = codigo(fl, "Leer clasificación", JS_LEER + JS_HTML + JS_FECHA + r"""
const x = $('Prompt clasificador').item.json;
const r = leerClaude($json);
const cat = r.ok ? (r.data.categoria || 'otro') : 'otro';
const resumen = r.ok ? (r.data.resumen || '') : ('sin clasificar: ' + r.motivo);
const sug = r.ok ? (r.data.sugerencia_respuesta || '') : '';
const mail = String(x.lead.email || '').toLowerCase();
return { json: {
  fila: { id: x.lead.id, estado: cat === 'otro' ? 'respondio' : cat,
          respuesta: cat + ' · ' + hoy() + ' · ' + resumen },
  baja: cat === 'baja' ? { email: mail, dominio: mail.split('@')[1] || '', fecha: hoy(), motivo: resumen } : null,
  alerta: ['interesado', 'pide_precio', 'otro'].includes(cat),
  telegram_text: '<b>' + (cat === 'pide_precio' ? '💰 Pide precio' : cat === 'interesado' ? '🔥 Interesado' : '📩 Respondió') +
    ': ' + esc(x.lead.nombre) + '</b>\n' + esc(x.lead.web) + '\n\n' + esc(resumen) +
    '\n\n<i>Respondió:</i>\n' + esc(x.texto.slice(0, 700)) +
    (sug ? '\n\n<i>Sugerencia (revisala antes de mandar):</i>\n' + esc(sug) : ''),
} };
""", por_item=True)
    fila = codigo(fl, "Fila respuesta", "return { json: $json.fila };", por_item=True)
    g = escribir_hoja(fl, "Guardar respuesta", cfg, "Leads")
    es_baja = si(fl, "¿Es baja?", "!!$json.baja", pos=(fl.x - 480, 220))
    fila_b = codigo(fl, "Fila baja", "return { json: $json.baja };", por_item=True, pos=(fl.x - 240, 220))
    g_b = escribir_hoja(fl, "Agregar a Bajas", cfg, "Bajas", "append", pos=(fl.x, 220))
    alerta = si(fl, "¿Avisar a Martin?", "$json.alerta", pos=(fl.x - 480, 440))
    tg = telegram(fl, "Aviso a Martin", cfg, pos=(fl.x - 240, 440))
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, hilos, hilo, resp, prep, cl, leer, fila, g)
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
    cfg = config(fl, "Config", {"TELEGRAM_CHAT_ID": CONFIG_BASE["TELEGRAM_CHAT_ID"]})
    prep = codigo(fl, "Prompt bienvenida", JS_CLAUDE + r"""
// Espera un POST con { nombre, canal, telefono, mensaje }.
// Puede venir de WhatsApp Cloud API, de un formulario de la web o de ManyChat.
const SYSTEM = %s;
const c = $('Consulta entrante').first().json.body || {};
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
  esc(c.nombre || '') + ' ' + esc(c.telefono || '') + '\n\n' + esc(c.mensaje || '') +
  '\n\n<i>Resumen:</i> ' + esc(d.resumen) +
  '\n\n<i>Respuesta sugerida (revisala):</i>\n' + esc(d.respuesta_sugerida) +
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


def webhook_respuesta(fl, nombre, ruta, pos):
    """Webhook que contesta con una pagina corta (el boton de Telegram abre el navegador)."""
    return fl.nodo(nombre, "n8n-nodes-base.webhook", 2,
                   {"httpMethod": "GET", "path": ruta, "responseMode": "responseNode",
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
const c = $('Config').first().json;
const ahora = Date.now(), lim = ahora + Number(c.HORAS_ANTES || 36) * 3600e3;
const link = (id, acc) => c.URL_APROBAR_IG + '?id=' + encodeURIComponent(id) + '&a=' + acc + '&t=' + encodeURIComponent(c.TOKEN);
const out = [];
for (const r of $('Leer Calendario').all()) {
  const f = r.json;
  if (String(f.estado || '').trim() !== 'pendiente' || !f.id) continue;
  const t = enUY(f.fecha, f.hora).getTime();
  if (isNaN(t) || t > lim || t < ahora - 12 * 3600e3) continue;
  const urls = String(f.urls || '').split('|').filter(Boolean);
  const foto = urls.find(u => /\.jpe?g$/i.test(u)) || '';
  const cuando = new Date(t).toLocaleString('es-UY', { timeZone: 'America/Montevideo', weekday: 'long', day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
  const pie = String(f.pie || '');
  // el pie de una foto de Telegram tiene 1024 caracteres como máximo
  const vista = pie.length > 600 ? pie.slice(0, 600) + '…' : pie;
  const texto = '<b>' + esc(f.tipo) + ' · ' + esc(f.titulo) + '</b>\n' + esc(cuando) +
    ' · ' + urls.length + ' archivo' + (urls.length === 1 ? '' : 's') + '\n\n' + esc(vista) +
    (f.tipo === 'REEL' && !foto ? '\n\n<a href="' + esc(urls[0]) + '">Ver el video</a>' : '') +
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
if (!q.t || q.t !== c.TOKEN) {
  return [{ json: { ok: false, html: pagina('Link no válido', 'El token no coincide. No se cambió nada.') } }];
}
const f = $input.all().map(r => r.json).find(r => String(r.id) === String(q.id));
if (!f) return [{ json: { ok: false, html: pagina('No encontré esa publicación', String(q.id || '')) } }];
if (f.publicado_en) return [{ json: { ok: false, html: pagina('Ya está publicada', f.titulo + ' · ' + f.publicado_en) } }];
const aprobar = q.a === 'aprobar';
const fila = { id: f.id, estado: aprobar ? 'aprobado' : 'rechazado',
               aprobado_por: aprobar ? 'Martin (Telegram)' : '', aprobado_en: aprobar ? ahoraISO() : '', error: '' };
const cuando = enUY(f.fecha, f.hora).toLocaleString('es-UY', { timeZone: 'America/Montevideo', weekday: 'long', day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
return [{ json: { ok: true, fila,
  html: pagina(aprobar ? 'Aprobado ✓' : 'No se publica', aprobar ? f.titulo + ' sale el ' + cuando + '.' : f.titulo + ' quedó afuera del calendario.'),
  telegram_text: (aprobar ? '✅ Aprobado: ' : '✖️ No se publica: ') + '<b>' + esc(f.titulo) + '</b>' + (aprobar ? '\nSale el ' + esc(cuando) + '.' : '') } }];
""", pos=(720, y))
    valido = si(fl, "¿Válido?", "$json.ok", pos=(960, y))
    fila = codigo(fl, "Fila aprobación", "return [{ json: $input.first().json.fila }];", pos=(1200, y - 100))
    g = escribir_hoja(fl, "Guardar aprobación", cfg2, "Calendario", pos=(1440, y - 100))
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
  } else {
    throw new Error('tipo desconocido: ' + f.tipo);
  }
  const pub = await llamar('POST', user + '/media_publish', { creation_id: creacion });
  let aviso_com = '';
  if (f.primer_comentario) {
    try { await llamar('POST', '/' + pub.id + '/comments', { message: f.primer_comentario }); }
    catch (e) { aviso_com = '\n(No se pudo dejar el primer comentario: ' + e.message + ')'; }
  }
  let link = '';
  try { link = (await llamar('GET', '/' + pub.id, { fields: 'permalink' })).permalink || ''; } catch (e) {}
  return [{ json: {
    fila: { id: f.id, estado: 'publicado', publicado_en: new Date().toISOString(), ig_media_id: pub.id, error: '' },
    telegram_text: '📣 Publicado: <b>' + esc(f.titulo) + '</b>' + (link ? '\n' + esc(link) : '') + esc(aviso_com),
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
    a, b = disparadores(fl, {"field": "minutes", "minutesInterval": 15})
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


if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for f, archivo in ((f01, "01_prospector.json"), (f02, "02_auditor.json"),
                       (f03, "03_redactor_envio.json"), (f04, "04_seguimiento.json"),
                       (f05, "05_respuestas.json"), (f06, "06_bienvenida_whatsapp.json"),
                       (f07, "07_aprobacion_instagram.json"), (f08, "08_publicador_instagram.json")):
        fl = f()
        nombres = {n["name"] for n in fl.nodos}
        for a, salidas in fl.con.items():
            assert a in nombres, a
            for s in salidas["main"]:
                for c in s:
                    assert c["node"] in nombres, c["node"]
        print(fl.guardar(archivo), len(fl.nodos), "nodos")
