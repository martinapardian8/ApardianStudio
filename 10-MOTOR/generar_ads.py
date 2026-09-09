# -*- coding: utf-8 -*-
"""Renderiza las 50 piezas de pauta en los dos formatos que pide Meta:
posteo 4:5 para el feed e historia 9:16 para stories y reels.

Sale todo numerado para que Martin lo suba en orden.
"""
import os, re, unicodedata, json
from motor_ads import *
import plantillas_ads as P
from campanas import TODO

DEST = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/08-CONTENIDO-INSTAGRAM"
D_POST  = os.path.join(DEST, "01-posteos-pauta")
D_STORY = os.path.join(DEST, "02-historias-pauta")

# plantillas que en vertical funcionan mejor cambiadas
CAMBIO_STORY = {
    "grilla_cuatro": "dos_fotos",     # cuatro fotos en 9:16 quedan diminutas
    "marco_hueso":   "mitad_color",   # el marco no respira en vertical
}
# cuantas fotos necesita cada plantilla
MULTI = {"grilla_cuatro": 4, "dos_fotos": 2}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:46]


def rutas_para(plant, cat, idx):
    """Una sola foto, o varias que no cuenten lo mismo.

    Antes se tomaban indices salteados y salian cuatro mesas montadas casi
    iguales. Ahora el selector exige variedad de tema: gente, luz y color.
    """
    import similitud as S
    # La misma foto se usa en posteo y en historia, asi que tiene que encuadrar
    # bien en los DOS formatos. Antes solo se controlaba el 4:5 y en vertical
    # quedaban rostros cortados.
    malas = S._vetadas(POST) | S._vetadas(STORY)
    n = MULTI.get(plant, 1)
    if n == 1:
        r = foto(cat, idx)
        if r in malas:
            for k in range(1, 20):
                alt = foto(cat, idx + k)
                if alt not in malas:
                    return alt
        return r
    from motor_ads import pool
    cands = pool().get(cat) or []
    cands = [p for p in cands if p not in malas] or cands
    return S.variadas(cands, n, arranque=idx, size=POST)


def render(c, size, story):
    plant = c["_plant"]
    if story:
        plant = CAMBIO_STORY.get(plant, plant)
    fn = getattr(P, plant)
    cc = {k: v for k, v in c.items() if not k.startswith("_")}
    if plant == "mitad_color" and "fondo" not in cc:
        cc["fondo"] = "negro"
    if plant in ("lista_servicio",) and "items" not in cc:
        plant = "barra_inferior"; fn = getattr(P, plant)
    if plant in ("oferta_numero", "prueba_social") and "numero" not in cc:
        plant = "titular_sobre_foto"; fn = getattr(P, plant)
    return fn(size, story, rutas_para(plant, c["_cat"], c["_idx"]), cc)


def main():
    os.makedirs(D_POST, exist_ok=True)
    os.makedirs(D_STORY, exist_ok=True)
    indice = []
    for i, c in enumerate(TODO, 1):
        nom = f"{i:03d}_{c['_camp']}_{slug(c['titular'])}.jpg"
        try:
            render(c, POST, False).save(os.path.join(D_POST, nom), "JPEG",
                                        quality=90, optimize=True)
            render(c, STORY, True).save(os.path.join(D_STORY, nom), "JPEG",
                                        quality=90, optimize=True)
            indice.append({"n": i, "campana": c["_camp"], "titular": c["titular"],
                           "cta": c["cta"], "archivo": nom})
        except Exception as e:
            print(f"  FALLO {i:03d} {c['_camp']}: {type(e).__name__}: {e}")
    json.dump(indice, open(os.path.join(DEST, "indice_pauta.json"), "w"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"posteos": len(os.listdir(D_POST)),
                      "historias": len(os.listdir(D_STORY))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
