# -*- coding: utf-8 -*-
"""Los quince carruseles, rehechos con la estética del IG de Martin
(09-ESTUDIO/ESTETICA_IG.md, 28/10/2026). Reemplaza a carruseles_collage.py,
que queda sin usar (cinta, papel y fotos chicas sobre fondo: Lupa los frenó).

Cada lámina es una foto de Martin de lado a lado, sin marcos ni collage:
- lámina 1: la foto más fuerte con un titular mínimo (Anton blanco, dos
  líneas, a lo sumo un cuarto de la imagen, donde no hay cara ni motivo);
- las del medio: fotos puras;
- la última: la llamada chica a WhatsApp sobre la foto.
Si para llenar el 4:5 hay que perder más del 22 % de la foto, va entera de
lado a lado sobre la misma foto desenfocada (lamina.Capa).

python3 10-MOTOR/carruseles_fotos.py            # todos
python3 10-MOTOR/carruseles_fotos.py 01 04      # algunos

Sale a 08-CONTENIDO-INSTAGRAM/06-carruseles-collage/<slug>/NN.jpg (los mismos
nombres que usa el calendario), con _panorama.jpg en cada carpeta y
00_TODOS.jpg para ver todo de un vistazo (esos dos no se suben).
"""
import os, sys, glob, json
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from motor_ads import RAIZ, IMG, work, display, escribir
import lamina as L

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "06-carruseles-collage")
POST = (1080, 1350)
MARGEN = 80                 # más de 70 px de los costados (la grilla corta a 3:4)
MARCA = os.path.join(RAIZ, "04-VIDEOS-IA", "contenido ia", "marca")
CAP = os.path.join(RAIZ, "10-MOTOR", "capturas_web")


def F(cat, nombre):
    p = os.path.join(IMG, cat, "web", nombre)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return p


def M(rel):
    """Una aplicación de la marca de Martin (mockup de 04-VIDEOS-IA)."""
    return os.path.join(MARCA, rel)


# Cada carrusel: titular de la lámina 1 y sus fotos en orden (la primera es la
# portada, la última lleva la llamada a WhatsApp). Se alternan fríos y
# cálidos, y ninguna foto se repite entre carruseles (lupa.py lo revisa con
# el calendario). Nada del fuego ni de las empanadas en gastronomía: la foto
# muestra el plato (fotos.json, 'contenido').
CARRUSELES = {
    "01-bodas-un-si": dict(
        titulo="Un sí dura un segundo.",
        fotos=[F("bodas", "portfolio__IMG_8771.jpg"), F("bodas", "nw__IMG_9717.jpg"),
               F("salones", "golf-b__IMG_0346.jpg"), F("bodas", "portfolio__IMG_9601.jpg"),
               F("bodas", "portfolio__IMG_8769.jpg"), F("bodas", "nw__IMG_4672.jpg")]),
    "02-gastronomia-cuatro-fotos": dict(
        titulo="La gente come con los ojos.",
        fotos=[F("gastronomia", "sergio__IMG_7391.jpg"), F("gastronomia", "nw__IMG_7064.jpg"),
               F("gastronomia", "alfajor__IMG_5423.jpg"), F("gastronomia", "sergio__IMG_7234.jpg"),
               F("gastronomia", "v__73.jpg"), F("gastronomia", "v__70.jpg")]),
    "03-marca-personal-cinco-usos": dict(
        titulo="Tu marca personal no entra en una selfie.",
        fotos=[F("retratos", "horacio__IMG_6701.jpg"), F("retratos", "horacio__IMG_6475.jpg"),
               F("retratos", "horacio__IMG_6256.jpg"), F("retratos", "horacio__IMG_6499.jpg"),
               F("retratos", "nw__IMG_6981.jpg"), F("retratos", "horacio__IMG_6581.jpg")]),
    # eventos de empresa reales: OdontoVita, Lokotas y la fiesta de fin de año
    # con Papá Noel (la que ya se usó como "fiesta de empresa" en historias)
    "04-fin-de-anio": dict(
        titulo="La fiesta de fin de año pasa una vez.",
        fotos=[F("eventos", "v__13.jpg"), F("empresas", "odontovita__IMG_5142.jpg"),
               F("empresas", "lokotas__IMG_7552.jpg"), F("empresas", "odontovita__IMG_4928.jpg"),
               F("empresas", "odontovita__IMG_5182.jpg"), F("eventos", "v__21.jpg")]),
    "05-producto-del-olivo-a-la-mesa": dict(
        titulo="Del olivo a la mesa.",
        fotos=[F("marcas", "v__83.jpg"), F("marcas", "v__74.jpg"), F("marcas", "v__75.jpg"),
               F("marcas", "v__81.jpg"), F("marcas", "v__77.jpg"), F("marcas", "v__80.jpg"),
               F("marcas", "v__82.jpg")]),
    # edición: retratos y bodas, nunca fiestas (Martin, 28/10/2026)
    "06-edicion-vos-disparas": dict(
        titulo="Vos disparás. Yo edito.",
        fotos=[F("retratos", "v__114.jpg"), F("retratos", "v__118.jpg"),
               F("bodas", "nw__IMG_9726.jpg"), F("retratos", "v__119.jpg"),
               F("retratos", "horacio__IMG_6804.jpg"), F("retratos", "v__116.jpg")]),
    # la web de Martin, tal cual se ve: capturas reales, sin marco de celular
    "07-web-tu-instagram-no-es-tu-web": dict(
        titulo="Tu Instagram no es tu página web.",
        fotos=[os.path.join(CAP, "d_web.png"), os.path.join(CAP, "m_galeria.png"),
               os.path.join(CAP, "d_trabajos.png"), os.path.join(CAP, "m_servicios.png"),
               os.path.join(CAP, "d_galeria.png"), os.path.join(CAP, "d_contacto.png")]),
    "08-cuadros-regala-un-lugar": dict(
        titulo="Regalá un lugar.",
        fotos=[F("naturaleza", "nw__IMG_1996.jpg"), F("naturaleza", "v__28.jpg"),
               F("naturaleza", "v__54.jpg"), F("naturaleza", "v__23.jpg"),
               F("naturaleza", "v__43.jpg"), F("naturaleza", "v__58.jpg")]),
    # shows y ensayos que fotografió Martin: el titular habla del servicio
    "09-musica-de-la-idea-al-master": dict(
        titulo="Tu tema, de la idea al master.",
        fotos=[F("musica", "la-estacion__IMG_8043.jpg"), F("musica", "nw__IMG_7237.jpg"),
               F("musica", "la-estacion__IMG_8038.jpg"), F("musica", "nw__IMG_7233.jpg"),
               F("musica", "la-estacion__IMG_8052.jpg"), F("musica", "la-estacion__IMG_8091.jpg")]),
    "10-cuadros-un-viaje-que-se-cuelga": dict(
        titulo="Un viaje que se cuelga.",
        fotos=[F("naturaleza", "nw__FullSizeRender_6.jpg"), F("naturaleza", "v__26.jpg"),
               F("naturaleza", "nw__IMG_1985.jpg"), F("naturaleza", "v__40.jpg"),
               F("naturaleza", "v__63.jpg"), F("naturaleza", "v__53.jpg")]),
    "11-eventos-el-verano-se-festeja": dict(
        titulo="El verano se festeja afuera.",
        fotos=[F("eventos", "ivanna-santiago__IMG_4794.jpg"), F("eventos", "15-sol__IMG_8179.jpg"),
               F("eventos", "ivanna-santiago__IMG_4865.jpg"), F("eventos", "v__14.jpg"),
               F("eventos", "15-sol__IMG_8164.jpg"), F("eventos", "v__22.jpg")]),
    "12-gastronomia-carta-de-verano": dict(
        titulo="Tu carta de verano entra por los ojos.",
        fotos=[F("gastronomia", "v__69.jpg"), F("gastronomia", "v__71.jpg"),
               F("gastronomia", "sergio__IMG_7420.jpg"), F("gastronomia", "sergio__IMG_7258.jpg"),
               F("gastronomia", "nw__IMG_7086.jpg"), F("gastronomia", "sergio__IMG_7503.jpg")]),
    "13-bodas-entre-el-si-y-la-fiesta": dict(
        titulo="Entre el sí y la fiesta pasa todo.",
        fotos=[F("bodas", "portfolio__IMG_9582.jpg"), F("salones", "golf-b__IMG_0339.jpg"),
               F("bodas", "portfolio__IMG_9594.jpg"), F("salones", "golf-b__IMG_0332.jpg"),
               F("bodas", "golf-a__IMG_4684.jpg"), F("bodas", "nw__IMG_4697.jpg")]),
    "14-edicion-en-enero-no-se-duerme": dict(
        titulo="En enero no se duerme.",
        fotos=[F("retratos", "juan-luz__IMG_2643.jpg"), F("retratos", "v__115.jpg"),
               F("retratos", "juan-luz__IMG_2696.jpg"), F("retratos", "horacio__IMG_6828.jpg"),
               F("retratos", "v__117.jpg"), F("retratos", "juan-luz__IMG_2712.jpg")]),
    # la marca de Martin: el manual y sus aplicaciones (mockups: el pie lo dice)
    "15-marca-360-una-marca-entera": dict(
        titulo="Una marca se ve igual en todos lados.",
        fotos=[M("01-logo/n702_neon.jpg"), os.path.join(IMG, "marca360", "manual_apardian.jpg"),
               M("02-papeleria/caja_prints.jpg"),
               M("04-ropa/gorra_hueso.jpg"), M("02-papeleria/bolsa_papel.jpg"),
               M("04-ropa/remera_negra.jpg")]),
}


def es_captura(ruta):
    return ruta.startswith(CAP)


class CapaCaptura(L.Capa):
    """Una captura de la web de Martin, tal cual (no es una foto, no hay caras
    que cuidar). La del celular muestra la primera pantalla, de arriba, como
    se ve al abrir la web; la de escritorio va entera, sin recortar letras."""

    def __init__(self, ruta, size):
        self.ruta, self.size = ruta, size
        W, H = size
        self.orig = Image.open(ruta).convert("RGB")
        sw, sh = self.orig.size
        if sw < sh:
            ch = min(int(round(sw * H / W)), sh)
            self.modo, self.fondo = "sangre", None
            # la ventana empieza y termina en una fila lisa: ninguna letra
            # queda cortada por el borde
            g = Image.open(ruta).convert("L")
            def ruido(y):
                fila = g.crop((0, max(0, y - 2), sw, min(sh, y + 2))).getextrema()
                return fila[1] - fila[0]
            y0 = min(range(0, sh - ch + 1, 4), key=lambda y: (ruido(y) + ruido(y + ch - 1), y))
            self.recorte = (0, y0, sw, ch)
            self.caja = (0, 0, W, H)
        else:
            self.modo = "entera"
            self.recorte = (0, 0, sw, sh)
            fh = int(round(W * sh / sw))
            self.caja = (0, (H - fh) // 2, W, fh)
            f = self.orig.resize((W // 4, fh // 4), Image.BILINEAR).resize((W // 4, H // 4))
            f = f.filter(ImageFilter.GaussianBlur(12)).resize((W, H), Image.BICUBIC)
            self.fondo = ImageEnhance.Brightness(f).enhance(0.38)

    def caras(self, conf=0.6, con_conf=False):
        return []

    def centro_motivo(self):
        return None


# fotos que van enteras aunque el recorte sea chico: el recorte cortaría el
# motivo (el punto rojo del logo en neón queda pegado al borde)
ENTERAS = {M("01-logo/n702_neon.jpg")}


def capa(ruta, size):
    if es_captura(ruta):
        return CapaCaptura(ruta, size)
    return L.Capa(ruta, size, entera=ruta in ENTERAS)


def laminas(slug, size=POST, top=MARGEN, bot=None, margen=MARGEN):
    """[(Capa, capa_texto RGBA o None)] de un carrusel. Lo usa también el reel."""
    c = CARRUSELES[slug]
    bot = bot or size[1] - MARGEN
    out = []
    n = len(c["fotos"])
    for i, ruta in enumerate(c["fotos"]):
        k = capa(ruta, size)
        txt = None
        if i == 0 and c.get("titulo"):
            txt = L.capa_titulo(k, c["titulo"], top, bot, margen,
                                px=104 if size[1] <= 1350 else 112)[0]
        elif i == n - 1 and c.get("cta", True):
            txt = L.capa_cta(k, top, bot, margen)[0]
        out.append((k, txt))
    return out


def armar(slug):
    carpeta = os.path.join(DEST, slug)
    os.makedirs(carpeta, exist_ok=True)
    for f in glob.glob(os.path.join(carpeta, "*.jpg")):
        os.remove(f)
    ims = []
    for i, (k, txt) in enumerate(laminas(slug)):
        im = L.componer(k.cuadro(), txt)
        im.save(os.path.join(carpeta, f"{i + 1:02d}.jpg"), "JPEG", quality=92,
                optimize=True, subsampling=0)
        ims.append(im)
    # el carrusel entero de un vistazo (no se sube)
    th = 450
    tw = int(th * POST[0] / POST[1])
    p = Image.new("RGB", (tw * len(ims) + 6 * (len(ims) - 1), th), (255, 255, 255))
    for i, im in enumerate(ims):
        p.paste(im.resize((tw, th), Image.LANCZOS), (i * (tw + 6), 0))
    p.save(os.path.join(carpeta, "_panorama.jpg"), quality=85)
    return carpeta, len(ims)


def todos():
    """00_TODOS.jpg: una fila por carrusel, con el nombre."""
    filas = []
    for slug in CARRUSELES:
        fs = sorted(glob.glob(os.path.join(DEST, slug, "[0-9][0-9].jpg")))
        filas.append((slug, fs))
    tw, th, et = 270, 337, 34
    W = tw * 8
    im = Image.new("RGB", (W, len(filas) * (th + et)), (248, 247, 246))
    d = ImageDraw.Draw(im)
    for r, (slug, fs) in enumerate(filas):
        y = r * (th + et)
        escribir(d, (8, y + 6), f"{slug} · {len(fs)} láminas", work(20, "SemiBold"), (23, 23, 23))
        for i, f in enumerate(fs):
            im.paste(Image.open(f).resize((tw - 4, th - 4), Image.LANCZOS), (i * tw + 2, y + et))
    im.save(os.path.join(DEST, "00_TODOS.jpg"), quality=82)


def fotos_usadas():
    """{slug: [ruta relativa]} para revisar repeticiones."""
    return {s: [os.path.relpath(f, RAIZ) for f in c["fotos"]] for s, c in CARRUSELES.items()}


def main(nums):
    hechos = {}
    for slug in CARRUSELES:
        if nums and slug[:2] not in nums:
            continue
        carpeta, n = armar(slug)
        hechos[slug] = n
        print(slug, n, "láminas", flush=True)
    todos()
    print(json.dumps(hechos, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
