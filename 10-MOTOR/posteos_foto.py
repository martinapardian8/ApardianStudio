# -*- coding: utf-8 -*-
"""Posteos de foto pura: una foto de Martin de lado a lado, sin texto encima.

Es lo que manda en su grilla (09-ESTUDIO/ESTETICA_IG.md): de cada 3 posteos,
al menos 2 son fotos puras. El mensaje va en el pie, con el llamado a
WhatsApp. Solo fotos verticales: el recorte a 4:5 no puede perder más del 22 %
(APRENDIZAJES: "No recortar mal"), y el recorte cuida las caras (recorte.py).
El lugar sale en el pie solo si está confirmado en fotos.json.

python3 10-MOTOR/posteos_foto.py
Sale a 08-CONTENIDO-INSTAGRAM/10-fotos/NN_slug.jpg + indice.json
"""
import os, re, json, unicodedata
from PIL import Image
from motor_ads import IMG, RAIZ
from recorte import cargar_ok, guardar_cache, hay_cara_cortada

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "10-fotos")
W, H = 1080, 1350
PERDIDA_MAX = 0.22
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

# (campaña, foto en 05-WEB/img/<cat>/web, primera línea del pie: dice lo que muestra la foto)
FOTOS = [
    ("cuadros", "naturaleza/nw__IMG_1985.jpg", "Roca, palmeras y el mar quieto abajo."),
    ("retratos", "retratos/horacio__IMG_6701.jpg", "Brazos cruzados, entre libros."),
    ("gastronomia", "gastronomia/v__69.jpg", "Arroz con langosta, recién servido."),
    ("bodas", "salones/golf-b__IMG_0346.jpg", "El jardín, de noche, con faroles en el camino."),
    ("cuadros", "naturaleza/v__54.jpg", "Un velero y el horizonte."),
    ("eventos", "eventos/nw__IMG_9236.jpg", "Dieciséis, una sola vez."),
    ("gastronomia", "gastronomia/sergio__IMG_7488.jpg", "La salsa, sobre la carne recién cortada."),
    ("cuadros", "naturaleza/nw__IMG_2011_2.jpg", "El camino termina en el faro."),
    ("retratos", "retratos/v__114.jpg", "La luz entre las hojas, en la cara."),
    ("bodas", "bodas/portfolio__IMG_8771.jpg", "De la mano, con el agua de fondo."),
    ("cuadros", "naturaleza/v__59.jpg", "Los rascacielos detrás de las flores."),
    ("gastronomia", "gastronomia/sergio__IMG_7391.jpg", "La pizza, recién salida."),
    ("eventos", "eventos/caro60__IMG_9671.jpg", "Rosas y velas, antes de que llegue la gente."),
    ("cuadros", "naturaleza/nw__IMG_1999.jpg", "Mirar para abajo y que el agua sea así de clara."),
    ("retratos", "retratos/v__118.jpg", "Blanco y negro, sin vueltas."),
    ("bodas", "salones/golf-a__IMG_4674.jpg", "Flores, velas y copas esperando."),
    ("cuadros", "naturaleza/v__55.jpg", "Una combi naranja cargada de tablas."),
    ("gastronomia", "gastronomia/v__73.jpg", "Un bocado por cuchara."),
    ("retratos", "retratos/nw__IMG_6981.jpg", "Al teléfono, sobre el piso a cuadros."),
    ("cuadros", "naturaleza/v__56.jpg", "Un río entre montañas y un barco que pasa."),
    ("eventos", "eventos/nw__IMG_4664.jpg", "Velas y flores en cada mesa."),
    ("gastronomia", "gastronomia/sergio__IMG_7234.jpg", "Recién hechas, sobre la tabla."),
    ("bodas", "salones/golf-b__IMG_0366.jpg", "Un sillón, un farol y flores amarillas."),
    ("cuadros", "naturaleza/v__43.jpg", "Una roca que cae derecho al mar."),
    ("retratos", "retratos/horacio__IMG_6581.jpg", "Brazos abiertos en la terraza."),
    ("gastronomia", "gastronomia/sergio__IMG_7377.jpg", "Las manos arman la pizza."),
    ("cuadros", "naturaleza/v__53.jpg", "Un canal, botes y palmeras."),
    ("bodas", "bodas/nw__IMG_4672.jpg", "Cada mesa tiene su centro."),
    ("retratos", "retratos/v__120.jpg", "Sentada en el pasto, con la última luz."),
    ("cuadros", "naturaleza/v__45.jpg", "Tan clara que se ven las piedras del fondo."),
    ("gastronomia", "gastronomia/alfajor__IMG_5423.jpg", "El cuchillo entra y el chocolate todavía brilla."),
    ("eventos", "eventos/nw__IMG_4682.jpg", "La mesa puesta, todo en su lugar."),
    ("cuadros", "naturaleza/v__57.jpg", "El río abajo, entre árboles y rocas."),
    ("retratos", "retratos/horacio__IMG_6071.jpg", "Una foto que se parece a vos."),
    ("bodas", "salones/golf-b__IMG_0358.jpg", "Luces colgadas y flores secas sobre la mesa."),
    ("cuadros", "naturaleza/nw__IMG_1996.jpg", "Agua quieta, roca y nada más."),
    ("gastronomia", "gastronomia/sergio__IMG_7503.jpg", "Cortada en la tabla, lista para servir."),
    ("retratos", "retratos/v__115.jpg", "Pensando, detrás del vidrio."),
    ("bodas", "salones/golf-a__IMG_4694.jpg", "Un rincón con velas."),
    ("retratos", "retratos/horacio__IMG_6904.jpg", "Brazos cruzados y la luz del lugar."),
    # 28/10/2026: reemplazan a los carruseles y reels que no tienen fotos
    # verticales (olivo, música, marca 360); ver 08-CONTENIDO-INSTAGRAM/ajustes.json
    ("gastronomia", "gastronomia/alfajor__IMG_5430.jpg", "El alfajor, partido al medio."),
    ("retratos", "retratos/nw__IMG_6420.jpg", "Con auriculares, frente a la computadora."),
    ("bodas", "salones/golf-a__IMG_4682.jpg", "Una mesa lista, con flores blancas."),
]


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:40]


def lugar(foto, catalogo):
    f = catalogo.get(foto, {})
    return f.get("lugar") if f.get("confirmado") else None


def main():
    os.makedirs(DEST, exist_ok=True)
    for f in os.listdir(DEST):
        if f.endswith(".jpg"):
            os.remove(os.path.join(DEST, f))
    catalogo = json.load(open(os.path.join(RAIZ, "10-MOTOR", "fotos.json"), encoding="utf-8"))["fotos"]
    indice, vistas = [], set()
    for k, (camp, foto, primera) in enumerate(FOTOS, 1):
        assert foto not in vistas, "foto repetida: " + foto
        vistas.add(foto)
        ruta = os.path.join(IMG, foto.split("/")[0], "web", foto.split("/")[1])
        sw, sh = Image.open(ruta).size
        perdida = 1 - min(sw / sh, W / H) / max(sw / sh, W / H)
        assert perdida <= PERDIDA_MAX, "%s pierde %d %% al recortar a 4:5" % (foto, perdida * 100)
        assert sw >= 1000, "%s es chica (%d px): se vería borrosa" % (foto, sw)
        assert not hay_cara_cortada(ruta, (W, H)), "el recorte de %s parte una cara" % foto
        archivo = "%02d_%s.jpg" % (k, slug(primera))
        cargar_ok(ruta, (W, H)).save(os.path.join(DEST, archivo), quality=92, optimize=True)
        cuerpo, cta, tags = CIERRES[camp]
        donde = lugar(foto, catalogo)
        pie = primera + ("\n" + donde + "." if donde else "") + "\n\n" + cuerpo + "\n\n" + cta + "\n\n" + tags
        indice.append({"n": k, "id": "f%02d" % k, "archivo": archivo, "campana": camp,
                       "foto": foto, "titulo": primera.rstrip("."), "lugar": donde or "", "pie": pie})
    guardar_cache()
    json.dump(indice, open(os.path.join(DEST, "indice.json"), "w"), ensure_ascii=False, indent=1)
    print(len(indice), "posteos de foto")


if __name__ == "__main__":
    main()
