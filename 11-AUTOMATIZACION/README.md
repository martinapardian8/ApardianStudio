# Mapa de automatización — APARDIAN STUDIO

La idea: que la IA haga el trabajo repetitivo (buscar, mirar, escribir el primer
borrador, recordar seguimientos) y que Martin haga lo que vende: mirar, decidir,
conversar y fotografiar.

Todo corre en **n8n**. Los cerebros son llamadas a Claude. El CRM es una planilla
de Google Sheets. Martin aprueba desde Telegram.

---

## 1. Qué automatizar primero (ordenado por ROI)

ROI = plata que puede traer ÷ (horas de armado + costo mensual). Los números de
costo son estimados con precios públicos a octubre 2026; los de impacto son
hipótesis a validar con la operación real (se anotan en `09-ESTUDIO/APRENDIZAJES.md`).

| P | Idea | Qué resuelve | Esfuerzo de armado | Costo mensual | Impacto en ventas | Semana |
|---|---|---|---|---|---|---|
| **P1** | **Respuesta rápida a consultas** (WhatsApp Business + DM de Instagram): bienvenida, 3 preguntas de calificación, borrador de respuesta para Martin | Hoy cada consulta espera a que Martin la vea. Quien responde primero suele cerrar | Bajo · 2 h (respuestas rápidas de WhatsApp Business) + 2 h (flujo `06`) | US$ 0–5 | **Alto**: no se pierde ninguna consulta que ya llegó, y es el dinero más cercano | 1 |
| **P2** | **Seguimiento automático de presupuestos** | Presupuestos que se mandan y nadie vuelve a tocar | Bajo · 2 h (planilla + recordatorio en Telegram a los 2 y 5 días) | US$ 0 | **Alto**: se recuperan cierres que hoy se enfrían | 1 |
| **P3** | **Prospección + auditoría + mail en frío B2B** (flujos `01`–`05`) | No hay flujo constante de clientes nuevos; depende del boca a boca | Medio · 1 día de armado + 1 semana de calentamiento del dominio | US$ 25–60 (n8n + Claude + Places + dominio) | **Alto y escalable**: restaurantes, marcas, salones, inmobiliarias. Cada cierre de gastronomía o web paga varios meses del sistema | 2–3 |
| **P4** | **Prospección de fotógrafos para edición en Lightroom** (mismo motor, otro rubro, ES/EN/PT) | El servicio que más escala no tiene canal de venta propio | Bajo una vez hecho P3 · 3 h (rubro nuevo + plantillas en 3 idiomas) | +US$ 5–10 | **Alto a mediano plazo**: cliente recurrente, sin estar presente, de cualquier país | 4 |
| **P5** | **Pedido de reseña y testimonio post-entrega** | Falta prueba social con nombre y apellido (Google, web, Instagram) | Bajo · 1 h (mensaje a los 3 días de entregar) | US$ 0 | **Medio**: mejora la conversión de todo lo demás, incluido el mail en frío | 2 |
| **P6** | **Reactivación de clientes viejos** (80+ proyectos entregados) | Gente que ya confió y no volvió a saber de Martin | Bajo · 2 h (lista + mensaje por temporada) | US$ 0 | **Medio-alto**: el cliente que ya pagó es el más barato de volver a cerrar. Fechas clave: fin de año, verano, Día de la Madre | 3 |
| **P7** | **Calendario con aprobación y publicación automática en Instagram** (flujos `07` y `08`: Martin aprueba desde Telegram y el agente publica a la hora con la Instagram Graph API) | Publicar a mano, olvidarse semanas, o que salga algo sin que Martin lo vea | Medio · 2–3 h (cuenta profesional, app de Meta, token, planilla) | US$ 0 | **Medio**: constancia sin perder control. No vende solo, pero sostiene todo | 2 |
| **P8** | **Reporte semanal de métricas** (lunes 9:00 en Telegram) | No se sabe qué canal trae consultas (pregunta abierta en `APRENDIZAJES.md`) | Medio · 3 h | US$ 0–2 | **Medio**: decide dónde poner plata y tiempo | 4 |

**Orden de ataque:** primero P1 y P2 (cuidan las consultas que ya existen, cero
riesgo), después P3 (trae consultas nuevas), y recién con P3 andando, P4.

**P7 en detalle:** la planilla `Calendario` tiene un posteo y una historia
por día, con su pie de foto. Lupa (`10-MOTOR/lupa.py`) revisa cada pieza; lo
que pasa, el flujo 07 se lo manda a Martin por Telegram un día antes con dos
botones, *Aprobar* y *No publicar*. Lo aprobado lo publica el flujo 08 a la
hora fijada (feed, reels e historias). Lo que no se aprueba no sale. Solo la
historia del lunes con sticker de enlace queda a mano. Ver
`INSTAGRAM_APROBACION.md` y el equipo en `09-ESTUDIO/EQUIPO.md`.

---

## 2. Cómo funciona el sistema de prospección (P3)

Cinco agentes, cada uno hace una sola cosa. Ninguno manda nada sin que Martin lo vea.

```
 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌───────────────────┐
 │ 01 PROSPECTOR│──▶│ 02 AUDITOR   │──▶│ 03 REDACTOR  │──▶│ 11 BANDEJA        │
 │ Google Places│   │ mira la web, │   │ escribe el   │   │ Martin aprueba o  │
 │ rating ≥ 4,5 │   │ puntúa 0-100 │   │ mail (≤120   │   │ edita; el 12 lo   │
 │ → Leads      │   │ y detecta el │   │ palabras)    │   │ manda (contacto@) │
 └──────────────┘   │ problema real│   └──────────────┘   └─────────┬─────────┘
                    └──────────────┘                                │ enviado
                                                                    ▼
 ┌──────────────┐   ┌──────────────┐                      ┌───────────────────┐
 │ CRM (Sheets) │◀──│ 05 RESPUESTAS│◀─────────────────────│ 04 SEGUIMIENTO    │
 │ Leads, Bajas │   │ clasifica:   │                      │ día 4: aporta algo│
 │ estado de    │   │ interesado,  │                      │ día 9: cierre     │
 │ cada lead    │   │ precio, baja │                      │ elegante. Máx. 2  │
 └──────────────┘   └──────┬───────┘                      └───────────────────┘
                           │ interesado / pide precio
                           ▼
                   Telegram a Martin → conversación humana → presupuesto
```

En palabras:

1. **Prospector** (`n8n/01_prospector.json`). Todos los días busca en Google
   Maps negocios por rubro y ciudad, con foco en marcas de moda, empresas y
   pymes ("tiendas de ropa de mujer en Montevideo", "estudios contables en
   Montevideo"). Guarda solo los que tienen **buena reputación** (rating 4,5 o
   más con 15 reseñas o más) y no están ya en la planilla, tengan web o no.
2. **Auditor** (`n8n/02_auditor.json`). Entra a cada web, mide cosas concretas
   (título, si anda en celular, cuántas fotos hay, si tiene botón de WhatsApp, si
   carga lento, si tiene HTTPS) y Claude la evalúa como un consultor de
   comunicación visual. Devuelve un puntaje de oportunidad, el servicio de
   Apardian que más le sirve (casi siempre la **página web**) y **el problema
   con su evidencia**. Si no hay evidencia, no hay problema: el prompt le
   prohíbe inventar. A los que no tienen web, o no publican mail, les escribe
   un WhatsApp para que Martin lo mande a mano.
3. **Redactor** (`n8n/03_redactor.json`). Para los leads con puntaje ≥ 60,
   escribe un mail corto: qué vimos, qué problema tiene, cómo lo resolvemos, una
   prueba y una pregunta fácil de contestar. Lo deja en la **bandeja**
   (`n8n/11_radar_bandeja.json`): Martin lo lee, lo edita si quiere y lo
   aprueba. El **envío** (`n8n/12_radar_envio.json`) lo manda desde
   **contacto@apardianstudio.com** en el horario de oficina del destinatario.
4. **Seguimiento** (`n8n/04_seguimiento.json`). Si a los 4 días no contestó, un
   segundo mail que aporta algo (una idea concreta). A los 9 días, uno de cierre
   elegante. Después, se deja tranquilo. También pasan por la bandeja.
5. **Respuestas** (`n8n/05_respuestas.json`). Lee la bandeja de contacto@ por
   IMAP (solo los mails de negocios a los que Radar les escribió; las consultas
   de la web quedan intactas, sin marcar como leídas), las clasifica
   y avisa a Martin solo cuando hay interés. Las bajas van a una lista negra que
   todos los flujos consultan.

Los textos que manejan a cada agente están en `prompts/` y se editan sin tocar
n8n. Ejemplos escritos a mano por rubro en `prompts/plantillas_mail.md`.

### La regla de la casa

> Antes de mandar cualquier mensaje a un cliente real, se lo muestra a Martin.

Sin excepciones (decisión de Martin, 25/10/2026, que reemplaza la del 24/10):
los mails de **Radar** también pasan por su aprobación. Radar escribe de lunes
a viernes a las 8 y le avisa por Telegram; Martin abre la **bandeja** desde el
Centro → Radar (o desde el aviso), lee cada mail con lo que vio Radar, lo edita
si quiere y lo aprueba o lo descarta. Lo aprobado sale desde contacto@ en el
horario de oficina del destinatario, hasta 90 por día. Los WhatsApp los manda
Martin a mano desde la misma bandeja. Las respuestas de los clientes las
contesta Martin. Todo el detalle, incluidos los mercados de afuera y la parte
legal por país, en `RADAR_PASO_A_PASO.md`.

---

## 3. Lo que hay que saber antes de prender (sin esto, no funciona)

### Que los mails lleguen (entregabilidad)

- **La casilla de envío** es `contacto@apardianstudio.com`, en Hostinger
  (decisión de Martin, 25/10/2026). Es el dominio de la web: si los mails en
  frío caen en spam, lo sufre todo `apardianstudio.com`, también `martin@`.
  Por eso Radar tiene un **tope total por día** (`LIMITE_TOTAL_DIA`, nuevos +
  seguimientos) y el reporte avisa si rebota más del 5 %.
- **El plan de correo de Hostinger pone el techo**: el gratis manda 100 mails
  por día por casilla (ventana de 24 horas). Martin eligió quedarse ahí:
  `LIMITE_TOTAL_DIA` en 90 deja 10 para lo que conteste a mano, y Radar
  escribe hasta 30 nuevos por día para que entren sus seguimientos.
- **SPF, DKIM y DMARC** en el DNS de `apardianstudio.com` (Hostinger →
  Emails → Configuración de DNS). Sin esto, todo va a spam.
- **Calentamiento:** 2 semanas mandando poco (5–10 por día, mejor a gente que
  responde). Recién después, **20–40 mails por día como máximo**. Nunca 200 de golpe.
- **Nunca comprar listas.** Solo negocios encontrados por el prospector, con datos
  públicos de su propia web o ficha de Google.
- Texto plano, sin imágenes adjuntas, un solo link (apardianstudio.com). Nada de
  "GRATIS", "OFERTA", signos de exclamación en el asunto.

### Lo legal (Uruguay, Ley 18.331 de protección de datos personales)

- Solo **datos públicos de empresas** (web, ficha de Google Maps, mail de contacto
  publicado en su sitio). No adivinar mails personales tipo nombre.apellido@.
- Identificarse siempre: nombre, estudio, web y teléfono en la firma.
- **Opción clara de baja** en cada mail ("Si no te interesa, respondé 'no' y no te
  escribo más"). Quien responde "no" o "baja" va a la hoja `Bajas` y nunca más
  recibe nada de ningún flujo.
- **Máximo 2 seguimientos.** Tres mails en total y se cierra.
- Guardar el registro de bajas (la hoja `Bajas` es ese registro).
- Esto es una guía práctica, no asesoramiento legal. Si el volumen crece, vale
  una consulta con un abogado.

---

## 4. Puesta en marcha (checklist)

**n8n: cloud o propio**

| Opción | Costo | Cuándo |
|---|---|---|
| n8n Cloud (plan Starter) | ~US$ 24/mes | Para arrancar ya, sin servidor. Recomendado |
| Self-host en un VPS (Hostinger VPS, Hetzner) | US$ 5–8/mes | Cuando haya más de 2.500 ejecuciones por mes o se quiera ahorrar |

**Credenciales que hay que crear en n8n** (Settings → Credentials). Los flujos
las buscan con estos nombres exactos:

- [ ] `Anthropic API` — tipo **Header Auth**: name `x-api-key`, value la API key
      de console.anthropic.com.
- [ ] `Google Places API` — tipo **Header Auth**: name `X-Goog-Api-Key`, value una
      API key de Google Cloud con **Places API (New)** habilitada.
- [ ] `Google Sheets` — tipo Google Sheets OAuth2.
- [ ] `Hostinger SMTP (contacto@)` — tipo **SMTP**: host `smtp.hostinger.com`,
      puerto `465`, SSL/TLS activado, usuario `contacto@apardianstudio.com` y
      su contraseña. La usa el 12.
- [ ] `Hostinger IMAP (contacto@)` — tipo **IMAP**: host `imap.hostinger.com`,
      puerto `993`, SSL/TLS activado, el mismo usuario y contraseña. La usa el 05.
- [ ] `Telegram Apardian` — token de un bot creado con @BotFather. Mandarle un
      mensaje al bot y anotar tu `chat_id`.

**Datos a completar** en el nodo `Config` de cada flujo (y en `Config guardar`
del 11):

- `SHEET_ID` — el ID de la planilla (lo que va entre `/d/` y `/edit` en la URL).
- `TELEGRAM_CHAT_ID` — el chat de Martin.
- `MI_EMAIL` — ya viene `Martin Apardian <contacto@apardianstudio.com>`.
- `LIMITE_TOTAL_DIA` (12) — 90 con el correo gratis de Hostinger.
- `URL_BANDEJA` (03 y 10) — la URL de producción del webhook `apardian-bandeja`
  (se ve al abrir el nodo *Abrir bandeja* del flujo 11).
- `TOKEN` — una clave larga inventada por vos, **la misma** en el 03, el 09,
  el 10 y los dos `Config` del 11, y en el Centro → Radar → Conexión. Evita
  que cualquiera que adivine el link pueda abrir la bandeja o aprobar mails.

**Si cambiás un prompt** (`prompts/*.md`), corré
`python3 11-AUTOMATIZACION/armar_flujos.py` y reimportá el flujo. También
podés pegar el texto directo en el nodo `Prompt …` de n8n.

**Planilla:** crear una Google Sheet con las hojas `Leads` y `Bajas` usando las
columnas de `sheets_estructura.md` (o importar `leads_plantilla.csv`).

**Importar flujos:** en n8n, *Workflows → Import from file* → cada JSON de `n8n/`.
Después de importar, abrir cada nodo con credencial y elegirla en el desplegable
(n8n a veces no la enlaza sola por nombre).

**Probar en este orden:** 01 con un solo rubro y ciudad → 02 con 3 leads → 03 con 1
lead, mirar el mail en la bandeja y aprobarlo → 12 con un mail a vos mismo → 05 respondiéndote a vos mismo. Recién entonces, activar
los disparadores programados.

---

## 5. Cuánto cuesta por mes (estimado)

| Ítem | Costo |
|---|---|
| n8n Cloud Starter | ~US$ 24 |
| Claude (Opus 5.5: US$ 4 / US$ 20 por millón de tokens). Auditoría ≈ 6.000 tokens de entrada + 1.000 de salida ≈ US$ 0,045. Mail ≈ US$ 0,03. Clasificación ≈ US$ 0,01 | 300 leads/mes ≈ **US$ 25** |
| Google Places Text Search (New) | 200 búsquedas/mes ≈ US$ 7 (Google da crédito mensual que suele cubrirlo) |
| Correo de Hostinger (contacto@) | incluido en tu plan (gratis: 100 por día) |
| **Total** | **~US$ 55–65/mes** con 300 leads auditados |

Para bajar costo cuando el sistema esté probado: pasar la clasificación de
respuestas a `claude-haiku-5-5` (es una tarea simple). La auditoría y la redacción
conviene dejarlas en Opus: son las que venden.

---

## 6. Archivos

| Archivo | Qué es |
|---|---|
| `n8n/01_prospector.json` | Busca negocios en Google Places y los carga como leads |
| `n8n/02_auditor.json` | Audita la web de cada lead con Claude |
| `n8n/03_redactor.json` | Escribe el primer mail y lo deja en la bandeja |
| `n8n/04_seguimiento.json` | Seguimientos a los 4 y 9 días, también a la bandeja |
| `n8n/05_respuestas.json` | Lee contacto@ por IMAP, clasifica respuestas y rebotes, avisa a Martin |
| `n8n/06_bienvenida_whatsapp.json` | Recibe una consulta y propone respuesta (P1) |
| `n8n/07_aprobacion_instagram.json` | Pide aprobación por Telegram de lo que sale en las próximas 36 h (P7) |
| `n8n/08_publicador_instagram.json` | Publica en Instagram lo aprobado, a su hora (P7) |
| `n8n/09_radar_conexion_centro.json` | Recibe del Centro las ofertas y el entrenamiento de Radar |
| `n8n/10_radar_reporte.json` | El reporte de Radar de las 18:00 |
| `n8n/11_radar_bandeja.json` | La bandeja: Martin aprueba, edita o descarta mails y WhatsApp |
| `n8n/12_radar_envio.json` | Manda lo aprobado desde contacto@, en horario y con tope de 90 por día |
| `prompts/whatsapp.md` | El WhatsApp para los que no tienen web o mail |
| `radar_busquedas.csv` | Plan de búsquedas: moda, empresas y pymes primero |
| `calendario_instagram.csv` | La hoja `Calendario` lista para importar (sale de `10-MOTOR/calendario_sheet.py`) |
| `INSTAGRAM_APROBACION.md` | Cómo se arma y se usa la publicación con aprobación |
| `prompts/*.md` | Los textos que guían a cada agente. Editables |
| `prompts/plantillas_mail.md` | Mails de ejemplo por rubro, escritos a mano |
| `sheets_estructura.md` | Columnas y estados del CRM |
| `leads_plantilla.csv` / `bajas_plantilla.csv` | Encabezados para importar a Sheets |
| `armar_flujos.py` | Regenera los JSON de `n8n/` a partir de `prompts/` |
| `../09-ESTUDIO/CM_VENTAS.md` | Playbook del community manager de ventas |
| `../.claude/agents/trato-ventas.md` | Trato, el agente de ventas (equipo en `09-ESTUDIO/EQUIPO.md`) |
