# -*- coding: utf-8 -*-
"""Reels 9:16 de los carruseles (carruseles_fotos.py), sin gastar créditos.

Cada foto del carrusel a pantalla completa, de 1,5 a 2,5 s, con un
acercamiento lento (1,00 → 1,06) y cortes secos. Solo fotos verticales que
llenen el 9:16 perdiendo 22 % como mucho (Martin, 28/10/2026: "nunca una foto
horizontal en un lienzo vertical"): las del carrusel que no lo llenan quedan
afuera y, si quedan pocas, se suman otras del mismo tema
(carruseles_fotos.fotos_reel). Si no hay al menos tres, el reel no se rehace
y Lupa lo frena.

Texto solo dos veces y quieto: el titular en la primera foto y, en la última,
"ESCRIBIME POR WHATSAPP / +598 91 962 962". Todo dentro de la zona segura de
Instagram: más de 250 px del borde de arriba, más de 340 px del de abajo y
más de 70 px de los costados.

Audio: una pista AAC en silencio (la API de Instagram la pide). La música la
pone Martin (idealmente, un tema suyo).

python3 10-MOTOR/reels_collage.py            # todos
python3 10-MOTOR/reels_collage.py 01 04      # algunos

Sale a 08-CONTENIDO-INSTAGRAM/07-reels-collage/<slug>.mp4 y <slug>_portada.jpg
(la portada es la primera foto con el titular).
"""
import os, sys
import lamina as L
import carruseles_fotos as C
from motor_ads import RAIZ

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "07-reels-collage")
STORY = (1080, 1920)
TOP, BOT, MARGEN = 270, 1920 - 360, 80       # zona segura, con un poco de aire
ZOOM = 0.06


def duraciones(n):
    """La primera y la última, 2,5 s (se leen); las del medio, lo que haga
    falta para que el reel dure de 12 a 18 s, entre 1,5 y 2,5 s cada una."""
    if n <= 2:
        return [2.5] * n
    medio = max(1.5, min(2.5, (15.0 - 5.0) / (n - 2)))
    ds = [2.5] + [medio] * (n - 2) + [2.5]
    total = sum(ds)
    if total < 12:
        ds = [d * 12 / total for d in ds]
    return ds


def reel(slug):
    out = os.path.join(DEST, slug + ".mp4")
    fotos = C.fotos_reel(slug, STORY)
    if not fotos:
        raise ValueError("no hay tres fotos verticales del tema que llenen el 9:16")
    lams = C.laminas(slug, STORY, TOP, BOT, MARGEN, fotos=fotos)
    ds = duraciones(len(lams))
    total = sum(int(round(d * L.FPS)) for d in ds) / L.FPS
    enc = L.Codificador(out, STORY, total)
    for i, ((capa, txt), d) in enumerate(zip(lams, ds)):
        n = int(round(d * L.FPS))
        centro = capa.centro_motivo()
        for f in range(n):
            z = 1.0 + ZOOM * f / max(1, n - 1)
            im = L.componer(capa.cuadro(z, centro), txt)
            if i == 0 and f == 0:
                im.save(out.replace(".mp4", "_portada.jpg"), "JPEG", quality=90)
            enc.cuadro(im)
    enc.cerrar()
    return out, total


def main(nums):
    from motor_ads import se_puede_escribir
    os.makedirs(DEST, exist_ok=True)
    for slug in C.CARRUSELES:
        if nums and slug[:2] not in nums:
            continue
        if not se_puede_escribir(os.path.join(DEST, slug + ".mp4")):
            print("  ", slug, "ya salió: no se rehace")
            continue
        try:
            out, total = reel(slug)
        except ValueError as e:
            print("  SIN REHACER", slug, "·", e, flush=True)
            continue
        print(os.path.relpath(out, RAIZ), f"{total:.1f} s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
