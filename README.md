# APARDIAN STUDIO

Sitio, identidad y contenido de [apardianstudio.com](https://apardianstudio.com) —
fotografía, video, páginas web y edición en Lightroom, desde Uruguay.

## Qué hay en cada carpeta

| Carpeta | Contenido |
|---|---|
| `05-WEB` | El sitio: `index.html`, `css/`, `js/`, `img/`. `js/data.js` es **generado**, no se edita a mano. |
| `06-NOTAS` | `picks.json` (única fuente de verdad de la galería), `estado.md` (bitácora) y `servidor.py`. |
| `07-PUBLICAR` | Build liviano listo para subir a `public_html` en Hostinger. |
| `08-CONTENIDO-INSTAGRAM` | 364 piezas: avisos de pauta, carruseles, historias y videos. `00-SUBIR-EN-ORDEN` trae doce publicaciones armadas. |
| `09-ESTUDIO` | Base de conocimiento del negocio y de los agentes de IA. |
| `10-MOTOR` | Los scripts que generan todo lo anterior. |
| `marca` | 123 piezas de identidad: logo, papelería, flyers, ropa, objetos. |
| `01`–`04`, `FOTOS *` | Referencias, archivo fotográfico y material generado con IA. |

## Cómo se trabaja

```bash
# levantar el sitio en local, sin caché
python3 06-NOTAS/servidor.py        # http://localhost:8788

# regenerar la galería después de tocar picks.json
python3 10-MOTOR/build_site.py

# regenerar el contenido de Instagram
cd 10-MOTOR && python3 generar_ads.py && python3 carruseles.py && python3 historias.py

# armar el build para publicar
bash 10-MOTOR/publicar.sh
```

El editor visual del sitio se abre con `?edit=1` y guarda en `localStorage`.

## Sistema de marca

Hueso `#F8F7F6`, negro `#171717`, rojo `#FF0033`. Titulares en **Anton**
(Koulen no tiene mayúsculas acentuadas y rompe el español), texto en **Work Sans**.

## Publicar

El contenido de `07-PUBLICAR` va a la raíz de `public_html` en Hostinger.
El dominio no cambia.
