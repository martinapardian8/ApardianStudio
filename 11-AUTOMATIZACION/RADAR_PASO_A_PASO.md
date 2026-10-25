# Radar — paso a paso

Radar busca marcas y empresas con **muy buena reputación** (4,5 o más en
Google) y una **web floja o sin web**, sobre todo de moda, empresas y pymes.
Mira lo que tienen, le escribe a cada una una propuesta de página web hecha
para ella y prepara dos seguimientos. **Nada sale sin tu OK** (decisión tuya
del 25/10/2026): cada mail, seguimiento y WhatsApp lo aprobás o editás en la
**bandeja**, que abrís desde el Centro → Radar. Lo aprobado sale desde
contacto@, hasta 90 por día. Las ofertas y el entrenamiento también los
aprobás en el Centro.

```
 Busquedas (hoja)          Google Maps            la web del negocio
       │                        │                         │
 01 Prospector ── 12 búsquedas por día ──▶ Leads ──▶ 02 Auditor (90 por día)
                                                          │ puntaje, problema, propuesta
                                                          ▼
 Centro → Radar ── aprobás ofertas y entrenamiento ──▶ 09 ──▶ hojas Ofertas / Entrenamiento
                                                          │
                                                          ▼
                         03 Redactor (8:00) y 04 Seguimientos (día 4 y día 9)
                         10 → 20 → 30 borradores nuevos por día
                                                          │
                         11 Bandeja: vos aprobás, editás o descartás
                            (también los WhatsApp, que mandás vos)
                                                          │
                         12 Envío (cada hora, 9 a 17): desde contacto@,
                            en el horario de cada país, hasta 90 por día
                                                          │
                 05 Respuestas: interesado → Telegram ────┤──▶ Trato y vos
                 10 Reporte diario, 18:00, por Telegram ◀─┘
```

En Uruguay Radar ofrece todo, incluido ir al lugar. En Argentina, México y
Latinoamérica, España y EE.UU. ofrece solo lo que se hace online: páginas web,
edición en Lightroom, marca 360 + manual y producción musical.

---

## Lo que hacés vos (una sola vez, unas 4 horas repartidas en dos semanas)

Los mismos pasos están en el Centro → Radar → Puesta en marcha, para ir
tildándolos.

### Semana 1 — la casilla

Radar manda desde **contacto@apardianstudio.com**, la casilla de Hostinger que
ya creaste (decisión tuya del 25/10/2026). Es el mismo dominio de la web y de
`martin@`: si los mails en frío caen en spam, lo sienten todos. Por eso Radar
sube de a poco, tiene un tope por día y el reporte te avisa si rebota más del 5 %.

1. **El plan de correo: el gratis alcanza** (decisión tuya). Manda 100 mails
   por día; Radar usa hasta 90 (`LIMITE_TOTAL_DIA`) y deja 10 para lo que
   contestes vos desde contacto@. Si un día querés más, Business Starter manda
   1.000 por día.
2. **SPF, DKIM y DMARC.** Hostinger → Emails → apardianstudio.com →
   Configuración de DNS (o Autenticación): los tres tienen que estar en verde.
   Si DMARC falta, agregá en Hostinger → Dominios → DNS un registro TXT con
   nombre `_dmarc` y valor
   `v=DMARC1; p=none; rua=mailto:contacto@apardianstudio.com`. Probalo en
   mail-tester.com mandando un mail desde contacto@: tiene que dar 9/10 o más.
3. **Foto y firma en contacto@** (webmail de Hostinger → Configuración):
   `Martin Apardian · APARDIAN STUDIO · apardianstudio.com · WhatsApp +598 91 962 962`.
4. **Calentá la casilla dos semanas**: 5 a 10 mails reales por día desde
   contacto@ a gente que te conoce y te contesta (clientes, colegas, amigos).
   Que respondan es lo que les enseña a Gmail y a Outlook que sos de confianza.
5. **Las respuestas llegan a contacto@.** Radar lee esa bandeja, te avisa por
   Telegram cuando alguien se interesa y no toca nada más: las consultas que
   lleguen desde la web siguen ahí, sin marcar como leídas.

### Semana 1 — las cuentas

6. **n8n**: n8n.io → plan Starter. Ahí corren todos los flujos.
7. **Clave de Google Places**: console.cloud.google.com → proyecto nuevo →
   activar **Places API (New)** → Credenciales → Crear clave de API.
   Restringila a Places API y **poné un tope de gasto mensual** (Facturación →
   Presupuestos y alertas).
8. **Clave de Claude**: console.anthropic.com → API keys. **Poné un límite de
   gasto mensual** (Settings → Limits). Radar audita unas 90 webs y escribe
   unos 30 mails y 15 WhatsApp por día: el primer mes mirá cuánto gasta y ajustá.
9. **Bot de Telegram**: en Telegram, @BotFather → /newbot. Guardá el token y tu
   chat ID (te lo da @userinfobot). Ahí te llegan el reporte diario y los
   clientes interesados.

### Semana 2 — conectar

10. **La planilla**: una planilla de Google Sheets con las hojas `Leads`,
    `Bajas`, `Busquedas`, `Ofertas` y `Entrenamiento`. Importá en cada una su
    plantilla de esta carpeta (`leads_plantilla.csv`, `bajas_plantilla.csv`,
    `radar_busquedas.csv`, `ofertas_plantilla.csv`,
    `entrenamiento_plantilla.csv`).
11. **Importá en n8n los flujos** `01` a `05` y `09` a `12` de `n8n/`
    (Import from file). En cada nodo **Config**:
    - `SHEET_ID`: el ID de la planilla (lo que está entre `/d/` y `/edit` en su link).
    - `TELEGRAM_CHAT_ID`: tu chat.
    - `MI_EMAIL` (12): ya viene `Martin Apardian <contacto@apardianstudio.com>`.
    - `LIMITE_TOTAL_DIA` (12): ya viene en 90.
    - `FECHA_INICIO` (03 y 10): el primer día de envío, `AAAA-MM-DD`.
    - `DIRECCION_POSTAL` (03, 04 y 12): si querés escribirle a EE.UU. (ver la parte legal).
    - `TOKEN` (03, 09, 10 y los dos Config del 11): la misma clave larga
      inventada por vos.
    - `URL_BANDEJA` (03 y 10): la dirección de producción del webhook del
      flujo 11 (termina en `/webhook/apardian-bandeja`).
    - Elegí las credenciales (Google Sheets, Telegram, Google Places,
      Anthropic y las dos de contacto@) donde dice `REEMPLAZAR`. Las de
      contacto@ se crean en n8n → Credentials:
      - **SMTP** `Hostinger SMTP (contacto@)`: `smtp.hostinger.com`, puerto
        `465`, SSL activado, usuario `contacto@apardianstudio.com` y su contraseña.
      - **IMAP** `Hostinger IMAP (contacto@)`: `imap.hostinger.com`, puerto
        `993`, SSL activado, el mismo usuario y contraseña.
      La contraseña va solo ahí, nunca en la planilla.
12. **Conectá el Centro**: Centro → Radar → Conexión con n8n. Pegá la dirección
    de producción del webhook del flujo 09 (termina en
    `/webhook/apardian-radar`), la misma clave del paso 11 y la fecha de
    arranque. Con eso, el botón **Abrir la bandeja** del Centro ya funciona.
13. **Entrená a Radar y aprobá las primeras ofertas**: Centro → Radar.
    Contestá el entrenamiento (lo que puedas) y tocá **Enseñarle a Radar**.
    Pedile 3 propuestas de ofertas, editalas y aprobá las que te gusten. Cada
    aprobación abre una pestaña de n8n que dice *Oferta activada ✓*.
14. **Publicá la web nueva** (decile a Claude "publicá la web"): los mails
    llevan a `apardianstudio.com/propuesta.html`, que tiene que existir antes
    del primer envío.
15. **Prendé los flujos** 01 a 05 y 09 a 12. A las 8 del día siguiente te
    llega el aviso de la bandeja; a las 18:00, el primer reporte.

### Todos los días (15 a 20 minutos)

- **A las 8, la bandeja.** Te llega un aviso por Telegram. Abrí la bandeja
  (Centro → Radar → Abrir la bandeja): cada mail viene con el negocio, su
  reputación, su web y lo que vio Radar. Editá lo que quieras y marcá
  *Aprobar* o *Descartar*; si todos te convencen, *Aprobar todos los mails*.
  Tocá **Guardar**. Lo aprobado sale ese día en el horario de cada país. Lo
  que no marques queda para después.
- **Los WhatsApp** están en la misma bandeja: tocá *Abrir en WhatsApp*,
  mandalo desde tu teléfono, volvé y marcá *Ya lo mandé*. Mandá pocos por día
  (10 a 15) y en horario comercial: WhatsApp bloquea los números que escriben
  mucho a desconocidos.
- A las 18:00, el reporte de Radar por Telegram: cuántos salieron, a qué
  países, cuántos respondieron, cuánto queda para aprobar y si hay algo para
  mirar.
- Cuando alguien responde con interés, te llega un aviso. **Esa respuesta la
  contestás vos** (Trato te arma el borrador en el Centro).

### Cada semana (15 minutos)

- Mirá las ofertas: pausá lo que no funciona y aprobá ideas nuevas de Radar.
- Si el reporte dice que quedan pocos leads, pedile a Radar (en Claude Code o
  en el Centro) búsquedas nuevas para la hoja `Busquedas`.

---

## Cuántos por día

| Semana desde FECHA_INICIO | Mails nuevos por día para aprobar |
|---|---|
| 1 | 10 |
| 2 | 20 |
| 3 en adelante | 30 |

Con 30 nuevos por día, más sus dos seguimientos, la casilla queda cerca de
los 90 por día, dentro de los 100 del correo gratis de Hostinger. Si en la
bandeja ya hay 60 esperando, Radar no escribe más hasta que los revises.
Salen de lunes a viernes, de a pocos cada hora, y solo en horario de oficina
**del país del destinatario** (de 9 a 17 allá). Si llega al tope de 90, ese
día no sale nada más. Si querés otro ritmo, cambiá `CUPOS_POR_SEMANA` en los
flujos 03 y 10.

A 30 por día son unos 650 mails por mes. Con 1 a 3 % de respuestas, lo
habitual en mail en frío bien hecho, son 6 a 20 conversaciones por mes, más
lo que traigan los WhatsApp. Es una estimación: los números reales los da el
reporte.

**Frenos que tiene solo:**
- Si rebotan más del 5 % de los mails, el reporte te avisa para pausar
  (apagá el flujo 12 y revisá las direcciones).
- Si un lead responde mientras su seguimiento espera en la bandeja, el
  seguimiento ya no sale.
- Quien responde "no" o "baja" va a la hoja `Bajas` y nunca más recibe nada.
- Quien responde deja de recibir seguimientos.
- Nunca más de `LIMITE_TOTAL_DIA` mails por día desde contacto@, sumando
  nuevos y seguimientos, ni más de uno por día al mismo negocio.

---

## La parte legal (léela antes de prender)

Esto es una guía práctica, no asesoramiento legal. Si el volumen crece, vale
una consulta con un abogado.

- **En todos lados:** solo mails de empresas publicados en su propia web, nunca
  listas compradas ni mails personales adivinados. Identificación completa en
  cada mail, un solo link y la opción de baja. Máximo dos seguimientos.
- **WhatsApp:** lo mandás vos, uno por uno, solo al número comercial que el
  negocio publica en Google, con tu nombre y la opción de no recibir más. Si
  alguien dice que no, marcalo *Descartar* y no se le escribe más.
- **Uruguay (Ley 18.331) y Argentina (Ley 25.326):** datos públicos de
  empresas, identificación y baja inmediata. Es lo que ya hace Radar.
- **México (LFPDPPP) y el resto de Latinoamérica:** igual: datos de contacto
  comerciales publicados por la empresa, baja respetada siempre.
- **EE.UU. (CAN-SPAM):** se permite el mail comercial en frío, pero exige
  **una dirección postal física** en el mail (puede ser una casilla de correo
  o un servicio de dirección virtual) y la baja en menos de 10 días. Sin
  `DIRECCION_POSTAL` en los flujos 03 y 04, Radar no le escribe a EE.UU.
- **España (LSSI, art. 21):** **es la más estricta**: prohíbe mandar
  publicidad por mail a quien no la pidió, también a empresas, y la AEPD
  multa. Por eso las búsquedas de España arrancan **apagadas** (`activo = no`
  en la hoja `Busquedas`). Opciones: dejarla apagada, contactar en España
  solo por formulario web o Instagram (a mano), o consultarlo con un abogado
  antes de prenderla.

---

## Qué se armó (para Claude Code)

| Archivo | Qué es |
|---|---|
| `../.claude/agents/radar-prospeccion.md` | Radar |
| `prompts/auditor.md`, `prompts/redactor.md`, `prompts/seguimiento.md` | Cómo audita y escribe (mercados, idiomas, precios) |
| `radar_busquedas.csv` | El plan de búsquedas (102: primero moda, empresas y pymes; España apagada) |
| `n8n/01` a `05` | Buscar (con rating mínimo), auditar, escribir, seguir, leer respuestas |
| `n8n/11_radar_bandeja.json` | La bandeja donde aprobás, editás o descartás |
| `n8n/12_radar_envio.json` | Manda lo aprobado desde contacto@ |
| `prompts/whatsapp.md` | El WhatsApp para los que no tienen web o mail |
| `n8n/09_radar_conexion_centro.json` | Recibe del Centro las ofertas y el entrenamiento |
| `n8n/10_radar_reporte.json` | El reporte de las 18:00 |
| Centro → Radar | Ofertas, entrenamiento, puesta en marcha y conexión |
