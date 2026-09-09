#!/bin/bash
SRC="/Users/martinapardian/Desktop/FOTOGRAFIA"
PROJ="/Users/martinapardian/Desktop/WEB APARDIANSTUDIO"
STAGE="$PROJ/02-FOTOS-ORIGINALES/_stage"
OUT="$PROJ/03-FOTOS-OPTIMIZADAS"
LOG="$PROJ/06-NOTAS/pipeline.log"
mkdir -p "$STAGE" "$OUT" "$PROJ/06-NOTAS"
: > "$LOG"

# categoria|ruta relativa dentro de FOTOGRAFIA|slug
JOBS=(
"eventos-bodas|IVANNA Y SANTIAGO EDITADAS|ivanna-santiago"
"eventos-bodas|CUMPLE LETICIA 40 EDITADAS|leticia40"
"eventos-bodas|EDITADAS - CUMPLE 60 - CARO - 2024|caro60"
"eventos-bodas|EDITADAS 15 SOL|15-sol"
"eventos-bodas|EDITADAS CUMPLE DE MAMA|cumple-mama"
"eventos-bodas|NICOL CUMPLE EDITADAS|nicol"
"eventos-bodas|SALON EDITADAS LA CONDESA|la-condesa"
"eventos-bodas|EDITADAS JUAN LUZ|juan-luz"
"eventos-bodas|EDITADAS BALCON/BALCON|balcon"
"eventos-bodas|DON APO EDITADAS|don-apo"
"gastronomia|DIA DEL ALFAJOR EDITADAS 2026|alfajor"
"gastronomia|LA ESTACION/EDIT LA ESTACION 2|la-estacion"
"deporte-accion|EDITADAS GOLF|golf-a"
"deporte-accion|GOLF EDITADO|golf-b"
"empresas|ODONTOVITA/odontovita aniversario editadas|odontovita"
"empresas|LOKOTAS EDITADAS|lokotas"
"empresas|SERGIO DA SILVA EDITADAS|sergio"
"retratos|HORACIO EDITADAS|horacio"
"retratos|PORTFOLIO 2|portfolio"
)

for job in "${JOBS[@]}"; do
  CAT="${job%%|*}"; rest="${job#*|}"; REL="${rest%%|*}"; SLUG="${rest##*|}"
  echo "[$(date +%H:%M:%S)] START $SLUG ($CAT)" >> "$LOG"
  rm -rf "$STAGE/$SLUG"; mkdir -p "$STAGE/$SLUG"
  osascript <<EOF >> "$LOG" 2>&1
tell application "Finder"
  set srcF to folder (POSIX file "$SRC/$REL")
  set dstF to folder (POSIX file "$STAGE/$SLUG")
  duplicate (every file of srcF) to dstF with replacing
end tell
EOF
  mkdir -p "$OUT/$CAT/web" "$OUT/$CAT/thumb"
  n=0
  for f in "$STAGE/$SLUG"/*.[jJ][pP][gG] "$STAGE/$SLUG"/*.[jJ][pP][eE][gG] "$STAGE/$SLUG"/*.[pP][nN][gG]; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); b="${b%.*}"
    sips -Z 1800 -s format jpeg -s formatOptions 74 "$f" --out "$OUT/$CAT/web/${SLUG}__${b}.jpg" >/dev/null 2>&1
    sips -Z 420  -s format jpeg -s formatOptions 60 "$f" --out "$OUT/$CAT/thumb/${SLUG}__${b}.jpg" >/dev/null 2>&1
    n=$((n+1))
  done
  rm -rf "$STAGE/$SLUG"
  echo "[$(date +%H:%M:%S)] DONE  $SLUG -> $n fotos" >> "$LOG"
done
rm -rf "$STAGE"
echo "[$(date +%H:%M:%S)] === PIPELINE COMPLETO ===" >> "$LOG"
find "$OUT" -name '*.jpg' -path '*/web/*' | wc -l | xargs echo "TOTAL WEB:" >> "$LOG"
