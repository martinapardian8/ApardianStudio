# -*- coding: utf-8 -*-
"""Una foto de Martin a cuadro completo, con texto mínimo y movimiento suave.

Lo usan los carruseles (carruseles_fotos.py), sus reels (reels_collage.py) y
los videos de pauta (video_ads.py). Reglas que aplica (09-ESTUDIO/ESTETICA_IG.md
y APRENDIZAJES.md):

- La foto llena el cuadro si para eso se pierde 22 % o menos. En un cuadro
  vertical (4:5 o 9:16) solo entra una foto vertical que lo llene así (Martin,
  28/10/2026: "nunca una foto horizontal en un lienzo vertical"); si no, Capa
  da ValueError y el que arma la pieza elige otra. Solo en un cuadro
  horizontal o cuadrado una foto que no entra va entera sobre la misma foto
  desenfocada.
- El recorte no parte caras (recorte.caja_recorte, caras.json).
- El texto va en el tercio de arriba o de abajo, donde no hay caras y la foto
  está más tranquila, con un degradado suave solo detrás de él.
- Anton para el titular (1,0 de interlineado; 1,14 si la línea de abajo lleva
  tilde), Work Sans para lo chico, el rojo #FF0033 solo en una regla corta.
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

from motor_ads import (HUESO, ROJO, CARBON, display, work, escribir, ancho,
                       medir_titular, titular, _tinta_abajo, luminancia,
                       _mezcla_necesaria, PERDIDA_MAX, apta)
from recorte import caras, caja_recorte

WA = "+598 91 962 962"
FPS = 30


# ------------------------------------------------------------------ encuadre
def _caja(ruta, ratio):
    """(x0, y0, cw, ch) del recorte de proporción `ratio` que no parte caras."""
    sw, sh = Image.open(ruta).size
    if sw / sh > ratio:
        ch = sh; cw = int(round(ch * ratio))
    else:
        cw = sw; ch = int(round(cw / ratio))
    cw, ch = min(cw, sw), min(ch, sh)
    x0, y0 = caja_recorte(ruta, sw, sh, cw, ch)
    x0 = max(0, min(sw - cw, x0)); y0 = max(0, min(sh - ch, y0))
    return x0, y0, cw, ch


def perdida(ruta, size):
    w, h = Image.open(ruta).size
    a, b = w / h, size[0] / size[1]
    return 1 - min(a, b) / max(a, b)


class Capa:
    """La foto ya ubicada en un cuadro W x H.

    modo "sangre": la foto llena el cuadro (caja = todo el cuadro).
    modo "entera" (solo en cuadros horizontales o cuadrados): la foto va en
    `caja` sobre `fondo` (la misma foto
    desenfocada y oscura).
    `caras` quedan en coordenadas del cuadro, para no taparlas con texto."""

    def __init__(self, ruta, size, entera=False):
        self.ruta, self.size = ruta, size
        W, H = size
        if H > W and (entera or not apta(ruta, size)):
            raise ValueError("%s no llena un cuadro vertical de %dx%d (horizontal, pierde más "
                             "del 22 %% o parte una cara): va otra foto vertical" % (os.path.basename(ruta), W, H))
        self.orig = Image.open(ruta).convert("RGB")
        sw, sh = self.orig.size
        if perdida(ruta, size) <= PERDIDA_MAX and not entera:
            self.modo = "sangre"
            self.recorte = _caja(ruta, W / H)
            self.caja = (0, 0, W, H)
            self.fondo = None
        else:
            self.modo = "entera"
            ar = sw / sh
            # se recorta como mucho PERDIDA_MAX, con el encuadre que cuida caras
            tope = 0.0 if entera else PERDIDA_MAX
            ar2 = ar * (1 - tope) if ar > W / H else ar / (1 - tope)
            if ar2 >= W / H:
                fw, fh = W, int(round(W / ar2))
            else:
                fh, fw = H, int(round(H * ar2))
            self.recorte = _caja(ruta, ar2)
            self.caja = ((W - fw) // 2, (H - fh) // 2, fw, fh)
            x0, y0, cw, ch = _caja(ruta, W / H)
            f = self.orig.crop((x0, y0, x0 + cw, y0 + ch)).resize((W // 4, H // 4), Image.BILINEAR)
            f = f.filter(ImageFilter.GaussianBlur(12)).resize((W, H), Image.BICUBIC)
            self.fondo = ImageEnhance.Brightness(f).enhance(0.38)

    def mover_foto(self, y):
        """En modo entera, sube o baja la foto (para dejar lugar al texto)."""
        x, _, w, h = self.caja
        self.caja = (x, int(max(0, min(self.size[1] - h, y))), w, h)

    def caras(self, conf=0.6, con_conf=False):
        x0, y0, cw, ch = self.recorte
        bx, by, bw, bh = self.caja
        out = []
        for (fx, fy, fw, fh, c) in caras(self.ruta):
            if c < conf:
                continue
            a = ((fx - x0) / cw, (fy - y0) / ch, (fx + fw - x0) / cw, (fy + fh - y0) / ch)
            if a[2] < 0 or a[0] > 1 or a[3] < 0 or a[1] > 1:
                continue
            out.append((bx + a[0] * bw, by + a[1] * bh, bx + a[2] * bw, by + a[3] * bh)
                       + ((c,) if con_conf else ()))
        return out

    def foto(self, z=1.0, centro=None):
        """La foto del tamaño de su caja, con un acercamiento z (1.0 a 1.06)."""
        x0, y0, cw, ch = self.recorte
        _, _, bw, bh = self.caja
        w, h = cw / z, ch / z
        cx, cy = centro if centro else (x0 + cw / 2, y0 + ch / 2)
        cx = max(x0 + w / 2, min(x0 + cw - w / 2, cx))
        cy = max(y0 + h / 2, min(y0 + ch - h / 2, cy))
        return self.orig.resize((bw, bh), Image.BICUBIC,
                                box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))

    def centro_motivo(self):
        """Hacia dónde acercarse: el centro de las caras, si hay; si no, el medio."""
        x0, y0, cw, ch = self.recorte
        fs = [f for f in caras(self.ruta) if f[4] >= 0.6
              and x0 <= f[0] + f[2] / 2 <= x0 + cw and y0 <= f[1] + f[3] / 2 <= y0 + ch]
        if not fs:
            return None
        cx = sum(f[0] + f[2] / 2 for f in fs) / len(fs)
        cy = sum(f[1] + f[3] / 2 for f in fs) / len(fs)
        # a mitad de camino entre el centro y las caras: el movimiento es leve
        return ((cx + x0 + cw / 2) / 2, (cy + y0 + ch / 2) / 2)

    def cuadro(self, z=1.0, centro=None):
        W, H = self.size
        im = self.fondo.copy() if self.fondo is not None else Image.new("RGB", (W, H), CARBON)
        x, y, _, _ = self.caja
        im.paste(self.foto(z, centro), (x, y))
        return im


# ------------------------------------------------------------------ dónde va el texto
def _detalle(im, y0, y1):
    W, H = im.size
    y0, y1 = int(max(0, y0)), int(min(H, y1))
    if y1 - y0 < 8:
        return 1e9
    r = im.crop((0, y0, W, y1)).convert("L").resize((120, max(8, (y1 - y0) * 120 // W)), Image.BILINEAR)
    e = list(r.filter(ImageFilter.FIND_EDGES).getdata())
    return sum(e) / len(e)


def elegir_zona(capa, alto, top, bot, preferir=None):
    """'arriba' o 'abajo': donde el bloque de `alto` px no pisa caras y la
    foto está más tranquila. top/bot: límites de la zona segura."""
    im = capa.cuadro()
    zonas = {"arriba": (top - 30, top + alto + 30), "abajo": (bot - alto - 30, bot + 30)}
    pun = {}
    for k, (a, b) in zonas.items():
        p = _detalle(im, a, b)
        for (x0, y0, x1, y1, c) in capa.caras(conf=0.6, con_conf=True):
            ov = max(0.0, min(y1, b + 20) - max(y0, a - 20)) / max(1.0, y1 - y0)
            if ov > 0:
                # pisar una cara es lo peor; pisarla entera, peor que rozarle el mentón
                p += (1000 * c + (x1 - x0) * (y1 - y0) / 20) * (0.3 + 0.7 * ov)
        if capa.modo == "entera":
            # en una foto entera, el texto va en la banda desenfocada si entra
            bx, by, bw, bh = capa.caja
            fuera = (by - a) if k == "arriba" else (b - (by + bh))
            p -= 3 if fuera > 0 else 0
        if preferir == k:
            p *= 0.8
        pun[k] = p
    return min(pun, key=pun.get)


# ------------------------------------------------------------------ capas de texto
def _velo(size, y0, y1, fuerza, desde_arriba, pluma=280):
    """Degradado negro (RGBA) solo detrás del texto: más fuerte en el borde,
    más liviano bajo la última línea y se apaga suave hacia la foto."""
    W, H = size
    a = Image.new("L", (1, H), 0)
    px = a.load()
    largo = max(1, (y1 if desde_arriba else H - y0))
    for y in range(H):
        d = y if desde_arriba else H - 1 - y          # distancia al borde
        if d <= largo:
            v = 1.0 - 0.35 * (d / largo)
        else:
            t = min(1.0, (d - largo) / pluma)
            v = 0.65 * (1 - t * t * (3 - 2 * t))
        px[0, y] = int(255 * fuerza * v)
    capa = Image.new("RGBA", (W, H), CARBON + (0,))
    capa.putalpha(a.resize((W, H)))
    return capa


REGLA, GAP_REGLA = 6, 30
_D = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def _partir(txt, f, max_w):
    """Una o dos líneas, cortadas donde quedan más parejas."""
    pal = txt.split()
    if ancho(_D, txt, f) <= max_w * 0.62 or len(pal) < 3:
        if ancho(_D, txt, f) <= max_w:
            return [txt]
    mejor = None
    for k in range(1, len(pal)):
        ls = [" ".join(pal[:k]), " ".join(pal[k:])]
        w = max(ancho(_D, l, f) for l in ls)
        if mejor is None or w < mejor[0]:
            mejor = (w, ls)
    return mejor[1]


def _salto(px, ls):
    # Anton: 1,0 de interlineado; 1,14 si la línea de abajo lleva tilde o Ñ
    return int(px * (1.14 if any(any(c in "ÁÉÍÓÚÑÜ" for c in l) for l in ls[1:]) else 1.0))


def medir_titulo(txt, max_w, px, max_alto):
    """(px, líneas, salto, alto real de la tinta). Dos líneas como máximo."""
    t = txt.upper()
    while px > 36:
        f = display(px)
        ls = _partir(t, f, max_w)
        salto = _salto(px, ls)
        alto = (len(ls) - 1) * salto + _tinta_abajo(f, ls[-1])
        if len(ls) <= 2 and all(ancho(_D, l, f) <= max_w for l in ls) and alto <= max_alto:
            return px, ls, salto, alto
        px -= 2
    return px, ls, salto, alto


def _sombra(capa_rgba, dibujo):
    """Sombra suave bajo el texto blanco: se lee sin oscurecer más la foto."""
    m = Image.new("L", capa_rgba.size, 0)
    dibujo(ImageDraw.Draw(m), 255)
    m = m.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.55))
    sombra = Image.new("RGBA", capa_rgba.size, CARBON + (0,))
    sombra.putalpha(m)
    capa_rgba.alpha_composite(sombra, (0, 3))


def capa_titulo(capa, txt, top, bot, margen, px=104, max_alto=None, kicker=None,
                reserva_abajo=0, preferir=None):
    """Capa RGBA con el degradado y el titular. Devuelve (capa, zona, caja_texto).
    reserva_abajo: lugar libre debajo del titular para la llamada que aparece
    después (así nada se mueve)."""
    W, H = capa.size
    max_w = W - 2 * margen
    max_alto = max_alto or H // 4
    pxk = 24
    alto_k = (int(pxk * 1.2) + 18) if kicker else 0
    fijo = REGLA + GAP_REGLA + alto_k + reserva_abajo
    if capa.modo == "entera":
        # si la foto entera deja una banda, el titular se achica para entrar ahí
        banda = (bot - top) - capa.caja[3] - 36
        if banda - fijo >= 120:
            max_alto = min(max_alto, banda)
    px2, ls, salto, alto_t = medir_titulo(txt, max_w, px, max_alto - fijo)
    alto = fijo + alto_t
    zona = _zona(capa, alto, top, bot, preferir or "arriba")
    y0 = top if zona == "arriba" else bot - alto
    c = _fondo_texto(capa, y0, y0 + alto, zona)
    f = display(px2)

    def dibujo(d, a=255, sombra=False):
        col = (a if sombra else HUESO) if sombra else HUESO + (a,)
        y = y0
        if not sombra:
            d.rectangle([margen, y, margen + 72, y + REGLA], fill=ROJO + (a,))
        y += REGLA + GAP_REGLA
        if kicker:
            escribir(d, (margen, y), kicker.upper(), work(pxk, "SemiBold"), col, 5)
            y += alto_k
        for i, l in enumerate(ls):
            escribir(d, (margen, y + i * salto), l, f, col)

    _sombra(c, lambda d, a: dibujo(d, a, True))
    dibujo(ImageDraw.Draw(c))
    return c, zona, (margen, y0, W - margen, y0 + alto)


def _zona(capa, alto, top, bot, lado):
    """Foto entera con lugar arriba o abajo: el texto va en la banda
    desenfocada del lado pedido y la foto se corre. Si no hay lugar (la foto
    ocupa todo el alto), se elige como en una foto a sangre."""
    if capa.modo == "entera" and capa.caja[3] <= (bot - top) - alto - 30:
        _acomodar(capa, alto, top, bot, lado)
        return lado
    return elegir_zona(capa, alto, top, bot, lado)


def _acomodar(capa, alto, top, bot, lado):
    """Foto entera: la corre para que el texto entre en la banda desenfocada."""
    bx, by, bw, bh = capa.caja
    if lado == "arriba":
        capa.mover_foto(max(by, top + alto + 30))
    else:
        capa.mover_foto(min(by, bot - alto - 30 - bh))


def _fondo_texto(capa, y0, y1, zona):
    """El degradado justo para que el texto blanco se lea (mide la foto)."""
    W, H = capa.size
    im = capa.cuadro()
    lum = luminancia(im, (0, y0, W, y1))
    f = max(0.22, _mezcla_necesaria(lum, 72))
    bx, by, bw, bh = capa.caja
    if capa.modo == "entera" and (y1 < by or y0 > by + bh):
        f = 0.0          # el texto va sobre el fondo desenfocado: ya es oscuro
    if zona == "arriba":
        return _velo((W, H), 0, y1 + 30, f, True)
    return _velo((W, H), y0 - 30, H, f, False)


def alto_cta():
    return REGLA + GAP_REGLA + int(24 * 1.2) + 16 + _tinta_abajo(display(70), WA)


def dibujar_cta(d, x, y, alfa=255, sombra=False):
    col = alfa if sombra else HUESO + (alfa,)
    if not sombra:
        d.rectangle([x, y, x + 72, y + REGLA], fill=ROJO + (alfa,))
    y += REGLA + GAP_REGLA
    escribir(d, (x, y), "ESCRIBIME POR WHATSAPP", work(24, "SemiBold"), col, 5)
    y += int(24 * 1.2) + 16
    escribir(d, (x, y), WA, display(70), col)


def capa_cta(capa, top, bot, margen, preferir="abajo"):
    """Capa RGBA con el degradado y 'ESCRIBIME POR WHATSAPP / +598 91 962 962'."""
    W, H = capa.size
    alto = alto_cta()
    zona = _zona(capa, alto, top, bot, preferir)
    y0 = top if zona == "arriba" else bot - alto
    c = _fondo_texto(capa, y0, y0 + alto, zona)
    _sombra(c, lambda d, a: dibujar_cta(d, margen, y0, a, True))
    dibujar_cta(ImageDraw.Draw(c), margen, y0)
    return c, zona, (margen, y0, W - margen, y0 + alto)


def componer(base, capa_rgba):
    if capa_rgba is None:
        return base
    b = base.convert("RGBA")
    b.alpha_composite(capa_rgba)
    return b.convert("RGB")


# ------------------------------------------------------------------ video
def suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Codificador:
    """Manda cuadros RGB a ffmpeg: H.264 + una pista AAC en silencio
    (Instagram la exige por API; la música la pone Martin)."""

    def __init__(self, salida, size, segundos):
        self.size = size
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        W, H = size
        self.p = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
             "-t", f"{segundos:.3f}", "-map", "0:v", "-map", "1:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
             "-profile:v", "high", "-c:a", "aac", "-b:a", "128k",
             "-movflags", "+faststart", salida],
            stdin=subprocess.PIPE)

    def cuadro(self, im):
        self.p.stdin.write(im.convert("RGB").tobytes())

    def cerrar(self):
        self.p.stdin.close()
        if self.p.wait() != 0:
            raise RuntimeError("ffmpeg falló")
