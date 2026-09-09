# -*- coding: utf-8 -*-
"""Baja resultados de Higgsfield y los guarda como JPEG en la carpeta de marca.
Uso: python3 bajar.py '<json: [{"carpeta":..,"nombre":..,"url":..}, ...]>' """
import sys, json, os, urllib.request
from PIL import Image
BASE = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/contenido ia/marca"
TMP  = "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/png"
os.makedirs(TMP, exist_ok=True)
items = json.loads(sys.argv[1])
ok, mal = [], []
for it in items:
    dest_dir = os.path.join(BASE, it["carpeta"]); os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, it["nombre"] + ".jpg")
    try:
        raw = os.path.join(TMP, it["nombre"] + ".png")
        urllib.request.urlretrieve(it["url"], raw)
        im = Image.open(raw)
        if im.mode in ("RGBA", "P", "LA"):
            fondo = Image.new("RGB", im.size, (248, 247, 246))
            im = im.convert("RGBA"); fondo.paste(im, mask=im.split()[-1]); im = fondo
        else:
            im = im.convert("RGB")
        im.save(dest, "JPEG", quality=92, optimize=True)
        ok.append((it["carpeta"] + "/" + it["nombre"], im.size))
    except Exception as e:
        mal.append((it["nombre"], str(e)[:80]))
print(json.dumps({"bajados": len(ok), "fallaron": mal,
                  "muestra": [f"{a} {b[0]}x{b[1]}" for a, b in ok[:4]]}, ensure_ascii=False))
