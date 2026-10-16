# The Lobster Roll · Barcelona — web

Sitio estático (HTML + CSS + JS vanilla, sin build) pensado como **plantilla reutilizable** para
restaurantes con marca fuerte. Todo lo que cambia de un restaurante a otro vive en `data/`:
carta, textos, fotos y datos del negocio. El HTML casi no se toca.

```
lobster-roll-web/
├── index.html              ← la página (contenido en español ya escrito, para SEO)
├── aviso-legal.html, privacidad.html, cookies.html   ← placeholders legales
├── css/styles.css          ← estilos; la paleta y las fuentes son variables en :root
├── css/fonts.css           ← @font-face de las fuentes autoalojadas
├── js/main.js              ← carga data/*.json, idioma, carta, galería, horario, cookies…
├── data/
│   ├── carta.json          ← la carta (rolls y combos) con precios y descripciones por idioma
│   ├── restaurante.json    ← dirección, teléfono, horario, reservas, redes
│   ├── fotos.json          ← ÚNICO lugar que decide qué foto va en cada sitio
│   └── i18n/es.json, ca.json, en.json   ← todos los textos de la interfaz
├── assets/
│   ├── fotos/              ← fotos en WebP (hoy: placeholders)
│   ├── img/                ← logo.svg, roll-ilustrado.svg, mapa.svg
│   ├── hojas/              ← monstera y palma en SVG (decoración)
│   └── fonts/              ← Gloock, Oswald y Figtree en woff2
├── scripts/
│   ├── descargar_fotos.py  ← baja las fotos de la web actual y las pasa a WebP
│   ├── fuentes.sh          ← vuelve a bajar las fuentes de Google Fonts
│   ├── capturas.js + coser.py ← capturas a 375 / 768 / 1440 px con Playwright
└── capturas/               ← capturas del resultado
```

## Ver el sitio en local

Los datos se cargan con `fetch`, así que hace falta un servidor (con `file://` la página
muestra el español del HTML pero no la carta):

```bash
cd lobster-roll-web
python3 -m http.server 8080        # → http://localhost:8080
```

## Publicar

Es una carpeta estática: subí el contenido de `lobster-roll-web/` tal cual a Netlify, Vercel
(sin framework, "Other") o a `public_html` en Hostinger. No hay paso de build.

Antes de publicar en el dominio definitivo, reemplazá `https://www.thelobsterrollbcn.com/`
en `index.html` (canonical, hreflang, `og:url`, `og:image` y el bloque `schema.org`) si el dominio cambia,
y poné una foto real de 1200×630 en `og:image`.

## Cambiar las fotos

1. Guardá las fotos nuevas en `assets/fotos/` en WebP (calidad 80, máximo 1600 px de ancho).
   Con Pillow: `python3 -c "from PIL import Image; im=Image.open('x.jpg'); im.thumbnail((1600,1600)); im.save('assets/fotos/x.webp','WEBP',quality=80)"`
2. Editá `data/fotos.json`. Cada slot tiene `src`, `ancho`, `alto` y `alt` por idioma:
   - `roll_recortado`: el PNG **sin fondo** del lobster roll (hero y titular de la carta). Hoy es
     `assets/img/roll-ilustrado.svg`, una ilustración provisoria.
   - `historia` y `historia_detalle`: la foto vertical y la cuadrada de la sección "El restaurante".
   - `bloque_lobster`: la foto vertical del bloque 50/50.
   - `og`: la imagen para compartir en redes (1200×630).
   - `galeria`: la lista de fotos de la galería, en orden. Podés agregar o quitar.
   Opcional: `srcset` y `sizes` por foto, si generás varias anchuras.
3. Para bajar las fotos actuales de la web vieja: `python3 scripts/descargar_fotos.py`
   (genera también `assets/fotos/contacto.jpg` para elegir).

## Cambiar la carta

Editá `data/carta.json`. Cada categoría (`rolls`, `combos`) tiene sus `items` con `nombre`,
`precio` (número, en euros) y `descripcion` por idioma. `"destacado": true` marca la especialidad
(sale con la etiqueta roja y el fondo mantequilla). En los combos, `roll` apunta al `id` del roll
incluido. El bloque 50/50 lee los precios de `lobster` y `lobster-xl` por `id`
(`data-precio-de` en el HTML).

Si agregás una categoría nueva, sumá una pestaña y un panel en `index.html` (copiá el bloque
`role="tab"` / `role="tabpanel"` y poné `data-categoria="<id>"` en la lista).

## Cambiar los textos

- Interfaz y secciones: `data/i18n/es.json`, `ca.json`, `en.json`. Cada elemento del HTML con
  `data-i18n="clave"` toma su texto de ahí; `data-i18n-attr="alt:clave"` hace lo mismo con atributos.
  Las tres versiones tienen que tener las mismas claves.
- Datos del negocio (dirección, teléfono, horario, reservas, parking, redes): `data/restaurante.json`.
  El horario usa `dias` (0 = domingo … 6 = sábado) con tramos `[apertura, cierre]`; lista vacía = cerrado.
  El indicador "abierto/cerrado" y la tabla con el día resaltado salen de ahí, en hora de `Europe/Madrid`.
- El idioma por defecto es español. Se cambia con el selector, con `?lang=ca` / `?lang=en` o
  queda guardado en `localStorage`.
- El texto de la cinta roja está en `cinta` dentro de cada i18n.
- Los textos legales están en los tres `.html` de la raíz (son placeholders).
- El JSON-LD (`schema.org/Restaurant`) está escrito a mano en el `<head>` de `index.html`:
  cambiá ahí dirección, horario, teléfono y URL de reservas si cambian.

## Cambiar colores y tipografía

Todo está en `:root` de `css/styles.css`:

```css
--green: #123524;   /* fondo de las secciones oscuras */
--paper: #f3ecdf;   /* fondo de las secciones claras  */
--lobster: #c9412b; /* el único acento fuerte         */
--butter: #e6b54a;  /* toques mínimos                  */
--f-display: 'Gloock'; --f-label: 'Oswald'; --f-body: 'Figtree';
```

Para otras fuentes, cambiá la URL en `scripts/fuentes.sh`, ejecutalo y ajustá `--f-*`.
Las hojas decorativas están en `assets/hojas/`; se colocan con la clase `.hoja` y las variables
`--rot` (rotación) y `--sx` (espejo). `data-parallax="0.1"` les da movimiento suave al hacer scroll.
El logo es un `<symbol id="i-logo">` al principio de `index.html` (y `assets/img/logo.svg` para favicon).

## Cookies

El aviso guarda la elección en `localStorage` (`lr-cookies` = `aceptar` | `rechazar`).
Hoy no hay ningún script de terceros. Si se agrega analítica, cargarla dentro de
`aplicarConsentimiento()` en `js/main.js`, solo cuando el valor sea `aceptar`.

## Capturas

```bash
npm i playwright-core   # una vez
python3 -m http.server 8080 &
node scripts/capturas.js http://localhost:8080/ capturas && python3 scripts/coser.py capturas
```

## Medios alojados fuera del repo (Higgsfield)

Las fotos reales del restaurante, el roll recortado, el poster y el video del hero están hoy en el
CDN de Higgsfield (`*.cloudfront.net`), referenciados desde `data/fotos.json` e `index.html`.
Para traerlos al repositorio y publicar sin dependencias externas:

```bash
python3 scripts/localizar_medios.py   # baja todo a assets/fotos/ y reescribe fotos.json
grep -n cloudfront index.html          # reemplazar a mano og:image, poster y src del hero
```

El video del hero (`hero_video` en `fotos.json`) se reproduce en bucle, sin audio, con un fotograma
fijo (`poster`) de respaldo; con `prefers-reduced-motion` solo se muestra el fotograma.

## Qué quedó provisorio

- **Logo:** recreación en SVG (sello circular con bogavante). Coincide en concepto con el neón del local, pero hay que pedir el original.
- **Fotos del local:** son las 16 de la web actual, pasadas a WebP (las 5 principales mejoradas a 2K con IA). Se reemplazan por las de la sesión de octubre editando `data/fotos.json`.
- **Roll recortado y video del hero:** generados con IA (no son fotos del producto real). Reemplazar por material propio cuando exista.
- **Descripciones inventadas:** "Shot de ostra" y "Nutella Roll" (marcadas con `"provisional": true` en `carta.json`).
  "Atún Roll" se suavizó a "Atún en pan brioche".
- **Metro:** líneas "L1, L2" de Universitat puestas por conocimiento general; confirmar.
- **Redes sociales:** vacías en `restaurante.json`; el footer muestra "pendiente".
- **Páginas legales:** esqueleto con los datos por completar (NIF, correo, titular).
- **Mapa:** esquema ilustrado, sin escala. Verificar posición relativa de Muntaner 22 / parking.
