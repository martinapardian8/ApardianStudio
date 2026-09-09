# -*- coding: utf-8 -*-
"""Plantillas de aviso para pauta paga.

Cada una recibe la foto real de Martin y el texto, y devuelve la pieza armada.
Todas funcionan en 4:5 (posteo) y en 9:16 (historia). En historia respetan los
margenes seguros para que la interfaz de Instagram no tape nada.

Regla de oro: primero se mide, despues se dibuja. Nada se pisa.
"""
from PIL import Image, ImageDraw
from motor_ads import *

M = 76   # margen lateral


def _caja(size, story):
    """Devuelve (W, H, margen, tope_util, piso_util)."""
    W, H = size
    return W, H, M, (SAFE_STORY_TOP if story else M), H - (SAFE_STORY_BOT if story else M)


# ---------------------------------------------------------------- 1
def barra_inferior(size, story, ruta, c):
    """Foto a sangre + barra oscura abajo. El caballito de batalla."""
    W, H, m, top, bot = _caja(size, story)
    im = velo(cargar(ruta, size, foco=0.42), 0.06, 0.38, 0.55)
    d = ImageDraw.Draw(im)

    y0 = bot - int(H * (0.40 if story else 0.44))
    d.rectangle([0, y0, W, H], fill=CARBON)
    bloque(d, m, y0 + 52, bot - 20, W - 2*m, c, HUESO, ROJO,
           px_titular=112 if story else 100, firma_x=W - m)
    return im


# ---------------------------------------------------------------- 2
def titular_sobre_foto(size, story, ruta, c):
    """Titular enorme sobre la foto oscurecida. El que mas corta el scroll."""
    W, H, m, top, bot = _caja(size, story)
    im = cargar(ruta, size, foco=0.4)
    y0 = bot - int(H * (0.50 if story else 0.54))
    im = velo_banda(im, y0 - 40, H, objetivo=48, pluma=240, piso=0.42)
    d = ImageDraw.Draw(im)
    bloque(d, m, y0, bot - 20, W - 2*m, c, HUESO, ROJO,
           px_titular=142 if story else 124, con_regla=True, firma_x=W - m,
           color_kicker=HUESO)
    return im


# ---------------------------------------------------------------- 3
def mitad_color(size, story, ruta, c):
    """Foto arriba, bloque de color abajo. Maxima legibilidad del texto."""
    W, H, m, top, bot = _caja(size, story)
    corte = int(H * (0.52 if story else 0.54))
    im = Image.new("RGB", size, HUESO)
    im.paste(cargar(ruta, (W, corte), foco=0.45), (0, 0))
    d = ImageDraw.Draw(im)

    fondo = c.get("fondo", "hueso")
    col = {"hueso": HUESO, "negro": CARBON, "rojo": ROJO}[fondo]
    d.rectangle([0, corte, W, H], fill=col)
    tinta  = NEGRO if fondo == "hueso" else HUESO
    acento = ROJO if fondo == "hueso" else HUESO

    bloque(d, m, corte + 54, bot - 16, W - 2*m, c, tinta, acento,
           px_titular=110 if story else 100, cta_oscura=(fondo == "rojo"),
           firma_x=W - m, firma_clara=(fondo != "hueso"))
    return im


# ---------------------------------------------------------------- 4
def antes_despues(size, story, ruta, c):
    """La misma foto sin editar y editada. El aviso que vende edicion."""
    W, H, m, top, bot = _caja(size, story)
    alto = int(H * (0.54 if story else 0.58))
    base = cargar(ruta, (W, alto), foco=0.45)
    izq, der = aplanar(base), realzar(base)
    mix = Image.new("RGB", (W, alto))
    mix.paste(izq.crop((0, 0, W//2, alto)), (0, 0))
    mix.paste(der.crop((W//2, 0, W, alto)), (W//2, 0))

    im = Image.new("RGB", size, CARBON)
    yf = top if story else 0
    im.paste(mix, (0, yf))
    d = ImageDraw.Draw(im)
    d.rectangle([W//2 - 2, yf, W//2 + 2, yf + alto], fill=ROJO)

    et = work(24, "SemiBold")
    for txt, cx in (("ANTES", W//4), ("DESPUÉS", 3*W//4)):
        w = ancho(d, txt, et, 5) + 44
        d.rectangle([cx - w//2, yf + alto - 64, cx + w//2, yf + alto - 18], fill=CARBON)
        escribir(d, (cx, yf + alto - 56), txt, et, HUESO, 5, "c")

    bloque(d, m, yf + alto + 46, bot - 16, W - 2*m, c, HUESO, ROJO,
           px_titular=100 if story else 92, firma_x=W - m)
    return im


# ---------------------------------------------------------------- 5
def grilla_cuatro(size, story, rutas, c):
    """Cuatro trabajos reales. Muestra volumen y variedad de un vistazo."""
    W, H, m, top, bot = _caja(size, story)
    im = Image.new("RGB", size, HUESO)
    d = ImageDraw.Draw(im)

    g, yz = 8, (top if story else 0)
    zh = int(H * (0.50 if story else 0.54))
    cw, ch = (W - g)//2, (zh - g)//2
    for i, r in enumerate(rutas[:4]):
        im.paste(cargar(r, (cw, ch), foco=0.45), ((i % 2)*(cw+g), yz + (i//2)*(ch+g)))

    bloque(d, m, yz + zh + 48, bot - 16, W - 2*m, c, NEGRO, ROJO,
           px_titular=98 if story else 92, firma_x=W - m, firma_clara=False)
    return im


# ---------------------------------------------------------------- 6
def oferta_numero(size, story, ruta, c):
    """Un numero enorme: precio, plazo o cantidad. Ideal para remarketing."""
    W, H, m, top, bot = _caja(size, story)
    im = Image.new("RGB", size, CARBON)
    hf = int(H * (0.28 if story else 0.30))
    im.paste(velo(cargar(ruta, (W, hf), foco=0.45), 0.15, 0.70, 0.4), (H and 0, H - hf))
    d = ImageDraw.Draw(im)

    y = top + (54 if story else 30)
    kicker(d, W//2, y, c["kicker"], ROJO, 25, "c"); y += 26 + 20
    y += numeral(d, c["numero"], W//2, y, 290 if story else 250, HUESO, "c") + 28

    piso = H - hf - 30
    cc = {k: v for k, v in c.items() if k != "kicker"}
    bloque(d, W//2, y, piso, W - 2*m - 40, cc, HUESO, ROJO,
           px_titular=76 if story else 68, anchor_x="c")
    firma(d, W//2 + 60, H - 76, 1.0, True, "r")
    return im


# ---------------------------------------------------------------- 7
def franja_roja(size, story, ruta, c):
    """Foto a sangre con una franja roja. Imposible pasarla de largo."""
    W, H, m, top, bot = _caja(size, story)
    im = cargar(ruta, size, foco=0.4)
    im = velo_banda(im, int(H * 0.52), H, objetivo=54, pluma=200, piso=0.34)
    d = ImageDraw.Draw(im)

    _, _, _, ht = medir_titular(d, c["titular"], W - 2*m, 100 if story else 92)
    alto = ht + 96
    cy = int(H * (0.46 if story else 0.44))
    d.rectangle([0, cy - alto//2, W, cy + alto//2], fill=ROJO)
    titular(d, c["titular"], m, cy - alto//2 + 46, W - 2*m,
            100 if story else 92, HUESO)

    y = cy + alto//2 + 44
    cc = {k: v for k, v in c.items() if k != "titular"}
    if cc.get("sub"):
        y += parrafo(d, cc["sub"], m, y, W - 2*m - 40, 32, HUESO, "Medium") + 36
    cta_pastilla(d, m, min(y, bot - 96), c["cta"], oscura=True)
    firma(d, W - m, min(y, bot - 96) + 22, 1.0, True, "r")
    return im


# ---------------------------------------------------------------- 8
def marco_hueso(size, story, ruta, c):
    """Foto enmarcada sobre hueso. El mas editorial: para servicios caros."""
    W, H, m, top, bot = _caja(size, story)
    im = Image.new("RGB", size, HUESO)
    d = ImageDraw.Draw(im)
    mm = 92
    fw = W - 2*mm
    fh = int(fw * (1.02 if story else 0.82))
    yf = top + (36 if story else 24)
    im.paste(cargar(ruta, (fw, fh), foco=0.45), (mm, yf))

    bloque(d, mm, yf + fh + 44, bot - 16, fw, c, NEGRO, ROJO,
           px_titular=92 if story else 84, firma_x=W - mm, firma_clara=False)
    return im


# ---------------------------------------------------------------- 9
def lista_servicio(size, story, ruta, c):
    """Foto + que incluye. Para el que ya compara presupuestos."""
    W, H, m, top, bot = _caja(size, story)
    im = Image.new("RGB", size, CARBON)
    hf = int(H * (0.36 if story else 0.38))
    yf = top if story else 0
    f = cargar(ruta, (W, hf), foco=0.42)
    f = velo_banda(f, hf - 190, hf, objetivo=44, pluma=170, piso=0.36)
    im.paste(f, (0, yf))
    d = ImageDraw.Draw(im)

    kicker(d, m, yf + hf - 148, c["kicker"], HUESO)
    titular(d, c["titular"], m, yf + hf - 96, W - 2*m, 78, HUESO, max_lineas=1)

    y = yf + hf + 44
    for it in c["items"]:
        d.ellipse([m, y + 12, m + 13, y + 25], fill=ROJO)
        escribir(d, (m + 34, y), it, work(32, "Regular"), HUESO)
        y += 56
    y += 12
    if c.get("sub"):
        y += parrafo(d, c["sub"], m, y, W - 2*m - 50, 28, (176, 174, 171)) + 28
    y = min(y, bot - 96)
    cta_pastilla(d, m, y, c["cta"])
    firma(d, W - m, y + 22, 1.0, True, "r")
    return im


# ---------------------------------------------------------------- 10
def prueba_social(size, story, ruta, c):
    """El numero de trabajos entregados sobre una foto fuerte. Da confianza."""
    W, H, m, top, bot = _caja(size, story)
    im = cargar(ruta, size, foco=0.42)
    y = top + (30 if story else 16)
    alto_num = int((200 if story else 176) * 1.24)
    im = velo_caja(im, (0, y - 30, W, y + alto_num + 92), objetivo=44, pluma=120, piso=0.34)
    y0 = bot - int(H * (0.34 if story else 0.36))
    im = velo_banda(im, y0 - 30, H, objetivo=48, pluma=210, piso=0.40)
    d = ImageDraw.Draw(im)

    y += numeral(d, c["numero"], m, y, 200 if story else 176, HUESO) + 34
    kicker(d, m, y, c["kicker"], HUESO, 27)

    cc = {k: v for k, v in c.items() if k != "kicker"}
    bloque(d, m, y0, bot - 16, W - 2*m, cc, HUESO, ROJO,
           px_titular=92 if story else 86, firma_x=W - m, color_kicker=HUESO)
    return im


# ---------------------------------------------------------------- 11
def cita(size, story, ruta, c):
    """Testimonio. La pieza que mejor rinde para volver a impactar."""
    W, H, m, top, bot = _caja(size, story)
    im = Image.new("RGB", size, HUESO)
    d = ImageDraw.Draw(im)
    hf = int(H * (0.38 if story else 0.40))
    im.paste(bn(cargar(ruta, (W, hf), foco=0.35)), (0, H - hf))
    d.rectangle([0, H - hf, W, H - hf + 5], fill=NEGRO)

    y = top + (34 if story else 18)
    y += comillas(d, m - 6, y, 150, ROJO) - 24
    y += titular(d, c["titular"], m, y, W - 2*m, 84 if story else 78, NEGRO, 0.94,
                 mayus=False) + 28
    regla(d, m, y, 104); y += 5 + 32
    if c.get("sub"):
        parrafo(d, c["sub"], m, y, W - 2*m - 50, 28, (92, 90, 88), "Medium")

    ycta = H - hf - 116
    cta_pastilla(d, m, ycta, c["cta"])
    firma(d, W - m, H - 76, 1.0, True, "r")
    return im


# ---------------------------------------------------------------- 12
def dos_fotos(size, story, rutas, c):
    """Dos trabajos lado a lado con la oferta arriba."""
    W, H, m, top, bot = _caja(size, story)
    im = Image.new("RGB", size, CARBON)
    d = ImageDraw.Draw(im)

    y = top + (46 if story else 28)
    kicker(d, m, y, c["kicker"]); y += 26 + 16
    y += titular(d, c["titular"], m, y, W - 2*m, 104 if story else 96, HUESO,
                 max_lineas=3) + 34

    g = 8
    cw = (W - g)//2
    alto = int(H * (0.34 if story else 0.30))
    for i, r in enumerate(rutas[:2]):
        im.paste(cargar(r, (cw, alto), foco=0.45), (i*(cw+g), y))
    y += alto + 40

    if c.get("sub"):
        y += parrafo(d, c["sub"], m, y, W - 2*m - 40, 30, (214, 212, 209)) + 30
    y = min(y, bot - 96)
    cta_pastilla(d, m, y, c["cta"])
    firma(d, W - m, y + 22, 1.0, True, "r")
    return im
