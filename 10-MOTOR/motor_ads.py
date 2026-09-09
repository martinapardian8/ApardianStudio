# -*- coding: utf-8 -*-
"""Motor de piezas publicitarias para APARDIAN STUDIO.

Compone avisos para pauta paga usando las fotos REALES de Martin
(las que ya estan publicadas en la galeria) con el sistema de marca:
Koulen para titulares, Work Sans para el resto, y solo tres colores.

No usa IA: la foto es de el, el diseno lo pone este archivo.
"""
import os, glob, random, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

S     = "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad"
IMG   = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/05-WEB/img"
KOULEN  = os.path.join(S, "fuentes", "Koulen-Regular.ttf")   # solo el logotipo
DISPLAY = os.path.join(S, "fuentes", "Anton-Regular.ttf")    # titulares
WORK   = os.path.join(S, "fuentes", "WorkSans.ttf")

HUESO = (248, 247, 246)
NEGRO = (23, 23, 23)
ROJO  = (255, 0, 51)
CARBON = (12, 11, 10)

POST  = (1080, 1350)   # 4:5 — el formato que mas pantalla ocupa en el feed
STORY = (1080, 1920)   # 9:16 — historias y reels

# margenes seguros de historias: arriba la foto de perfil, abajo el "deslizar"
SAFE_STORY_TOP, SAFE_STORY_BOT = 260, 340


# ---------------------------------------------------------------- tipografia
_cache = {}
def koulen(px):
    k = ("k", px)
    if k not in _cache: _cache[k] = ImageFont.truetype(KOULEN, px)
    return _cache[k]

def display(px):
    """Titulares. Koulen no tiene mayusculas acentuadas (ÁÉÍÓÚÑÜ salen como
    cuadrado vacio), asi que los titulares van en Anton, que tiene el mismo
    peso condensado y el español completo."""
    k = ("d", px)
    if k not in _cache: _cache[k] = ImageFont.truetype(DISPLAY, px)
    return _cache[k]


def work(px, peso="Regular"):
    k = ("w", px, peso)
    if k not in _cache:
        f = ImageFont.truetype(WORK, px)
        try: f.set_variation_by_name(peso)
        except Exception: pass
        _cache[k] = f
    return _cache[k]


def ancho(d, txt, fnt, track=0):
    if not txt: return 0
    w = d.textlength(txt, font=fnt)
    return int(w + track * max(0, len(txt) - 1))


def escribir(d, xy, txt, fnt, fill, track=0, anchor_x="l"):
    """Dibuja texto con letter-spacing opcional. anchor_x: l, c o r."""
    x, y = xy
    if anchor_x != "l":
        w = ancho(d, txt, fnt, track)
        x = x - w // 2 if anchor_x == "c" else x - w
    if track == 0:
        d.text((x, y), txt, font=fnt, fill=fill)
        return
    for ch in txt:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + track


def quebrar(d, txt, fnt, max_w, track=0):
    """Parte el texto en lineas que entren en max_w."""
    palabras, lineas, act = txt.split(), [], ""
    for p in palabras:
        prueba = (act + " " + p).strip()
        if ancho(d, prueba, fnt, track) <= max_w or not act:
            act = prueba
        else:
            lineas.append(act); act = p
    if act: lineas.append(act)
    return lineas


def _tinta_abajo(fnt, linea):
    """Hasta donde baja de verdad la tinta de una linea, medido desde y."""
    if not linea: return 0
    try:
        return fnt.getbbox(linea)[3]
    except Exception:
        return int(fnt.size * 1.05)


def medir_titular(d, txt, max_w, px, interlinea=0.88, track=0, max_lineas=4):
    """Devuelve (cuerpo_final, lineas, salto, alto_real) sin dibujar nada."""
    while px > 30:
        f = display(px)
        ls = quebrar(d, txt, f, max_w, track)
        if len(ls) <= max_lineas and all(ancho(d, l, f, track) <= max_w for l in ls):
            break
        px -= 4
    f = display(px)
    ls = quebrar(d, txt, f, max_w, track)
    salto = int(px * interlinea)
    alto = (len(ls) - 1) * salto + _tinta_abajo(f, ls[-1] if ls else "")
    return px, ls, salto, alto


def titular(d, txt, x, y, max_w, px, fill, interlinea=0.88, anchor_x="l", track=0,
            max_lineas=4, alto_max=None, mayus=True):
    """Titular de display. Se achica hasta entrar en el ancho y, si se pide, en el alto.
    Devuelve el alto real de la tinta, no una estimacion.
    Va en mayuscula porque asi es la marca; los testimonios pasan mayus=False."""
    if mayus: txt = txt.upper()
    px, ls, salto, alto = medir_titular(d, txt, max_w, px, interlinea, track, max_lineas)
    while alto_max and alto > alto_max and px > 30:
        px -= 4
        px, ls, salto, alto = medir_titular(d, txt, max_w, px, interlinea, track, max_lineas)
    f = display(px)
    for i, l in enumerate(ls):
        escribir(d, (x, y + i * salto), l, f, fill, track, anchor_x)
    return alto


def medir_parrafo(d, txt, max_w, px, peso="Regular", interlinea=1.34):
    f = work(px, peso)
    ls = quebrar(d, txt, f, max_w)
    salto = int(px * interlinea)
    alto = (len(ls) - 1) * salto + _tinta_abajo(f, ls[-1] if ls else "")
    return ls, salto, alto


def parrafo(d, txt, x, y, max_w, px, fill, peso="Regular", interlinea=1.34, anchor_x="l",
            alto_max=None):
    ls, salto, alto = medir_parrafo(d, txt, max_w, px, peso, interlinea)
    while alto_max and alto > alto_max and px > 20:
        px -= 2
        ls, salto, alto = medir_parrafo(d, txt, max_w, px, peso, interlinea)
    f = work(px, peso)
    for i, l in enumerate(ls):
        escribir(d, (x, y + i * salto), l, f, fill, 0, anchor_x)
    return alto


def numeral(d, txt, x, y, px, fill, anchor_x="l"):
    """Un numero enorme. Devuelve el alto real."""
    f = display(px)
    escribir(d, (x, y), txt, f, fill, 0, anchor_x)
    return _tinta_abajo(f, txt)


def comillas(d, x, y, px, fill):
    """Comilla de apertura. Koulen no la trae, asi que va en Work Sans."""
    f = work(px, "Bold")
    d.text((x, y), "\u201c", font=f, fill=fill)
    return _tinta_abajo(f, "\u201c")


# ---------------------------------------------------------------- foto
def cargar(ruta, size, foco=0.5):
    """Recorta la foto al tamano pedido SIN partir rostros.

    El parametro foco quedo por compatibilidad, pero ya no manda: el encuadre
    lo decide recorte.py mirando donde estan las caras y donde esta el detalle.
    """
    from recorte import cargar_ok
    return cargar_ok(ruta, size)


def velo(im, arriba=0.0, abajo=0.85, desde=0.35):
    """Degradado oscuro de arriba hacia abajo para que el texto se lea."""
    W, H = im.size
    cap = Image.new("L", (1, H), 0)
    px = cap.load()
    for y in range(H):
        t = y / max(1, H - 1)
        if t < desde:
            v = arriba * (t / max(1e-6, desde))
        else:
            v = arriba + (abajo - arriba) * ((t - desde) / max(1e-6, 1 - desde)) ** 1.5
        px[0, y] = int(255 * v)
    cap = cap.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), CARBON), im, cap)


def velo_plano(im, fuerza=0.55):
    return Image.blend(im, Image.new("RGB", im.size, CARBON), fuerza)


def aplanar(im):
    """Simula una foto SIN editar: gris, plana, con los negros levantados."""
    im = ImageEnhance.Color(im).enhance(0.42)
    im = ImageEnhance.Contrast(im).enhance(0.62)
    im = ImageEnhance.Brightness(im).enhance(1.06)
    base = Image.new("RGB", im.size, (128, 126, 122))
    return Image.blend(im, base, 0.16)


def realzar(im):
    im = ImageEnhance.Color(im).enhance(1.10)
    im = ImageEnhance.Contrast(im).enhance(1.14)
    return im


def bn(im):
    return ImageOps.grayscale(im).convert("RGB")


# ---------------------------------------------------------------- firma
def firma(d, x, y, escala=1.0, claro=True, anchor_x="l"):
    """El logotipo: APARDIAN + punto rojo."""
    px = int(30 * escala)
    f = koulen(px)
    col = HUESO if claro else NEGRO
    txt = "APARDIAN"
    tr = px * 0.04
    w = ancho(d, txt, f, tr)
    xx = x - w // 2 if anchor_x == "c" else (x - w - int(px * 0.42) if anchor_x == "r" else x)
    escribir(d, (xx, y), txt, f, col, tr)
    r = max(3, int(px * 0.10))
    cx = xx + w + int(px * 0.16)
    cy = y + int(px * 0.80)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO)


TELEFONO = "+598 91 962 962"

def cta_pastilla(d, x, y, texto, ancho_max=None, oscura=False, anchor_x="l",
                 tinta=None, telefono=False):
    """Llamada a la accion TIPOGRAFICA, no un boton.

    Un posteo de Instagram no se puede clickear, asi que dibujar una pastilla
    con forma de boton promete algo que no existe. Va una regla roja, la accion
    en mayuscula y el telefono debajo: se puede leer y copiar.
    """
    col = tinta if tinta is not None else (NEGRO if oscura else HUESO)
    px, tr = 30, 3.0
    f = work(px, "SemiBold")
    w = ancho(d, texto, f, tr)
    xx = x - w // 2 if anchor_x == "c" else (x - w if anchor_x == "r" else x)

    d.rectangle([xx, y, xx + max(112, min(w, 190)), y + 5], fill=ROJO)
    escribir(d, (xx, y + 26), texto, f, col, tr)
    alto = 26 + int(px * 1.15)
    if telefono:
        ft = work(27, "Regular")
        escribir(d, (xx, y + alto + 6), TELEFONO, ft,
                 (col[0]*3//5 + 60, col[1]*3//5 + 60, col[2]*3//5 + 60) if col == HUESO
                 else (110, 108, 106), 1.2)
        alto += 6 + 32
    return w, alto


def kicker(d, x, y, texto, color=ROJO, px=25, anchor_x="l"):
    escribir(d, (x, y), texto.upper(), work(px, "SemiBold"), color, px * 0.22, anchor_x)
    return int(px * 1.6)


def regla(d, x, y, w, color=ROJO, alto=5):
    d.rectangle([x, y, x + w, y + alto], fill=color)


# ---------------------------------------------------------------- catalogo de fotos
_POOL = None
def pool():
    """Todas las fotos publicadas, agrupadas por seccion y por forma."""
    global _POOL
    if _POOL is None:
        _POOL = {}
        for d in sorted(os.listdir(IMG)):
            w = os.path.join(IMG, d, "web")
            if not os.path.isdir(w): continue
            fs = sorted(glob.glob(os.path.join(w, "*.jpg")))
            if fs: _POOL[d] = fs
    return _POOL


def foto(cat, i=0, forma=None):
    """Elige una foto de la categoria. forma: 'alta', 'ancha' o None."""
    fs = pool().get(cat) or []
    if not fs:
        for k in ("retratos", "bodas", "gastronomia", "naturaleza"):
            if pool().get(k): fs = pool()[k]; break
    if forma:
        fil = []
        for f in fs:
            try:
                w, h = Image.open(f).size
            except Exception:
                continue
            r = w / h
            if forma == "alta" and r < 0.9: fil.append(f)
            elif forma == "ancha" and r > 1.1: fil.append(f)
        if fil: fs = fil
    return fs[i % len(fs)]


# ---------------------------------------------------------------- bloque de texto
def bloque(d, x, y_top, y_bot, max_w, c, tinta, acento,
           px_titular=110, px_sub=32, cta_oscura=False, anchor_x="l",
           con_regla=False, con_firma=True, firma_x=None, firma_clara=True,
           color_kicker=None, mayus=True):
    """Maqueta kicker + titular + (regla) + bajada + boton dentro de la caja dada.

    Mide todo primero y achica la tipografia hasta que entre de verdad.
    Nunca deja que dos cosas se pisen: ese era el error de la primera version.
    """
    GAP_K, GAP_T, GAP_R, GAP_S = 18, 26, 34, 30
    ALTO_CTA = 86
    disponible = y_bot - y_top

    px_t, px_s = px_titular, px_sub
    while True:
        alto = 0
        if c.get("kicker"): alto += int(25 * 1.05) + GAP_K
        _, _, _, h_t = medir_titular(d, c["titular"].upper() if mayus else c["titular"], max_w, px_t)
        alto += h_t + GAP_T
        if con_regla: alto += 5 + GAP_R
        h_s = 0
        if c.get("sub"):
            _, _, h_s = medir_parrafo(d, c["sub"], max_w, px_s)
            alto += h_s + GAP_S
        if c.get("cta"): alto += ALTO_CTA
        if alto <= disponible: break
        if px_t > 46:   px_t -= 4
        elif px_s > 24: px_s -= 2
        elif c.get("sub"): c = dict(c); c.pop("sub")   # la bajada es lo primero que se sacrifica
        else: break

    y = y_top
    if c.get("kicker"):
        kicker(d, x, y, c["kicker"], color_kicker or acento, 25, anchor_x)
        y += int(25 * 1.05) + GAP_K
    y += titular(d, c["titular"], x, y, max_w, px_t, tinta, anchor_x=anchor_x, mayus=mayus) + GAP_T
    if con_regla:
        rx = x - 66 if anchor_x == "c" else x
        regla(d, rx, y, 132, acento); y += 5 + GAP_R
    if c.get("sub"):
        y += parrafo(d, c["sub"], x, y, max_w, px_s, tinta if anchor_x == "c" else tinta,
                     anchor_x=anchor_x) + GAP_S
    if c.get("cta"):
        cta_pastilla(d, x, y, c["cta"], oscura=cta_oscura, anchor_x=anchor_x)
        if con_firma and firma_x is not None:
            firma(d, firma_x, y + 22, 1.0, firma_clara, "r")
        y += ALTO_CTA
    return y


# ---------------------------------------------------------------- velo que mide
def luminancia(im, caja):
    """Luminancia media (0-255) de una region de la foto."""
    x0, y0, x1, y1 = [int(v) for v in caja]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width, x1), min(im.height, y1)
    if x1 <= x0 or y1 <= y0: return 128.0
    r = im.crop((x0, y0, x1, y1)).convert("L").resize((24, 24), Image.BILINEAR)
    px = list(r.getdata())
    return sum(px) / len(px)


def _mezcla_necesaria(L, objetivo):
    """Cuanto hay que mezclar con carbon para que una banda de luminancia L
    baje al objetivo. Devuelve 0..0.92."""
    if L <= objetivo: return 0.0
    negro = 12.0
    return min(0.92, (L - objetivo) / max(1.0, L - negro))


def velo_banda(im, y0, y1, objetivo=56, pluma=180, piso=0.30):
    """Oscurece SOLO lo necesario para que el texto claro se lea sobre esa banda.

    Mide la foto de verdad. Una foto ya oscura casi no se toca; una clara se
    oscurece fuerte. `pluma` es el degradado de entrada, para que no se vea el corte.
    """
    W, H = im.size
    y0, y1 = int(max(0, y0)), int(min(H, y1))
    if y1 <= y0: return im
    f = max(piso, _mezcla_necesaria(luminancia(im, (0, y0, W, y1)), objetivo))

    cap = Image.new("L", (1, H), 0)
    px = cap.load()
    for y in range(H):
        if y < y0 - pluma:      v = 0.0
        elif y < y0:            v = f * ((y - (y0 - pluma)) / pluma) ** 1.6
        else:                   v = f
        px[0, y] = int(255 * v)
    return Image.composite(Image.new("RGB", (W, H), CARBON), im, cap.resize((W, H)))


def velo_caja(im, caja, objetivo=56, pluma=90, piso=0.28):
    """Como velo_banda pero para un rectangulo suelto (un numero, un kicker)."""
    W, H = im.size
    x0, y0, x1, y1 = [int(v) for v in caja]
    f = max(piso, _mezcla_necesaria(luminancia(im, caja), objetivo))
    cap = Image.new("L", (W, H), 0)
    ImageDraw.Draw(cap).rectangle([x0, y0, x1, y1], fill=int(255 * f))
    cap = cap.filter(ImageFilter.GaussianBlur(pluma / 2.2))
    return Image.composite(Image.new("RGB", (W, H), CARBON), im, cap)
