#!/usr/bin/env python3
"""Descarga a assets/fotos/ todos los medios remotos (http/https) de data/fotos.json
y reescribe las rutas para que el sitio no dependa de ningún CDN externo.
Uso: python3 scripts/localizar_medios.py
"""
import json, os, urllib.request, hashlib
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
F = os.path.join(RAIZ, "data", "fotos.json")
DEST = os.path.join(RAIZ, "assets", "fotos")
os.makedirs(DEST, exist_ok=True)
d = json.load(open(F, encoding="utf-8"))
n = 0
def bajar(url):
    global n
    nombre = url.rsplit("/", 1)[-1]
    if len(nombre) > 60: nombre = hashlib.sha1(url.encode()).hexdigest()[:12] + os.path.splitext(nombre)[1]
    destino = os.path.join(DEST, nombre)
    if not os.path.exists(destino):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f: f.write(r.read())
        n += 1; print("  ✓", nombre)
    return "assets/fotos/" + nombre
def recorrer(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("src", "mp4", "poster") and isinstance(v, str) and v.startswith("http"): o[k] = bajar(v)
            else: recorrer(v)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str) and v.startswith("http"): o[i] = bajar(v)
            else: recorrer(v)
recorrer(d)
json.dump(d, open(F, "w", encoding="utf-8"), ensure_ascii=False, indent=2); open(F, "a").write("\n")
print(f"{n} archivos descargados. Revisá también og:image, el poster del <video> y los src de index.html (buscá 'cloudfront').")
