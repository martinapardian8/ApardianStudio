# -*- coding: utf-8 -*-
"""Versiones en video de las piezas de pauta (08-CONTENIDO-INSTAGRAM/05-videos).

Rehecho el 28/10/2026 con los criterios de los reels (lo frenó Lupa: "LAS
EDITAS" sin tilde, el titular que saltaba de lugar a los 2-3 s, líneas que se
pisaban y sin audio):

- la foto de Martin a cuadro completo, siempre vertical y perdiendo 22 %
  como mucho (Martin, 28/10/2026: nada de foto horizontal sobre la misma foto
  desenfocada; lamina.Capa no lo permite), con un acercamiento lento de 1,00
  a 1,06 en todo el video;
- el texto se arma una sola vez y no se mueve: el antetítulo y el titular
  desde el primer cuadro, y al final aparece (sin moverse nada) la llamada
  "ESCRIBIME POR WHATSAPP / +598 91 962 962" en el lugar que ya estaba
  reservado;
- Anton con 1,0 de interlineado y 1,14 si la línea de abajo lleva tilde;
- todo dentro de la zona segura (historia: más de 250 px arriba, más de 340
  abajo; los dos formatos: más de 70 px de los costados);
- H.264 + una pista AAC en silencio (Instagram la pide; la música la pone
  Martin).

Todo se compone local con Pillow y se codifica con ffmpeg. No usa créditos.
"""
import os
from PIL import Image, ImageDraw
from motor_ads import RAIZ
import lamina as L

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "05-videos")
SEG = 12.0
APARECE_CTA, FUNDIDO = 7.0, 0.4          # segundos
ZOOM = 0.06


def zonas(size, story):
    W, H = size
    if story:
        return 270, H - 360
    return 90, H - 110


def capas(ruta, c, size, story):
    """(Capa de la foto, capa del titular, capa de la llamada). Se calculan
    una vez: así nada cambia de lugar mientras corre el video."""
    W, H = size
    top, bot = zonas(size, story)
    capa = L.Capa(ruta, size)
    reserva = L.alto_cta() + 30
    tit, zona, caja = L.capa_titulo(capa, c["titular"], top, bot, L_MARGEN,
                                    px=112 if story else 100,
                                    max_alto=H // 4 + reserva + 70,
                                    kicker=c.get("kicker"), reserva_abajo=reserva)
    y_cta = caja[3] - L.alto_cta()
    cta = Image.new("RGBA", size, (0, 0, 0, 0))
    L._sombra(cta, lambda d, a: L.dibujar_cta(d, L_MARGEN, y_cta, a, True))
    L.dibujar_cta(ImageDraw.Draw(cta), L_MARGEN, y_cta)
    return capa, tit, cta


L_MARGEN = 80


def render(nombre, ruta, c, size, story):
    """Arma el video y devuelve su ruta."""
    salida = os.path.join(DEST, nombre + ".mp4")
    capa, tit, cta = capas(ruta, c, size, story)
    centro = capa.centro_motivo()
    n = int(SEG * L.FPS)
    enc = L.Codificador(salida, size, SEG)
    a_cta = cta.getchannel("A")
    for f in range(n):
        t = f / L.FPS
        im = L.componer(capa.cuadro(1.0 + ZOOM * f / (n - 1), centro), tit)
        a = L.suave((t - APARECE_CTA) / FUNDIDO)
        if a > 0:
            capa_a = cta.copy()
            capa_a.putalpha(a_cta.point(lambda v: int(v * a)))
            im = L.componer(im, capa_a)
        enc.cuadro(im)
    enc.cerrar()
    return salida
