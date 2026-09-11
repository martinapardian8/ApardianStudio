# -*- coding: utf-8 -*-
"""Punto de foco de cada foto para object-position.

Toma el recorte cuadrado que elige recorte.py (rostros + textura) y devuelve el
centro de ese recorte como porcentaje de la foto. Un solo dato sirve para la
grilla (1:1), la tira (3:2) y las tarjetas (4:5): object-position alinea ese
punto con el mismo porcentaje del cuadro, asi que el sujeto queda a la vista.
"""
import os, json
from PIL import Image
import recorte

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focos.json")

# Fotos donde el sujeto es chico y de color apagado (autos de drift entre humo):
# ni los rostros ni la textura ni la saturacion lo encuentran, asi que va a mano.
MANUAL = {
    "v__86.jpg": "50% 74%", "v__89.jpg": "50% 78%", "v__90.jpg": "50% 78%", "v__91.jpg": "50% 78%",
}
_c = None

def _cache():
    global _c
    if _c is None:
        _c = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    return _c

def foco_de(ruta):
    """'50% 32%' — x e y del sujeto, en porcentaje de la foto."""
    if os.path.basename(ruta) in MANUAL:
        return MANUAL[os.path.basename(ruta)]
    c = _cache()
    k = os.path.abspath(ruta)
    try:
        st = os.path.getmtime(k)
    except OSError:
        return "50% 50%"
    if k in c and c[k].get("mtime") == st:
        return c[k]["foco"]
    im = Image.open(ruta); sw, sh = im.size
    lado = min(sw, sh)
    x0, y0 = recorte.caja_recorte(ruta, sw, sh, lado, lado)
    fx = (x0 + lado / 2.0) / sw; fy = (y0 + lado / 2.0) / sh
    # tambien el recorte 3:2 en vertical, que es el mas exigente (la tira)
    if sh > sw:
        ch = int(sw * 2 / 3.0)
        _, y1 = recorte.caja_recorte(ruta, sw, sh, sw, ch)
        fy = (y1 + ch / 2.0) / sh
    # Sin rostros, el sujeto suele ser lo mas saturado de la foto (un auto,
    # un ave, un plato): si esa mancha queda fuera del recorte, se corre.
    if not recorte.caras(ruta):
        fx, fy = _hacia_lo_saturado(im, sw, sh, fx, fy)
    foco = "%d%% %d%%" % (round(fx * 100), round(fy * 100))
    c[k] = {"foco": foco, "mtime": st}
    return foco


def _hacia_lo_saturado(im, sw, sh, fx, fy):
    """Mueve el foco hacia la mancha de color mas saturada si es compacta."""
    import numpy as np
    from PIL import ImageFilter
    chico = im.convert("RGB").copy(); chico.thumbnail((160, 160))
    hsv = np.asarray(chico.convert("HSV")).astype(float)
    sat = hsv[:, :, 1] * (hsv[:, :, 2] / 255.0)          # saturacion real (no cuenta lo oscuro)
    umbral = np.percentile(sat, 94)
    if umbral < 70:                                       # foto poco saturada: no hay sujeto de color
        return fx, fy
    mask = sat >= umbral
    ys, xs = np.nonzero(mask)
    if len(xs) < mask.size * 0.004:
        return fx, fy
    # compacidad: si la mancha se reparte por toda la foto es fondo (pasto, cielo)
    if np.std(ys) / mask.shape[0] > 0.22 and np.std(xs) / mask.shape[1] > 0.22:
        return fx, fy
    cx = np.median(xs) / mask.shape[1]; cy = np.median(ys) / mask.shape[0]
    # solo importa el eje que se recorta
    if sh > sw:
        fy = 0.35 * fy + 0.65 * cy
    else:
        fx = 0.35 * fx + 0.65 * cx
    return fx, fy

def guardar():
    if _c is not None:
        json.dump(_c, open(CACHE, "w"), indent=0)
        recorte.guardar_cache()
