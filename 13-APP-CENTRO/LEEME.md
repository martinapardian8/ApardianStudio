# Centro APARDIAN — la app de escritorio

`Centro APARDIAN.app` abre la app del estudio (calendario, carruseles, clientes
y guiones) con su ícono propio. Con Chrome, Brave o Edge se abre en una
ventana sola, sin pestañas, como una app de verdad. Si no tenés ninguno, se
abre en tu navegador. Lo que marcás se guarda en tu cuenta de Claude, así que
lo ves igual en la compu y en el celular.

## Instalar (una vez)

1. Bajá `Centro-APARDIAN-Mac.zip` (100 KB, no hace falta el repo entero) y
   hacé doble clic para descomprimirlo. O, si tenés el repo, `git pull`.
2. Abrí la carpeta y hacé doble clic en `instalar.command`.
   Deja la app en Aplicaciones, un acceso en el escritorio y la abre.
3. Para tenerla en el Dock: con la app abierta, clic derecho en su ícono del
   Dock → Opciones → Mantener en el Dock.

Si macOS dice que no puede abrir `instalar.command` "porque es de un
desarrollador no identificado": Configuración del Sistema → Privacidad y
seguridad → al final, **Abrir igualmente** (en macOS anteriores a Sequoia,
clic derecho → Abrir → Abrir). Es una sola vez.

La primera vez que se abre, si Chrome no tiene tu sesión de claude.ai, te
pide entrar. Después queda.

## El ícono

`icono/` tiene el ícono en PNG (1024 a 32 px) y en `.icns`. Se regenera con
`python3 10-MOTOR/icono_app.py`: squircle negro, la A en Anton y el punto
rojo de APARDIAN.

## Windows

`Centro-APARDIAN-Windows.zip` trae todo lo necesario (son 25 KB; no hace falta
bajar el repo entero):

1. Clic derecho en el ZIP → **Extraer todo** → Extraer.
2. Doble clic en `instalar-windows.bat`. Si aparece *Windows protegió su PC*:
   **Más información** → **Ejecutar de todas formas** (una sola vez).
3. Queda **Centro APARDIAN** en el Escritorio y en el menú Inicio, con su
   ícono, y se abre en ventana propia con Chrome o con Edge.

Los archivos sueltos están en `windows/` (`instalar.ps1` hace el trabajo:
crea los accesos directos y copia el ícono a `%LOCALAPPDATA%\CentroAPARDIAN`).
Si cambia el ícono, `CentroAPARDIAN.ico` se rehace desde `icono/icono_1024.png`.
