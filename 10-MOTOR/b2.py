# -*- coding: utf-8 -*-
"""Bajada compacta: cada linea es  carpeta|nombre|cola_del_archivo"""
import sys, os, urllib.request
from PIL import Image
BASE = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/contenido ia/marca"
CDN  = "https://d8j0ntlcm91z4.cloudfront.net/user_3CVTKHXGGh4BrFHiP6f98Bqa8GI/"
TMP  = "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/png"
os.makedirs(TMP, exist_ok=True)
ok, mal = 0, []
for ln in sys.stdin.read().strip().splitlines():
    ln = ln.strip()
    if not ln: continue
    carp, nom, cola = ln.split("|")
    d = os.path.join(BASE, carp); os.makedirs(d, exist_ok=True)
    try:
        raw = os.path.join(TMP, nom + ".png")
        urllib.request.urlretrieve(CDN + cola, raw)
        im = Image.open(raw)
        if im.mode in ("RGBA","P","LA"):
            f = Image.new("RGB", im.size, (248,247,246)); im = im.convert("RGBA")
            f.paste(im, mask=im.split()[-1]); im = f
        else: im = im.convert("RGB")
        im.save(os.path.join(d, nom + ".jpg"), "JPEG", quality=92, optimize=True)
        ok += 1
    except Exception as e:
        mal.append((nom, str(e)[:60]))
print({"bajados": ok, "fallaron": mal})
