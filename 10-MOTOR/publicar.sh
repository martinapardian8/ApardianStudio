#!/bin/bash
# Arma una copia liviana del sitio, lista para subir a un hosting estatico.
set -e
P="$(cd "$(dirname "$0")/.." && pwd)"   # la carpeta del proyecto, este donde este
SRC="$P/05-WEB"
DST="$P/07-PUBLICAR"
LOG="$P/06-NOTAS/publicar.log"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
: > "$LOG"
rm -rf "$DST"; mkdir -p "$DST"

# 1) todo menos videos e imagenes grandes
#    ni archivos de trabajo: nada de esto tiene que quedar publico
rsync -a --exclude 'img/video/*.mp4' --exclude '_qa_*' \
      --exclude '.DS_Store' --exclude '._*' --exclude '.git' --exclude '* 2.*' --exclude '* 3.*' \
      --exclude '*.md' --exclude '*.py' --exclude '*.sh' --exclude '*.json' --exclude '*.log' \
      --exclude '*.bak' --exclude '*~' --exclude '*.psd' --exclude '*.lrcat' --exclude '*.xmp' \
      "$SRC/" "$DST/" 2>>"$LOG"

# 2) videos: 720p, mas comprimidos. Se guardan en cache por tamaño+fecha del
#    original, asi las corridas siguientes no vuelven a codificar 17 videos.
CACHE="$P/06-NOTAS/.cache-video"
mkdir -p "$DST/img/video" "$CACHE"
for f in "$SRC/img/video/"*.mp4; do
  b=$(basename "$f")
  # tamaño y fecha del original: stat de macOS (-f) o de Linux (-c)
  if [ "$(uname)" = "Darwin" ]; then firma=$(stat -f "%z-%m" "$f"); else firma=$(stat -c "%s-%Y" "$f"); fi
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
DST_IMG="$DST/img" python3 - >>"$LOG" 2>&1 <<'PY'
from PIL import Image
import os
DST=os.environ["DST_IMG"]
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

# 4) control: si algo privado se coló en el build, se frena aca
if find "$DST" \( -name '_qa_*' -o -name '*.md' -o -name '*.py' -o -name '*.sh' -o -name '*.json' -o -name '.git' \) | grep -q .; then
  echo "ERROR: hay archivos privados en $DST" | tee -a "$LOG"; exit 1
fi

echo "=== LISTO ===" >> "$LOG"
du -sh "$DST" >> "$LOG"
