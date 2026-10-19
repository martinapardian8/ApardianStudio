#!/bin/bash
# Copia a 07-PUBLICAR/ig/ los archivos que figuran en la planilla de
# Instagram (11-AUTOMATIZACION/calendario_instagram.csv), con la misma ruta
# relativa que tienen en 08-CONTENIDO-INSTAGRAM. Así quedan en
# https://apardianstudio.com/ig/... cuando se publica el sitio, que es de
# donde Instagram los baja al publicar (la API pide URLs públicas).
#
# Correr DESPUÉS de publicar.sh: publicar.sh borra 07-PUBLICAR entero.
#
#   bash 10-MOTOR/preparar_ig.sh             # copia
#   bash 10-MOTOR/preparar_ig.sh --dry-run   # solo muestra qué copiaría
#   bash 10-MOTOR/preparar_ig.sh --pista-muda
#       además les agrega a los .mp4 una pista de audio en silencio (AAC),
#       sin recodificar la imagen. Solo si Instagram rechaza un reel por no
#       tener audio; por defecto se copian tal cual.
set -e
P="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$P/08-CONTENIDO-INSTAGRAM"
DST="$P/07-PUBLICAR/ig"
CSV="$P/11-AUTOMATIZACION/calendario_instagram.csv"
SECO=0; MUDA=0
for a in "$@"; do
  case "$a" in
    --dry-run) SECO=1 ;;
    --pista-muda) MUDA=1 ;;
    *) echo "opción desconocida: $a"; exit 2 ;;
  esac
done
[ -f "$CSV" ] || { echo "Falta $CSV: corré python3 10-MOTOR/calendario_sheet.py"; exit 1; }

# la lista sale de la columna "archivos" (separados por |), sin repetir
LISTA=$(python3 - "$CSV" <<'PY'
import csv, sys
vistos = []
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    for a in r["archivos"].split("|"):
        if a and a not in vistos:
            vistos.append(a)
print("\n".join(vistos))
PY
)

n=0; faltan=0; bytes=0
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  case "$rel" in
    *.jpg|*.jpeg|*.mp4) ;;
    *) echo "salteo (no es jpg ni mp4): $rel"; continue ;;
  esac
  case "$rel" in *..*) echo "ruta rara, salteo: $rel"; continue ;; esac
  o="$SRC/$rel"; d="$DST/$rel"
  if [ ! -f "$o" ]; then echo "FALTA: $rel"; faltan=$((faltan+1)); continue; fi
  t=$(wc -c < "$o"); bytes=$((bytes+t))
  if [ "$SECO" = 1 ]; then
    echo "copiaría $rel ($((t/1024)) KB)"
  else
    mkdir -p "$(dirname "$d")"
    if [ "$MUDA" = 1 ] && [ "${rel##*.}" = "mp4" ]; then
      ffmpeg -loglevel error -y -i "$o" -f lavfi -i anullsrc=r=48000:cl=stereo \
             -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 64k -shortest \
             -movflags +faststart "$d"
    else
      cp "$o" "$d"
    fi
  fi
  n=$((n+1))
done <<< "$LISTA"

echo "---"
echo "$n archivos ($((bytes/1048576)) MB) $( [ "$SECO" = 1 ] && echo 'se copiarían' || echo "copiados a $DST" )"
[ "$faltan" = 0 ] || { echo "$faltan archivos faltan: revisá la planilla"; exit 1; }
