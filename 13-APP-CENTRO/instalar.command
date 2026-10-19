#!/bin/bash
# Doble clic: copia Centro APARDIAN a Aplicaciones y deja un acceso en el escritorio.
cd "$(dirname "$0")"
APP="Centro APARDIAN.app"
mkdir -p "$HOME/Applications"
rm -rf "$HOME/Applications/$APP"
cp -R "$APP" "$HOME/Applications/"
chmod +x "$HOME/Applications/$APP/Contents/MacOS/centro"
# la app la hicimos nosotros: se le saca la marca de "bajado de internet"
xattr -dr com.apple.quarantine "$HOME/Applications/$APP" 2>/dev/null
ln -sfn "$HOME/Applications/$APP" "$HOME/Desktop/$APP"
touch "$HOME/Applications/$APP"
echo "Listo: Centro APARDIAN está en tu escritorio y en Aplicaciones."
echo "Para tenerla en el Dock: abrila y, con clic derecho en su ícono del Dock, Opciones → Mantener en el Dock."
open "$HOME/Applications/$APP"
