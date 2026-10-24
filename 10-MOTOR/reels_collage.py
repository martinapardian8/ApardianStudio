# -*- coding: utf-8 -*-
"""Reels 9:16 a partir de los carruseles collage, sin gastar creditos.

El carrusel entero (las seis laminas pegadas) se recorre de izquierda a
derecha con una camara suave, y al final queda quieto en el pedido.
Sale sin musica: en Instagram se le pone un tema (idealmente, uno tuyo).

python3 10-MOTOR/reels_collage.py            # todos
python3 10-MOTOR/reels_collage.py 01 04      # algunos
"""
import os, sys, glob, subprocess, tempfile
from PIL import Image, ImageDraw
from motor_ads import HUESO, NEGRO, ROJO, display, work, escribir, titular, firma
from collage import textura

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COL = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "06-carruseles-collage")
DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "07-reels-collage")
W, H = 1080, 1920
ALTO_TIRA = 1100
Y_TIRA = 470
DUR, PAN0, PAN1 = 15.0, 1.2, 12.6       # segundos: total, empieza y termina el paseo

OSCUROS = ("02", "04", "06", "09", "11", "13", "14")
TITULOS = {"01": ("Bodas · temporada 26/27", "Un sí dura un segundo."),
           "02": ("Gastronomía", "La gente come con los ojos."),
           "03": ("Marca personal", "No entra en una selfie."),
           "04": ("Eventos · diciembre", "La fiesta de fin de año pasa una vez."),
           "05": ("Producto", "Del olivo a la mesa."),
           "06": ("Para fotógrafos", "Vos disparás. Yo edito."),
           "07": ("Páginas web", "Tu Instagram no es tu página web."),
           "08": ("Cuadros", "Regalá un lugar."),
           "09": ("Producción musical", "De la idea al master."),
           "10": ("Cuadros · Navidad y Reyes", "Un viaje que se cuelga."),
           "11": ("Eventos · verano", "El verano se festeja afuera."),
           "12": ("Gastronomía · temporada", "Tu carta de verano entra por los ojos."),
           "13": ("Bodas", "Entre el sí y la fiesta pasa todo."),
           "14": ("Para fotógrafos", "En enero no se duerme."),
           "15": ("Marca 360", "Una marca se ve igual en todos lados.")}


def fondo(num):
    oscuro = num in OSCUROS
    bg = textura("carbon" if oscuro else "hueso", W, H)
    d = ImageDraw.Draw(bg)
    tinta = HUESO if oscuro else NEGRO
    kick, tit = TITULOS[num]
    escribir(d, (76, 150), kick.upper(), work(28, "SemiBold"), ROJO, 6)
    titular(d, tit, 76, 196, W - 152, 104, tinta, max_lineas=2, alto_max=250)
    y = Y_TIRA + ALTO_TIRA + 70
    escribir(d, (76, y), "ESCRIBIME POR WHATSAPP", work(26, "SemiBold"), tinta, 5)
    escribir(d, (76, y + 40), "+598 91 962 962", display(76), ROJO)
    firma(d, W - 76 - 300, H - 170, 1.5, oscuro)
    return bg


def panorama(carpeta):
    lams = sorted(glob.glob(os.path.join(carpeta, "[0-9][0-9].jpg")))
    ims = [Image.open(p).convert("RGB") for p in lams]
    p = Image.new("RGB", (sum(i.width for i in ims), ims[0].height))
    x = 0
    for i in ims:
        p.paste(i, (x, 0)); x += i.width
    esc = ALTO_TIRA / p.height
    return p.resize((int(p.width * esc), ALTO_TIRA), Image.LANCZOS)


def reel(carpeta):
    num = os.path.basename(carpeta)[:2]
    os.makedirs(DEST, exist_ok=True)
    out = os.path.join(DEST, os.path.basename(carpeta) + ".mp4")
    with tempfile.TemporaryDirectory() as tmp:
        fondo(num).save(os.path.join(tmp, "bg.png"))
        panorama(carpeta).save(os.path.join(tmp, "pano.png"))
        # camara: quieta, paseo con aceleracion suave (smoothstep) y quieta al final
        x = (f"-(overlay_w-main_w)*st(0,clip((t-{PAN0})/{PAN1 - PAN0},0,1))"
             f"*ld(0)*(3-2*ld(0))")
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-loop", "1", "-framerate", "30", "-i", os.path.join(tmp, "bg.png"),
               "-loop", "1", "-framerate", "30", "-i", os.path.join(tmp, "pano.png"),
               "-filter_complex", f"[0][1]overlay=x='{x}':y={Y_TIRA}:shortest=1,format=yuv420p",
               "-t", str(DUR), "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
               "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
        # portada para la grilla del perfil
        Image.open(os.path.join(tmp, "bg.png")).save(out.replace(".mp4", "_portada.jpg"), quality=88)
    return out


def main(nums):
    for c in sorted(glob.glob(os.path.join(COL, "[0-9][0-9]-*"))):
        if nums and os.path.basename(c)[:2] not in nums:
            continue
        print(reel(c))


if __name__ == "__main__":
    main(sys.argv[1:])
