# -*- coding: utf-8 -*-
"""Lámina "manual de marca" para la fila Marca 360 de la web.

El caso es la propia marca APARDIAN (real): logo, paleta, tipografías y
piezas ya publicadas (carruseles collage e ícono de la app). Nada inventado.

    python3 10-MOTOR/marca360_lamina.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUE = os.path.join(RAIZ, "10-MOTOR", "fuentes")
OUT = os.path.join(RAIZ, "05-WEB", "img", "marca360")
HUESO, NEGRO, ROJO, GRIS = (248, 247, 246), (23, 23, 23), (255, 0, 51), (118, 115, 113)
W, H = 1920, 1200


def f(nombre, t):
    return ImageFont.truetype(os.path.join(FUE, nombre), t)


def anton(t): return f("Anton-Regular.ttf", t)
def work(t, peso=400):
    fo = f("WorkSans.ttf", t)
    try: fo.set_variation_by_axes([peso])
    except Exception: pass
    return fo


def espaciado(d, xy, txt, fo, color, track):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=fo, fill=color)
        x += d.textlength(ch, font=fo) + track
    return x


def main():
    os.makedirs(OUT, exist_ok=True)
    im = Image.new("RGB", (W, H), HUESO)
    d = ImageDraw.Draw(im)
    m = 96
    # cabecera de manual
    espaciado(d, (m, 70), "MANUAL DE MARCA · APARDIAN STUDIO", work(22, 500), GRIS, 5)
    d.line([(m, 112), (W - m, 112)], fill=(220, 218, 215), width=2)
    espaciado(d, (W - m - 230, 70), "PÁG. 01 / 12", work(22, 500), GRIS, 5)
    # logo
    fo = anton(230)
    d.text((m - 6, 150), "APARDIAN", font=fo, fill=NEGRO)
    x = m - 6 + d.textlength("APARDIAN", font=fo) + 8
    d.rectangle([x, 150 + 222, x + 40, 150 + 262], fill=ROJO)
    espaciado(d, (m, 450), "LOGO  ·  ANTON EN MAYÚSCULAS + EL PUNTO ROJO", work(20, 500), GRIS, 4)
    # paleta
    y0 = 540
    for i, (nom, col, hx) in enumerate([("HUESO", HUESO, "#F8F7F6"), ("NEGRO", NEGRO, "#171717"), ("ROJO", ROJO, "#FF0033")]):
        x0 = m + i * 250
        d.rectangle([x0, y0, x0 + 220, y0 + 220], fill=col, outline=(214, 211, 207) if col == HUESO else None, width=2)
        d.text((x0, y0 + 236), nom, font=anton(34), fill=NEGRO)
        espaciado(d, (x0, y0 + 284), hx, work(22, 500), GRIS, 2)
    # tipografías
    y1 = 900
    d.text((m, y1), "Aa", font=anton(150), fill=NEGRO)
    d.text((m + 190, y1 + 22), "ANTON", font=anton(44), fill=NEGRO)
    espaciado(d, (m + 190, y1 + 84), "TÍTULOS · SIEMPRE EN MAYÚSCULAS", work(19, 500), GRIS, 3)
    d.text((m + 760, y1 + 8), "Aa", font=work(140, 400), fill=NEGRO)
    d.text((m + 960, y1 + 22), "Work Sans", font=work(44, 500), fill=NEGRO)
    espaciado(d, (m + 960, y1 + 84), "TEXTO · ETIQUETAS ESPACIADAS", work(19, 500), GRIS, 3)
    # piezas reales: dos carruseles y el ícono de la app
    pz = [os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "06-carruseles-collage", "01-bodas-un-si", "01.jpg"),
          os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "06-carruseles-collage", "09-musica-de-la-idea-al-master", "01.jpg")]
    xa = 1180
    espaciado(d, (xa, 150), "APLICACIONES", work(20, 500), GRIS, 4)
    for i, p in enumerate(pz):
        a = Image.open(p).convert("RGB").resize((300, 375), Image.LANCZOS)
        im.paste(a, (xa + i * 330, 196))
    ic = Image.open(os.path.join(RAIZ, "13-APP-CENTRO", "icono", "icono_512.png")).convert("RGBA").resize((200, 200), Image.LANCZOS)
    im.paste(ic, (xa, 640), ic)
    d.text((xa + 230, 668), "Ícono de app", font=anton(40), fill=NEGRO)
    espaciado(d, (xa + 230, 724), "LA A Y EL PUNTO, SOBRE NEGRO", work(19, 500), GRIS, 3)
    espaciado(d, (xa, 600), "CARRUSELES PARA INSTAGRAM", work(19, 500), GRIS, 3)
    # pie
    d.line([(m, H - 96), (W - m, H - 96)], fill=(220, 218, 215), width=2)
    espaciado(d, (m, H - 74), "CASO: NUESTRA PROPIA MARCA", work(22, 600), ROJO, 5)
    espaciado(d, (W - m - 330, H - 74), "APARDIANSTUDIO.COM", work(22, 500), GRIS, 5)
    im.save(os.path.join(OUT, "manual_apardian.jpg"), quality=86, optimize=True, progressive=True)
    im.resize((960, 600), Image.LANCZOS).save(os.path.join(OUT, "manual_apardian_960.jpg"), quality=84, optimize=True, progressive=True)
    print("ok")


if __name__ == "__main__":
    main()
