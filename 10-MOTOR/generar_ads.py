# -*- coding: utf-8 -*-
"""Renderiza las 50 piezas de pauta en los dos formatos que pide Meta:
posteo 4:5 para el feed e historia 9:16 para stories y reels.

Sale todo numerado para que Martin lo suba en orden.
"""
import os, re, unicodedata, json
from motor_ads import *
from campanas import TODO

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
D_POST  = os.path.join(DEST, "01-posteos-pauta")
D_STORY = os.path.join(DEST, "02-historias-pauta")

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:46]


def rutas_para(cat, idx):
    """La foto de la pieza. Tiene que encuadrar bien en los DOS formatos (la
    misma foto va en posteo y en historia). En gastronomía, solo comida."""
    import similitud as S
    malas = S._vetadas(POST) | S._vetadas(STORY)
    que = COMIDA if cat == "gastronomia" else None
    for k in range(20):
        r = foto_de(cat, idx + k, que)
        if r not in malas:
            return r
    return foto_de(cat, idx, que)


def render(c, size, story, ruta):
    """Todas las piezas con la misma idea: la foto de Martin manda, el texto
    va al pie (pieza_foto). Pedido de Martin del 26/10/2026. Las listas de lo
    que incluye cada servicio van en el pie de foto, no en la imagen."""
    cc = {k: v for k, v in c.items() if not k.startswith("_") and k not in ("items", "fondo")}
    return pieza_foto(ruta, size, story, cc)[0]


def texto_de(c):
    return " · ".join(str(c[k]) for k in ("numero", "kicker", "titular", "sub") if c.get(k))


def main():
    os.makedirs(D_POST, exist_ok=True)
    os.makedirs(D_STORY, exist_ok=True)
    indice = []
    IDX = os.path.join(DEST, "indice_pauta.json")
    viejo = {x["n"]: x["archivo"] for x in json.load(open(IDX, encoding="utf-8"))} if os.path.exists(IDX) else {}
    for i, c in enumerate(TODO, 1):
        # el archivo conserva su nombre aunque cambie el texto: el calendario lo usa
        nom = viejo.get(i) or f"{i:03d}_{c['_camp']}_{slug(c['titular'])}.jpg"
        try:
            ruta = rutas_para(c["_cat"], c["_idx"])
            render(c, POST, False, ruta).save(os.path.join(D_POST, nom), "JPEG",
                                              quality=90, optimize=True)
            render(c, STORY, True, ruta).save(os.path.join(D_STORY, nom), "JPEG",
                                              quality=90, optimize=True)
            indice.append({"n": i, "campana": c["_camp"], "titular": c["titular"],
                           "cta": c["cta"], "archivo": nom,
                           "foto": os.path.relpath(ruta, RAIZ), "texto": texto_de(c)})
        except Exception as e:
            print(f"  FALLO {i:03d} {c['_camp']}: {type(e).__name__}: {e}")
    json.dump(indice, open(os.path.join(DEST, "indice_pauta.json"), "w"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"posteos": len(os.listdir(D_POST)),
                      "historias": len(os.listdir(D_STORY))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
