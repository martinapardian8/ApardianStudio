# Instagram: conectar la publicación automática, paso a paso

Para Martin. Hacelo en la computadora: Meta Business no se maneja bien
desde el celular. Lleva alrededor de una hora la primera vez.

Cómo funciona cuando está andando: vos tocás ✓ en el Centro, n8n publica
a la hora del calendario y te avisa por Telegram. El token de Instagram
vive solo en n8n: no va en el chat, ni en la planilla, ni en un mail.

---

## Parte A · La cuenta de Instagram (5 min)

1. En la app de Instagram: tu perfil → ☰ → **Configuración y actividad** →
   **Tipo de cuenta y herramientas** → **Cambiar a cuenta profesional** →
   **Empresa**. Si ya dice "Cuenta profesional", seguí al paso 2.
2. Vinculá la página de Facebook del estudio: perfil → **Editar perfil** →
   **Página** → **Conectar** y elegí la página. Si no tenés página, ahí mismo
   te deja crear una.

## Parte B · El portfolio comercial (10 min)

3. Entrá a https://business.facebook.com/settings con tu Facebook.
   Si te pide crear un portfolio comercial, creá uno: **APARDIAN STUDIO**.
4. Menú izquierdo → **Cuentas** → **Páginas** → **Agregar** → elegí la
   página del estudio.
5. **Cuentas** → **Cuentas de Instagram** → **Agregar** → iniciá sesión con
   apardian.studio.

## Parte C · La app de Meta (10 min)

6. Entrá a https://developers.facebook.com/apps → **Crear app**.
7. Caso de uso: **Otro** → tipo de app: **Empresa** → nombre:
   **APARDIAN Publicador** → tu mail → portfolio comercial:
   **APARDIAN STUDIO** → **Crear app**.
8. En el panel de la app, en **Agregar productos**, buscá **Instagram** →
   **Configurar** → elegí **API con inicio de sesión de Facebook**
   (no la de inicio de sesión de Instagram).
9. Dejala en **modo desarrollo**. Alcanza para publicar en tu propia cuenta y
   no hace falta que Meta la revise.

## Parte D · El usuario del sistema y su token (10 min)

El "usuario del sistema" es un usuario robot de tu portfolio. Su token no
vence, así que no hay que renovarlo cada 60 días.

10. Volvé a https://business.facebook.com/settings → **Usuarios** →
    **Usuarios del sistema** → **Agregar** → nombre: **n8n-publicador** →
    rol: **Administrador** → **Crear usuario del sistema**.
    Ya existe: **n8n Editor**, con la app **APARDIAN Editor**. Usá ese.
11. Con el usuario elegido → **Asignar activos**:
    - **Apps** → APARDIAN Editor → **Control total**
    - **Páginas** → Estudio Apardian → **Control total** (al 31/10 decía
      "Aún no hay nada asignado": sin esto el token no ve la cuenta)
    - **Cuentas de Instagram** → apardian.studio → **Control total**
    → **Guardar cambios**.
12. **Generar token** → app: **APARDIAN Editor** → caducidad: **Nunca** →
    marcá estos permisos:
    - `instagram_basic`
    - `instagram_content_publish`
    - `instagram_manage_insights`
    - `pages_show_list`
    - `pages_read_engagement`
    - `business_management`

    → **Generar token**.
13. **Copiá el token y guardalo en tu gestor de contraseñas.** Meta lo
    muestra una sola vez. Si lo perdés, generás otro igual (paso 12).
    Ese texto largo que empieza con `EAA` es "el token del usuario del
    sistema".

## Parte E · Probar el token (5 min)

14. Abrí https://developers.facebook.com/tools/debug/accesstoken/ → pegá el
    token → **Depurar**. Tiene que decir **Caduca: Nunca** y listar los seis
    permisos del paso 12.
15. Abrí https://developers.facebook.com/tools/explorer/ → en
    **Token de acceso** pegá tu token → en la barra escribí
    `me/accounts?fields=instagram_business_account{id,username}` →
    **Enviar**. Tiene que aparecer `"username": "apardian.studio"` y
    `"id": "17841449627698502"`. Ese id ya viene cargado en los flujos.
    Si sale otro número, avisame.

## Parte F · La planilla (5 min)

16. Abrí la planilla de Radar:
    https://docs.google.com/spreadsheets/d/1r5y3eKsDaIwNYuHGpV7E9esgMd7WdnDlcDtkKgmfJTQ/edit
17. Abajo a la izquierda, **+** → renombrá la hoja nueva a **Calendario**
    (exacto, con mayúscula). **Archivo → Importar → Subir** →
    `Calendario.csv` del kit → **Reemplazar la hoja actual** → **Importar
    datos**.
18. Otra hoja nueva: **Metricas** (sin tilde) → importá `Metricas.csv`
    igual que en el paso 17.

## Parte G · Los flujos en n8n (15 min)

19. Entrá a https://apardianstudio.app.n8n.cloud/home/workflows. Si ya hay
    flujos viejos "07 · Aprobación de Instagram" u "08 · Publicador",
    archivalos (⋯ → **Archive**): dos flujos con el mismo webhook chocan.
20. **Create workflow** → arriba a la derecha **⋯** → **Import from File…**
    → `IG_07_aprobacion.json`.
21. Los nodos con un triángulo rojo piden credencial. Abrí cada uno →
    **Credential** → elegí la de **Google Sheets** o la de **Telegram**, las
    mismas que usa Radar. En el 07 son: Leer Calendario, Pedir aprobación
    (foto), Pedir aprobación (texto), Leer Calendario (aprobación), Guardar
    aprobación y Confirmar en Telegram.
22. **Save** → **Publish**.
23. Repetí los pasos 20 a 22 con `IG_08_publicador.json`, y además: abrí el
    nodo **Config** → en `ACCESS_TOKEN` borrá `PEGAR_TOKEN…` y pegá el token
    del paso 13. Credenciales en: Leer Calendario, Guardar resultado, Avisar
    a Martin, Avisar cupo/token, Guardar vencida y Avisar vencida.
24. Lo mismo con `IG_13_metricas.json`: el token en **Config** →
    `ACCESS_TOKEN`, y credenciales en Leer Calendario, Guardar métricas y
    Avisar falla.

## Parte H · La primera publicación (5 min)

25. En el celular, abrí
    https://apardianstudio.com/ig/08-tus-fotos-en-el-mundo/06_parada_rambla.jpg
    Si ves la foto, Instagram también la puede bajar.
26. Abrí el Centro: https://claude.ai/artifact/7rZCs1Sf3iuHJwueEd9QYf →
    **Calendario** → el día de hoy → **✓** en el posteo o en la historia.
    Se abre una página que dice "Aprobado ✓".
27. El 08 pasa a las 11, 11:30, 12, 12:30, 13, 13:30, 19, 19:30, 20 y 20:30
    (Montevideo). A la siguiente pasada publica y te avisa por Telegram con
    el link.
28. Si no llega el aviso, mirá
    https://apardianstudio.app.n8n.cloud/home/executions → la ejecución en
    rojo → mandame una captura del error.

## Parte I · Antes del 9/11

29. Pasá n8n al plan **Starter** desde https://app.n8n.cloud/ para que los
    flujos no se apaguen al terminar la prueba gratis.

---

## El día a día

- **Publicar:** ✓ en el Centro. Lo que no aprobás no sale nunca. A las 10:00
  también te llega por Telegram lo de las próximas 36 horas, con Aprobar y
  No publicar.
- **Pedir algo nuevo:** orden en Centro → Agentes ("Luz: subí esta foto el
  martes"). Luz la arma en la pasada siguiente (cada 2 horas) y te pide el ✓.
- **Editar antes de que salga:** ✗ → **Mejorar** → escribís qué cambiar. Luz
  la rehace y te vuelve a pedir el ✓. O cambiás el pie en la hoja Calendario
  antes de la hora.
- **Frenar algo aprobado:** `rechazado` en la columna `estado` de la hoja.
- **Lo ya publicado:** la API de Instagram no deja cambiar la foto ni el
  texto. Eso, la música de Instagram, los stickers y las etiquetas se hacen
  desde la app.
- **Métricas:** el 13 corre todos los días a las 7:30 y llena la hoja
  Metricas. Con eso Luz y Trato aprenden qué vende.
