# Estructura del CRM (Google Sheets)

Una planilla con dos hojas. Los flujos de n8n leen y escriben acá; Martin
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
