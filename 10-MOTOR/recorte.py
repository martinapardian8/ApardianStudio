# -*- coding: utf-8 -*-
"""Recorte que no corta caras.

El recorte anterior tomaba siempre el centro de la foto. Eso parte rostros por
la mitad y descarta al sujeto. Este mira donde estan las caras y donde esta el
detalle de la imagen, y elige el encuadre que mejor puntua.
"""
import os, json, hashlib
import cv2
import numpy as np
from PIL import Image

MOD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos", "yunet.onnx")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caras.json")

_det = None
_cache = None


def _detector():
    global _det
    if _det is None:
        _det = cv2.FaceDetectorYN.create(MOD, "", (320, 320), 0.50, 0.3, 5000)
    return _det


def _leer_cache():
    global _cache
    if _cache is None:
        _cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    return _cache


def guardar_cache():
    if _cache is not None:
        json.dump(_cache, open(CACHE, "w"))


def caras(ruta):
    """[(x, y, w, h, confianza)] en coordenadas de la foto original."""
    c = _leer_cache()
    k = ruta
    if k in c:
        return [tuple(f) for f in c[k]]
    im = cv2.imread(ruta)
    if im is None:
        c[k] = []; return []
    h, w = im.shape[:2]
    esc = min(1.0, 1600.0 / max(h, w))
    ch = cv2.resize(im, (max(1, int(w*esc)), max(1, int(h*esc))))
    d = _detector()
    d.setInputSize((ch.shape[1], ch.shape[0]))
    try:
        _, res = d.detect(ch)
    except Exception:
        res = None
    out = []
    if res is not None:
        for f in res:
            out.append((float(f[0]/esc), float(f[1]/esc),
                        float(f[2]/esc), float(f[3]/esc), float(f[14])))
    c[k] = out
    return out


def _energia(ruta, eje, n):
    """Perfil de detalle (bordes) por fila o por columna. Sirve cuando no hay caras."""
    im = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
    if im is None:
        return np.ones(n)
    im = cv2.resize(im, (240, 240))
    g = np.abs(cv2.Laplacian(im, cv2.CV_32F))
    perfil = g.sum(axis=1 if eje == "y" else 0)
    perfil = np.interp(np.linspace(0, len(perfil)-1, n),
                       np.arange(len(perfil)), perfil)
    s = perfil.sum()
    return perfil / s if s > 0 else np.ones(n) / n


def caja_recorte(ruta, ancho_src, alto_src, cw, ch):
    """Devuelve (x0, y0) del recorte de cw x ch dentro de la foto.

    Puntua cada posicion: cortar una cara resta mucho, incluirla entera suma,
    y a igualdad de condiciones gana el encuadre con mas detalle y con la linea
    de los ojos cerca del tercio superior.
    """
    libre_x, libre_y = ancho_src - cw, alto_src - ch
    if libre_x <= 0 and libre_y <= 0:
        return 0, 0
    eje = "x" if libre_x > libre_y else "y"
    libre = max(libre_x, libre_y)
    pasos = min(60, max(12, libre // 8))
    cands = [int(round(libre * k / pasos)) for k in range(pasos + 1)]

    fs = caras(ruta)
    area_foto = float(ancho_src * alto_src)
    ener = _energia(ruta, eje, 200)

    mejor, mejor_p = cands[0], -1e18
    for off in cands:
        x0 = off if eje == "x" else max(0, libre_x // 2)
        y0 = off if eje == "y" else max(0, libre_y // 2)
        x1, y1 = x0 + cw, y0 + ch
        p = 0.0

        for (fx, fy, fw, fh, conf) in fs:
            # Una persona es el sujeto de la escena aunque ocupe poco cuadro.
            # Antes el peso era proporcional al area y una pareja a lo lejos
            # pesaba sesenta veces menos que la textura del fondo: ganaba la arena.
            peso = max(0.55, (fw * fh) / area_foto * 45.0) * conf
            fcx, fcy = fx + fw/2.0, fy + fh/2.0
            ojos_y = fy + fh * 0.42

            # la cara cruda cruza el borde del recorte?
            cortada = not (fx >= x1 or fx + fw <= x0 or fy >= y1 or fy + fh <= y0) and \
                      not (fx >= x0 and fy >= y0 and fx + fw <= x1 and fy + fh <= y1)
            if cortada:
                p -= peso * 320          # partir un rostro es el peor error posible
                continue
            dentro = fx >= x0 and fy >= y0 and fx + fw <= x1 and fy + fh <= y1
            if not dentro:
                continue                  # la cara quedo afuera del cuadro: ni suma ni resta
            p += peso * 70

            # --- aire sobre la cabeza -------------------------------------
            # sin aire arriba la foto se siente apretada aunque la cara entre entera
            aire = (fy - y0) / max(1.0, fh)
            if aire < 0.35:   p -= peso * 150 * (0.35 - aire) / 0.35
            elif aire > 2.2:  p -= peso * 40 * min(1.0, (aire - 2.2) / 2.0)

            # --- margen a los bordes laterales ----------------------------
            m_izq = (fx - x0) / float(cw)
            m_der = (x1 - (fx + fw)) / float(cw)
            m_min = min(m_izq, m_der)
            if m_min < 0.04: p -= peso * 120 * (0.04 - m_min) / 0.04

            # --- cuerpo cortado -------------------------------------------
            # si el cuadro termina justo debajo del menton, corta el cuello:
            # es el recorte que mas incomoda al mirar
            bajo = (y1 - (fy + fh)) / max(1.0, fh)
            if bajo < 0.6:   p -= peso * 130 * (0.6 - bajo) / 0.6
            elif bajo < 1.6: p -= peso * 35 * (1.6 - bajo) / 1.0

            # --- regla de los tercios --------------------------------------
            ty = (ojos_y - y0) / float(ch)
            p += peso * 34 * max(0.0, 1.0 - abs(ty - 0.36) / 0.34)
            tx = (fcx - x0) / float(cw)
            cerca = min(abs(tx - 0.33), abs(tx - 0.5), abs(tx - 0.67))
            p += peso * 16 * max(0.0, 1.0 - cerca / 0.18)

        # --- las personas, como grupo, tienen que quedar bien ubicadas ----
        if fs:
            vis = [f for f in fs if f[4] >= 0.6]
            if vis:
                gx = sum(f[0] + f[2]/2.0 for f in vis) / len(vis)
                gy = sum(f[1] + f[3]*0.42 for f in vis) / len(vis)
                if x0 <= gx <= x1 and y0 <= gy <= y1:
                    rx = (gx - x0) / float(cw)
                    ry = (gy - y0) / float(ch)
                    # cerca del centro o de un tercio, nunca pegado a un borde
                    p += 55 * max(0.0, 1.0 - min(abs(rx-0.5), abs(rx-0.33), abs(rx-0.67)) / 0.22)
                    p += 30 * max(0.0, 1.0 - abs(ry - 0.42) / 0.34)
                    if rx < 0.16 or rx > 0.84: p -= 120   # sujeto contra el borde
                else:
                    p -= 90       # el grupo quedo fuera del cuadro

        # detalle contenido
        a = int(off / max(1, libre) * 199)
        b = int(min(199, (off + (cw if eje == "x" else ch)) / max(1, ancho_src if eje == "x" else alto_src) * 199))
        p += float(ener[a:max(a+1, b)].sum()) * 2.2

        # sin caras, un leve sesgo hacia arriba: el cielo aburre menos que el piso
        if not fs and eje == "y":
            p += (1.0 - off / max(1, libre)) * 0.6

        if p > mejor_p:
            mejor_p, mejor = p, off

    if eje == "x":
        return mejor, max(0, libre_y // 2)
    return max(0, libre_x // 2), mejor


def cargar_ok(ruta, size):
    """Abre la foto y la recorta al tamaño pedido sin partir rostros."""
    im = Image.open(ruta).convert("RGB")
    W, H = size
    sw, sh = im.size
    r_dest, r_src = W / float(H), sw / float(sh)
    if r_src > r_dest:                 # sobra ancho
        ch = sh; cw = int(round(ch * r_dest))
    else:                              # sobra alto
        cw = sw; ch = int(round(cw / r_dest))
    cw, ch = min(cw, sw), min(ch, sh)
    x0, y0 = caja_recorte(ruta, sw, sh, cw, ch)
    x0 = max(0, min(sw - cw, x0)); y0 = max(0, min(sh - ch, y0))
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)


def hay_cara_cortada(ruta, size):
    """Control de calidad: ¿este encuadre parte algun rostro?"""
    im = Image.open(ruta); sw, sh = im.size
    W, H = size
    r_dest, r_src = W / float(H), sw / float(sh)
    if r_src > r_dest: ch = sh; cw = int(round(ch * r_dest))
    else:              cw = sw; ch = int(round(cw / r_dest))
    cw, ch = min(cw, sw), min(ch, sh)
    x0, y0 = caja_recorte(ruta, sw, sh, cw, ch)
    x1, y1 = x0 + cw, y0 + ch
    for (fx, fy, fw, fh, conf) in caras(ruta):
        if conf < 0.7 or fw * fh < (sw * sh) * 0.0016:
            continue
        toca = not (fx >= x1 or fx + fw <= x0 or fy >= y1 or fy + fh <= y0)
        entera = fx >= x0 and fy >= y0 and fx + fw <= x1 and fy + fh <= y1
        if toca and not entera:
            return True
    return False


def revisar(ruta, size):
    """Control de calidad de un encuadre. Devuelve la lista de problemas."""
    from PIL import Image as _I
    im = _I.open(ruta); sw, sh = im.size
    W, H = size
    rd, rs = W / float(H), sw / float(sh)
    if rs > rd: ch = sh; cw = int(round(ch * rd))
    else:       cw = sw; ch = int(round(cw / rd))
    cw, ch = min(cw, sw), min(ch, sh)
    x0, y0 = caja_recorte(ruta, sw, sh, cw, ch)
    x0 = max(0, min(sw - cw, x0)); y0 = max(0, min(sh - ch, y0))
    x1, y1 = x0 + cw, y0 + ch

    fs = [f for f in caras(ruta) if f[4] >= 0.65]
    mal = []
    if not fs:
        return mal

    dentro = []
    for (fx, fy, fw, fh, conf) in fs:
        toca = not (fx >= x1 or fx + fw <= x0 or fy >= y1 or fy + fh <= y0)
        entera = fx >= x0 and fy >= y0 and fx + fw <= x1 and fy + fh <= y1
        if toca and not entera:
            mal.append("rostro cortado")
        elif entera:
            dentro.append((fx, fy, fw, fh, conf))
            if (fy - y0) / max(1.0, fh) < 0.28:
                mal.append("sin aire sobre la cabeza")

    if dentro:
        gx = sum(f[0] + f[2]/2.0 for f in dentro) / len(dentro)
        rx = (gx - x0) / float(cw)
        if rx < 0.15 or rx > 0.85:
            mal.append("sujeto contra el borde")
    elif fs:
        mal.append("las personas quedaron fuera del cuadro")
    return sorted(set(mal))
