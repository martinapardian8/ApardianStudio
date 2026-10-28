# -*- coding: utf-8 -*-
"""Motor de piezas publicitarias para APARDIAN STUDIO.

Compone avisos para pauta paga usando las fotos REALES de Martin
(las que ya estan publicadas en la galeria) con el sistema de marca:
Koulen para titulares, Work Sans para el resto, y solo tres colores.

No usa IA: la foto es de el, el diseno lo pone este archivo.
"""
import os, glob, random, hashlib, json, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

# rutas relativas al repositorio: funciona igual en la Mac y en cualquier copia
RAIZ  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S     = os.path.join(RAIZ, "10-MOTOR")
IMG   = os.path.join(RAIZ, "05-WEB", "img")
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
    """Se mantiene por compatibilidad: desde el 13/9/2026 todo va en Anton, como la web."""
    return display(px)

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


def medir_titular(d, txt, max_w, px, interlinea=1.0, track=0, max_lineas=4):
    """Devuelve (cuerpo_final, lineas, salto, alto_real) sin dibujar nada."""
    while px > 30:
        f = display(px)
        ls = quebrar(d, txt, f, max_w, track)
        if len(ls) <= max_lineas and all(ancho(d, l, f, track) <= max_w for l in ls):
            break
        px -= 4
    f = display(px)
    ls = quebrar(d, txt, f, max_w, track)
    # Anton: la mayúscula ocupa 0,88 del cuerpo, así que con menos de 1,0 de
    # interlineado las líneas se tocan; la tilde de la segunda (DÍA, ÓMNIBUS,
    # ASÍ) sube 0,23 más.
    if any(re.search("[ÁÉÍÓÚÑÜ]", l) for l in ls[1:]):
        interlinea = max(interlinea, 1.14)
    salto = int(px * interlinea)
    alto = (len(ls) - 1) * salto + _tinta_abajo(f, ls[-1] if ls else "")
    return px, ls, salto, alto


def titular(d, txt, x, y, max_w, px, fill, interlinea=1.0, anchor_x="l", track=0,
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
    f = display(px)   # el logotipo tambien en Anton, igual que en la web
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
           color_kicker=None, mayus=True, max_lineas=4):
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
        _, _, _, h_t = medir_titular(d, c["titular"].upper() if mayus else c["titular"], max_w, px_t, max_lineas=max_lineas)
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
    y += titular(d, c["titular"], x, y, max_w, px_t, tinta, anchor_x=anchor_x, mayus=mayus, max_lineas=max_lineas) + GAP_T
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
        elif y < y0:
            # entra suave y llega suave: sin un borde recto que parezca una
            # franja sobre la foto (Martin, 28/10/2026)
            t = (y - (y0 - pluma)) / pluma
            v = f * t * t * (3 - 2 * t)
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


# ---------------------------------------------------------------- foto primero
# Pedido de Martin (26/10/2026): en cada posteo e historia la protagonista es su
# fotografía, con la estética de la web. El texto va chico y abajo, y la foto
# no se recorta de más: si para llenar el cuadro hay que perder más de
# PERDIDA_MAX de la foto, se muestra entera, de lado a lado, sobre negro.
PERDIDA_MAX = 0.22


def perdida_recorte(ruta, size):
    """Qué parte de la foto se pierde si se la recorta para llenar `size`."""
    w, h = Image.open(ruta).size
    a, b = w / h, size[0] / size[1]
    return 1 - min(a, b) / max(a, b)


def _alto_bloque(size, c, max_w, px_titular, px_sub, max_lineas=4):
    prueba = Image.new("RGB", size)
    return bloque(ImageDraw.Draw(prueba), 0, 0, size[1], max_w, c, HUESO, ROJO,
                  px_titular=px_titular, px_sub=px_sub, con_firma=False, max_lineas=max_lineas)


def _detalle(im, y0, y1):
    """Cuánto pasa en una franja (bordes): el sujeto suele estar donde hay más.
    Un cielo o un fondo desenfocado da poco; una cara, un plato o un perro, mucho."""
    W, H = im.size
    y0, y1 = int(max(0, y0)), int(min(H, y1))
    if y1 - y0 < 8: return 1e9
    r = im.crop((0, y0, W, y1)).convert("L").resize((120, max(8, (y1 - y0) * 120 // W)), Image.BILINEAR)
    e = list(r.filter(ImageFilter.FIND_EDGES).getdata())
    return sum(e) / len(e)


def _caras_en_cuadro(ruta, size):
    """Las caras de la foto en coordenadas del cuadro, con el mismo recorte que
    hace cargar() (recorte.cargar_ok)."""
    from recorte import caras, caja_recorte
    W, H = size
    sw, sh = Image.open(ruta).size
    if sw / sh > W / H:
        ch = sh; cw = int(round(ch * W / H))
    else:
        cw = sw; ch = int(round(cw * H / W))
    cw, ch = min(cw, sw), min(ch, sh)
    x0, y0 = caja_recorte(ruta, sw, sh, cw, ch)
    x0 = max(0, min(sw - cw, x0)); y0 = max(0, min(sh - ch, y0))
    k = W / cw
    return [((fx - x0) * k, (fy - y0) * k, (fx + fw - x0) * k, (fy + fh - y0) * k)
            for (fx, fy, fw, fh, conf) in caras(ruta) if conf >= 0.6]


def _pisa_cara(caras_c, y0, y1):
    """Cuánto de las caras cae en la franja y0..y1 (0 = ninguna)."""
    t = 0.0
    for (_, cy0, _, cy1) in caras_c:
        ov = max(0.0, min(cy1, y1) - max(cy0, y0)) / max(1.0, cy1 - cy0)
        t += ov
    return t


def pieza_foto(ruta, size, story, c, extra_abajo=0):
    """La foto de Martin como protagonista y el texto al pie.

    c: kicker, titular, sub, cta (y numero, que va adelante del kicker).
    extra_abajo: alto reservado debajo del texto (las opciones de una pregunta).
    Devuelve (imagen, y donde termina el texto).

    En un lienzo vertical solo entra una foto vertical que lo llene (Martin,
    28/10/2026): si `ruta` no sirve, se cambia por otra vertical del mismo tema
    (vertical()); si no hay ninguna, ValueError. La foto usada queda en
    imagen.info["foto"]."""
    W, H = size
    if lienzo_vertical(size) and not apta(ruta, size):
        nueva = vertical(ruta, size)
        if nueva is None:
            raise ValueError("no hay una foto vertical de Martin del mismo tema que "
                             + _clave(ruta) + " para un lienzo %dx%d" % size)
        ruta = nueva
    m = 76
    top = SAFE_STORY_TOP if story else m
    bot = H - (SAFE_STORY_BOT if story else m) - extra_abajo
    c = dict(c)
    if c.get("numero"):
        c["kicker"] = (str(c.pop("numero")) + " · " + c.get("kicker", "")).strip(" ·")
    # Estética del IG de Martin (28/10/2026): el titular en dos líneas como
    # máximo, chico, y donde no tape el motivo.
    px_t, px_s = (64, 28) if story else (56, 26)
    max_w = W - 2 * m
    alto = _alto_bloque(size, c, max_w, px_t, px_s, max_lineas=2)

    if perdida_recorte(ruta, size) <= PERDIDA_MAX:
        # a sangre: la foto llena el cuadro y solo se oscurece detrás del texto.
        # El texto va arriba o abajo, donde la foto está más tranquila (cielo,
        # fondo desenfocado): así no tapa la cara, el plato ni el producto.
        im = cargar(ruta, size)
        # el texto no tapa una cara (APRENDIZAJES: ni la cara ni el motivo)
        cs = _caras_en_cuadro(ruta, size)
        p_arr = _detalle(im, top, top + alto + 40) + 1000 * _pisa_cara(cs, top - 40, top + alto + 80)
        p_aba = _detalle(im, bot - alto - 40, bot) + 1000 * _pisa_cara(cs, bot - alto - 80, H)
        arriba = not extra_abajo and p_arr < 0.75 * p_aba
        if arriba:
            y0 = top
            im = ImageOps.flip(velo_banda(ImageOps.flip(im), H - (y0 + alto + 40), H,
                                          objetivo=46, pluma=320, piso=0.30))
        else:
            y0 = bot - alto
            im = velo_banda(im, y0 - 40, H, objetivo=46, pluma=320, piso=0.30)
    else:
        # solo en lienzos horizontales o cuadrados (en los verticales la foto
        # siempre llena el cuadro, ver arriba).
        # entera: de lado a lado (o de arriba abajo), sin recortar nada
        # se recorta como mucho PERDIDA_MAX (con el encuadre que cuida rostros
        # y sujeto) para que la foto ocupe más, y el resto se muestra entero
        # de fondo, la misma foto llenando el cuadro, desenfocada y oscura:
        # nada de franjas negras vacías (Martin, 26 y 28/10/2026)
        im = ImageEnhance.Brightness(cargar(ruta, size).filter(ImageFilter.GaussianBlur(48))).enhance(0.38)
        w0, h0 = Image.open(ruta).size
        ar = w0 / h0
        ar2 = ar * (1 - PERDIDA_MAX) if ar > W / H else ar / (1 - PERDIDA_MAX)
        hueco = bot - alto - 56 - (0 if not story else 40)
        fw = W if ar2 >= W / max(1, hueco) else int(hueco * ar2)
        fh = int(fw / ar2)
        if fh > hueco:
            fh = hueco; fw = int(fh * ar2)
        f = cargar(ruta, (fw, fh))
        # foto y texto juntos, como una lámina, centrados en el cuadro
        total = fh + 56 + alto
        yf = max(0, min((H - total) // 2, bot - total))
        im.paste(f, ((W - fw) // 2, yf))
        y0 = yf + fh + 56
    d = ImageDraw.Draw(im)
    fin = bloque(d, m, y0, H, max_w, c, HUESO, ROJO, px_titular=px_t, px_sub=px_s,
                 firma_x=W - m, color_kicker=ROJO if perdida_recorte(ruta, size) > PERDIDA_MAX else HUESO,
                 max_lineas=2)
    if not c.get("cta"):
        firma(d, W - m, y0 - 6 if c.get("kicker") else y0 - 46, 0.9, True, "r")
    im.info["foto"] = ruta
    return im, fin


# ---------------------------------------------------------------- lo que se sabe de cada foto
_FOTOS = None
def ficha(ruta):
    """{lugar, confirmado, contenido} de una foto (fotos.json). Vacío si no se sabe."""
    global _FOTOS
    if _FOTOS is None:
        _FOTOS = json.load(open(os.path.join(S, "fotos.json"), encoding="utf-8"))["fotos"]
    partes = ruta.replace("\\", "/").split("/")
    return _FOTOS.get(partes[-3] + "/" + partes[-1], {}) if len(partes) >= 3 else {}


# Comida: cuando la pieza habla de carta, platos o comida, la foto tiene que
# mostrar comida (Martin, 24/10/2026: "si hablamos de una carta, la foto en vez
# de un kamado debería ser comida").
COMIDA = ("plato", "preparacion")


def foto_de(cat, i=0, contenido=None):
    """Como foto(), pero solo entre las que muestran `contenido` (fotos.json)."""
    fs = pool().get(cat) or []
    if contenido:
        ok = [f for f in fs if ficha(f).get("contenido") in contenido]
        if ok:
            return ok[i % len(ok)]
    return foto(cat, i)


# ---------------------------------------------------------------- solo fotos verticales
# Martin, 28/10/2026: "No me gusta que pongas una foto horizontal en un canva
# vertical". En un lienzo vertical (posteo o carrusel 4:5, historia o reel
# 9:16) va solo una foto vertical (alto > ancho) que lo llene de lado a lado,
# con un recorte que pierda PERDIDA_MAX como mucho y que no parta caras
# (recorte.py, caras.json, fotos_que_cortan.json). Nada de foto chica sobre la
# misma foto desenfocada, ni franjas, ni marcos. Si la foto elegida no sirve,
# se cambia por otra vertical de Martin de la misma carpeta (el mismo tema) y
# con el mismo 'contenido' de fotos.json. Nunca se inventa una foto.
def lienzo_vertical(size):
    return size[1] > size[0]


def _clave(ruta):
    """'<carpeta>/web/<archivo>': la misma foto en la Mac y en cualquier copia."""
    return "/".join(ruta.replace("\\", "/").split("/")[-3:])


_VETO = None
def _vetada(ruta, size):
    """La foto está en fotos_que_cortan.json para ese formato (parte una cara)."""
    global _VETO
    if _VETO is None:
        p = os.path.join(S, "fotos_que_cortan.json")
        d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        _VETO = {k: {_clave(x) for x in v} for k, v in d.items()}
    clave = "4:5" if size[1] / size[0] < 1.5 else "9:16"
    return _clave(ruta) in _VETO.get(clave, set())


_APTA = {}
def apta(ruta, size):
    """¿La foto llena este lienzo vertical como pide Martin? (vertical, recorte
    de PERDIDA_MAX como mucho y sin partir caras)."""
    k = (_clave(ruta), tuple(size))
    if k not in _APTA:
        w, h = Image.open(ruta).size
        ok = h > w and perdida_recorte(ruta, size) <= PERDIDA_MAX and not _vetada(ruta, size)
        if ok:
            from recorte import hay_cara_cortada
            ok = not hay_cara_cortada(ruta, size)
        _APTA[k] = ok
    return _APTA[k]


def apta_en(ruta, sizes):
    return all(apta(ruta, s) for s in sizes if lienzo_vertical(s))


def _huella(ruta):
    """Hash perceptual de la foto (similitud.phash): igual en las dos carpetas."""
    import similitud as SIM
    return SIM.phash(ruta) if os.path.exists(ruta) else ruta


def misma_foto(a, b, umbral=10):
    """¿Son la misma foto (o dos tomas casi iguales), aunque cambie el nombre?"""
    import similitud as SIM
    if _clave(a) == _clave(b) or os.path.basename(a) == os.path.basename(b):
        return True
    if not (os.path.exists(a) and os.path.exists(b)):
        return False
    return SIM.distancia(SIM.phash(a), SIM.phash(b)) < umbral


def _parecido(a, b):
    """Cuánto se parecen dos fotos en lo que cuentan: misma gente (retrato,
    grupo, nadie), misma luz, mismo color, misma sesión."""
    import similitud as SIM
    pa, pb = SIM.perfil(a), SIM.perfil(b)
    return 3 * (pa[0] == pb[0]) + (pa[1] == pb[1]) + (pa[2] == pb[2]) + 0.5 * (pa[3] == pb[3])


def vertical(ruta, sizes, excluir=(), contenido=None, evitar=()):
    """La foto si llena el lienzo; si no, otra vertical de Martin del mismo tema.

    sizes: un tamaño o una lista (la misma foto va en posteo e historia).
    excluir: fotos que no se pueden usar (ya salen esos días).
    contenido: 'contenido' que tiene que mostrar la foto (fotos.json); si no
    se pasa, el de la foto original.
    evitar: fotos que ya salen esas semanas (con repetición): entre dos que
    sirven igual, gana la que menos se vio. Devuelve None si no hay ninguna."""
    sizes = [sizes] if isinstance(sizes[0], int) else list(sizes)
    fuera = {_clave(x) for x in excluir}
    def afuera(f):
        # la misma foto puede estar en dos carpetas, o casi igual con otro
        # nombre (dos tomas seguidas): se compara lo que muestra, no el nombre
        return _clave(f) in fuera or any(misma_foto(f, x) for x in excluir)
    if apta_en(ruta, sizes) and not afuera(ruta):
        return ruta
    fi = ficha(ruta)
    que = contenido or ((fi["contenido"],) if fi.get("contenido") else None)
    cat = _clave(ruta).split("/")[0]
    cands = [f for f in pool().get(cat, [])
             if not afuera(f) and _clave(f) != _clave(ruta)
             and (not que or ficha(f).get("contenido") in que) and apta_en(f, sizes)]
    if not cands:
        return None
    # las de menos de 1000 px de ancho se ven blandas a 1080: solo si no hay otra
    nitidas = [f for f in cands if Image.open(f).size[0] >= 1000]
    cands = nitidas or cands
    lugar = fi.get("lugar") if fi.get("confirmado") else None
    vistas = {}
    for x in evitar:
        vistas[_huella(x)] = vistas.get(_huella(x), 0) + 1

    def puntaje(f):
        g = ficha(f)
        mismo_lugar = 4 if lugar and g.get("confirmado") and g.get("lugar") == lugar else 0
        azar = int(hashlib.md5((_clave(ruta) + _clave(f)).encode()).hexdigest()[:6], 16) / 16 ** 6
        return mismo_lugar + _parecido(ruta, f) + azar - 2.5 * vistas.get(_huella(f), 0)
    return max(cands, key=puntaje)


# ---------------------------------------------------------------- el calendario (solo lectura)
CALENDARIO_CSV = os.path.join(RAIZ, "11-AUTOMATIZACION", "calendario_instagram.csv")
IG_DIR = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
_CAL = None
def fechas_calendario():
    """{archivo relativo a 08-CONTENIDO-INSTAGRAM: primera fecha en que sale}."""
    global _CAL
    if _CAL is None:
        import csv
        _CAL = {}
        if os.path.exists(CALENDARIO_CSV):
            for f in csv.DictReader(open(CALENDARIO_CSV, encoding="utf-8")):
                for a in (f.get("archivos") or "").split("|"):
                    if a and (a not in _CAL or f["fecha"] < _CAL[a]):
                        _CAL[a] = f["fecha"]
    return _CAL


SOLO = set()      # --solo: rehacer solo estas piezas (rutas relativas a 08-CONTENIDO-INSTAGRAM)


def se_puede_escribir(ruta, desde=None):
    """Lo que ya salió no se toca. Con `desde` (AAAA-MM-DD), solo se escriben
    las piezas del calendario que salen ese día o después. Con --solo, solo
    las piezas nombradas (aunque salgan antes: las pide Martin a mano)."""
    import datetime as _dt
    rel = os.path.relpath(ruta, IG_DIR).replace("\\", "/")
    if SOLO:
        return rel in SOLO
    f = fechas_calendario().get(rel)
    if desde:
        return f is not None and f >= desde
    return f is None or f >= _dt.date.today().isoformat()


def opcion_desde(argv):
    """--desde AAAA-MM-DD de la línea de comandos (o None). Lee también
    --solo pieza1,pieza2 (rutas relativas a 08-CONTENIDO-INSTAGRAM)."""
    if "--solo" in argv:
        SOLO.update(a.strip() for a in argv[argv.index("--solo") + 1].split(",") if a.strip())
    return argv[argv.index("--desde") + 1] if "--desde" in argv else None


_USO = None
def _fotos_por_pieza():
    """{archivo del calendario: [fotos de Martin que muestra]}, de los índices."""
    global _USO
    if _USO is None:
        _USO = {}
        def j(nombre):
            p = os.path.join(IG_DIR, nombre)
            return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
        for x in j("indice_historias.json"):
            _USO["04-historias-organicas/" + x["archivo"]] = [os.path.join(RAIZ, x["foto"])]
        pauta = {}
        for x in j("indice_pauta.json"):
            pauta[x["n"]] = os.path.join(RAIZ, x["foto"])
            for c in ("01-posteos-pauta/", "02-historias-pauta/"):
                _USO[c + x["archivo"]] = [pauta[x["n"]]]
        for x in j("indice_videos.json"):
            if x.get("foto"):
                _USO["05-videos/" + x["archivo"]] = [os.path.join(RAIZ, x["foto"])]
            elif x["n"] in pauta:
                _USO["05-videos/" + x["archivo"]] = [pauta[x["n"]]]
        for x in j(os.path.join("08-tus-fotos-en-el-mundo", "indice.json")):
            if "/" in x.get("foto", ""):
                cat, nom = x["foto"].split("/")
                _USO["08-tus-fotos-en-el-mundo/" + x["archivo"]] = [os.path.join(IMG, cat, "web", nom)]
        for x in j(os.path.join("10-fotos", "indice.json")):
            cat, nom = x["foto"].split("/")
            _USO["10-fotos/" + x["archivo"]] = [os.path.join(IMG, cat, "web", nom)]
        try:
            import carruseles_fotos as CF
            for slug, c in CF.CARRUSELES.items():
                for i, f in enumerate(c["fotos"]):
                    _USO[f"06-carruseles-collage/{slug}/{i + 1:02d}.jpg"] = [f.partition("#")[0]]
                _USO[f"07-reels-collage/{slug}.mp4"] = [f.partition("#")[0] for f in
                                                        (CF.fotos_reel(slug) or c["fotos"])]
                _USO[f"07-reels-collage/{slug}_portada.jpg"] = _USO[f"07-reels-collage/{slug}.mp4"][:1]
        except Exception:
            pass
    return _USO


def registrar(ruta_pieza, fotos):
    """Anota qué fotos muestra una pieza recién hecha (para las que siguen)."""
    rel = os.path.relpath(ruta_pieza, IG_DIR).replace("\\", "/")
    _fotos_por_pieza()[rel] = list(fotos)


def usos_cerca(ruta_pieza, dias=3):
    """[fotos] que salen en otras piezas a menos de `dias` días de esta (una
    vez por pieza que la usa)."""
    import datetime as _dt
    rel = os.path.relpath(ruta_pieza, IG_DIR).replace("\\", "/")
    cal = fechas_calendario()
    if rel not in cal:
        return []
    hoy = _dt.date.fromisoformat(cal[rel])
    out = []
    for a, fs in _fotos_por_pieza().items():
        if a == rel or a not in cal:
            continue
        if abs((_dt.date.fromisoformat(cal[a]) - hoy).days) < dias:
            out += fs
    return out


def fotos_cerca(ruta_pieza, dias=3):
    """Fotos que salen en otras piezas a menos de `dias` días de esta: la
    misma foto no sale dos veces en menos de 3 días (Lupa lo frena)."""
    return set(usos_cerca(ruta_pieza, dias))
