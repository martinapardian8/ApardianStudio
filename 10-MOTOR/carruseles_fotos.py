# -*- coding: utf-8 -*-
"""Los quince carruseles, rehechos con la estética del IG de Martin
(09-ESTUDIO/ESTETICA_IG.md, 28/10/2026). Reemplaza a carruseles_collage.py,
que queda sin usar (cinta, papel y fotos chicas sobre fondo: Lupa los frenó).

Cada lámina es una foto de Martin de lado a lado, sin marcos ni collage:
- lámina 1: la foto más fuerte con un titular mínimo (Anton blanco, dos
  líneas, a lo sumo un cuarto de la imagen, donde no hay cara ni motivo);
- las del medio: fotos puras;
- la última: la llamada chica a WhatsApp sobre la foto.
Solo fotos verticales que llenen el 4:5 perdiendo 22 % como mucho y sin
partir caras (Martin, 28/10/2026: "nunca una foto horizontal en un lienzo
vertical"). Nada de foto chica sobre la misma foto desenfocada, franjas ni
marco: lamina.Capa no lo permite. Si un tema no tiene verticales para seis
láminas, el carrusel es más corto.

python3 10-MOTOR/carruseles_fotos.py            # todos
python3 10-MOTOR/carruseles_fotos.py 01 04      # algunos
(los que ya salieron no se rehacen: motor_ads.se_puede_escribir)

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


def CAPT(nombre, ventana=0, desde=None):
    """Una captura de la web en el celular; ventana: qué tramo de la página
    (0 el de arriba, 1 el de abajo); desde: dónde empieza la ventana, en
    fracción del alto (0.0 = arriba de todo), si hay que fijarla."""
    p = os.path.join(CAP, nombre)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return p + ("#y%.3f" % desde if desde is not None else "#%d" % ventana)


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
    # fiesta y eventos de empresa, solo verticales nítidas (v__4 y v__5 son de
    # 533 px) y sin marcas ni carteles de
    # clientes a la vista (Martin, 28/10/2026: no va la del cartel de OdontoVita;
    # tampoco la del vaso con marca ni la de las cajas en la ventana)
    "04-fin-de-anio": dict(
        titulo="La fiesta de fin de año pasa una vez.",
        fotos=[F("eventos", "la-condesa__IMG_3167.jpg"), F("empresas", "lokotas__IMG_7661.jpg"),
               F("eventos", "caro60__IMG_9671.jpg"), F("eventos", "nw__IMG_4664.jpg"),
               F("eventos", "nw__IMG_4682.jpg")]),
    # Sin rehacer: todas las fotos del olivo y el aceite son horizontales y el
    # titular habla del olivo. Lupa lo frena hasta que Martin mande verticales
    # o cambie el carrusel.
    "05-producto-del-olivo-a-la-mesa": dict(
        titulo="Del olivo a la mesa.",
        fotos=[F("marcas", "v__83.jpg"), F("marcas", "v__74.jpg"), F("marcas", "v__75.jpg"),
               F("marcas", "v__81.jpg"), F("marcas", "v__77.jpg"), F("marcas", "v__80.jpg"),
               F("marcas", "v__82.jpg")]),
    # edición: retratos y bodas, nunca fiestas (Martin, 28/10/2026)
    "06-edicion-vos-disparas": dict(
        titulo="Vos disparás. Yo edito.",
        fotos=[F("retratos", "v__114.jpg"), F("retratos", "v__118.jpg"),
               F("retratos", "juan-luz__IMG_2669.jpg"), F("retratos", "horacio__IMG_6804.jpg"),
               F("retratos", "v__120.jpg"), F("retratos", "horacio__IMG_6679.jpg")]),
    # la web de Martin, tal cual se ve: capturas reales del celular, sin marco
    # (las de escritorio son horizontales: no van en un 4:5). CAPT(nombre, k):
    # la ventana k de la captura (0 arriba, 1 abajo). La primera, la foto de la
    # portada de la web sin su titular (no se pisa con el del carrusel).
    "07-web-tu-instagram-no-es-tu-web": dict(
        titulo="Tu Instagram no es tu página web.",
        cta=False,     # la última es la página de contacto: ya tiene el WhatsApp
        fotos=[CAPT("m_hero.png", desde=0.0), CAPT("m_galeria.png", 0),
               CAPT("m_servicios.png", 0), CAPT("m_galeria.png", 1),
               CAPT("m_hero.png", 1), CAPT("m_contacto.png", 0)]),
    "08-cuadros-regala-un-lugar": dict(
        titulo="Regalá un lugar.",
        fotos=[F("naturaleza", "nw__IMG_1996.jpg"), F("naturaleza", "nw__IMG_1985.jpg"),
               F("naturaleza", "v__54.jpg"), F("naturaleza", "nw__IMG_2011_2.jpg"),
               F("naturaleza", "v__56.jpg"), F("naturaleza", "v__43.jpg")]),
    # shows y ensayos que fotografió Martin: el titular habla del servicio.
    # Música tiene dos fotos verticales: el carrusel queda de dos láminas.
    "09-musica-de-la-idea-al-master": dict(
        titulo="Tu tema, de la idea al master.",
        fotos=[F("musica", "la-estacion__IMG_8043.jpg"), F("musica", "la-estacion__IMG_8091.jpg")]),
    "10-cuadros-un-viaje-que-se-cuelga": dict(
        titulo="Un viaje que se cuelga.",
        fotos=[F("naturaleza", "nw__IMG_1986.jpg"), F("naturaleza", "v__59.jpg"),
               F("naturaleza", "nw__IMG_1999.jpg"), F("naturaleza", "v__53.jpg"),
               F("naturaleza", "v__45.jpg"), F("naturaleza", "v__57.jpg")]),
    # afuera: el jardín del salón, de noche (las fotos de gente al aire libre
    # son horizontales)
    "11-eventos-el-verano-se-festeja": dict(
        titulo="El verano se festeja afuera.",
        fotos=[F("salones", "golf-b__IMG_0346.jpg"), F("salones", "golf-b__IMG_0350.jpg"),
               F("salones", "golf-b__IMG_0339.jpg"), F("salones", "golf-b__IMG_0332.jpg"),
               F("salones", "golf-b__IMG_0358.jpg")]),
    "12-gastronomia-carta-de-verano": dict(
        titulo="Tu carta de verano entra por los ojos.",
        fotos=[F("gastronomia", "v__69.jpg"), F("gastronomia", "sergio__IMG_7420.jpg"),
               F("gastronomia", "alfajor__IMG_5427.jpg"), F("gastronomia", "nw__IMG_7086.jpg"),
               F("gastronomia", "sergio__IMG_7488.jpg"), F("gastronomia", "sergio__IMG_7503.jpg")]),
    "13-bodas-entre-el-si-y-la-fiesta": dict(
        titulo="Entre el sí y la fiesta pasa todo.",
        fotos=[F("bodas", "portfolio__IMG_8771.jpg"), F("salones", "golf-b__IMG_0366.jpg"),
               F("salones", "golf-a__IMG_4667.jpg"), F("salones", "golf-a__IMG_4674.jpg"),
               F("salones", "golf-a__IMG_4694.jpg"), F("bodas", "nw__IMG_4697.jpg")]),
    "14-edicion-en-enero-no-se-duerme": dict(
        titulo="En enero no se duerme.",
        fotos=[F("retratos", "juan-luz__IMG_2643.jpg"), F("retratos", "v__115.jpg"),
               F("retratos", "juan-luz__IMG_2696.jpg"), F("retratos", "horacio__IMG_6905.jpg"),
               F("retratos", "v__117.jpg"), F("retratos", "nw__IMG_6668.jpg")]),
    # la marca de Martin: sus aplicaciones (mockups: el pie lo dice), solo las
    # verticales (el neón y el manual son horizontales)
    "15-marca-360-una-marca-entera": dict(
        titulo="Una marca se ve igual en todos lados.",
        fotos=[M("05-objetos/n1128_cartel_calado.jpg"), M("02-papeleria/pack_completo.jpg"),
               M("02-papeleria/caja_prints.jpg"),
               M("04-ropa/gorra_hueso.jpg"), M("02-papeleria/bolsa_papel.jpg"),
               M("04-ropa/remera_negra.jpg")]),
}


def es_captura(ruta):
    return ruta.startswith(CAP)


# Los reels (9:16) usan las fotos del carrusel que llenan el 9:16; las que
# solo llenan el 4:5 quedan afuera. Si quedan pocas, se suman otras verticales
# del mismo tema (acá, elegidas para que no salgan esos mismos días).
REEL_EXTRA = {
    "08-cuadros-regala-un-lugar": [F("naturaleza", "nw__FullSizeRender_6.jpg"), F("naturaleza", "v__53.jpg")],
    "10-cuadros-un-viaje-que-se-cuelga": [F("naturaleza", "v__54.jpg"), F("naturaleza", "v__56.jpg")],
}
MIN_REEL = 4
# Reels con otra selección que su carrusel (si hace falta): {slug: [fotos]}
REEL_FOTOS = {}


def llena(ruta, size):
    """¿La foto (o captura) llena este cuadro sin franjas?"""
    if es_captura(ruta):
        return Image.open(ruta.partition("#")[0]).size[0] < Image.open(ruta.partition("#")[0]).size[1]
    from motor_ads import apta
    return apta(ruta, size)


def fotos_reel(slug, size=(1080, 1920)):
    """Las fotos del reel: las del carrusel que llenan el 9:16, y si son menos
    de MIN_REEL, las de REEL_EXTRA. Lista vacía si no alcanza."""
    fs = [f for f in REEL_FOTOS.get(slug, CARRUSELES[slug]["fotos"]) if llena(f, size)]
    for f in REEL_EXTRA.get(slug, []):
        if len(fs) >= MIN_REEL + 1:
            break
        if f not in fs and llena(f, size):
            fs.append(f)
    return fs if len(fs) >= 3 else []


class CapaCaptura(L.Capa):
    """Una captura de la web de Martin, tal cual (no es una foto, no hay caras
    que cuidar). La del celular llena el cuadro con una ventana de la página
    (la de arriba, como se ve al abrir la web, o la de abajo: 'archivo.png#1').
    La de escritorio es horizontal: en un cuadro vertical no va (Martin,
    28/10/2026); solo en uno horizontal, entera."""

    def __init__(self, ruta, size):
        ruta, _, ventana = ruta.partition("#")
        fija = float(ventana[1:]) if ventana.startswith("y") else None
        ventana = 0 if fija is not None else int(ventana or 0)
        self.ruta, self.size = ruta, size
        W, H = size
        self.orig = Image.open(ruta).convert("RGB")
        sw, sh = self.orig.size
        if sw < sh:
            ch = min(int(round(sw * H / W)), sh)
            self.modo, self.fondo = "sangre", None
            # la ventana empieza y termina en una fila lisa: ninguna letra
            # queda cortada por el borde; la de abajo, lo más abajo posible
            g = Image.open(ruta).convert("L")
            def ruido(y):
                fila = g.crop((0, max(0, y - 2), sw, min(sh, y + 2))).getextrema()
                return fila[1] - fila[0]
            meta = 0 if ventana == 0 else sh - ch
            y0 = min(range(0, sh - ch + 1, 4),
                     key=lambda y: (ruido(y) + ruido(y + ch - 1), abs(y - meta)))
            if ventana and y0 < (sh - ch) * 0.5:
                # que no repita la de arriba: entre las de la mitad de abajo
                y0 = min(range((sh - ch) // 2, sh - ch + 1, 4),
                         key=lambda y: (ruido(y) + ruido(y + ch - 1), abs(y - meta)))
            if fija is not None:
                y0 = int(round(fija * (sh - ch)))
            self.recorte = (0, y0, sw, ch)
            self.caja = (0, 0, W, H)
        elif H > W:
            raise ValueError(os.path.basename(ruta) + ": captura horizontal, no va en un cuadro vertical")
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


# fotos que van enteras aunque el recorte sea chico: solo en cuadros
# horizontales (en uno vertical, Capa no lo permite)
ENTERAS = {M("01-logo/n702_neon.jpg")}


def capa(ruta, size):
    if es_captura(ruta):
        return CapaCaptura(ruta, size)
    return L.Capa(ruta, size, entera=ruta in ENTERAS)


def laminas(slug, size=POST, top=MARGEN, bot=None, margen=MARGEN, fotos=None):
    """[(Capa, capa_texto RGBA o None)] de un carrusel. Lo usa también el reel
    (con sus fotos: fotos_reel)."""
    c = CARRUSELES[slug]
    fotos = fotos or c["fotos"]
    bot = bot or size[1] - MARGEN
    out = []
    n = len(fotos)
    for i, ruta in enumerate(fotos):
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
    from motor_ads import se_puede_escribir
    if not se_puede_escribir(os.path.join(carpeta, "01.jpg")):
        print("  ", slug, "ya salió: no se rehace")
        return carpeta, 0
    lams = laminas(slug)          # si alguna foto no llena el 4:5, falla antes de borrar nada
    for f in glob.glob(os.path.join(carpeta, "*.jpg")):
        os.remove(f)
    ims = []
    for i, (k, txt) in enumerate(lams):
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
        try:
            carpeta, n = armar(slug)
        except ValueError as e:
            print("  SIN REHACER", slug, "·", e)
            continue
        hechos[slug] = n
        print(slug, n, "láminas", flush=True)
    todos()
    print(json.dumps(hechos, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
