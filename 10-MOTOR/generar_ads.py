# -*- coding: utf-8 -*-
"""Renderiza las 50 piezas de pauta en los dos formatos que pide Meta:
posteo 4:5 para el feed e historia 9:16 para stories y reels.

Sale todo numerado para que Martin lo suba en orden. Solo fotos verticales
que llenen el cuadro (Martin, 28/10/2026).

python3 10-MOTOR/generar_ads.py                      # todo lo que no salió
python3 10-MOTOR/generar_ads.py --desde 2026-11-02   # solo lo del calendario desde ese día
"""
import os, re, unicodedata, json
from motor_ads import *
from motor_ads import _vetada
from campanas import TODO

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
D_POST  = os.path.join(DEST, "01-posteos-pauta")
D_STORY = os.path.join(DEST, "02-historias-pauta")

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:46]


# La foto de la pieza era horizontal y Martin no tiene una vertical que
# muestre lo que dice el texto: no se rehace y Lupa la frena hasta que Martin
# decida. Si hace falta elegir una a mano, va acá la ruta.
VERTICAL = {
    27: None,   # Una botella que se vende sola: no hay botella en vertical
    17: os.path.join(IMG, "naturaleza", "web", "v__54.jpg"),   # el velero (orden del Centro 28/10)
}

# Motivo al medio y fotos derechas (Martin, orden del Centro 28/10/2026:
# "centrá y ajustá la foto bien en el medio, el barco"): motor_ads.encuadrar.
# centro = (x, y) del motivo en la foto original; girar en grados (antihorario).
ENCUADRE = {
    17: dict(centro=(605, 1050)),   # el velero, al medio
}


def rutas_para(cat, idx, excluir=(), evitar=()):
    """La foto de la pieza. Tiene que llenar los DOS formatos (la misma foto va
    en posteo 4:5 y en historia 9:16): vertical, recorte de 22 % como mucho y
    sin partir caras (Martin, 28/10/2026). En gastronomía, solo comida. Si la
    del catálogo no sirve, otra vertical del mismo tema que no salga esos días."""
    que = COMIDA if cat == "gastronomia" else None
    r = foto_de(cat, idx, que)
    for k in range(20):
        alt = foto_de(cat, idx + k, que)
        if not (_vetada(alt, POST) or _vetada(alt, STORY)):
            r = alt
            break
    return (vertical(r, [POST, STORY], excluir=excluir, contenido=que, evitar=evitar)
            or vertical(r, [POST, STORY], contenido=que))


def render(c, size, story, ruta):
    """Todas las piezas con la misma idea: la foto de Martin manda, el texto
    va al pie (pieza_foto). Pedido de Martin del 26/10/2026. Las listas de lo
    que incluye cada servicio van en el pie de foto, no en la imagen."""
    cc = {k: v for k, v in c.items() if not k.startswith("_") and k not in ("items", "fondo")}
    return pieza_foto(ruta, size, story, cc)[0]


def texto_de(c):
    return " · ".join(str(c[k]) for k in ("numero", "kicker", "titular", "sub") if c.get(k))


def main(desde=None):
    """desde (AAAA-MM-DD): solo rehace las piezas del calendario que salen ese
    día o después. Lo que ya salió no se toca nunca."""
    os.makedirs(D_POST, exist_ok=True)
    os.makedirs(D_STORY, exist_ok=True)
    indice = []
    IDX = os.path.join(DEST, "indice_pauta.json")
    viejo = {x["n"]: x for x in json.load(open(IDX, encoding="utf-8"))} if os.path.exists(IDX) else {}
    for i, c in enumerate(TODO, 1):
        # el archivo conserva su nombre aunque cambie el texto: el calendario lo usa
        nom = viejo[i]["archivo"] if i in viejo else f"{i:03d}_{c['_camp']}_{slug(c['titular'])}.jpg"
        salidas = [(os.path.join(D, nom), size, story) for D, size, story in
                   ((D_POST, POST, False), (D_STORY, STORY, True))]
        salidas = [x for x in salidas if se_puede_escribir(x[0], desde)]
        if not salidas:
            if i in viejo:
                indice.append(viejo[i])
            continue
        try:
            cerca, vistas = set(), []
            for destino, _, _ in salidas:
                cerca |= fotos_cerca(destino)
                vistas += usos_cerca(destino, 12)
            ruta = VERTICAL[i] if i in VERTICAL else rutas_para(c["_cat"], c["_idx"], cerca, vistas)
            if ruta is None:
                raise ValueError("no hay una foto vertical de Martin que muestre lo que dice el texto")
            for destino, size, story in salidas:
                rp = encuadrar(ruta, size, nombre="p%03d" % i, **ENCUADRE[i]) if i in ENCUADRE else ruta
                render(c, size, story, rp).save(destino, "JPEG", quality=90, optimize=True)
                registrar(destino, [ruta])
            indice.append({"n": i, "campana": c["_camp"], "titular": c["titular"],
                           "cta": c["cta"], "archivo": nom,
                           "foto": os.path.relpath(ruta, RAIZ), "texto": texto_de(c)})
        except Exception as e:
            print(f"  FALLO {i:03d} {c['_camp']}: {type(e).__name__}: {e}")
            if i in viejo:
                indice.append(viejo[i])
    json.dump(indice, open(os.path.join(DEST, "indice_pauta.json"), "w"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"posteos": len(os.listdir(D_POST)),
                      "historias": len(os.listdir(D_STORY))}, ensure_ascii=False))


if __name__ == "__main__":
    import sys
    main(opcion_desde(sys.argv))
