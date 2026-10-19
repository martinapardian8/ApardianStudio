# -*- coding: utf-8 -*-
"""Icono de la app Centro APARDIAN (macOS): squircle negro, la A de Anton en
hueso y el punto rojo de la marca. Sale a 13-APP-CENTRO/icono/ en PNG 1024 y
en .icns para el .app."""
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUE = os.path.join(RAIZ, "10-MOTOR", "fuentes", "Anton-Regular.ttf")
OUT = os.path.join(RAIZ, "13-APP-CENTRO", "icono")
HUESO, NEGRO, ROJO = (248, 247, 246), (23, 23, 23), (255, 0, 51)
S = 4                      # se dibuja a 4x y se achica: bordes limpios
N = 1024 * S


def squircle(d, caja, fill, n=5.0):
    """Superelipse como la de los iconos de macOS (no un rectangulo redondeado)."""
    import math
    x0, y0, x1, y1 = caja
    cx, cy, a, b = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    pts = []
    for k in range(720):
        t = 2 * math.pi * k / 720
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + a * (abs(c) ** (2 / n)) * (1 if c >= 0 else -1),
                    cy + b * (abs(s) ** (2 / n)) * (1 if s >= 0 else -1)))
    d.polygon(pts, fill=fill)


def icono():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = 100 * S                                   # margen de la grilla de Apple
    caja = (m, m, N - m, N - m)
    # sombra corta abajo, como los iconos del sistema
    sombra = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    squircle(ImageDraw.Draw(sombra), (m, m + 14 * S, N - m, N - m + 14 * S), (0, 0, 0, 70))
    im.alpha_composite(sombra)
    squircle(d, caja, NEGRO + (255,))
    # la A en Anton, centrada opticamente un poco a la izquierda para dejar lugar al punto
    f = ImageFont.truetype(FUE, 640 * S)
    bb = d.textbbox((0, 0), "A", font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    x = (N - w) // 2 - bb[0] - 66 * S
    y = (N - h) // 2 - bb[1] + 6 * S
    d.text((x, y), "A", font=f, fill=HUESO)
    # el punto rojo, al pie de la A, como en el logotipo APARDIAN.
    r = 46 * S
    px = x + bb[2] + 30 * S + r          # aire entre la A y el punto, como en el logotipo
    py = y + bb[3] - r
    d.rectangle([px - r, py - r, px + r, py + r], fill=ROJO)
    return im.resize((1024, 1024), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    im = icono()
    im.save(os.path.join(OUT, "icono_1024.png"))
    for t in (512, 256, 180, 128, 64, 32):
        im.resize((t, t), Image.LANCZOS).save(os.path.join(OUT, f"icono_{t}.png"))
    im.save(os.path.join(OUT, "AppIcon.icns"), sizes=[(16, 16), (32, 32), (64, 64), (128, 128),
                                                      (256, 256), (512, 512), (1024, 1024)])
    print("ok")


if __name__ == "__main__":
    main()
