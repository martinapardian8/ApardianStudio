# -*- coding: utf-8 -*-
"""Carruseles collage de APARDIAN STUDIO.

Un carrusel continuo es UN solo lienzo ancho (n laminas x 1080) que despues se
corta en laminas de 1080x1350. Lo que cruza un corte (una foto, una cinta, el
hilo rojo, una palabra) obliga a deslizar para ver el resto: esa es la gracia.

Reglas que no se rompen:
- Las fotos son de Martin (05-WEB/img). La IA solo puso los materiales del
  collage: papel, chinches, cinta, clips, la mano y las copias en blanco.
- Ningun rostro queda partido por un corte de lamina (se avisa al armar).
- Tres colores: hueso, negro, rojo. El rojo es el hilo y los acentos.
"""
import os, math, random, json, glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from motor_ads import (HUESO, NEGRO, ROJO, CARBON, IMG, RAIZ, display, work,
                       escribir, ancho, titular, parrafo, medir_titular,
                       medir_parrafo, kicker, firma, aplanar, realzar, bn)
from recorte import cargar_ok, caras, caja_recorte, guardar_cache

LAM = 1080
ALTO = 1350
M = 76
MAT = os.path.join(RAIZ, "04-VIDEOS-IA", "higgsfield", "collage")
REC = os.path.join(MAT, "recortes")
DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "06-carruseles-collage")

COPIA = (252, 251, 248)        # el blanco del papel fotografico
TINTA_SUAVE = (92, 88, 84)


def F(cat, nombre):
    """Ruta de una foto publicada de la galeria."""
    p = os.path.join(IMG, cat, "web", nombre)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return p


# ------------------------------------------------------------------ materiales
_mat = {}
def material(nombre):
    if nombre not in _mat:
        _mat[nombre] = Image.open(nombre if os.path.isabs(nombre)
                                  else os.path.join(REC, nombre)).convert("RGBA")
    return _mat[nombre]


def textura(tipo, ancho_total, alto=ALTO, tinte=None):
    """Papel continuo para todo el carrusel. Se espeja cada tramo para que no se
    note la union, y se lleva el tono al color exacto de la marca."""
    src = Image.open(os.path.join(MAT, "papel_hueso.jpg" if tipo == "hueso"
                                  else "papel_carbon.jpg")).convert("RGB")
    esc = alto / src.height
    src = src.resize((int(src.width * esc) + 1, alto), Image.LANCZOS)
    a = np.asarray(src).astype(np.float32)
    if tipo == "carbon":
        a = a.mean(axis=2, keepdims=True).repeat(3, axis=2)   # neutro, sin violeta
    objetivo = np.array(tinte or ((247, 245, 241) if tipo == "hueso" else (24, 23, 22)),
                        np.float32)
    a = a - a.reshape(-1, 3).mean(axis=0) + objetivo
    tramo = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    out = Image.new("RGB", (ancho_total, alto))
    x, k = 0, 0
    while x < ancho_total:
        out.paste(tramo if k % 2 == 0 else ImageOps.mirror(tramo), (x, 0))
        x += tramo.width; k += 1
    return out


# ------------------------------------------------------------------ geometria
def girar_punto(dx, dy, grados):
    """Como PIL.rotate: angulo positivo gira en sentido antihorario."""
    t = math.radians(grados)
    return (dx * math.cos(t) + dy * math.sin(t),
            -dx * math.sin(t) + dy * math.cos(t))


class Pieza:
    """Lo que queda pegado en el lienzo: sirve para colgarle chinches y cintas."""
    def __init__(self, cx, cy, w, h, rot):
        self.cx, self.cy, self.w, self.h, self.rot = cx, cy, w, h, rot

    def punto(self, fx, fy):
        """Punto relativo (0..1, 0..1) de la pieza ya girada, en el lienzo."""
        dx, dy = (fx - 0.5) * self.w, (fy - 0.5) * self.h
        rx, ry = girar_punto(dx, dy, self.rot)
        return (int(self.cx + rx), int(self.cy + ry))


# ------------------------------------------------------------------ lienzo
class Lienzo:
    """estilo="editorial" (el de la marca): fotos derechas, sin borde de copia,
    sin sombra, sin cinta ni papel rasgado; las etiquetas son tipograficas.
    estilo="collage" conserva el look de mesa de trabajo, por si algun dia sirve."""
    def __init__(self, n, fondo="hueso", tinte=None, estilo="editorial"):
        self.estilo = estilo
        self.editorial = estilo == "editorial"
        self.n, self.W, self.H = n, n * LAM, ALTO
        self.fondo = fondo
        self.oscuro = fondo == "carbon"
        self.im = textura(fondo, self.W, tinte=tinte)
        self.avisos = []
        self.tinta = HUESO if self.oscuro else NEGRO
        self.suave = (200, 197, 192) if self.oscuro else TINTA_SUAVE

    # x de una lamina: X(2, .5) es la mitad de la tercera lamina
    @staticmethod
    def X(i, f=0.0):
        return int(round((i + f) * LAM))

    @property
    def d(self):
        return ImageDraw.Draw(self.im)

    # ---------------------------------------------------------------- pegado
    def pegar(self, capa, cx, cy, rot=0.0, sombra=True, opacidad=1.0):
        """Pega una capa RGBA centrada en (cx, cy), girada, con sombra dura."""
        if rot:
            capa = capa.rotate(rot, resample=Image.BICUBIC, expand=True)
        if opacidad < 1:
            a = capa.split()[3].point(lambda v: int(v * opacidad))
            capa.putalpha(a)
        x0, y0 = int(cx - capa.width / 2), int(cy - capa.height / 2)
        if sombra:
            # sombra plana y corta, nunca difusa: es papel sobre papel
            fuerza = 0.42 if self.oscuro else 0.16
            a = capa.split()[3].point(lambda v: int(v * fuerza))
            a = a.filter(ImageFilter.GaussianBlur(1.6))
            s = Image.new("RGBA", capa.size, (0, 0, 0, 0))
            s.putalpha(a)
            negro = Image.new("RGBA", capa.size, (8, 6, 4, 255))
            negro.putalpha(a)
            self.im.paste(negro, (x0 + 7, y0 + 10), negro)
        self.im.paste(capa, (x0, y0), capa)

    def _revisar_cortes(self, ruta, pz, recorte_src, size):
        """Avisa si un corte de lamina pasa por una cara."""
        x0s, y0s, cw, ch = recorte_src
        W, H = size
        for (fx, fy, fw, fh, conf) in caras(ruta):
            if conf < 0.7:
                continue
            # caja de la cara dentro de la copia, y de ahi al lienzo
            ax, ay = (fx - x0s) / cw, (fy - y0s) / ch
            bx, by = (fx + fw - x0s) / cw, (fy + fh - y0s) / ch
            if bx < 0 or ax > 1 or by < 0 or ay > 1:
                continue
            pts = [pz.punto(ax, ay), pz.punto(bx, ay), pz.punto(ax, by), pz.punto(bx, by)]
            xs = [p[0] for p in pts]
            for k in range(1, self.n):
                corte = k * LAM
                if min(xs) - 6 < corte < max(xs) + 6:
                    self.avisos.append(f"cara cortada por la lamina {k}|{k+1}: "
                                       f"{os.path.basename(ruta)}")

    def foto(self, ruta, cx, cy, w, h, rot=0.0, borde=16, sombra=True, filtro=None,
             color_borde=COPIA, borde_abajo=None):
        """Una copia impresa: la foto recortada sin partir caras y su borde blanco.
        borde_abajo > borde la vuelve una instantanea."""
        if self.editorial:
            rot, borde, sombra, borde_abajo = 0.0, 0, False, None
        ph = cargar_ok(ruta, (w, h))
        if filtro:
            ph = filtro(ph)
        bb = borde if borde_abajo is None else borde_abajo
        card = Image.new("RGBA", (w + 2 * borde, h + borde + bb), color_borde + (255,))
        card.paste(ph, (borde, borde))
        pz = Pieza(cx, cy, card.width, card.height, rot)
        self.pegar(card, cx, cy, rot, sombra)
        # para el control de caras, el recorte equivalente en la foto original
        sw, sh = Image.open(ruta).size
        r = w / h
        cw, ch = (int(sh * r), sh) if sw / sh > r else (sw, int(sw / r))
        x0s, y0s = caja_recorte(ruta, sw, sh, min(cw, sw), min(ch, sh))
        pz_foto = Pieza(cx, cy, w, h, rot)
        # la foto esta desplazada dentro de la copia si el borde de abajo es mas alto
        if bb != borde:
            off = (borde - bb) / 2
            dx, dy = girar_punto(0, off, rot)
            pz_foto.cx, pz_foto.cy = cx + dx, cy + dy
        self._revisar_cortes(ruta, pz_foto, (x0s, y0s, min(cw, sw), min(ch, sh)), (w, h))
        return pz

    def foto_libre(self, ruta, x, y, w, h, filtro=None):
        """Foto a sangre, sin borde ni giro (fondos de lamina)."""
        ph = cargar_ok(ruta, (w, h))
        if filtro:
            ph = filtro(ph)
        self.im.paste(ph, (x, y))
        pz = Pieza(x + w / 2, y + h / 2, w, h, 0)
        sw, sh = Image.open(ruta).size
        r = w / h
        cw, ch = (int(sh * r), sh) if sw / sh > r else (sw, int(sw / r))
        x0s, y0s = caja_recorte(ruta, sw, sh, min(cw, sw), min(ch, sh))
        self._revisar_cortes(ruta, pz, (x0s, y0s, min(cw, sw), min(ch, sh)), (w, h))
        return pz

    def circulo(self, ruta, cx, cy, r, borde=12):
        if self.editorial:
            borde = 0
        ph = cargar_ok(ruta, (2 * r, 2 * r)).convert("RGBA")
        m = Image.new("L", (8 * r, 8 * r), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 8 * r - 1, 8 * r - 1], fill=255)
        ph.putalpha(m.resize((2 * r, 2 * r), Image.LANCZOS))
        R = r + borde
        card = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
        m2 = Image.new("L", (8 * R, 8 * R), 0)
        ImageDraw.Draw(m2).ellipse([0, 0, 8 * R - 1, 8 * R - 1], fill=255)
        base = Image.new("RGBA", (2 * R, 2 * R), COPIA + (255,))
        base.putalpha(m2.resize((2 * R, 2 * R), Image.LANCZOS))
        card.alpha_composite(base)
        card.alpha_composite(ph, (borde, borde))
        self.pegar(card, cx, cy, 0, not self.editorial)
        return Pieza(cx, cy, 2 * R, 2 * R, 0)

    def marco(self, ruta, cx, cy, w, h, rot=0.0, grosor=26, paspartu=54, color=(20, 18, 16)):
        """Cuadro enmarcado: marco de madera negra y paspartu blanco."""
        if self.editorial:
            rot = 0.0
        ph = cargar_ok(ruta, (w, h))
        W2, H2 = w + 2 * (grosor + paspartu), h + 2 * (grosor + paspartu)
        card = Image.new("RGBA", (W2, H2), color + (255,))
        d = ImageDraw.Draw(card)
        d.rectangle([grosor, grosor, W2 - grosor - 1, H2 - grosor - 1], fill=COPIA)
        # bisel del paspartu: una linea fina mas oscura
        g = grosor + paspartu
        d.rectangle([g - 3, g - 3, g + w + 2, g + h + 2], fill=(222, 219, 214))
        card.paste(ph, (g, g))
        self.pegar(card, cx, cy, rot, not self.editorial)
        return Pieza(cx, cy, W2, H2, rot)

    # ---------------------------------------------------------------- utiles
    def cinta(self, cx, cy, largo, rot=0.0, k=1, opacidad=0.9):
        if self.editorial:
            return
        c = material(f"cinta_{(k - 1) % 8 + 1:02d}.png")
        esc = largo / c.width
        c = c.resize((int(largo), max(30, int(c.height * esc * 0.85))), Image.LANCZOS)
        self.pegar(c, cx, cy, rot, sombra=False, opacidad=opacidad)

    def cinta_en(self, pieza, fx, fy, largo=170, rot=None, k=1):
        x, y = pieza.punto(fx, fy)
        self.cinta(x, y, largo, pieza.rot + (rot if rot is not None else 0), k)

    def chinche(self, x, y, k=3, tam=92):
        c = material(f"chinche_{(k - 1) % 8 + 1:02d}.png")
        esc = tam / max(c.size)
        c = c.resize((int(c.width * esc), int(c.height * esc)), Image.LANCZOS)
        self.pegar(c, x, y, 0, True)

    def clip(self, x, y, rot=0.0, k=1, tam=150):
        c = material(f"clip_{(k - 1) % 5 + 1:02d}.png")
        esc = tam / max(c.size)
        c = c.resize((int(c.width * esc), int(c.height * esc)), Image.LANCZOS)
        self.pegar(c, x, y, rot, True)

    def broche(self, x, y, rot=0.0, k=1, tam=150):
        if self.editorial:
            return
        c = material(f"broche_{(k - 1) % 2 + 1:02d}.png")
        esc = tam / max(c.size)
        c = c.resize((int(c.width * esc), int(c.height * esc)), Image.LANCZOS)
        self.pegar(c, x, y, rot, True)

    # ---------------------------------------------------------------- hilo
    def hilo(self, puntos, grosor=5, color=ROJO, caida=0.07):
        """El hilo rojo: une las piezas de lamina a lamina, con la curva de un
        hilo de verdad colgando entre dos chinches."""
        S = 2
        m = Image.new("L", (self.W * S, self.H * S), 0)
        d = ImageDraw.Draw(m)
        traz = []
        for (x0, y0), (x1, y1) in zip(puntos, puntos[1:]):
            dist = math.hypot(x1 - x0, y1 - y0)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + caida * dist + 8
            for k in range(41):
                t = k / 40
                x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t ** 2 * x1
                y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t ** 2 * y1
                traz.append((x * S, y * S))
        d.line(traz, fill=255, width=grosor * S, joint="curve")
        m = m.resize((self.W, self.H), Image.LANCZOS)
        capa = Image.new("RGB", (self.W, self.H), color)
        self.im.paste(capa, (0, 0), m)

    # ---------------------------------------------------------------- texto
    def titulo(self, txt, x, y, w, px, color=None, interlinea=0.9, max_lineas=4, alto_max=None):
        return titular(self.d, txt, x, y, w, px, color or self.tinta,
                       interlinea=interlinea, max_lineas=max_lineas, alto_max=alto_max)

    def texto(self, txt, x, y, w, px, color=None, peso="Regular", interlinea=1.34):
        return parrafo(self.d, txt, x, y, w, px, color or self.suave, peso, interlinea)

    def etiqueta(self, txt, x, y, color=None, px=24, track=5):
        escribir(self.d, (x, y), txt.upper(), work(px, "SemiBold"), color or ROJO, track)
        return int(px * 1.5)

    def papel(self, cx, cy, w, h, rot, txt, k=1, color="blanco", px=40, sub=None,
              fuente="display"):
        """Un papel rasgado con texto, como un recorte pegado. En editorial es
        una etiqueta tipografica: regla roja corta, nombre en Anton y bajada."""
        if self.editorial:
            return self._etiqueta_editorial(cx, cy, w, h, txt, sub, px)
        # el cuarto recorte es casi un triangulo: no sirve para escribir
        p = material(f"papel_{(k - 1) % 3 + 1:02d}.png").resize((w, h), Image.LANCZOS)
        if color == "rojo":
            a = np.asarray(p).astype(np.float32)
            lum = a[..., :3].mean(axis=2, keepdims=True) / 255.0
            tint = np.array(ROJO, np.float32) * (0.80 + 0.20 * lum) + 255 * 0.10 * (lum - 0.9).clip(0)
            a[..., :3] = tint.clip(0, 255)
            p = Image.fromarray(a.astype(np.uint8))
        elif color == "negro":
            a = np.asarray(p).astype(np.float32)
            lum = a[..., :3].mean(axis=2, keepdims=True) / 255.0
            a[..., :3] = (np.array(NEGRO, np.float32) + 60 * (1 - lum)).clip(0, 255)
            p = Image.fromarray(a.astype(np.uint8))
        d = ImageDraw.Draw(p)
        tinta = HUESO if color in ("rojo", "negro") else NEGRO
        # el papel rasgado no llena su caja: el texto vive en el 62 % central
        mw = int(w * 0.56)
        if fuente == "display":
            lineas = txt.upper().split("\n")
            while px > 20 and max(ancho(d, l, display(px)) for l in lineas) > mw:
                px -= 2
            f = display(px)
            sub_px = max(17, int(px * 0.40))
            alto = len(lineas) * int(px * 0.95) + (int(sub_px * 1.6) if sub else 0)
            y = (h - alto) // 2 - int(px * 0.08)
            for l in lineas:
                escribir(d, (w // 2, y), l, f, tinta, 0, "c"); y += int(px * 0.95)
        else:
            f = work(px, "SemiBold")
            lineas = txt.upper().split("\n")
            y = (h - len(lineas) * int(px * 1.3)) // 2
            for l in lineas:
                escribir(d, (w // 2, y), l, f, tinta, 4, "c"); y += int(px * 1.3)
        if sub:
            sp = max(17, int(px * 0.40))
            while sp > 14 and ancho(d, sub.upper(), work(sp, "SemiBold"), 3) > mw:
                sp -= 1
            escribir(d, (w // 2, y + 8), sub.upper(), work(sp, "SemiBold"),
                     ROJO if color == "blanco" else tinta, 3, "c")
        self.pegar(p, cx, cy, rot, True)
        return Pieza(cx, cy, w, h, rot)

    def _etiqueta_editorial(self, cx, cy, w, h, txt, sub, px):
        d = self.d
        x0 = int(cx - w / 2)
        lineas = txt.upper().split("\n")
        tam = max(30, min(int(px * 0.9), 58))
        while tam > 24 and max(ancho(d, l, display(tam)) for l in lineas) > w:
            tam -= 2
        salto = int(tam * 0.95)
        alto = 22 + len(lineas) * salto + (int(tam * 0.3) + 34 if sub else 0)
        y = int(cy - alto / 2)
        d.rectangle([x0, y, x0 + 46, y + 4], fill=ROJO)
        y += 22
        for l in lineas:
            escribir(d, (x0, y), l, display(tam), self.tinta); y += salto
        if sub:
            # Anton baja mas que su salto de linea: la bajada va debajo de la tinta
            escribir(d, (x0, y + int(tam * 0.3) + 6), sub.upper(), work(19, "SemiBold"), self.suave, 4)
        return Pieza(cx, cy, w, alto, 0)

    def palabra_foto(self, txt, ruta, x, y, px, track=0, contorno=False):
        """Una palabra enorme rellena con una foto."""
        f = display(px)
        txt = txt.upper()
        tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
        w = ancho(tmp, txt, f, track) + 20
        h = int(px * 1.25)
        m = Image.new("L", (w, h), 0)
        escribir(ImageDraw.Draw(m), (10, 0), txt, f, 255, track)
        bb = m.getbbox()
        m = m.crop(bb)
        ph = cargar_ok(ruta, m.size).convert("RGBA")
        ph.putalpha(m)
        self.im.paste(ph, (x, y), ph)
        return m.size

    def deslizar(self, i, y=None, claro=None):
        """Señal de deslizar, abajo a la derecha de la lamina i."""
        claro = self.oscuro if claro is None else claro
        col = HUESO if claro else NEGRO
        y = y or ALTO - 100
        f = work(25, "SemiBold")
        d = self.d
        w = ancho(d, "DESLIZÁ", f, 5)
        x = self.X(i, 1) - M - w - 70
        escribir(d, (x, y), "DESLIZÁ", f, col, 5)
        ax = x + w + 18
        d.line([(ax, y + 13), (ax + 50, y + 13)], fill=ROJO, width=4)
        d.polygon([(ax + 52, y + 13), (ax + 38, y + 4), (ax + 38, y + 22)], fill=ROJO)

    def firma(self, i, y=None, x=None, escala=0.9):
        firma(self.d, x if x is not None else self.X(i) + M, y or ALTO - 110, escala,
              self.oscuro)

    def numero(self, txt, x, y, px=60, color=ROJO):
        escribir(self.d, (x, y), txt, display(px), color)

    # ---------------------------------------------------------------- pantallas
    def navegador(self, captura, cx, cy, w, rot=0.0, url="apardianstudio.com"):
        """Una ventana de navegador con una captura real del sitio."""
        if self.editorial:
            rot = 0.0
        im = Image.open(captura).convert("RGB")
        h = int(w * im.height / im.width)
        im = im.resize((w, h), Image.LANCZOS)
        barra = 46
        card = Image.new("RGBA", (w, h + barra), (34, 33, 31, 255))
        d = ImageDraw.Draw(card)
        for k, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
            d.ellipse([18 + k * 24, 16, 32 + k * 24, 30], fill=c)
        d.rounded_rectangle([110, 10, w - 110, 36], 13, fill=(58, 56, 53))
        escribir(d, (w // 2, 14), url, work(17, "Medium"), (200, 197, 192), 1, "c")
        card.paste(im, (0, barra))
        m = Image.new("L", card.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, card.height - 1], 14, fill=255)
        card.putalpha(m)
        self.pegar(card, cx, cy, rot, True)
        return Pieza(cx, cy, card.width, card.height, rot)

    def telefono(self, captura, cx, cy, h, rot=0.0):
        """Un celular negro con una captura real de la version movil."""
        if self.editorial:
            rot = 0.0
        im = Image.open(captura).convert("RGB")
        marco = int(h * 0.028)
        hh = h - 2 * marco
        ww = int(hh * im.width / im.height)
        im = im.resize((ww, hh), Image.LANCZOS)
        W2, H2 = ww + 2 * marco, h
        r = int(W2 * 0.13)
        card = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([0, 0, W2 - 1, H2 - 1], r, fill=(14, 13, 12, 255))
        pant = Image.new("L", (ww, hh), 0)
        ImageDraw.Draw(pant).rounded_rectangle([0, 0, ww - 1, hh - 1], r - marco, fill=255)
        card.paste(im, (marco, marco), pant)
        d.rounded_rectangle([W2 // 2 - 46, marco + 12, W2 // 2 + 46, marco + 40], 14,
                            fill=(14, 13, 12, 255))
        self.pegar(card, cx, cy, rot, True)
        return Pieza(cx, cy, W2, H2, rot)

    def antes_despues(self, ruta, cx, cy, w, h, rot=0.0, borde=16, corte=0.5, k=7):
        """Una copia rasgada por el medio: a la izquierda la foto plana, como sale
        de la camara, y a la derecha la edicion. El 'antes' es una simulacion
        hecha desde la foto final (igual que en los avisos de edicion)."""
        ph = cargar_ok(ruta, (w, h))
        izq, der = aplanar(ph), ph
        rnd = random.Random(k)
        xs, x = [], int(w * corte)
        for y in range(0, h + 1, 10):
            x += rnd.randint(-7, 7); x = max(int(w * corte) - 26, min(int(w * corte) + 26, x))
            xs.append((x, y))
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon([(0, 0)] + xs + [(0, h)], fill=255)
        comp = der.copy(); comp.paste(izq, (0, 0), m)
        d = ImageDraw.Draw(comp)
        # el borde rasgado deja ver el papel blanco con fibras
        d.line(xs, fill=COPIA, width=7)
        d.line([(px + 4, py) for px, py in xs], fill=(232, 229, 224), width=2)
        card = Image.new("RGBA", (w + 2 * borde, h + 2 * borde), COPIA + (255,))
        card.paste(comp, (borde, borde))
        dd = ImageDraw.Draw(card)
        et = work(20, "SemiBold")
        for txt, fx in (("SIN EDITAR", 0.25), ("EDITADA", 0.75)):
            tw = ancho(dd, txt, et, 4) + 30
            cx0 = borde + int(w * fx)
            dd.rectangle([cx0 - tw // 2, borde + h - 64, cx0 + tw // 2, borde + h - 26],
                         fill=CARBON if txt == "SIN EDITAR" else ROJO)
            escribir(dd, (cx0, borde + h - 58), txt, et, HUESO, 4, "c")
        self.pegar(card, cx, cy, rot, True)
        return Pieza(cx, cy, card.width, card.height, rot)

    # ---------------------------------------------------------------- montaje
    def montar_en_copias(self, base, rutas, x, y, w, h, umbral=200, sat=8, margen=0.90, orden=None):
        """Pone fotos reales dentro de las copias en blanco de una foto de
        Higgsfield (la mano, la mesa negra). Detecta cada rectangulo blanco,
        deforma la foto a su perspectiva y conserva la luz del papel original.
        Devuelve las esquinas de cada copia (arriba-izq, arriba-der, abajo-der,
        abajo-izq) en coordenadas del lienzo."""
        src = Image.open(os.path.join(MAT, base)).convert("RGB")
        src = ImageOps.fit(src, (w, h), Image.LANCZOS)
        a = np.asarray(src)
        hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
        # la copia es mas blanca y mas neutra que el papel de fondo
        blanco = ((hsv[..., 2] > umbral) & (hsv[..., 1] < sat)).astype(np.uint8) * 255
        blanco = cv2.morphologyEx(blanco, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        blanco = cv2.morphologyEx(blanco, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(blanco, 8)
        zonas = [k for k in range(1, n) if st[k][4] > (w * h) * 0.012]
        if orden == "lectura":      # de arriba a abajo y de izquierda a derecha
            zonas.sort(key=lambda k: (int(cen[k][1] // (h * 0.2)), cen[k][0]))
        else:
            zonas.sort(key=lambda k: -st[k][4])
        out = a.astype(np.float32).copy()
        quads = []
        lum_papel = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        usadas = 0
        for k, ruta in zip(zonas, rutas):
            mk = (lab == k).astype(np.uint8) * 255
            cs, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            c = cv2.convexHull(max(cs, key=cv2.contourArea))
            quad = cv2.boxPoints(cv2.minAreaRect(c))           # 4 esquinas
            ap = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(ap) == 4:
                quad = ap.reshape(4, 2).astype(np.float32)
            # ordenar: arriba-izq, arriba-der, abajo-der, abajo-izq
            s = quad.sum(axis=1); df = np.diff(quad, axis=1).ravel()
            q = np.array([quad[np.argmin(s)], quad[np.argmin(df)],
                          quad[np.argmax(s)], quad[np.argmax(df)]], np.float32)
            # margen blanco de copia: la foto entra un 5 % hacia adentro
            cen_q = q.mean(axis=0)
            qi = cen_q + (q - cen_q) * margen
            ancho_q = np.linalg.norm(qi[1] - qi[0]); alto_q = np.linalg.norm(qi[3] - qi[0])
            ph = np.asarray(cargar_ok(ruta, (max(8, int(ancho_q)), max(8, int(alto_q)))))
            hh, ww = ph.shape[:2]
            Mx = cv2.getPerspectiveTransform(
                np.float32([[0, 0], [ww, 0], [ww, hh], [0, hh]]), qi)
            warp = cv2.warpPerspective(ph, Mx, (w, h), flags=cv2.INTER_LANCZOS4)
            mq = np.zeros((h, w), np.uint8)
            cv2.fillConvexPoly(mq, qi.astype(np.int32), 255)
            # solo donde habia papel: un dedo encima de la copia queda encima
            papel = (hsv[..., 1] < sat + 6).astype(np.uint8) * 255
            mfin = cv2.bitwise_and(mq, cv2.dilate(papel, np.ones((3, 3), np.uint8)))
            mfin = cv2.GaussianBlur(mfin, (3, 3), 0).astype(np.float32) / 255.0
            luz = (lum_papel / max(0.6, float(np.percentile(lum_papel[mk > 0], 70))))[..., None]
            luz = luz.clip(0.75, 1.06)
            comp = warp.astype(np.float32) * luz
            out = out * (1 - mfin[..., None]) + comp * mfin[..., None]
            usadas += 1
            quads.append([(int(px + x), int(py + y)) for px, py in q])
        im = Image.fromarray(out.clip(0, 255).astype(np.uint8))
        self.im.paste(im, (x, y))
        return quads

    # ---------------------------------------------------------------- salida
    def guardar(self, slug, previa=True):
        carpeta = os.path.join(DEST, slug)
        os.makedirs(carpeta, exist_ok=True)
        for f in glob.glob(os.path.join(carpeta, "*.jpg")):
            os.remove(f)
        for i in range(self.n):
            lam = self.im.crop((i * LAM, 0, (i + 1) * LAM, ALTO))
            lam.save(os.path.join(carpeta, f"{i + 1:02d}.jpg"), "JPEG", quality=92,
                     optimize=True, subsampling=0)
        if previa:
            p = self.im.copy()
            p.thumbnail((self.n * 360, 450))
            d = ImageDraw.Draw(p)
            for i in range(1, self.n):
                x = int(i * p.width / self.n)
                d.line([(x, 0), (x, p.height)], fill=(0, 200, 255), width=1)
            p.save(os.path.join(carpeta, "_panorama.jpg"), quality=85)
        for a in sorted(set(self.avisos)):
            print("  AVISO", slug, a)
        return carpeta
