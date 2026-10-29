# -*- coding: utf-8 -*-
"""Tus fotos en el mundo: fotos de Martin montadas en carteles, pantallas y
afiches de escenas generadas en Higgsfield (04-VIDEOS-IA/higgsfield/mundo).

La escena es IA; la foto es la de Martin, sin retocar: se deforma a la
perspectiva del cartel y toma la luz de la escena, nada mas. Por eso cada
pie de foto dice que es un montaje.

python3 10-MOTOR/mundo.py
"""
import os, json
import cv2
import numpy as np
from PIL import Image, ImageDraw
from motor_ads import (HUESO, NEGRO, ROJO, CARBON, IMG, RAIZ, display, work, escribir, titular, firma,
                       medir_titular, velo_banda, se_puede_escribir, opcion_desde)
from recorte import cargar_ok, guardar_cache

ESC = os.path.join(RAIZ, "04-VIDEOS-IA", "higgsfield", "mundo")
CAP = os.path.join(RAIZ, "10-MOTOR", "capturas_web")
DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "08-tus-fotos-en-el-mundo")
POST = (1080, 1350)

# esquinas del cartel en blanco (arriba-izq, arriba-der, abajo-der, abajo-izq),
# medidas a mano sobre cada escena; None = se detecta sola
ESCENAS = [
    # archivo, esquinas, foto, lugar, titular
    ("manhattan_edificio.jpg", [(500, 88), (690, 90), (748, 1132), (455, 1132)],
     ("retratos", "juan-luz__IMG_2696.jpg"), "Nueva York", "Un retrato que se ve desde la esquina."),
    ("estacion_central.jpg", [(972, 186), (1299, 186), (1298, 687), (972, 687)],
     ("bodas", "portfolio__IMG_8771.jpg"), "Nueva York · Grand Central", "Un sí, entre miles que pasan."),
    ("tokio_pantalla.jpg", [(418, 300), (790, 288), (797, 540), (414, 553)],
     ("musica", "nw__IMG_7237.jpg"), "Tokio · Shibuya", "La banda que fotografié, en la pantalla más grande."),
    ("londres_subte.jpg", [(981, 140), (1297, 112), (1204, 697), (948, 599)],
     ("retratos", "v__114.jpg"), "Londres · Underground", "La luz que te frena en la escalera."),
    ("aeropuerto.jpg", [(784, 225), (1379, 114), (1380, 478), (784, 471)],
     ("naturaleza", "v__23.jpg"), "Aeropuerto · llegadas", "Lo primero que ves al llegar."),
    ("parada_rambla.jpg", [(391, 279), (604, 279), (604, 590), (391, 590)],
     ("gastronomia", "nw__IMG_7064.jpg"), "Montevideo · Rambla", "Un plato que se ve desde el ómnibus."),
    ("paris_columna.jpg", [(429, 399), (773, 399), (773, 966), (429, 966)],
     ("retratos", "v__117.jpg"), "París", "Blanco y negro, como tiene que ser."),
    # Martin, orden del Centro 28/10/2026: "centrá la foto para que se vea la
    # marca del aceite": el cartel muestra la etiqueta (foco, en fracción de la foto)
    ("los_angeles_cartel.jpg", [(681, 223), (1375, 112), (1380, 382), (679, 427)],
     ("marcas", "v__77.jpg#0.52,0.63"), "Los Ángeles", "Un producto uruguayo, a la altura de cualquier ruta."),
    ("revista.jpg", [(91, 419), (1017, 421), (1018, 1064), (91, 1063)],
     ("bodas", "nw__IMG_9717.jpg"), "Doble página", "Una boda que pide papel."),
    ("afiche_montevideo.jpg", [(233, 221), (979, 223), (981, 1270), (233, 1271)],
     ("eventos", "nw__IMG_9236.jpg"), "Montevideo · Ciudad Vieja", "Un cumpleaños que merece afiche."),
    ("cuadro_living.jpg", [(683, 383), (955, 383), (955, 701), (683, 701)],
     ("naturaleza", "nw__IMG_1996.jpg"), "En tu casa", "El mar, colgado en el living."),
    ("notebook.jpg", None,
     ("captura", "d_hero.png"), "Tu web", "Tu trabajo, en tu propia página."),
    # verano 26/27: las mismas escenas con otras fotos (sin gastar creditos)
    ("parada_rambla.jpg", [(391, 279), (604, 279), (604, 590), (391, 590)],
     ("gastronomia", "sergio__IMG_7211.jpg"), "Montevideo · Rambla", "La parrilla, a la vista de toda la Rambla."),
    ("afiche_montevideo.jpg", [(233, 221), (979, 223), (981, 1270), (233, 1271)],
     ("eventos", "leticia40__IMG_7731.jpg"), "Montevideo · Ciudad Vieja", "La fiesta, pegada en la pared de la ciudad."),
    ("los_angeles_cartel.jpg", [(681, 223), (1375, 112), (1380, 382), (679, 427)],
     ("eventos", "caro60__IMG_9862.jpg"), "Los Ángeles", "Un lote revelado parejo aguanta cualquier tamaño."),
]


def ruta_foto(cat, nombre):
    """Ruta de la foto; "nombre#fx,fy" fija el foco del recorte en el cartel
    (fracción del ancho y del alto de la foto: lo que tiene que quedar al medio)."""
    nombre = nombre.partition("#")[0]
    if cat == "captura":
        return os.path.join(CAP, nombre)
    return os.path.join(IMG, cat, "web", nombre)


def foco_de(nombre):
    f = nombre.partition("#")[2]
    return tuple(float(x) for x in f.split(",")) if f else None


def recorte_foco(foto, size, foco):
    """El recorte más grande con la proporción del cartel y `foco` al medio
    (si el borde no deja, se corre lo justo)."""
    im = Image.open(foto).convert("RGB")
    w, h = im.size
    r = size[0] / size[1]
    cw, ch = (w, w / r) if w / h < r else (h * r, h)
    cx = min(max(foco[0] * w, cw / 2), w - cw / 2)
    cy = min(max(foco[1] * h, ch / 2), h - ch / 2)
    caja = (int(round(cx - cw / 2)), int(round(cy - ch / 2)), int(round(cx + cw / 2)), int(round(cy + ch / 2)))
    return im.crop(caja).resize(size, Image.LANCZOS)


def detectar(a):
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 2] > 225) & (hsv[..., 1] < 22)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = cv2.convexHull(max(cs, key=cv2.contourArea))
    ap = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True).reshape(-1, 2)
    if len(ap) != 4:
        ap = cv2.boxPoints(cv2.minAreaRect(c))
    s = ap.sum(axis=1); d = np.diff(ap, axis=1).ravel()
    return [tuple(ap[np.argmin(s)]), tuple(ap[np.argmin(d)]), tuple(ap[np.argmax(s)]), tuple(ap[np.argmax(d)])]


def montar(escena, quad, foto, foco=None):
    """Deforma la foto al cartel y le pone la luz de la escena."""
    a = np.asarray(Image.open(os.path.join(ESC, escena)).convert("RGB"))
    h, w = a.shape[:2]
    q = np.float32(quad if quad else detectar(a))
    ancho = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
    alto = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
    esc = 3.0                                    # la foto entra con resolucion de sobra
    fw, fh = int(ancho * esc), int(alto * esc)
    if foto.endswith(".png"):
        ph = Image.open(foto).convert("RGB")
        r = fw / fh
        if ph.width / ph.height > r:
            nw = int(ph.height * r); ph = ph.crop(((ph.width - nw) // 2, 0, (ph.width + nw) // 2, ph.height))
        else:
            ph = ph.crop((0, 0, ph.width, int(ph.width / r)))
        ph = np.asarray(ph.resize((fw, fh), Image.LANCZOS))
    elif foco:
        ph = np.asarray(recorte_foco(foto, (fw, fh), foco))
    else:
        ph = np.asarray(cargar_ok(foto, (fw, fh)))
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [fw, 0], [fw, fh], [0, fh]]), q)
    warp = cv2.warpPerspective(ph, M, (w, h), flags=cv2.INTER_AREA)
    mq = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(mq, q.astype(np.int32), 255)
    # lo que tapa el cartel (un farol, una persona) queda delante
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    claro = ((hsv[..., 2] > 170) & (hsv[..., 1] < 70)).astype(np.uint8) * 255
    claro = cv2.morphologyEx(claro, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.bitwise_and(mq, claro)
    m = cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32)[..., None] / 255.0
    lum = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    ref = float(np.percentile(lum[mq > 0], 75)) or 1.0
    luz = (lum / ref).clip(0.72, 1.04)[..., None]
    out = a.astype(np.float32) * (1 - m) + warp.astype(np.float32) * luz * m
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


# Martin, 28/10/2026: nunca una foto horizontal en un lienzo vertical. Una
# escena horizontal sale como posteo horizontal, en su proporción (1080 de
# ancho, entre 1,91:1 y 4:5, lo que acepta Instagram), a sangre, sin fondo ni
# franjas: el texto chico abajo, sobre un degradado suave.
RATIO_MAX = 1.91


def pieza_horizontal(im, lugar, frase):
    W = 1080
    r = min(im.width / im.height, RATIO_MAX)
    H = int(round(W / r))
    base = im.resize((W, int(round(im.height * W / im.width))), Image.LANCZOS)
    if base.height > H:
        base = base.crop((0, (base.height - H) // 2, W, (base.height - H) // 2 + H))
    lienzo = base.convert("RGB")
    m = 56
    d = ImageDraw.Draw(lienzo)
    px, ls, salto, alto = medir_titular(d, frase.upper(), W - 2 * m - 40, 46, max_lineas=2)
    y = H - m - alto - 40
    lienzo = velo_banda(lienzo, y - 30, H, objetivo=46, pluma=200, piso=0.30)
    d = ImageDraw.Draw(lienzo)
    escribir(d, (m, y), lugar.upper(), work(20, "SemiBold"), HUESO, 4)
    titular(d, frase, m, y + 34, W - 2 * m - 40, 46, HUESO, max_lineas=2)
    firma(d, W - m, y - 6, 0.8, True, "r")
    return lienzo


def pieza(im, lugar, frase):
    """Las escenas verticales, 4:5 a sangre con una franja de texto abajo; las
    horizontales, posteo horizontal (pieza_horizontal)."""
    W, H = POST
    if im.width > im.height:
        return pieza_horizontal(im, lugar, frase)
    if im.height >= im.width:
        base = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
        base = base.crop((0, (base.height - H) // 2, W, (base.height - H) // 2 + H))
        lienzo = base.convert("RGB")
        d = ImageDraw.Draw(lienzo)
        d.rectangle([0, H - 230, W, H], fill=CARBON)
        y = H - 200
    else:
        lienzo = Image.new("RGB", POST, CARBON)
        esc = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
        lienzo.paste(esc, (0, 0))
        d = ImageDraw.Draw(lienzo)
        y = esc.height + 70
    escribir(d, (76, y), lugar.upper(), work(24, "SemiBold"), ROJO, 5)
    titular(d, frase, 76, y + 40, W - 152, 74 if im.height >= im.width else 96, HUESO,
            max_lineas=2 if im.height >= im.width else 4)
    # la firma va en la linea del lugar, a la derecha, para no pisar el titular
    firma(d, W - 76 - 230, y - 6, 1.0, True)
    return lienzo


def main(desde=None):
    """Lo que ya salió no se toca (con --solo, solo esas piezas)."""
    os.makedirs(DEST, exist_ok=True)
    indice = []
    for k, (escena, quad, (cat, nombre), lugar, frase) in enumerate(ESCENAS, 1):
        slug = f"{k:02d}_" + os.path.splitext(escena)[0]
        indice.append({"n": k, "archivo": slug + ".jpg", "escena": escena,
                       "foto": f"{cat}/{nombre.partition('#')[0]}", "lugar": lugar, "frase": frase})
        if not se_puede_escribir(os.path.join(DEST, slug + ".jpg"), desde):
            continue
        im = montar(escena, quad, ruta_foto(cat, nombre), foco_de(nombre))
        im.save(os.path.join(DEST, slug + "_escena.jpg"), quality=90)
        pieza(im, lugar, frase).save(os.path.join(DEST, slug + ".jpg"), quality=90, optimize=True)
        print("  ", slug)
    guardar_cache()
    json.dump(indice, open(os.path.join(DEST, "indice.json"), "w"), ensure_ascii=False, indent=1)
    print(len(indice), "piezas")


if __name__ == "__main__":
    import sys
    main(opcion_desde(sys.argv))
