# -*- coding: utf-8 -*-
"""Renderiza las versiones en video de los avisos más fuertes de cada campaña
(08-CONTENIDO-INSTAGRAM/05-videos) con video_ads.py.

La foto de cada video es la misma de su pieza de pauta (indice_pauta.json) y
el texto, el de campanas.py (con sus tildes). Los archivos conservan el
nombre que ya tenían: el calendario los usa.

python3 10-MOTOR/generar_videos.py            # todos
python3 10-MOTOR/generar_videos.py 018 041    # algunos
"""
import os, sys, json, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_ads as V
from motor_ads import POST, STORY, RAIZ
from campanas import TODO

IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
# el aviso más fuerte de cada campaña, por índice en TODO (base 1). El 17 era
# un antes/después simulado: no va (no tenemos los originales sin editar).
FEED = [1, 9, 24, 30, 37, 41, 47, 50, 18]
STORY_ = [1, 9, 30, 37]


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:40]


def main(solo):
    pauta = {x["n"]: x for x in json.load(open(os.path.join(IG, "indice_pauta.json"), encoding="utf-8"))}
    idx = os.path.join(IG, "indice_videos.json")
    viejo = {(x["n"], x["formato"]): x["archivo"] for x in json.load(open(idx, encoding="utf-8"))} \
        if os.path.exists(idx) else {}
    hechos = []
    for grupo, size, story, suf in ((FEED, POST, False, "feed"), (STORY_, STORY, True, "historia")):
        for n in grupo:
            c = TODO[n - 1]
            nom = viejo.get((n, suf)) or f"{n:03d}_{c['_camp']}_{slug(c['titular'])}_{suf}.mp4"
            nom = nom[:-4]
            if not solo or f"{n:03d}" in solo:
                ruta = os.path.join(RAIZ, pauta[n]["foto"])
                V.render(nom, ruta, {"kicker": c.get("kicker"), "titular": c["titular"]}, size, story)
                print("  ok", nom, flush=True)
            hechos.append({"n": n, "campana": c["_camp"], "formato": suf, "archivo": nom + ".mp4"})
    json.dump(hechos, open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"videos": len(hechos)}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
