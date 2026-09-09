# -*- coding: utf-8 -*-
"""Versiones en video de las piezas de pauta.

Se anima **la pieza**, no la foto: la imagen solo hace un empuje lentisimo, como
en cualquier placa de television. Lo que se mueve es la tipografia, la regla roja
y el velo. Nada inventado dentro de la fotografia.

Todo se compone local con Pillow y se codifica con ffmpeg. No usa creditos.
"""
import os, subprocess, shutil, math
import imageio_ffmpeg
from PIL import Image, ImageDraw
from motor_ads import *
import recorte

FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/frames"
DEST = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/08-CONTENIDO-INSTAGRAM/05-videos"

FPS, SEG = 25, 6
NF = FPS * SEG


# ---------------------------------------------------------------- curvas
def suave(t):
    """Entrada y salida suaves. Nada arranca ni frena de golpe."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def tramo(f, ini, dur):
    """Progreso 0..1 de un elemento que entra en el frame `ini` y dura `dur`."""
    return suave((f - ini) / float(max(1, dur)))


def mezclar(base, capa, a):
    """Superpone `capa` sobre `base` con opacidad a (0..1)."""
    if a <= 0.001:
        return base
    if a >= 0.999:
        return capa
    return Image.blend(base, capa, a)


# ---------------------------------------------------------------- pieza
def frame(f, ruta, c, size, story):
    """Arma un fotograma. `f` es el numero de cuadro."""
    W, H = size
    m = 76
    top = SAFE_STORY_TOP if story else m
    bot = H - (SAFE_STORY_BOT if story else m)

    # --- foto: empuje lentisimo, del 6% al 0% de sobre-escala -------------
    z = 1.065 - 0.065 * suave(f / float(NF - 1))
    gw, gh = int(W * 1.07), int(H * 1.07)
    grande = cargar(ruta, (gw, gh))
    cw, ch = int(W * z / 1.07 * 1.07 / z * 1.0), 0   # placeholder, se calcula abajo
    vw, vh = int(gw / z), int(gh / z)
    x0, y0 = (gw - vw) // 2, (gh - vh) // 2
    im = grande.crop((x0, y0, x0 + vw, y0 + vh)).resize((W, H), Image.LANCZOS)

    # --- velo: entra en el primer medio segundo --------------------------
    y_bloque = bot - int(H * (0.50 if story else 0.54))
    a_velo = tramo(f, 0, int(FPS * 0.6))
    oscuro = velo_banda(im, y_bloque - 40, H, objetivo=48, pluma=240, piso=0.42)
    im = mezclar(im, oscuro, a_velo)

    d = ImageDraw.Draw(im)
    y = y_bloque

    # --- kicker: aparece deslizando desde abajo --------------------------
    a_k = tramo(f, int(FPS * 0.35), int(FPS * 0.45))
    if a_k > 0 and c.get("kicker"):
        dy = int((1 - a_k) * 26)
        capa = im.copy()
        dc = ImageDraw.Draw(capa)
        kicker(dc, m, y + dy, c["kicker"], HUESO)
        im = mezclar(im, capa, a_k); d = ImageDraw.Draw(im)
    y += 26 + 18

    # --- titular: entra linea por linea ----------------------------------
    px, lineas, salto, alto = medir_titular(d, c["titular"].upper(), W - 2*m,
                                            142 if story else 124)
    ini_t = int(FPS * 0.65)
    for i, ln in enumerate(lineas):
        a = tramo(f, ini_t + i * int(FPS * 0.16), int(FPS * 0.42))
        if a <= 0:
            continue
        dy = int((1 - a) * 34)
        capa = im.copy()
        dc = ImageDraw.Draw(capa)
        escribir(dc, (m, y + i * salto + dy), ln, display(px), HUESO)
        im = mezclar(im, capa, a)
    d = ImageDraw.Draw(im)
    y += alto + 26

    # --- regla roja: barre de izquierda a derecha -------------------------
    a_r = tramo(f, int(FPS * 1.5), int(FPS * 0.45))
    if a_r > 0:
        d.rectangle([m, y, m + int(132 * a_r), y + 5], fill=ROJO)
    y += 5 + 30

    # --- bajada ----------------------------------------------------------
    a_s = tramo(f, int(FPS * 1.85), int(FPS * 0.5))
    if a_s > 0 and c.get("sub"):
        capa = im.copy()
        dc = ImageDraw.Draw(capa)
        h = parrafo(dc, c["sub"], m, y + int((1 - a_s) * 18), W - 2*m - 60, 32,
                    (222, 220, 217))
        im = mezclar(im, capa, a_s); d = ImageDraw.Draw(im)
        _, _, h = medir_parrafo(d, c["sub"], W - 2*m - 60, 32)
        y += h + 30

    # --- llamada a la accion: texto, no boton -----------------------------
    a_c = tramo(f, int(FPS * 2.4), int(FPS * 0.5))
    if a_c > 0:
        capa = im.copy()
        dc = ImageDraw.Draw(capa)
        cta_pastilla(dc, m, y + int((1 - a_c) * 16), c["cta"])
        im = mezclar(im, capa, a_c); d = ImageDraw.Draw(im)

    # --- firma -----------------------------------------------------------
    a_f = tramo(f, int(FPS * 2.9), int(FPS * 0.5))
    if a_f > 0:
        capa = im.copy()
        firma(ImageDraw.Draw(capa), W - m, bot - 34, 1.0, True, "r")
        im = mezclar(im, capa, a_f)
    return im


def render(nombre, ruta, c, size, story):
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP, exist_ok=True)
    for f in range(NF):
        frame(f, ruta, c, size, story).save(
            os.path.join(TMP, f"{f:04d}.jpg"), "JPEG", quality=93)
    os.makedirs(DEST, exist_ok=True)
    salida = os.path.join(DEST, nombre + ".mp4")
    r = subprocess.run(
        [FF, "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "%04d.jpg"),
         "-c:v", "libx264", "-preset", "slow", "-crf", "19",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida],
        capture_output=True, text=True)
    if r.returncode != 0:
        print("  ffmpeg:", r.stderr[-300:])
        return None
    return salida
