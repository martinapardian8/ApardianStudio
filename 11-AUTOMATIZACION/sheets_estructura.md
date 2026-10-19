# Estructura del CRM (Google Sheets)

Una planilla con tres hojas (`Leads`, `Bajas` y `Calendario`). Los flujos de n8n leen y escriben acá; Martin
también puede editar a mano (por ejemplo, poner `descartado` a un lead).

## Hoja `Leads`

| Columna | Qué guarda | Quién la llena |
|---|---|---|
| `id` | Identificador único (el `place_id` de Google) | 01 Prospector |
| `fecha` | Fecha en que entró el lead (AAAA-MM-DD) | 01 |
| `rubro` | restaurante, marca, salon, inmobiliaria, profesional, fotografo… | 01 |
| `nombre` | Nombre del negocio | 01 |
| `web` | URL del sitio | 01 |
| `instagram` | Link de Instagram si aparece en la web | 02 Auditor |
| `email` | Mail de contacto **publicado en su web** (`mailto:`) | 02 |
| `telefono` | Teléfono de la ficha de Google | 01 |
| `ciudad` | Ciudad / barrio de la búsqueda | 01 |
| `fuente` | `google_places`, `manual`, `referido`… | 01 |
| `score` | Puntaje de oportunidad 0–100 | 02 |
| `servicio` | Servicio de Apardian que más le sirve | 02 |
| `problemas` | Problemas con evidencia (texto) | 02 |
| `estado` | Ver tabla de estados | todos |
| `asunto` | Asunto del mail | 03 Redactor |
| `borrador` | Cuerpo del mail | 03 |
| `fecha_envio` | Fecha del primer envío | Martin / 03 |
| `seguimientos` | 0, 1 o 2 | 04 Seguimiento |
| `respuesta` | Categoría de la respuesta + resumen | 05 Respuestas |
| `notas` | Ficha de Google y, después de auditar, la auditoría completa en JSON | 01 / 02 / Martin |
| `draft_id` | ID del borrador pendiente en Gmail | 03 / 04 |
| `thread_id` | Hilo de Gmail del primer mail (para seguimientos y respuestas) | 03 |
| `mensaje_id` | ID del primer mail enviado | 03 |

El auditor reemplaza `notas` por un JSON con la auditoría completa y la ficha
de Google: lo usan el redactor y el seguimiento 1. Si Martin quiere anotar algo,
mejor al final de `respuesta` o en una columna extra.

### Estados

```
nuevo → auditado → borrador → enviado → borrador_seg1 → seguimiento_1 → borrador_seg2 → seguimiento_2 → cerrado_sin_respuesta
      ↘ descartado (score < 60) · sin_email · error_auditoria
enviado / seguimiento_* → interesado | pide_precio | no_ahora | baja | rebote
interesado / pide_precio → (pasa a 09-ESTUDIO/clientes.md como "conversando")
```

- `sin_web`: no tiene sitio. Igual puede ser buen prospecto para **página web**:
  queda para contacto manual por Instagram o WhatsApp.
- `sin_email`: tiene web pero no publica mail. Contacto manual por formulario,
  Instagram o teléfono.

## Hoja `Bajas`

| Columna | Qué guarda |
|---|---|
| `email` | Dirección que pidió no recibir más |
| `dominio` | Dominio de esa dirección (para no escribir a otros del mismo negocio) |
| `fecha` | Cuándo pidió la baja |
| `motivo` | Texto de la respuesta, resumido |

Todos los flujos consultan esta hoja antes de escribir. Es también el registro
de bajas que pide la Ley 18.331.

## Sobre los mails

El auditor busca `mailto:` en el HTML de la portada. Si el mail solo está en
la página de contacto, el lead queda `sin_email` y Martin lo completa a mano
(copiándolo de la web) y le cambia el estado a `auditado`. **Nunca se adivinan mails** (tipo nombre.apellido@dominio). Si no hay un
mail publicado, el lead queda `sin_email` para contacto manual.

## Hoja `Calendario` (Instagram con aprobación)

Se importa desde `calendario_instagram.csv`, que arma
`python3 10-MOTOR/calendario_sheet.py` a partir del calendario de contenido.
La leen el flujo 07 (pide aprobación por Telegram) y el 08 (publica).
Detalle completo en `INSTAGRAM_APROBACION.md`.

| Columna | Qué guarda | Quién la llena |
|---|---|---|
| `id` | `fecha-hora-pieza`, único | calendario_sheet.py |
| `fecha` / `hora` | Cuándo sale, hora de Montevideo (AAAA-MM-DD, HH:MM) | calendario_sheet.py · Martin puede cambiarla |
| `tipo` | `CAROUSEL`, `IMAGE` o `REEL` | calendario_sheet.py |
| `titulo` | Para reconocerla en Telegram | calendario_sheet.py |
| `archivos` | Rutas dentro de `08-CONTENIDO-INSTAGRAM`, separadas por `\|`, en orden de subida | calendario_sheet.py |
| `urls` | Las mismas rutas en `https://apardianstudio.com/ig/...` | calendario_sheet.py |
| `pie` | Pie de foto completo | calendario_sheet.py · Martin puede editarlo |
| `primer_comentario` | Comentario que se deja apenas sale (opcional) | calendario_sheet.py · Martin |
| `estado` | `pendiente` → `aprobado` / `rechazado` → `publicado` o `error` | 07 · 08 · Martin |
| `aprobado_por` / `aprobado_en` | Quién y cuándo aprobó | 07 |
| `publicado_en` | Cuándo salió | 08 |
| `ig_media_id` | ID de la publicación en Instagram | 08 |
| `error` | Por qué no salió (si no salió) | 08 · calendario_sheet.py |

**Regla:** el publicador solo toca filas en `aprobado`. Si cambiás el pie o la
fecha de una fila ya aprobada, no hace falta volver a aprobar; si querés que
no salga, ponele `rechazado` a mano.
