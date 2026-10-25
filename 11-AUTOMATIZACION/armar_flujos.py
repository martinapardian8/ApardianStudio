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


def escribir_hoja(fl, nombre, cfg, pestana, operacion="update", pos=None, clave="id"):
    p = {
        "operation": operacion,
        "documentId": hoja(cfg),
        "sheetName": {"__rl": True, "value": pestana, "mode": "name"},
        "columns": {"mappingMode": "autoMapInputData", "value": {},
                    "matchingColumns": [clave] if operacion in ("update", "appendOrUpdate") else [],
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
    v = dict(CONFIG_BASE); v["BUSQUEDAS_POR_DIA"] = (12, "number")
    cfg = config(fl, "Config", v)
    busq = leer_hoja(fl, "Leer Búsquedas", cfg, "Busquedas")
    elegir = codigo(fl, "Elegir búsquedas", JS_FECHA + r"""
// La hoja "Busquedas" es el plan de Radar: país, idioma, rubro, búsqueda en
// Google Maps y servicio que se le ofrece. Cada día toma las que hace más
// tiempo que no corren (las nunca usadas primero). Cada búsqueda trae hasta 20
// negocios: 12 por día alcanzan para sostener 50 mails diarios.
const n = Number($('Config').first().json.BUSQUEDAS_POR_DIA) || 12;
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
                     "places.rating,places.userRatingCount,places.nationalPhoneNumber,places.googleMapsUri",
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
      telefono: p.nationalPhoneNumber || '',
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
    fuente: 'google_places', score: '', servicio: p.servicio_objetivo, problemas: '',
    estado: p.web ? 'nuevo' : 'sin_web', asunto: '', borrador: '', fecha_envio: '',
    seguimientos: 0, respuesta: '',
    notas: [p.direccion, p.rating ? ('rating ' + p.rating + ' (' + p['reseñas'] + ' reseñas)') : '', p.maps].filter(Boolean).join(' · '),
    pais: p.pais, idioma: p.idioma, mercado: p.mercado, zona: p.zona, oferta_id: '',
    ultimo_envio: '', seg_asunto: '', seg_cuerpo: '',
  } });
}
return out;
""")
    guardar = escribir_hoja(fl, "Agregar a Leads", cfg, "Leads", "append")
    marca = codigo(fl, "Marcar búsquedas", JS_FECHA + r"""
return $('Elegir búsquedas').all().map(r => ({ json: { id: r.json.id, ultima_vez: hoy() } }));
""", pos=(fl.x - 960, 240))
    g_marca = escribir_hoja(fl, "Guardar búsquedas", cfg, "Busquedas", pos=(fl.x - 720, 240))
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, busq, elegir, places, plano, leads, dedupe, guardar)
    fl.cadena(elegir, marca, g_marca)
    return fl


# ================================================================== 02
def f02():
    fl = Flujo("APARDIAN 02 · Auditor")
    a, b = disparadores(fl, {"field": "days", "triggerAtHour": 9})
    # para sostener 50 mails por día hacen falta ~90 auditorías: la mitad no
    # publica mail o no tiene una oportunidad clara
    v = dict(CONFIG_BASE); v["LIMITE_DIARIO"] = (90, "number")
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    elegir = codigo(fl, "Elegir nuevos", r"""
const lim = $('Config').first().json.LIMITE_DIARIO || 90;
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
  idioma: a.idioma || lead.idioma || 'es', mercado: lead.mercado || 'uy',
  notas: JSON.stringify({ auditoria: a, ficha: lead.notas || '' }),
} };
""", por_item=True)
    guardar = escribir_hoja(fl, "Guardar auditoría", cfg, "Leads")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, elegir, bajar, senales, prep, cl, leer, guardar)
    return fl


# ================================================================== Radar
JS_RADAR = r"""
// Hora y día en la zona horaria del destinatario (Intl viene con Node).
const horaEn = z => { try { return Number(new Intl.DateTimeFormat('en-US', { timeZone: z, hour: 'numeric', hourCycle: 'h23' }).format(new Date())); } catch (e) { return 12; } };
const diaEn = z => { try { return new Intl.DateTimeFormat('en-US', { timeZone: z, weekday: 'short' }).format(new Date()); } catch (e) { return 'Mon'; } };
const horarioDeOficina = z => { const h = horaEn(z), d = diaEn(z); return d !== 'Sat' && d !== 'Sun' && h >= 9 && h < 17; };
const hoyUY = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Montevideo' }).format(new Date());
// Cuántos mails salieron hoy desde la casilla (primeros y seguimientos): cada
// lead recibe como mucho uno por día, así que alcanza con contar ultimo_envio.
const mailsHoy = leads => leads.filter(l => String(l.ultimo_envio || '') === hoyUY()).length;
"""


# ================================================================== 03
def f03():
    fl = Flujo("APARDIAN 03 · Radar: redactor y envío")
    # cada hora de 9 a 17 (Montevideo), de lunes a viernes: los mails salen de a
    # pocos durante el día, nunca en ráfaga
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "0 9-17 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({
        # Sale desde contacto@apardianstudio.com por el SMTP de Hostinger
        # (decisión de Martin, 25/10/2026).
        "MI_EMAIL": ("Martin Apardian <contacto@apardianstudio.com>", "string"),
        "SCORE_MINIMO": (60, "number"),
        # Envío automático (decisión de Martin, 24/10/2026): salen solos, con las
        # ofertas que aprobó en el Centro. Con false vuelve a pedir aprobación
        # por Telegram mail por mail (MAX_POR_DIA, a las 10).
        "AUTO_ENVIO": (True, "boolean"),
        "MAX_POR_DIA": (20, "number"),
        "SCORE_AUTO": (0, "number"),
        # Calentamiento: cupo de mails NUEVOS por día según la semana desde
        # FECHA_INICIO (AAAA-MM-DD). Sin fecha, usa el de la semana 1.
        "FECHA_INICIO": ("PEGAR_FECHA_DE_ARRANQUE", "string"),
        "CUPOS_POR_SEMANA": ("10,20,35,50", "string"),
        # Tope de la casilla: TODOS los mails del día (nuevos + seguimientos).
        # Correo gratis de Hostinger: 100 por día → 90. Business Starter: 1.000 → 900.
        "LIMITE_TOTAL_DIA": (90, "number"),
        # Obligatoria para escribir a EE.UU. (ley CAN-SPAM). Sin ella, Radar no les escribe.
        "DIRECCION_POSTAL": ("", "string"),
        "URL_APROBAR": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-aprobar", "string"),
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
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
// lo que todavía entra hoy en la casilla, contando los seguimientos
const libreCasilla = Math.max(0, (Number(c.LIMITE_TOTAL_DIA) || 90) - mailsHoy(todos));
let tanda;
if (c.AUTO_ENVIO) {
  // Cupo de nuevos según la semana de calentamiento, repartido en las horas que quedan.
  const cupos = String(c.CUPOS_POR_SEMANA || '10,20,35,50').split(',').map(Number).filter(n => n > 0);
  const ini = /^\d{4}-\d{2}-\d{2}$/.test(String(c.FECHA_INICIO || '')) ? c.FECHA_INICIO : '';
  const semana = ini ? Math.max(0, Math.floor(diasDesde(ini) / 7)) : 0;
  const cupo = cupos[Math.min(semana, cupos.length - 1)] || 10;
  const nuevosHoy = todos.filter(l => String(l.fecha_envio || '') === hoyUY()).length;
  const restante = Math.min(Math.max(0, cupo - nuevosHoy), libreCasilla);
  const horas = Math.max(1, 18 - horaEn('America/Montevideo'));
  tanda = Math.ceil(restante / horas);
} else {
  // Modo con aprobación: una vez por día, a las 10, deja borradores en la planilla.
  if (horaEn('America/Montevideo') !== 10) return [];
  tanda = Math.min(c.MAX_POR_DIA || 20, libreCasilla);
}
if (!tanda) return [];
return todos
  .filter(l => l.estado === 'auditado' && Number(l.score) >= (c.SCORE_MINIMO || 60) && l.email)
  .filter(l => { const e = String(l.email).toLowerCase(); return !bm.has(e) && !bd.has(e.split('@')[1]); })
  // a EE.UU. solo con dirección postal en la firma (CAN-SPAM)
  .filter(l => String(l.pais || '') !== 'Estados Unidos' || String(c.DIRECCION_POSTAL || '').trim())
  // en horario de oficina del destinatario: de lunes a viernes, de 9 a 17
  .filter(l => horarioDeOficina(l.zona || 'America/Montevideo'))
  .sort((x, y) => Number(y.score) - Number(x.score))
  .slice(0, tanda)
  .map(l => ({ json: l }));
""")
    prep = codigo(fl, "Prompt redactor", JS_CLAUDE + JS_FECHA + r"""
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
const usuario = 'MERCADO: ' + mercado + '\nPaís: ' + ($json.pais || 'Uruguay') + '\nIdioma: ' + ($json.idioma || 'es') +
  '\nNegocio: ' + $json.nombre + '\nRubro: ' + $json.rubro + '\nBúsqueda: ' + $json.ciudad +
  '\nWeb: ' + $json.web + ($json.instagram ? '\nInstagram: ' + $json.instagram : '') +
  (String($json.pais || '') === 'Estados Unidos' ? '\nDIRECCION_POSTAL (va en la firma): ' + c.DIRECCION_POSTAL : '') +
  '\n\nAuditoría:\n' + JSON.stringify(audit, null, 2) +
  '\n\nOfertas aprobadas por Martin para este mercado:\n' + (ofertas.length ? JSON.stringify(ofertas, null, 2) : '(ninguna: no menciones ofertas ni precios)') +
  '\n\nLo que Martin te enseñó:\n' + (entrenamiento || '(todavía nada)');
return { json: { lead: $json, claude_body: cuerpoClaude(SYSTEM, usuario, 6000, 'medium') } };
""" % json.dumps(prompt("redactor"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · redactor")
    leer = codigo(fl, "Leer mail", JS_LEER + r"""
const c = $('Config').first().json;
const lead = $('Prompt redactor').item.json.lead;
const r = leerClaude($json);
if (!r.ok || r.data.omitir) {
  return { json: { omitir: true, fila: { id: lead.id, estado: r.ok ? 'descartado' : 'error_redaccion', notas: lead.notas } } };
}
const m = r.data;
return { json: { omitir: false, lead, para: lead.email, asunto: m.asunto, cuerpo: m.cuerpo, oferta_id: m.oferta_id || '',
  auto: !!c.AUTO_ENVIO && Number(lead.score) >= (Number(c.SCORE_AUTO) || 0) } };
""", por_item=True)
    hay = si(fl, "¿Hay mail?", "!$json.omitir")
    descarte = codigo(fl, "Fila descartada", "return { json: $json.fila };", por_item=True, pos=(fl.x, 220))
    g_desc = escribir_hoja(fl, "Marcar descartado", cfg, "Leads", pos=(fl.x + 240, 220))
    auto = si(fl, "¿Auto-envío?", "$json.auto")
    env = enviar_mail(fl, "Enviar (contacto@)", "Config")
    fila_auto = codigo(fl, "Fila enviada", JS_RADAR + r"""
const x = $('Leer mail').item.json;
const ok = !$json.error && !(Array.isArray($json.rejected) && $json.rejected.length);
return { json: { id: x.lead.id, estado: ok ? 'enviado' : 'error_envio', fecha_envio: ok ? hoyUY() : '',
  ultimo_envio: ok ? hoyUY() : '', asunto: x.asunto, borrador: x.cuerpo, oferta_id: x.oferta_id, seguimientos: 0,
  respuesta: ok ? '' : ('envío: ' + String(($json.error && ($json.error.message || $json.error)) || 'rechazado').slice(0, 200)) } };
""", por_item=True)
    g_auto = escribir_hoja(fl, "Guardar envío", cfg, "Leads")
    datos = codigo(fl, "Borrador para aprobar", JS_HTML + r"""
const c = $('Config').first().json;
const x = $json;
const link = acc => c.URL_APROBAR + '?id=' + encodeURIComponent(x.lead.id) + '&k=inicial&a=' + acc + '&t=' + encodeURIComponent(c.TOKEN);
return { json: {
  fila: { id: x.lead.id, estado: 'borrador', asunto: x.asunto, borrador: x.cuerpo, oferta_id: x.oferta_id },
  telegram_text: '<b>Mail listo para ' + esc(x.lead.nombre) + '</b> (' + esc(x.lead.rubro) + ', ' + esc(x.lead.pais || 'Uruguay') + ', score ' + esc(x.lead.score) + ')\n' +
    esc(x.lead.web) + '\n\n<b>' + esc(x.asunto) + '</b>\n' + esc(x.cuerpo) +
    '\n\nSi querés cambiar algo, editá asunto y borrador en la planilla antes de aprobar.\n' +
    '<a href="' + esc(link('enviar')) + '">✅ Enviar</a>   <a href="' + esc(link('descartar')) + '">✖️ Descartar</a>',
} };
""", por_item=True, pos=(fl.x - 240, 240))
    f_borr = codigo(fl, "Fila borrador", "return { json: $json.fila };", por_item=True, pos=(fl.x, 240))
    g_borr = escribir_hoja(fl, "Guardar borrador", cfg, "Leads", pos=(fl.x + 240, 240))
    tg = telegram(fl, "Pedir aprobación", cfg, pos=(fl.x + 480, 240),
                  texto="$('Borrador para aprobar').item.json.telegram_text")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, ofertas, entren, elegir, prep, cl, leer, hay)
    fl.unir(hay, auto, 0)
    fl.unir(hay, descarte, 1)
    fl.unir(descarte, g_desc)
    fl.unir(auto, env, 0)
    fl.unir(auto, datos, 1)
    fl.cadena(env, fila_auto, g_auto)
    fl.cadena(datos, f_borr, g_borr, tg)

    # ---- segunda entrada: Martin toca "Enviar" o "Descartar" en Telegram
    y = 900
    wh = webhook(fl, "Aprobación (link de Telegram)", "apardian-aprobar", pos=(0, y))
    cfg2 = config(fl, "Config aprobación", {
        "SHEET_ID": CONFIG_BASE["SHEET_ID"],
        "TELEGRAM_CHAT_ID": CONFIG_BASE["TELEGRAM_CHAT_ID"],
        "MI_EMAIL": ("Martin Apardian <contacto@apardianstudio.com>", "string"),
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
const k = q.k || 'inicial';
const seg = k !== 'inicial';
return [{ json: { lead: l, k, enviar: q.a === 'enviar', para: l.email,
  asunto: seg ? l.seg_asunto : l.asunto, cuerpo: seg ? l.seg_cuerpo : l.borrador } }];
""", pos=(720, y))
    decide = si(fl, "¿Enviar?", "$json.enviar", pos=(960, y))
    env2 = enviar_mail(fl, "Enviar aprobado (contacto@)", "Config aprobación", pos=(1200, y - 100))
    fila_env = codigo(fl, "Estado enviado", JS_FECHA + JS_HTML + JS_RADAR + r"""
const x = $('Buscar lead').first().json;
const l = x.lead, ok = !$json.error && !(Array.isArray($json.rejected) && $json.rejected.length);
const f = { id: l.id };
if (!ok) f.estado = 'error_envio';
else if (x.k === 'seg1') { f.estado = 'seguimiento_1'; f.seguimientos = 1; f.ultimo_envio = hoyUY(); }
else if (x.k === 'seg2') { f.estado = 'seguimiento_2'; f.seguimientos = 2; f.ultimo_envio = hoyUY(); }
else { f.estado = 'enviado'; f.fecha_envio = hoyUY(); f.ultimo_envio = hoyUY(); f.seguimientos = 0; }
return [{ json: { fila: f, telegram_text: (ok ? '✅ Enviado a ' : '⚠️ No se pudo enviar a ') + esc(l.nombre) } }];
""", pos=(1440, y - 100))
    f_env = codigo(fl, "Fila enviado", "return [{ json: $input.first().json.fila }];", pos=(1680, y - 100))
    g_env = escribir_hoja(fl, "Guardar enviado", cfg2, "Leads", pos=(1920, y - 100))
    tg_env = telegram(fl, "Confirmar envío", cfg2, pos=(2160, y - 100),
                      texto="$('Estado enviado').first().json.telegram_text")
    fila_desc = codigo(fl, "Estado descartado", JS_HTML + r"""
const x = $('Buscar lead').first().json;
// Un seguimiento descartado vuelve al estado anterior; un primer mail, se descarta.
const estado = x.k === 'seg1' ? 'enviado' : x.k === 'seg2' ? 'seguimiento_1' : 'descartado';
return [{ json: { fila: { id: x.lead.id, estado }, telegram_text: '✖️ Descartado: ' + esc(x.lead.nombre) } }];
""", pos=(1200, y + 100))
    f_desc = codigo(fl, "Fila descarte", "return [{ json: $input.first().json.fila }];", pos=(1440, y + 100))
    g_desc2 = escribir_hoja(fl, "Guardar descarte", cfg2, "Leads", pos=(1680, y + 100))
    tg_desc = telegram(fl, "Confirmar descarte", cfg2, pos=(1920, y + 100),
                       texto="$('Estado descartado').first().json.telegram_text")
    fl.cadena(wh, cfg2, leads2, buscar, decide)
    fl.unir(decide, env2, 0)
    fl.unir(decide, fila_desc, 1)
    fl.cadena(env2, fila_env, f_env, g_env, tg_env)
    fl.cadena(fila_desc, f_desc, g_desc2, tg_desc)
    return fl


# ================================================================== 04
def f04():
    fl = Flujo("APARDIAN 04 · Radar: seguimiento")
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "30 9-17 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({
        "MI_EMAIL": ("Martin Apardian <contacto@apardianstudio.com>", "string"),
        # igual que en el 03: con true los seguimientos salen solos
        "AUTO_ENVIO": (True, "boolean"),
        "LIMITE_TOTAL_DIA": (90, "number"),
        "DIRECCION_POSTAL": ("", "string"),
        "URL_APROBAR": ("https://TU-INSTANCIA.app.n8n.cloud/webhook/apardian-aprobar", "string"),
        "TOKEN": ("CAMBIAR-POR-UNA-CLAVE-LARGA", "string"),
    })
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    bajas = leer_hoja(fl, "Leer Bajas", cfg, "Bajas")
    toca = codigo(fl, "¿A quién le toca?", JS_FECHA + JS_RADAR + r"""
// Día 4 sin respuesta: seguimiento 1. Día 9: seguimiento 2. Día 14: se cierra.
// Quien respondió ya cambió de estado (flujo 05) y no entra acá. Corre cada
// hora, solo toma a quien está en horario de oficina en su país y nunca pasa
// el tope diario de la casilla.
const c = $('Config').first().json;
const todos = $('Leer Leads').all().map(r => r.json).filter(l => l.id);
let libre = Math.max(0, (Number(c.LIMITE_TOTAL_DIA) || 90) - mailsHoy(todos));
const horas = Math.max(1, 18 - horaEn('America/Montevideo'));
libre = Math.ceil(libre / horas);
const bm = new Set($('Leer Bajas').all().map(r => String(r.json.email || '').toLowerCase()));
const out = [];
for (const l of todos) {
  const d = diasDesde(l.fecha_envio);
  if (!l.fecha_envio || !l.email || bm.has(String(l.email).toLowerCase())) continue;
  if (l.estado === 'seguimiento_2' && d >= 14) { out.push({ json: { lead: l, n: 0, cerrar: true } }); continue; }
  if (!horarioDeOficina(l.zona || 'America/Montevideo') || String(l.ultimo_envio || '') === hoyUY()) continue;
  if (l.estado === 'enviado' && d >= 4 && libre > 0) { out.push({ json: { lead: l, n: 1, cerrar: false } }); libre--; }
  else if (l.estado === 'seguimiento_1' && d >= 9 && libre > 0) { out.push({ json: { lead: l, n: 2, cerrar: false } }); libre--; }
}
return out;
""")
    cerrar = si(fl, "¿Cerrar?", "$json.cerrar")
    fila_c = codigo(fl, "Fila cerrada", "return { json: { id: $json.lead.id, estado: 'cerrado_sin_respuesta' } };",
                    por_item=True, pos=(fl.x, -220))
    g_c = escribir_hoja(fl, "Guardar cierre", cfg, "Leads", pos=(fl.x + 240, -220))
    prep = codigo(fl, "Prompt seguimiento", JS_CLAUDE + r"""
const SYSTEM = %s;
const c = $('Config').first().json;
const x = $json;
let audit = {};
try { audit = JSON.parse(x.lead.notas || '{}').auditoria || {}; } catch (e) {}
const usuario = 'Seguimiento número: ' + x.n + '\nNegocio: ' + x.lead.nombre +
  '\nPaís: ' + (x.lead.pais || 'Uruguay') + '\nIdioma: ' + (x.lead.idioma || 'es') +
  (String(x.lead.pais || '') === 'Estados Unidos' ? '\nDIRECCION_POSTAL: ' + c.DIRECCION_POSTAL : '') +
  '\n\nPrimer mail (asunto): ' + x.lead.asunto + '\nPrimer mail (cuerpo):\n' + x.lead.borrador +
  '\n\nAuditoría:\n' + JSON.stringify(audit, null, 2);
return { json: { ...x, claude_body: cuerpoClaude(SYSTEM, usuario, 4000, 'medium') } };
""" % json.dumps(prompt("seguimiento"), ensure_ascii=False), por_item=True)
    cl = claude(fl, "Claude · seguimiento")
    leer = codigo(fl, "Leer seguimiento", JS_LEER + r"""
const c = $('Config').first().json;
const x = $('Prompt seguimiento').item.json;
const r = leerClaude($json);
if (!r.ok) throw new Error('Seguimiento de ' + x.lead.nombre + ': ' + r.motivo);
const asunto = r.data.asunto || ('Re: ' + x.lead.asunto);
return { json: { lead: x.lead, n: x.n, para: x.lead.email, asunto, cuerpo: r.data.cuerpo, auto: !!c.AUTO_ENVIO } };
""", por_item=True)
    auto = si(fl, "¿Auto-envío?", "$json.auto")
    env = enviar_mail(fl, "Enviar seguimiento (contacto@)", "Config")
    fila_env = codigo(fl, "Fila seguimiento enviado", JS_RADAR + r"""
const x = $('Leer seguimiento').item.json;
const ok = !$json.error && !(Array.isArray($json.rejected) && $json.rejected.length);
return { json: ok ? { id: x.lead.id, estado: 'seguimiento_' + x.n, seguimientos: x.n, ultimo_envio: hoyUY() }
                  : { id: x.lead.id, estado: 'error_envio', respuesta: 'seguimiento ' + x.n + ': ' + String(($json.error && ($json.error.message || $json.error)) || 'rechazado').slice(0, 200) } };
""", por_item=True)
    g_env = escribir_hoja(fl, "Guardar seguimiento enviado", cfg, "Leads")
    datos = codigo(fl, "Seguimiento para aprobar", JS_HTML + r"""
const c = $('Config').first().json;
const x = $json;
const k = x.n === 1 ? 'seg1' : 'seg2';
const link = acc => c.URL_APROBAR + '?id=' + encodeURIComponent(x.lead.id) + '&k=' + k + '&a=' + acc + '&t=' + encodeURIComponent(c.TOKEN);
return { json: {
  fila: { id: x.lead.id, estado: 'borrador_seg' + x.n, seg_asunto: x.asunto, seg_cuerpo: x.cuerpo },
  telegram_text: '<b>Seguimiento ' + x.n + ' para ' + esc(x.lead.nombre) + '</b>\n\n<b>' + esc(x.asunto) + '</b>\n' +
    esc(x.cuerpo) + '\n\n<a href="' + esc(link('enviar')) + '">✅ Enviar</a>   <a href="' + esc(link('descartar')) + '">✖️ Descartar</a>',
} };
""", por_item=True, pos=(fl.x - 240, 240))
    f_b = codigo(fl, "Fila seguimiento borrador", "return { json: $json.fila };", por_item=True, pos=(fl.x, 240))
    g_b = escribir_hoja(fl, "Guardar borrador seguimiento", cfg, "Leads", pos=(fl.x + 240, 240))
    tg = telegram(fl, "Pedir aprobación", cfg, pos=(fl.x + 480, 240),
                  texto="$('Seguimiento para aprobar').item.json.telegram_text")
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, bajas, toca, cerrar)
    fl.unir(cerrar, fila_c, 0)
    fl.unir(fila_c, g_c)
    fl.unir(cerrar, prep, 1)
    fl.cadena(prep, cl, leer, auto)
    fl.unir(auto, env, 0)
    fl.unir(auto, datos, 1)
    fl.cadena(env, fila_env, g_env)
    fl.cadena(datos, f_b, g_b, tg)
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
    resp = codigo(fl, "¿Es de un lead?", r"""
// Une cada mail con el lead que lo mandó: por la dirección exacta o, si no es
// un mail genérico (gmail, hotmail…), por el dominio. Los rebotes
// (mailer-daemon) se unen por la dirección que aparece en el texto. Si el lead
// ya no está esperando respuesta, el mail se ignora: así un mismo mail no se
// procesa dos veces.
const abiertos = ['enviado', 'seguimiento_1', 'seguimiento_2', 'borrador_seg1', 'borrador_seg2'];
const genericos = /^(gmail|googlemail|hotmail|outlook|live|yahoo|icloud|me|aol|proton|protonmail)\./i;
const L = $('Leer Leads').all().map(r => r.json).filter(l => l.id && l.email && abiertos.includes(l.estado));
const porMail = new Map(L.map(l => [String(l.email).toLowerCase(), l]));
const porDominio = new Map();
for (const l of L) { const d = String(l.email).toLowerCase().split('@')[1] || ''; if (d && !genericos.test(d)) porDominio.set(d, l); }
const sinHtml = h => String(h || '').replace(/<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ');
const sinCita = t => String(t).split(/\r?\n(?:El .{5,120} escribió:|On .{5,120} wrote:|Em .{5,120} escreveu:)/)[0]
  .split('\n').filter(l => !l.startsWith('>')).join('\n').trim();
const out = [], vistos = new Set();
for (const it of $('Mail nuevo en contacto@').all()) {
  const m = it.json;
  const de = String((m.from && m.from.value && m.from.value[0] && m.from.value[0].address) ||
    (String(m.from && m.from.text || m.from || '').match(/[\w.+-]+@[\w.-]+/) || [''])[0]).toLowerCase();
  const texto = String(m.text || m.textPlain || sinHtml(m.html || m.textHtml) || '');
  let lead = porMail.get(de) || porDominio.get(de.split('@')[1] || '');
  const rebote = /mailer-daemon|postmaster/i.test(de);
  if (!lead && rebote) lead = L.find(l => texto.toLowerCase().includes(String(l.email).toLowerCase()));
  if (!lead || vistos.has(lead.id)) continue;
  vistos.add(lead.id);
  out.push({ json: { lead, de, asunto: m.subject || '', rebote, texto: (rebote ? texto : sinCita(texto)).slice(0, 4000) } });
}
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
let cat = r.ok ? (r.data.categoria || 'otro') : 'otro';
if (x.rebote) cat = 'rebote';
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
    '\n\n<i>Respondió (está en contacto@):</i>\n' + esc(x.texto.slice(0, 700)) +
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
if (!q.t || q.t !== c.TOKEN) return [{ json: { ok: false, html: pagina('Link no válido', 'La clave no coincide con la de n8n. Revisala en el Centro → Radar → Conexión.') } }];
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


# ================================================================== 10
def f10():
    fl = Flujo("APARDIAN 10 · Radar: reporte del día")
    a, b = disparadores(fl, {"field": "cronExpression", "expression": "0 18 * * 1-5"})
    v = dict(CONFIG_BASE)
    v.update({"FECHA_INICIO": ("PEGAR_FECHA_DE_ARRANQUE", "string"),
              "CUPOS_POR_SEMANA": ("10,20,35,50", "string")})
    cfg = config(fl, "Config", v)
    leads = leer_hoja(fl, "Leer Leads", cfg, "Leads")
    resumen = codigo(fl, "Resumen", JS_HTML + JS_FECHA + JS_RADAR + r"""
// Lo que hizo Radar hoy y si hay algo para mirar. Nada de esto manda mails.
const c = $('Config').first().json;
const L = $('Leer Leads').all().map(r => r.json).filter(l => l.id);
const h = hoyUY();
const n = f => L.filter(f).length;
const cupos = String(c.CUPOS_POR_SEMANA || '10,20,35,50').split(',').map(Number).filter(x => x > 0);
const ini = /^\d{4}-\d{2}-\d{2}$/.test(String(c.FECHA_INICIO || '')) ? c.FECHA_INICIO : '';
const semana = ini ? Math.max(0, Math.floor((diasDesde(ini) + 1) / 7)) : 0;
const cupoManana = cupos[Math.min(semana, cupos.length - 1)] || 10;
const hoyEnv = L.filter(l => String(l.fecha_envio || '') === h);
const enviados = n(l => l.fecha_envio);
const interes = L.filter(l => ['interesado', 'pide_precio'].includes(l.estado));
const rebotes = n(l => l.estado === 'rebote');
const stock = n(l => l.estado === 'auditado' && l.email);
const porPais = {};
for (const l of hoyEnv) porPais[l.pais || 'Uruguay'] = (porPais[l.pais || 'Uruguay'] || 0) + 1;
const avisos = [];
if (enviados >= 40 && rebotes / enviados > 0.05) avisos.push('⚠️ Rebotan ' + Math.round(100 * rebotes / enviados) + '% de los mails. Pausá el envío (AUTO_ENVIO en false en el flujo 03) y revisá las direcciones: un dominio con muchos rebotes termina en spam.');
if (stock < cupoManana * 2) avisos.push('Quedan ' + stock + ' leads listos para escribir. Subí BUSQUEDAS_POR_DIA en el flujo 01 o agregá búsquedas en la hoja Busquedas.');
if (!ini) avisos.push('Falta FECHA_INICIO en los flujos 03 y 10: Radar está en el cupo de la semana 1.');
const lineas = [
  '<b>Radar · ' + esc(h) + '</b>',
  'Mails nuevos hoy: <b>' + hoyEnv.length + '</b>' + (Object.keys(porPais).length ? ' (' + Object.entries(porPais).map(([p, k]) => esc(p) + ' ' + k).join(', ') + ')' : ''),
  'En total: ' + enviados + ' enviados · ' + interes.length + ' con interés · ' + n(l => l.estado === 'baja') + ' bajas · ' + rebotes + ' rebotes',
  'Mañana: cupo de ' + cupoManana + ' · ' + stock + ' leads listos · ' + n(l => l.estado === 'nuevo') + ' por auditar',
];
const nuevosInteres = interes.slice(-5).map(l => '• ' + esc(l.nombre) + ' (' + esc(l.pais || 'Uruguay') + ', ' + esc(l.servicio || '') + '): ' + esc(String(l.respuesta || '').slice(0, 120)));
if (nuevosInteres.length) lineas.push('', '<b>Para contestar vos</b>', ...nuevosInteres);
if (avisos.length) lineas.push('', ...avisos.map(esc));
return [{ json: { telegram_text: lineas.join('\n') } }];
""")
    tg = telegram(fl, "Mandar reporte", cfg)
    fl.unir(a, cfg); fl.unir(b, cfg)
    fl.cadena(cfg, leads, resumen, tg)
    return fl


if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for f, archivo in ((f01, "01_prospector.json"), (f02, "02_auditor.json"),
                       (f03, "03_redactor_envio.json"), (f04, "04_seguimiento.json"),
                       (f05, "05_respuestas.json"), (f06, "06_bienvenida_whatsapp.json"),
                       (f07, "07_aprobacion_instagram.json"), (f08, "08_publicador_instagram.json"),
                       (f09, "09_radar_conexion_centro.json"), (f10, "10_radar_reporte.json")):
        fl = f()
        nombres = {n["name"] for n in fl.nodos}
        for a, salidas in fl.con.items():
            assert a in nombres, a
            for s in salidas["main"]:
                for c in s:
                    assert c["node"] in nombres, c["node"]
        print(fl.guardar(archivo), len(fl.nodos), "nodos")
