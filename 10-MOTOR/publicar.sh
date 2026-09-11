#!/bin/bash
# Arma una copia liviana del sitio, lista para subir a un hosting estatico.
set -e
P="/Users/martinapardian/Desktop/WEB APARDIANSTUDIO"
SRC="$P/05-WEB"
DST="$P/07-PUBLICAR"
LOG="$P/06-NOTAS/publicar.log"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
: > "$LOG"
rm -rf "$DST"; mkdir -p "$DST"

# 1) todo menos videos e imagenes grandes
rsync -a --exclude 'img/video/*.mp4' --exclude '_qa_puente.html' --exclude '.DS_Store' "$SRC/" "$DST/" 2>>"$LOG"

# 2) videos: 720p, mas comprimidos. Se guardan en cache por tamaño+fecha del
#    original, asi las corridas siguientes no vuelven a codificar 17 videos.
CACHE="$P/06-NOTAS/.cache-video"
mkdir -p "$DST/img/video" "$CACHE"
for f in "$SRC/img/video/"*.mp4; do
  b=$(basename "$f")
  firma=$(stat -f "%z-%m" "$f")
  c="$CACHE/${b%.mp4}__$firma.mp4"
  if [ ! -s "$c" ]; then
    rm -f "$CACHE/${b%.mp4}__"*.mp4
    "$FF" -y -i "$f" -c:v libx264 -preset slow -crf 30 -vf "scale=1280:-2" -an \
          -movflags +faststart "$c" >>"$LOG" 2>&1
    echo "video codificado $b" >> "$LOG"
  else
    echo "video en cache $b" >> "$LOG"
  fi
  cp "$c" "$DST/img/video/$b"
done

# 3) imagenes grandes: 1500px, calidad 70
python3 - >>"$LOG" 2>&1 <<'PY'
from PIL import Image
import os
DST="/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/07-PUBLICAR/img"
n=0
for root,_,files in os.walk(DST):
    if os.path.basename(root) not in ("web","mockups"): continue
    lim = 1800 if os.path.basename(root)=="mockups" else 1500
    for f in files:
        if not f.lower().endswith(".jpg"): continue
        p=os.path.join(root,f)
        im=Image.open(p)
        if max(im.size)>lim: im.thumbnail((lim,lim), Image.LANCZOS)
        im.convert("RGB").save(p, quality=(76 if lim==1800 else 70), optimize=True, progressive=True)
        n+=1
print("imagenes recomprimidas:", n)
PY

echo "=== LISTO ===" >> "$LOG"
du -sh "$DST" >> "$LOG"
