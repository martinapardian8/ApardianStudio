# Centro APARDIAN — la app de escritorio

`Centro APARDIAN.app` abre la app del estudio (calendario, carruseles, clientes
y guiones) con su ícono propio. Con Chrome, Brave o Edge se abre en una
ventana sola, sin pestañas, como una app de verdad. Si no tenés ninguno, se
abre en tu navegador. Lo que marcás se guarda en tu cuenta de Claude, así que
lo ves igual en la compu y en el celular.

## Instalar (una vez)

1. Traé el repo actualizado (`git pull`) en `~/Desktop/WEB APARDIANSTUDIO`.
2. Abrí la carpeta `13-APP-CENTRO` y hacé doble clic en `instalar.command`.
   Deja la app en Aplicaciones, un acceso en el escritorio y la abre.
3. Para tenerla en el Dock: con la app abierta, clic derecho en su ícono del
   Dock → Opciones → Mantener en el Dock.

Si macOS dice que no puede abrir `instalar.command` "porque es de un
desarrollador no identificado": clic derecho → Abrir → Abrir. Es una sola vez.

La primera vez que se abre, si Chrome no tiene tu sesión de claude.ai, te
pide entrar. Después queda.

## El ícono

`icono/` tiene el ícono en PNG (1024 a 32 px) y en `.icns`. Se regenera con
`python3 10-MOTOR/icono_app.py`: squircle negro, la A en Anton y el punto
rojo de APARDIAN.
