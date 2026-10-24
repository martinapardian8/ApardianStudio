# -*- coding: utf-8 -*-
"""Posteos de portfolio: una foto de Martin por posteo, en una pagina
editorial (fondo hueso, la foto grande, una linea en Anton y la firma).

Rellenan la cola del calendario entre los carruseles, los reels y los
montajes del sabado. Cada uno lleva su pie con el llamado a WhatsApp.

python3 10-MOTOR/posteos_portfolio.py
Sale a 08-CONTENIDO-INSTAGRAM/09-posteos-portfolio/NN_slug.jpg + indice.json
"""
import os, re, json, unicodedata
from PIL import Image, ImageDraw
from motor_ads import HUESO, NEGRO, ROJO, IMG, RAIZ, display, work, escribir, titular, firma
from recorte import cargar_ok, guardar_cache

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "09-posteos-portfolio")
W, H = 1080, 1350
M = 76
WA = "+598 91 962 962"

CIERRES = {
    "cuadros": ("Fotos de mis viajes, impresas en papel de archivo y enmarcadas. Elegís la foto, el tamaño y el marco, y te llega lista para colgar.",
                "Pedila por WhatsApp: " + WA, "#cuadros #fotografiadeviaje #decoracion #regalos"),
    "eventos": ("Cumpleaños, fiestas de empresa y casamientos chicos: toda la fiesta, sin tope de fotos y con galería para los invitados. Entrega en 10 días.",
                "Contame tu fecha: " + WA, "#eventosuruguay #fotografodeeventos #fiestas #montevideo"),
    "gastronomia": ("Fotos para tu carta, tu delivery y tus redes, en una jornada en tu local. Entrega en 7 días.",
                    "Antes de la temporada: " + WA, "#fotografiagastronomica #restaurantesuruguay #puntadeleste #montevideo"),
    "bodas": ("Ceremonia, salón y fiesta, de principio a fin. Todas las fotos, editadas una por una. Entrega en 10 días.",
              "Contame tu fecha: " + WA, "#fotografodebodas #bodasuruguay #salonesdefiesta #montevideo"),
    "retratos": ("Retratos para tu web, LinkedIn y redes. Luz natural, tu ropa y tu lugar.",
                 "Escribime: " + WA, "#retratoprofesional #marcapersonal #fotografiaderetrato #montevideo"),
}

# (campaña, categoria, archivo, linea de la pieza, primera linea del pie)
POSTEOS = [
    ("cuadros", "naturaleza", "nw__IMG_1985.jpg", "El mar desde arriba.", "El mar desde arriba."),
    ("cuadros", "naturaleza", "v__43.jpg", "Agua que no se mueve.", "Agua que no se mueve."),
    ("cuadros", "naturaleza", "v__57.jpg", "Desde ahí arriba se ve todo.", "Desde ahí arriba se ve todo."),
    ("cuadros", "naturaleza", "v__68.jpg", "Un verano en otro lado.", "Un verano en otro lado."),
    ("eventos", "eventos", "15-sol__IMG_8335.jpg", "Los abrazos no se repiten.", "Los abrazos no se repiten. Por eso estoy atento toda la noche."),
    ("eventos", "eventos", "ivanna-santiago__IMG_4732.jpg", "La mesa, antes de que llegue la gente.", "La mesa, antes de que llegue la gente."),
    ("eventos", "eventos", "v__21.jpg", "Fin de año, con los chicos.", "Fin de año, con los chicos."),
    ("eventos", "eventos", "nw__IMG_4664.jpg", "Las velas se prenden una vez.", "Las velas se prenden una vez."),
    ("gastronomia", "gastronomia", "lokotas__IMG_7562.jpg", "Recién salidas.", "Recién salidas."),
    ("gastronomia", "gastronomia", "v__73.jpg", "Un bocado por cuchara.", "Un bocado por cuchara."),
    ("gastronomia", "gastronomia", "sergio__IMG_7060.jpg", "El corte, antes del fuego.", "El corte, antes del fuego."),
    ("gastronomia", "gastronomia", "sergio__IMG_7420.jpg", "Lo que se come con la mano.", "Lo que se come con la mano."),
    ("bodas", "salones", "golf-a__IMG_4673.jpg", "Cada mesa tiene su centro.", "Cada mesa tiene su centro."),
    ("bodas", "salones", "golf-b__IMG_0350.jpg", "El jardín, de noche.", "El jardín, de noche."),
    ("bodas", "salones", "la-condesa__IMG_3158.jpg", "Un salón listo para la fiesta.", "Un salón listo para la fiesta."),
    ("retratos", "retratos", "juan-luz__IMG_2643.jpg", "Una foto que se parece a vos.", "Una foto que se parece a vos."),
    ("retratos", "retratos", "horacio__IMG_6679.jpg", "En tu lugar, con tu luz.", "En tu lugar, con tu luz."),
    ("retratos", "retratos", "v__118.jpg", "Blanco y negro, sin vueltas.", "Blanco y negro, sin vueltas."),
    ("retratos", "retratos", "v__120.jpg", "Al aire libre.", "Al aire libre."),
    ("retratos", "retratos", "horacio__IMG_6821.jpg", "Cómodo en su lugar.", "Cómodo en su lugar."),
    ("retratos", "retratos", "juan-luz__IMG_2712.jpg", "La ciudad atrás.", "La ciudad atrás."),
    ("eventos", "eventos", "15-sol__IMG_8164.jpg", "Quince, de noche.", "Quince, de noche."),
    ("eventos", "eventos", "v__16.jpg", "La fiesta, entre árboles.", "La fiesta, entre árboles."),
    ("gastronomia", "gastronomia", "lokotas__IMG_7567.jpg", "Una bandeja, cien manos.", "Una bandeja, cien manos."),
    ("gastronomia", "gastronomia", "v__74.jpg", "Del árbol a la mesa.", "Del árbol a la mesa."),
    ("cuadros", "naturaleza", "v__37.jpg", "Rocas, mar y nada más.", "Rocas, mar y nada más."),
]
KICKER = {"cuadros": "Cuadros", "eventos": "Eventos", "gastronomia": "Gastronomía",
          "bodas": "Bodas y salones", "retratos": "Retrato"}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:40]


def pieza(ruta, kicker, linea):
    im = Image.new("RGB", (W, H), HUESO)
    fw, fh = W - 2 * M, 1010
    im.paste(cargar_ok(ruta, (fw, fh)), (M, M))
    d = ImageDraw.Draw(im)
    y = M + fh + 44
    escribir(d, (M, y), kicker.upper(), work(24, "SemiBold"), ROJO, 5)
    titular(d, linea, M, y + 40, W - 2 * M - 260, 64, NEGRO, max_lineas=2)
    firma(d, W - M - 210, y - 4, 1.0, False)
    return im


def main():
    os.makedirs(DEST, exist_ok=True)
    indice = []
    for k, (camp, cat, nombre, linea, primera) in enumerate(POSTEOS, 1):
        ruta = os.path.join(IMG, cat, "web", nombre)
        archivo = "%02d_%s.jpg" % (k, slug(linea))
        pieza(ruta, KICKER[camp], linea).save(os.path.join(DEST, archivo), quality=90, optimize=True)
        cuerpo, cta, tags = CIERRES[camp]
        pie = primera + "\n\n" + cuerpo + "\n\n" + cta + "\n\n" + tags
        indice.append({"n": k, "id": "p%02d" % k, "archivo": archivo, "campana": camp,
                       "foto": cat + "/" + nombre, "titulo": linea.rstrip("."), "pie": pie})
    guardar_cache()
    json.dump(indice, open(os.path.join(DEST, "indice.json"), "w"), ensure_ascii=False, indent=1)
    print(len(indice), "posteos")


if __name__ == "__main__":
    main()
