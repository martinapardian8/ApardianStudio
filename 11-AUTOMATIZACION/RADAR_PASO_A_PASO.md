# Radar — paso a paso

Radar busca negocios en Google Maps, mira su web, le escribe a cada uno una
propuesta hecha para él y hace dos seguimientos. Los mails salen solos, hasta
50 por día. Lo que sí pasa por vos: las **ofertas**, los **paquetes**, los
**precios** y el **entrenamiento**, que aprobás en el Centro (pestaña Radar).

```
 Busquedas (hoja)          Google Maps            la web del negocio
       │                        │                         │
 01 Prospector ── 12 búsquedas por día ──▶ Leads ──▶ 02 Auditor (90 por día)
                                                          │ puntaje, problema, propuesta
                                                          ▼
 Centro → Radar ── aprobás ofertas y entrenamiento ──▶ 09 ──▶ hojas Ofertas / Entrenamiento
                                                          │
                                                          ▼
                                    03 Redactor y envío (cada hora, 9 a 17)
                                    10 → 20 → 35 → 50 por día, en el horario de cada país
                                                          │
                 04 Seguimientos (día 4 y día 9) ◀────────┤
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

1. **Comprá el dominio para los mails.** Un dominio hermano, no el de tu web:
   por ejemplo `apardian.studio` o `apardianstudio.co` (en Hostinger, donde ya
   tenés la web). Si un día los mails en frío caen en spam, se quema ese, no
   `apardianstudio.com` ni tu mail principal.
2. **Creá la casilla en Google Workspace**: `martin@` el dominio nuevo. El plan
   Business Starter alcanza. Poné tu foto de perfil y la firma:
   `Martin Apardian · APARDIAN STUDIO · apardianstudio.com · WhatsApp +598 91 962 962`.
3. **SPF, DKIM y DMARC.** Google Workspace te muestra los tres registros; se
   pegan en Hostinger → Dominios → DNS. Empezá DMARC con `p=none`. Sin esto,
   todo va a spam. Probalo en mail-tester.com: tiene que dar 9/10 o más.
4. **Redirigí el dominio nuevo a apardianstudio.com** (Hostinger →
   Redirecciones), para que quien lo escriba te encuentre.
5. **Calentá la casilla dos semanas**: 5 a 10 mails reales por día a gente que
   te conoce y te contesta (clientes, colegas, amigos). Que respondan es lo que
   le enseña a Gmail que sos de confianza.

### Semana 1 — las cuentas

6. **n8n**: n8n.io → plan Starter. Ahí corren todos los flujos.
7. **Clave de Google Places**: console.cloud.google.com → proyecto nuevo →
   activar **Places API (New)** → Credenciales → Crear clave de API.
   Restringila a Places API y **poné un tope de gasto mensual** (Facturación →
   Presupuestos y alertas).
8. **Clave de Claude**: console.anthropic.com → API keys. **Poné un límite de
   gasto mensual** (Settings → Limits). Radar audita unas 90 webs y escribe
   unos 50 mails por día: el primer mes mirá cuánto gasta y ajustá.
9. **Bot de Telegram**: en Telegram, @BotFather → /newbot. Guardá el token y tu
   chat ID (te lo da @userinfobot). Ahí te llegan el reporte diario y los
   clientes interesados.

### Semana 2 — conectar

10. **La planilla**: una planilla de Google Sheets con las hojas `Leads`,
    `Bajas`, `Busquedas`, `Ofertas` y `Entrenamiento`. Importá en cada una su
    plantilla de esta carpeta (`leads_plantilla.csv`, `bajas_plantilla.csv`,
    `radar_busquedas.csv`, `ofertas_plantilla.csv`,
    `entrenamiento_plantilla.csv`).
11. **Importá en n8n los flujos** `01`, `02`, `03`, `04`, `05`, `09` y `10` de
    `n8n/` (Import from file). En cada nodo **Config**:
    - `SHEET_ID`: el ID de la planilla (lo que está entre `/d/` y `/edit` en su link).
    - `TELEGRAM_CHAT_ID`: tu chat.
    - `MI_EMAIL` (03 y 04): `Martin Apardian <martin@tu-dominio-nuevo>`.
    - `FECHA_INICIO` (03 y 10): el primer día de envío, `AAAA-MM-DD`.
    - `DIRECCION_POSTAL` (03 y 04): si querés escribirle a EE.UU. (ver la parte legal).
    - `TOKEN` (09): una clave larga inventada por vos.
    - Elegí las credenciales (Google Sheets, Gmail de la casilla nueva,
      Telegram, Google Places y Anthropic) donde dice `REEMPLAZAR`.
12. **Conectá el Centro**: Centro → Radar → Conexión con n8n. Pegá la dirección
    de producción del webhook del flujo 09 (termina en
    `/webhook/apardian-radar`), la misma clave del paso 11 y la fecha de
    arranque.
13. **Entrená a Radar y aprobá las primeras ofertas**: Centro → Radar.
    Contestá el entrenamiento (lo que puedas) y tocá **Enseñarle a Radar**.
    Pedile 3 propuestas de ofertas, editalas y aprobá las que te gusten. Cada
    aprobación abre una pestaña de n8n que dice *Oferta activada ✓*.
14. **Publicá la web nueva** (decile a Claude "publicá la web"): los mails
    llevan a `apardianstudio.com/propuesta.html`, que tiene que existir antes
    del primer envío.
15. **Prendé los flujos** 01, 02, 03, 04, 05, 09 y 10. A las 18:00 te llega el
    primer reporte.

### Todos los días (5 minutos)

- A las 18:00, el reporte de Radar por Telegram: cuántos salieron, a qué
  países, cuántos respondieron y si hay algo para mirar.
- Cuando alguien responde con interés, te llega un aviso. **Esa respuesta la
  contestás vos** (Trato te arma el borrador en el Centro).

### Cada semana (15 minutos)

- Mirá las ofertas: pausá lo que no funciona y aprobá ideas nuevas de Radar.
- Si el reporte dice que quedan pocos leads, pedile a Radar (en Claude Code o
  en el Centro) búsquedas nuevas para la hoja `Busquedas`.

---

## Cómo sube a 50 por día

| Semana desde FECHA_INICIO | Mails nuevos por día |
|---|---|
| 1 | 10 |
| 2 | 20 |
| 3 | 35 |
| 4 en adelante | 50 |

Salen de lunes a viernes, de a pocos cada hora, y solo en horario de oficina
**del país del destinatario** (de 9 a 17 allá). Los seguimientos van aparte y
no cuentan en el cupo. Si querés otro ritmo, cambiá `CUPOS_POR_SEMANA` en los
flujos 03 y 10 (por ejemplo `10,20,35,50,60`).

A 50 por día son unos 1.100 mails por mes. Con 1 a 3 % de respuestas, lo
habitual en mail en frío bien hecho, son 11 a 33 conversaciones por mes. Es una
estimación: los números reales los da el reporte.

**Frenos que tiene solo:**
- Si rebotan más del 5 % de los mails, el reporte te avisa para pausar
  (`AUTO_ENVIO` en `false` en el flujo 03: vuelve a pedirte aprobación por
  Telegram, mail por mail).
- Quien responde "no" o "baja" va a la hoja `Bajas` y nunca más recibe nada.
- Quien responde deja de recibir seguimientos.

---

## La parte legal (léela antes de prender)

Esto es una guía práctica, no asesoramiento legal. Si el volumen crece, vale
una consulta con un abogado.

- **En todos lados:** solo mails de empresas publicados en su propia web, nunca
  listas compradas ni mails personales adivinados. Identificación completa en
  cada mail, un solo link y la opción de baja. Máximo dos seguimientos.
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
| `radar_busquedas.csv` | El plan de búsquedas por país (58, España apagada) |
| `n8n/01` a `05` | Buscar, auditar, escribir y mandar, seguir, leer respuestas |
| `n8n/09_radar_conexion_centro.json` | Recibe del Centro las ofertas y el entrenamiento |
| `n8n/10_radar_reporte.json` | El reporte de las 18:00 |
| Centro → Radar | Ofertas, entrenamiento, puesta en marcha y conexión |
