# Instagram con aprobación: vos aprobás, el agente publica

La idea: nada sale en Instagram sin que lo veas. **Un posteo y una historia
por día.** Antes de llegarte, cada pieza pasa por Lupa, la crítica de diseño:
lo que no cumple (medidas, peso, pie, reglas de marca) se frena y no te
molesta. Un día antes te llega a Telegram cada publicación (la imagen, el pie
de foto y lo que dijo Lupa) con dos botones,
**Aprobar** y **No publicar**. Lo que aprobás se publica solo, a la hora del
calendario. Lo que no tocás, no sale.

## Cómo funciona

```
 calendario.json ──▶ calendario_sheet.py + Lupa ──▶ calendario_instagram.csv
                                                     │ (se importa una vez)
                                                     ▼
                                       Google Sheets · hoja "Calendario"
                                                     │
        ┌────────────────────────────────────────────┴───────────────┐
        ▼                                                            ▼
 07 · APROBACIÓN (todos los días 10:00)                08 · PUBLICADOR (11, 11:30, 12, 12:30, 13, 13:30, 19, 19:30, 20, 20:30)
 Busca lo "pendiente" que Lupa dejó "ok"            Busca lo "aprobado" cuya hora llegó
 de las próximas 36 h y te lo manda a Telegram       Revisa el cupo diario de Instagram
        │                                            Publica UNA por vuelta (Graph API)
        ▼                                            Escribe "publicado" y te avisa
 Tocás Aprobar ──▶ la fila pasa a "aprobado" ───────────────────────▶ │
 Tocás No publicar ──▶ "rechazado" (no sale nunca)                     ▼
                                                              Instagram
```

Las imágenes y los videos tienen que estar en una URL pública, porque
Instagram los baja de ahí. Por eso se copian a `apardianstudio.com/ig/...`
(paso 4).

## Lo que no se puede automatizar (y queda manual)

- **Stickers en historias.** Las historias se publican solas (imagen o
  video), pero la API no pone stickers de enlace, encuestas ni menciones. Por
  eso la historia de los lunes que comparte el carrusel con el link a WhatsApp
  queda a mano (en el calendario figura como *Historia (a mano)*).
- **Música de Instagram.** La API no pone canciones de la biblioteca de
  Instagram. Los reels salen con el sonido que tenga el archivo (los reels
  collage no tienen audio). Si a un reel le querés poner un tema desde la app,
  ese reel lo subís a mano y en la planilla le ponés `rechazado` para que el
  agente no lo publique.
- **Etiquetar personas, colaboradores y productos**: también a mano, desde la
  app, después de que sale.

---

## Puesta en marcha (una sola vez, 2–3 horas)

### 1. Cuenta profesional
1. En Instagram: *Configuración → Tipo de cuenta y herramientas → Cambiar a
   cuenta profesional* (Empresa o Creador; para el estudio, **Empresa**).
2. Vinculala a una **página de Facebook** del estudio (si no tenés, creás una
   en dos minutos). Es obligatorio para la API.

### 2. App de Meta
1. Entrá a <https://developers.facebook.com> con tu Facebook → *Mis apps → Crear
   app* → tipo **Empresa (Business)**.
2. Agregá el producto **Instagram** → *API de Instagram con inicio de sesión de
   Facebook* (Instagram API with Facebook Login).
3. La app puede quedar en **modo desarrollo**: alcanza para publicar en tu
   propia cuenta, no hace falta la revisión de Meta.
4. Permisos que tiene que pedir: `instagram_basic`,
   `instagram_content_publish`, `pages_show_list`, `pages_read_engagement` y
   `business_management`. Si querés que el agente deje el primer comentario,
   sumá `instagram_manage_comments`.

### 3. Token e ID de la cuenta
Dos caminos; el segundo es mejor porque no vence.

**A. Token de larga duración (vence a los 60 días)**
1. En el *Explorador de la API Graph* (Graph API Explorer) elegí tu app,
   marcá los permisos de arriba y tocá *Generate Access Token*.
2. Ese token dura una hora. Cambialo por uno de 60 días desde el depurador de
   tokens (*Access Token Debugger → Extend Access Token*).
3. Anotá en el calendario renovarlo cada 50 días (se repite el paso 2).

**B. Token de usuario del sistema (no vence)**
1. En <https://business.facebook.com> → *Configuración del negocio → Usuarios
   → Usuarios del sistema* → crear uno con rol de administrador.
2. Asignale la app, la página y la cuenta de Instagram.
3. *Generar token* con los mismos permisos y sin vencimiento.

**El ID de la cuenta de Instagram (IG_USER_ID):** en el explorador, con el
token puesto, pedí `me/accounts?fields=instagram_business_account{id,username}`.
El número de `instagram_business_account.id` es el que va.

### 4. Que los archivos estén en la web
Después de armar el sitio para publicar:

```bash
bash 10-MOTOR/publicar.sh            # arma 07-PUBLICAR (lo borra y lo rehace)
python3 10-MOTOR/calendario_sheet.py # rehace la planilla desde el calendario (Lupa revisa)
bash 10-MOTOR/preparar_ig.sh         # copia las piezas a 07-PUBLICAR/ig/
```

Y se sube como siempre (rama `hostinger`). Probá abrir una URL de la columna
`urls` en el navegador: si se ve la imagen, Instagram también la va a ver.

`preparar_ig.sh --dry-run` muestra qué copiaría sin tocar nada. Si Instagram
rechaza un reel por no tener audio, corré `preparar_ig.sh --pista-muda`: les
agrega a los videos una pista de audio en silencio, sin recodificar la imagen.

Requisitos de Instagram que ya cumplen las piezas (y que Lupa revisa en cada
una): JPEG de menos de 8 MB, proporción entre 4:5 y 1,91:1 (las nuestras son
4:5); historias 9:16 (1080×1920); reels en MP4 H.264.

### 5. La planilla
1. En la misma planilla de los leads, agregá una hoja llamada **Calendario**.
2. *Archivo → Importar → Subir* `11-AUTOMATIZACION/calendario_instagram.csv`
   → *Reemplazar la hoja actual*.
3. Podés editar a mano el `pie`, la `fecha` o la `hora` de cualquier fila.
   El publicador pasa a las 11, 12, 13, 19 y 20 (en punto y y media): una
   hora fuera de esas franjas sale en la pasada siguiente.
   Si cambiás el calendario, volvé a correr `calendario_sheet.py` e importá de
   nuevo solo las filas nuevas (las aprobadas o publicadas no las pises).

### 6. n8n
1. Importá `n8n/07_aprobacion_instagram.json` y `n8n/08_publicador_instagram.json`.
2. En el nodo **Config** de los dos: `SHEET_ID` (el de la planilla) y
   `TELEGRAM_CHAT_ID` (el mismo de los otros flujos).
3. En el 07: `URL_APROBAR_IG` = la URL de producción del webhook
   `apardian-ig-aprobar` de tu n8n, y un `TOKEN` largo inventado por vos (el
   mismo en `Config` y en `Config aprobación`).
4. En el 08: `IG_USER_ID`, `ACCESS_TOKEN` y `GRAPH_URL`. La versión de la API
   va en la URL (`v22.0`); usá la última que muestre el explorador de Meta,
   porque las versiones viejas se apagan a los dos años.
5. Elegí las credenciales de Google Sheets y Telegram en los nodos que las
   piden (quedan como `REEMPLAZAR`).
6. Activá primero el 07. Cuando hayas aprobado la primera publicación y la
   veas bien en Telegram, activá el 08.

---

## El día a día

- **A las 10:00** te llegan a Telegram las publicaciones de las próximas 36
  horas: el posteo y la historia de mañana. Mirás la imagen, el pie y la nota
  de Lupa, y tocás **Aprobar** o **No publicar**. Se
  abre una página que dice *Aprobado ✓* y te llega la confirmación por Telegram.
- Si no tocás nada, al otro día te lo vuelve a pedir. **Sin aprobación no se
  publica nunca.**
- A la hora fijada sale, y te llega el aviso con el link a la publicación.
- **Para cambiar el pie** de algo ya aprobado: editalo en la planilla antes de
  la hora. El publicador usa lo que diga la planilla en ese momento.
- **Para frenar algo ya aprobado:** poné `rechazado` en `estado`.

## Si algo falla

| Lo que ves | Qué pasó | Qué hacer |
|---|---|---|
| ⚠️ *No se pudo publicar… (código 190)* | El token venció o se revocó | Generá uno nuevo (paso 3) y pegalo en el `Config` del 08 |
| ⚠️ *…image_url… / código 9004* | Instagram no pudo bajar la imagen | Abrí la URL en el navegador; si da 404, faltó el paso 4 |
| ⏳ *sigue procesando* | Un reel tardó más de 3 minutos en procesarse | Nada: queda aprobado y se reintenta en la próxima pasada (media hora) |
| ⏸️ *Cupo casi lleno* | Llegaste al límite diario de publicaciones por API (hoy 50 cada 24 h) | Sale en la próxima vuelta con cupo |
| ⚠️ *Quedó aprobada pero sin publicar más de 48 h* | n8n estuvo apagado o el token caído | Cambiá la fecha y volvé a poner `aprobado` |
| No llega nada a las 10 | El 07 está inactivo o el `SHEET_ID` está mal | Abrí la ejecución en n8n y mirá el error |
| Falta una pieza en Telegram | Lupa la frenó (columna `revision`) | Mirá `06-NOTAS/lupa/REVISION.md`, corregí y volvé a correr `lupa.py` |

Las filas con `error` no se vuelven a intentar solas: arreglás la causa y
cambiás el estado a `aprobado` otra vez.

## Seguridad

- El **token de Instagram vive solo en n8n** (nodo `Config` del 08 o, si tu
  n8n lo permite, en una variable de entorno). Nunca en la planilla, nunca en
  el repositorio, nunca en un mail.
- El link de aprobación lleva un `TOKEN` propio: sin él, el webhook no cambia
  nada. Si alguien lo ve, cambialo en los dos `Config` del 07.
- La app de Meta en modo desarrollo solo puede publicar en las cuentas de los
  administradores de la app: vos.
- Si dejás de usarlo, borrá el token en el depurador de Meta y desactivá los
  flujos.

## Archivos

| Archivo | Qué es |
|---|---|
| `10-MOTOR/calendario_sheet.py` | Arma `calendario_instagram.csv` desde el calendario |
| `10-MOTOR/lupa.py` | Lupa: revisa cada pieza y llena `revision`; `--semana AAAA-MM-DD` arma la hoja de contacto |
| `10-MOTOR/preparar_ig.sh` | Copia las piezas a `07-PUBLICAR/ig/` (`--dry-run`, `--pista-muda`) |
| `n8n/07_aprobacion_instagram.json` | Pide aprobación por Telegram y guarda tu respuesta |
| `n8n/08_publicador_instagram.json` | Publica lo aprobado con la Graph API |
| `sheets_estructura.md` | Las columnas de la hoja `Calendario` |
