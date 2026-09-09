# -*- coding: utf-8 -*-
"""Renderiza las versiones en video de los avisos mas fuertes de cada campaña."""
import os, sys, json, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_ads as V
from motor_ads import POST, STORY, foto
from campanas import TODO
import generar_ads as G

# el aviso mas fuerte de cada campaña, por indice en TODO (base 1)
FEED  = [1, 9, 17, 24, 30, 37, 41, 47, 50, 18]
STORY_ = [1, 17, 9, 30, 37]

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:40]

hechos = []
for grupo, size, story, suf in ((FEED, POST, False, "feed"), (STORY_, STORY, True, "historia")):
    for n in grupo:
        c = TODO[n-1]
        cc = {k: v for k, v in c.items() if not k.startswith("_")}
        pl = G.CAMBIO_STORY.get(c["_plant"], c["_plant"]) if story else c["_plant"]
        r = G.rutas_para(pl, c["_cat"], c["_idx"])
        if isinstance(r, list): r = r[0]
        nom = f"{n:03d}_{c['_camp']}_{slug(c['titular'])}_{suf}"
        p = V.render(nom, r, cc, size, story)
        if p:
            hechos.append({"n": n, "campana": c["_camp"], "formato": suf,
                           "archivo": os.path.basename(p)})
            print("  ok", nom, flush=True)
json.dump(hechos, open("/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/08-CONTENIDO-INSTAGRAM/indice_videos.json", "w"),
          ensure_ascii=False, indent=1)
print(json.dumps({"videos": len(hechos)}, ensure_ascii=False))
