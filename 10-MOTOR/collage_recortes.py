# -*- coding: utf-8 -*-
"""Recorta los elementos de collage generados en Higgsfield sobre fondo verde.

Entra: 04-VIDEOS-IA/higgsfield/collage/{chinches,cintas}_verde.jpg
Sale:  04-VIDEOS-IA/higgsfield/collage/recortes/<tipo>_<n>.png con transparencia.

El verde se saca por dominancia (cuanto mas verde que rojo y azul) y despues se
le quita el reflejo verde a los bordes, que si no quedan con un halo.
"""
import os, json
import cv2
import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "04-VIDEOS-IA", "higgsfield", "collage")
DEST = os.path.join(SRC, "recortes")


def sin_verde(ruta):
    im = np.asarray(Image.open(ruta).convert("RGB")).astype(np.float32)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    dom = g - np.maximum(r, b)                      # >0 en el fondo
    alfa = np.clip(1.0 - (dom - 18) / 40.0, 0, 1)   # rampa corta: borde limpio
    # se come un pixel del borde: ahi vive el halo verde amarillento
    alfa = cv2.erode(alfa, np.ones((3, 3), np.uint8), iterations=2)
    alfa = cv2.GaussianBlur(alfa, (3, 3), 0)
    g2 = np.minimum(g, np.maximum(r, b) * 1.02)     # despill
    out = np.dstack([r, g2, b, alfa * 255]).clip(0, 255).astype(np.uint8)
    return out


def separar(rgba, minimo=1500):
    a = (rgba[..., 3] > 40).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(a, 8)
    piezas = []
    for k in range(1, n):
        x, y, w, h, area = st[k]
        if area < minimo:
            continue
        m = 6
        x0, y0 = max(0, x - m), max(0, y - m)
        x1, y1 = min(rgba.shape[1], x + w + m), min(rgba.shape[0], y + h + m)
        pz = rgba[y0:y1, x0:x1].copy()
        # solo este componente (los vecinos no se cuelan en la caja)
        mk = (lab[y0:y1, x0:x1] == k)
        mk = cv2.dilate(mk.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        pz[..., 3] = np.where(mk, pz[..., 3], 0)
        piezas.append(((y + h / 2) // 200, x, pz, (w, h)))
    piezas.sort(key=lambda p: (p[0], p[1]))
    return piezas


def clasificar_utiles(pz):
    """chinche (rojo), clip (gris metal), broche (negro), cinta (beige), papel (blanco)."""
    a = pz[..., 3] > 128
    px = pz[..., :3][a].astype(np.float32)
    r, g, b = px[:, 0].mean(), px[:, 1].mean(), px[:, 2].mean()
    if r > g * 1.6 and r > 120:
        return "chinche"
    if max(r, g, b) < 90:
        return "broche"
    return "clip"


def clasificar_papeles(pz, wh):
    w, h = wh
    px = pz[..., :3][pz[..., 3] > 128].astype(np.float32)
    r, b = px[:, 0].mean(), px[:, 2].mean()
    return "cinta" if (r - b) > 18 and w > h * 1.8 else "papel"


def main():
    os.makedirs(DEST, exist_ok=True)
    indice = {}
    for nombre, clasif in (("chinches_verde.jpg", "utiles"), ("cintas_verde.jpg", "papeles")):
        rgba = sin_verde(os.path.join(SRC, nombre))
        for _, _, pz, wh in separar(rgba):
            tipo = clasificar_utiles(pz) if clasif == "utiles" else clasificar_papeles(pz, wh)
            k = indice.get(tipo, 0) + 1
            indice[tipo] = k
            Image.fromarray(pz).save(os.path.join(DEST, f"{tipo}_{k:02d}.png"), optimize=True)
    print(json.dumps(indice))


if __name__ == "__main__":
    main()
