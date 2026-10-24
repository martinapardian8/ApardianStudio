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
 │ 01 PROSPECTOR│──▶│ 02 AUDITOR   │──▶│ 03 REDACTOR  │──▶│ APROBACIÓN MARTIN │
 │ Google Places│   │ mira la web, │   │ escribe el   │   │ borrador en Gmail │
 │ rubro×ciudad │   │ puntúa 0-100 │   │ mail (≤120   │   │ + aviso Telegram  │
 │ → Leads      │   │ y detecta el │   │ palabras)    │   │ "Enviar" / "No"   │
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

1. **Prospector** (`n8n/01_prospector.json`). Cada lunes busca en Google Maps
   negocios por rubro y ciudad ("restaurantes en Pocitos", "salones de eventos en
   Canelones", "inmobiliarias en Punta del Este"). Guarda los que tienen web y no
   están ya en la planilla.
2. **Auditor** (`n8n/02_auditor.json`). Entra a cada web, mide cosas concretas
   (título, si anda en celular, cuántas fotos hay, si tiene botón de WhatsApp, si
   carga lento, si tiene HTTPS) y Claude la evalúa como un consultor de
   comunicación visual. Devuelve un puntaje de oportunidad, el servicio de
   Apardian que más le sirve y **el problema con su evidencia**. Si no hay
   evidencia, no hay problema: el prompt le prohíbe inventar.
3. **Redactor** (`n8n/03_redactor_envio.json`). Para los leads con puntaje ≥ 60,
   escribe un mail corto: qué vimos, qué problema tiene, cómo lo resolvemos, una
   prueba y una pregunta fácil de contestar. Lo deja como **borrador en Gmail** y
   le avisa a Martin por Telegram.
4. **Seguimiento** (`n8n/04_seguimiento.json`). Si a los 4 días no contestó, un
   segundo mail que aporta algo (una idea concreta). A los 9 días, uno de cierre
   elegante. Después, se deja tranquilo.
5. **Respuestas** (`n8n/05_respuestas.json`). Lee las respuestas, las clasifica
   y avisa a Martin solo cuando hay interés. Las bajas van a una lista negra que
   todos los flujos consultan.

Los textos que manejan a cada agente están en `prompts/` y se editan sin tocar
n8n. Ejemplos escritos a mano por rubro en `prompts/plantillas_mail.md`.

### La regla de la casa, y su excepción

> Antes de mandar cualquier mensaje a un cliente real, se lo muestra a Martin.

Excepción decidida por Martin el 24/10/2026: los mails en frío de **Radar**
salen solos (`AUTO_ENVIO` en `true` en los flujos 03 y 04), hasta 50 nuevos
por día con calentamiento de 10 → 20 → 35 → 50, y solo con las ofertas y el
entrenamiento que Martin aprueba en el Centro (pestaña Radar, flujo 09). Las
respuestas de los clientes las contesta Martin. Todo el detalle, incluidos los
mercados de afuera y la parte legal por país, en `RADAR_PASO_A_PASO.md`.

Con `AUTO_ENVIO` en `false` vuelve el modo anterior: cada mail queda como
borrador y se aprueba por Telegram.

**Cómo se aprueba:** el mensaje de Telegram trae dos links, *Enviar* y
*Descartar*. Si querés cambiar algo, editás el borrador en Gmail (carpeta
Borradores) y después tocás *Enviar*: se manda la versión editada. Si el lead
respondió mientras tanto, el link ya no envía nada.

---

## 3. Lo que hay que saber antes de prender (sin esto, no funciona)

### Que los mails lleguen (entregabilidad)

- **Dominio de envío separado.** No mandar en frío desde `martinapardian8@gmail.com`
  ni desde el dominio principal. Comprar un dominio hermano (por ejemplo
  `apardian.studio` o `apardianstudio.co`) y usar `martin@` ese dominio con
  Google Workspace. Si algo sale mal, se quema ese dominio, no la web.
- **SPF, DKIM y DMARC** configurados en el DNS del dominio de envío (Google
  Workspace lo guía paso a paso). Sin esto, todo va a spam.
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
- [ ] `Gmail Apardian` — tipo Gmail OAuth2, con la cuenta del dominio de envío.
- [ ] `Telegram Apardian` — token de un bot creado con @BotFather. Mandarle un
      mensaje al bot y anotar tu `chat_id`.

**Datos a completar** en el nodo `Config` de cada flujo (y en `Config aprobación`
del 03):

- `SHEET_ID` — el ID de la planilla (lo que va entre `/d/` y `/edit` en la URL).
- `TELEGRAM_CHAT_ID` — el chat de Martin.
- `MI_EMAIL` / `MI_DIRECCION` — la casilla del dominio de envío.
- `URL_APROBAR` — la URL de producción del webhook `apardian-aprobar` (se ve al
  abrir el nodo *Aprobación* del flujo 03). Va en los flujos 03 y 04.
- `TOKEN` — una clave larga inventada por vos, **la misma** en los nodos
  `Config` y `Config aprobación` del 03 y en el `Config` del 04. Evita que
  cualquiera que adivine el link pueda mandar mails.

**Si cambiás un prompt** (`prompts/*.md`), corré
`python3 11-AUTOMATIZACION/armar_flujos.py` y reimportá el flujo. También
podés pegar el texto directo en el nodo `Prompt …` de n8n.

**Planilla:** crear una Google Sheet con las hojas `Leads` y `Bajas` usando las
columnas de `sheets_estructura.md` (o importar `leads_plantilla.csv`).

**Importar flujos:** en n8n, *Workflows → Import from file* → cada JSON de `n8n/`.
Después de importar, abrir cada nodo con credencial y elegirla en el desplegable
(n8n a veces no la enlaza sola por nombre).

**Probar en este orden:** 01 con un solo rubro y ciudad → 02 con 3 leads → 03 con 1
lead y mirar el borrador → 05 respondiéndote a vos mismo. Recién entonces, activar
los disparadores programados.

---

## 5. Cuánto cuesta por mes (estimado)

| Ítem | Costo |
|---|---|
| n8n Cloud Starter | ~US$ 24 |
| Claude (Opus 5.5: US$ 4 / US$ 20 por millón de tokens). Auditoría ≈ 6.000 tokens de entrada + 1.000 de salida ≈ US$ 0,045. Mail ≈ US$ 0,03. Clasificación ≈ US$ 0,01 | 300 leads/mes ≈ **US$ 25** |
| Google Places Text Search (New) | 200 búsquedas/mes ≈ US$ 7 (Google da crédito mensual que suele cubrirlo) |
| Dominio de envío + Google Workspace | ~US$ 1 + US$ 7 |
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
| `n8n/03_redactor_envio.json` | Escribe el mail, crea borrador y pide aprobación |
| `n8n/04_seguimiento.json` | Seguimientos a los 4 y 9 días |
| `n8n/05_respuestas.json` | Clasifica respuestas y avisa a Martin |
| `n8n/06_bienvenida_whatsapp.json` | Recibe una consulta y propone respuesta (P1) |
| `n8n/07_aprobacion_instagram.json` | Pide aprobación por Telegram de lo que sale en las próximas 36 h (P7) |
| `n8n/08_publicador_instagram.json` | Publica en Instagram lo aprobado, a su hora (P7) |
| `calendario_instagram.csv` | La hoja `Calendario` lista para importar (sale de `10-MOTOR/calendario_sheet.py`) |
| `INSTAGRAM_APROBACION.md` | Cómo se arma y se usa la publicación con aprobación |
| `prompts/*.md` | Los textos que guían a cada agente. Editables |
| `prompts/plantillas_mail.md` | Mails de ejemplo por rubro, escritos a mano |
| `sheets_estructura.md` | Columnas y estados del CRM |
| `leads_plantilla.csv` / `bajas_plantilla.csv` | Encabezados para importar a Sheets |
| `armar_flujos.py` | Regenera los JSON de `n8n/` a partir de `prompts/` |
| `../09-ESTUDIO/CM_VENTAS.md` | Playbook del community manager de ventas |
| `../.claude/agents/trato-ventas.md` | Trato, el agente de ventas (equipo en `09-ESTUDIO/EQUIPO.md`) |
