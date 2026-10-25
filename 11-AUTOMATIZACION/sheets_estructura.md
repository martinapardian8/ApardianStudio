# Estructura del CRM (Google Sheets)

Una planilla con estas hojas: `Leads`, `Bajas`, `Calendario` y, para Radar,
`Busquedas`, `Ofertas` y `Entrenamiento`. Los flujos de n8n leen y escriben acá; Martin
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
| `pais` | País del negocio (de su búsqueda) | 01 |
| `idioma` | `es` o `en` (el auditor puede corregirlo) | 01 / 02 |
| `mercado` | `uy` (se ofrece todo, presencial incluido) u `online` (solo lo que se hace a distancia) | 01 |
| `zona` | Zona horaria del negocio: el mail sale en su horario de oficina | 01 |
| `oferta_id` | Oferta aprobada que usó el mail, si usó alguna | 03 |
| `ultimo_envio` | Último día que le salió un mail (primero o seguimiento). Con esto se cuenta el tope diario de la casilla | 03 / 04 |
| `seg_asunto` | Asunto del seguimiento que espera aprobación (solo con `AUTO_ENVIO` en `false`) | 04 |
| `seg_cuerpo` | Cuerpo de ese seguimiento | 04 |

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
| `tipo` | `CAROUSEL`, `IMAGE`, `REEL` o `STORY` | calendario_sheet.py |
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
| `revision` | Lo que dijo Lupa: `ok`, `ok · nota: …` o `frenado: …`. El 07 solo pide aprobación de lo que empieza con `ok` | lupa.py · agente Lupa |

**Regla:** el publicador solo toca filas en `aprobado`. Si cambiás el pie o la
fecha de una fila ya aprobada, no hace falta volver a aprobar; si querés que
no salga, ponele `rechazado` a mano.


## Hoja `Busquedas` (el plan de Radar)

Se importa de `radar_busquedas.csv`. Cada fila es una búsqueda en Google Maps;
el flujo 01 corre 12 por día, empezando por las que hace más tiempo que no corren.

| Columna | Qué guarda |
|---|---|
| `id` | b001, b002… |
| `activo` | `si` o `no` (España arranca en `no`: ver la parte legal en `RADAR_PASO_A_PASO.md`) |
| `mercado` | `uy` u `online` |
| `pais` / `region` | País y su código de dos letras (UY, AR, MX, ES, US…) |
| `idioma` | `es` o `en` |
| `zona` | Zona horaria (America/Montevideo, Europe/Madrid…) |
| `rubro` | fotografo, restaurante, marca, hotel… |
| `query` | Lo que se busca en Google Maps |
| `servicio_objetivo` | Lo que se le quiere ofrecer a ese rubro |
| `ultima_vez` | Cuándo corrió por última vez (la llena el 01) |

## Hoja `Ofertas`

La llena el flujo 09 cuando Martin aprueba o pausa una oferta en el Centro.
No se edita a mano. Columnas: `id`, `estado` (`activa` o `pausada`),
`mercado` (`uy`, `online` o `todos`), `servicio`, `nombre`, `para_quien`,
`que_incluye`, `plazo`, `precio_desde`, `moneda`, `vigencia_hasta`, `angulo`,
`actualizado`. El redactor solo usa las `activa` vigentes de su mercado.

## Hoja `Entrenamiento`

Las respuestas de Martin a las preguntas de Radar en el Centro (flujo 09).
Columnas: `clave`, `pregunta`, `respuesta`, `actualizado`. El redactor las lee
antes de cada mail.
