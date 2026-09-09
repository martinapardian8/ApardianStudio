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
rsync -a --exclude 'img/video/*.mp4' "$SRC/" "$DST/" 2>>"$LOG"

# 2) videos: 720p, mas comprimidos
mkdir -p "$DST/img/video"
for f in "$SRC/img/video/"*.mp4; do
  b=$(basename "$f")
  "$FF" -y -i "$f" -c:v libx264 -preset slow -crf 30 -vf "scale=1280:-2" -an \
        -movflags +faststart "$DST/img/video/$b" >>"$LOG" 2>&1
  echo "video $b" >> "$LOG"
done

# 3) imagenes grandes: 1500px, calidad 70
python3 - >>"$LOG" 2>&1 <<'PY'
from PIL import Image
import os
DST="/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/07-PUBLICAR/img"
n=0
for root,_,files in os.walk(DST):
    if os.path.basename(root)!="web": continue
    for f in files:
        if not f.lower().endswith(".jpg"): continue
        p=os.path.join(root,f)
        im=Image.open(p)
        if max(im.size)>1500: im.thumbnail((1500,1500), Image.LANCZOS)
        im.convert("RGB").save(p, quality=70, optimize=True, progressive=True)
        n+=1
print("imagenes recomprimidas:", n)
PY

echo "=== LISTO ===" >> "$LOG"
du -sh "$DST" >> "$LOG"
