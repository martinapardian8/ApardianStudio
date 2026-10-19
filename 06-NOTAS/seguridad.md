# Seguridad de apardianstudio.com

Revisión del 19 de octubre de 2026. Todo lo que dice "arreglado" está hecho en
`05-WEB` y copiado a `07-PUBLICAR`, **sin publicar**. Se activa la próxima vez
que subas el build a la rama `hostinger`.

## Qué se revisó

- Todo lo que baja al navegador: `index.html`, los seis `.js`, los dos `.css`.
- El `.htaccess` (cabeceras, redirecciones, archivos bloqueados).
- El build de `07-PUBLICAR` contra la fuente de `05-WEB`.
- `10-MOTOR/publicar.sh` (qué entra al build) y `06-NOTAS/servidor.py` (el servidor de casa).
- El sitio cargado en Chromium con las mismas cabeceras que manda Hostinger:
  PC, celular y `?edit=1`, abriendo el Agente IA y bajando hasta el footer.

## Qué se encontró

### Crítico
Nada. No hay claves, tokens ni contraseñas en el código que baja al navegador.
El **Agente IA no llama a ninguna IA**: son cinco preguntas armadas en
`js/agente.js` que terminan abriendo WhatsApp con el pedido escrito. No hay
nada que robar ni ninguna cuenta que se pueda usar a costa tuya.

### Alto
**La carpeta `/.git` podía quedar a la vista.** El sitio se publica por Git
desde hPanel. Si Hostinger clona el repositorio dentro de `public_html`, la
carpeta `.git` queda ahí adentro. El `.htaccess` anterior bloqueaba los
archivos que empiezan con punto, pero no lo que hay *dentro* de `.git`
(`HEAD`, `config` y el resto no empiezan con punto). Con eso, cualquiera podía
bajarse el historial de la rama publicada.
→ **Arreglado:** todo lo que cuelga de una carpeta con punto devuelve 403,
salvo `/.well-known/`. No lo pude comprobar en el sitio en vivo porque esta
sesión no tiene salida a internet hacia tu dominio: **comprobalo después de
publicar** (abajo está la lista).

### Medio
- **Las tipografías venían de Google Fonts.** Era un tercero cargando código
  de estilo en tu página, y la IP de cada visitante viajaba a Google.
  → **Arreglado:** Anton y Work Sans se sirven desde el sitio (`05-WEB/fonts`,
  93 KB en total, el mismo rango de caracteres que usaba Google). Se ve
  idéntico: lo comparé captura contra captura. La CSP ya no permite
  `fonts.googleapis.com` ni `fonts.gstatic.com`.
- **La CSP iba a bloquear el reproductor de Spotify** de la sección de música
  (no tenía `frame-src`).
  → **Arreglado:** permite solo `open.spotify.com` y `youtube-nocookie.com`
  dentro de iframes; cualquier otro sitio queda bloqueado (probado).
- **Clickjacking.** El sitio se podía meter dentro de un iframe del mismo
  dominio (`SAMEORIGIN`).
  → **Arreglado:** `frame-ancestors 'none'` y `X-Frame-Options: DENY`. Nadie puede
  embeber tu web dentro de otra.
- **`publicar.sh` solo dejaba afuera `_qa_puente.html` y `.DS_Store`.** Cualquier
  `.md`, `.py`, `.json` o copia de iCloud que apareciera en `05-WEB` terminaba
  publicada.
  → **Arreglado:** quedan afuera los archivos de trabajo, las copias " 2." y
  " 3." de iCloud y `.git`. Si igual se cuela algo privado, el script frena con
  error antes de terminar. Además ya no depende de la ruta de tu escritorio:
  funciona desde cualquier carpeta.

### Bajo
- Los links que abren en otra pestaña ya tenían `noopener`. Se agregó
  `noreferrer` en los diez links y en el botón de WhatsApp del agente.
- Cabeceras nuevas: `Cross-Origin-Opener-Policy`, `Permissions-Policy` más
  completa (cámara, micrófono, ubicación, pagos y USB apagados), `Referrer-Policy`
  también como meta, `Options -MultiViews` y más extensiones bloqueadas (`.bak`,
  `.env`, `.zip`, `.psd`, `.lrcat`, `.xmp`, etc.).
- **El editor (`?edit=1`) se publica**, pero solo guarda en el navegador de
  quien lo abre (`localStorage`). No escribe en el servidor, así que nadie
  puede cambiar tu web desde afuera. Lo único posible: que alguien se engañe
  a sí mismo importando un archivo armado por otro. Riesgo mínimo, lo dejé
  como está porque es tu forma de trabajar. Si algún día no lo usás más en el
  sitio publicado, se saca del build con una línea en `publicar.sh`.
- **`servidor.py` escucha en toda la red de tu casa** (está hecho así para
  verlo desde otra PC). Ahora no sirve `.md`, `.py`, `.sh`, `.json` ni archivos
  con punto, y manda la misma CSP que Hostinger: si algo nuevo rompe la CSP, lo
  ves en local antes de publicar. Usalo solo en redes de confianza (no en el
  wifi de un café).
- Se agregaron `/.well-known/security.txt` (contacto para reportar fallas,
  vence el 19/10/2027), `robots.txt` y `sitemap.xml`.

## Cómo se verificó

- Chromium sin interfaz, con las cabeceras del `.htaccess` nuevo, en PC
  (1440×900), celular (390×844) y `?edit=1`: **cero violaciones de CSP y cero
  errores en consola**. Se abrió el Agente IA y se recorrió la página entera.
- Las dos tipografías cargan desde el sitio. Capturas del hero y de
  "Selección" comparadas contra el build anterior: iguales.
- Prueba de la CSP: un iframe de Spotify pasa; uno de `example.com` y un video
  externo quedan bloqueados.
- Lo que este entorno **no** puede probar: el comportamiento real de Apache o
  LiteSpeed en Hostinger (las reglas de `.htaccess` sobre `.git` y las
  extensiones bloqueadas). Por eso está la lista de abajo.

## Lo que solo podés hacer vos

1. **Verificación en dos pasos (2FA)** en Hostinger, GitHub y Google (el Gmail
   del estudio). Es lo que más protege, por lejos. Usá una app (Google
   Authenticator, 1Password, Authy), no SMS.
2. **Contraseñas únicas** con un gestor (1Password, Bitwarden). Ninguna repetida
   entre Hostinger, GitHub, Google, Instagram y el banco.
3. **GitHub → Settings → Applications:** revisá qué apps tienen acceso al
   repositorio. La de Hostinger necesita solo lectura y solo este repo.
   Si el repositorio es **público**, pasalo a **privado**: además del sitio
   tiene `09-ESTUDIO` (tu negocio y tus clientes) y `11-AUTOMATIZACION`.
4. **Dominio:** renovación automática activada y **bloqueo de transferencia**
   (Domain lock) prendido en Hostinger.
5. **Correo (DNS):** SPF, DKIM y DMARC para tu dominio. Es seguridad (nadie
   puede mandar mails haciéndose pasar por vos) y es requisito para que los
   mails del sistema de prospección no caigan en spam. Empezá DMARC en
   `p=none` con reportes y subilo a `p=quarantine` cuando todo pase.
6. **Backups:** confirmá que Hostinger tiene copias automáticas activas. El
   sitio además está en Git, pero el correo y la base de Hostinger no.
7. **Opcional, recomendado:** Cloudflare (plan gratis) delante del sitio: WAF,
   protección contra bots y caché. Se cambian los DNS; lo armamos juntos.
8. **Monitoreo:** UptimeRobot (gratis) con aviso a tu mail si la web se cae.
9. **HSTS preload:** no lo activé. Obliga a que todos los subdominios tengan
   HTTPS para siempre; lo vemos cuando confirmes que no hay ninguno sin
   certificado.

## Después de publicar: chequeo de cinco minutos

```bash
curl -sI https://apardianstudio.com/ | grep -iE "strict|content-security|x-frame|nosniff|referrer|permissions|cross-origin"
curl -s -o /dev/null -w "%{http_code}\n" https://apardianstudio.com/.git/HEAD          # 403 o 404, nunca 200
curl -s -o /dev/null -w "%{http_code}\n" https://apardianstudio.com/.htaccess          # 403
curl -s -o /dev/null -w "%{http_code}\n" https://apardianstudio.com/.well-known/security.txt   # 200
curl -s -o /dev/null -w "%{http_code}\n" http://apardianstudio.com/                    # 301 a https
```

- https://securityheaders.com/?q=apardianstudio.com → tiene que dar **A** o **A+**.
- https://developer.mozilla.org/en-US/observatory → buscá tu dominio.
- Abrí la web en el celular y en la PC y probá: hero, galería, el Agente IA,
  WhatsApp y (cuando esté) el reproductor de Spotify.

Si alguna de estas falla, no hace falta deshacer nada a mano: avisame con lo
que dio el `curl` y lo ajusto.
