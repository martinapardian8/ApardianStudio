# -*- coding: utf-8 -*-
"""Carruseles de Instagram para APARDIAN STUDIO.

Un carrusel no es una pila de avisos: es una secuencia. La lamina 1 frena el
scroll, las del medio muestran el trabajo casi sin gráfica encima (la foto ES
el producto) y la ultima pide algo.

15 carruseles de 8 laminas, todas en 4:5.
"""
import os, re, unicodedata, json
from PIL import Image, ImageDraw
from motor_ads import *
import plantillas_ads as PL

DEST = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/08-CONTENIDO-INSTAGRAM/03-carruseles"
M = 76


# ------------------------------------------------------------------ laminas
def tapa(ruta, c, total):
    """Lamina 1. Tiene que frenar el pulgar y prometer algo.

    La zona de abajo esta reservada para el logotipo y la senal de deslizar:
    el bloque de texto se mide y se achica para no invadirla.
    """
    W, H = POST
    im = cargar(ruta, POST, foco=0.42)
    im = velo_banda(im, int(H * 0.38), H, objetivo=44, pluma=260, piso=0.48)
    d = ImageDraw.Draw(im)

    PIE = 200                      # alto reservado abajo, intocable
    y0, y_tope = int(H * 0.42), H - PIE
    cc = {"kicker": c["kicker"], "titular": c["titular"], "sub": c.get("sub")}  # sin cta
    bloque(d, M, y0, y_tope, W - 2*M, cc, HUESO, HUESO,
           px_titular=124, con_regla=True, color_kicker=HUESO)

    # senal de deslizar y firma, siempre en el mismo lugar
    f = work(27, "SemiBold")
    escribir(d, (M, H - 108), "DESLIZÁ", f, HUESO, 5)
    w = ancho(d, "DESLIZÁ", f, 5)
    d.line([(M + w + 22, H - 96), (M + w + 78, H - 96)], fill=ROJO, width=4)
    for k in range(4):
        d.line([(M + w + 62 + k, H - 108 + k), (M + w + 78, H - 96)], fill=ROJO, width=3)
        d.line([(M + w + 62 + k, H - 84 - k), (M + w + 78, H - 96)], fill=ROJO, width=3)
    firma(d, M, H - 168, 0.95, True)
    return im


def foto_sola(ruta, n, total, pie=None):
    """Laminas del medio. Casi sin grafica: la foto tiene que respirar."""
    W, H = POST
    im = cargar(ruta, POST, foco=0.45)
    d = ImageDraw.Draw(im)
    if pie:
        im = velo_banda(im, H - 210, H, objetivo=52, pluma=150, piso=0.36)
        d = ImageDraw.Draw(im)
        parrafo(d, pie, M, H - 150, W - 2*M - 40, 31, HUESO, "Medium")
    return im


def cierre(ruta, c, total):
    """Ultima lamina. La unica que pide algo."""
    W, H = POST
    im = Image.new("RGB", POST, CARBON)
    hf = int(H * 0.42)
    f = cargar(ruta, (W, hf), foco=0.4)
    f = velo(f, 0.14, 0.62, 0.45)
    im.paste(f, (0, 0))
    d = ImageDraw.Draw(im)

    y = hf + 60
    kicker(d, M, y, c.get("kicker_cierre", "Apardian Studio"), ROJO); y += 26 + 16
    y += titular(d, c["cierre"], M, y, W - 2*M, 108, HUESO) + 28
    if c.get("sub_cierre"):
        y += parrafo(d, c["sub_cierre"], M, y, W - 2*M - 50, 32, (214, 212, 209)) + 34
    cta_pastilla(d, M, min(y, H - 190), c["cta"])
    firma(d, M, H - 110, 1.0, True)
    return im


def antes_despues_lamina(ruta, n, total, pie=None):
    """Lamina partida para el carrusel de edicion."""
    W, H = POST
    base = cargar(ruta, POST, foco=0.45)
    izq, der = aplanar(base), realzar(base)
    im = Image.new("RGB", POST)
    im.paste(izq.crop((0, 0, W//2, H)), (0, 0))
    im.paste(der.crop((W//2, 0, W, H)), (W//2, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([W//2 - 2, 0, W//2 + 2, H], fill=ROJO)

    et = work(24, "SemiBold")
    for txt, cx in (("ANTES", W//4), ("DESPUÉS", 3*W//4)):
        w = ancho(d, txt, et, 5) + 44
        d.rectangle([cx - w//2, H - 128, cx + w//2, H - 82], fill=CARBON)
        escribir(d, (cx, H - 120), txt, et, HUESO, 5, "c")
    if pie:
        im = velo_banda(im, H - 72, H, objetivo=48, pluma=60, piso=0.5)
        d = ImageDraw.Draw(im)
        escribir(d, (M, H - 58), pie, work(27, "Medium"), HUESO)
    return im


def texto_pleno(c, n, total, fondo="negro"):
    """Lamina solo de texto, para separar bloques dentro del carrusel."""
    W, H = POST
    col = {"negro": CARBON, "rojo": ROJO, "hueso": HUESO}[fondo]
    im = Image.new("RGB", POST, col)
    d = ImageDraw.Draw(im)
    tinta = NEGRO if fondo == "hueso" else HUESO
    acento = ROJO if fondo == "hueso" else HUESO
    y = int(H * 0.30)
    if c.get("kicker_lam"):
        kicker(d, M, y, c["kicker_lam"], acento); y += 26 + 18
    y += titular(d, c["texto"], M, y, W - 2*M, 116, tinta) + 30
    if c.get("pie"):
        parrafo(d, c["pie"], M, y, W - 2*M - 60, 32,
                (70, 68, 66) if fondo == "hueso" else (218, 216, 213))
    firma(d, M, H - 110, 1.0, fondo != "hueso")
    return im


# ------------------------------------------------------------------ catalogo
def C(slug, kicker, titular, sub, cat, cierre_t, sub_cierre, cta, idxs,
      pies=None, modo="foto", kicker_cierre=None, intermedia=None, laminas=None,
      mezcla=None, reutiliza=False, fijas=None):
    return dict(slug=slug, kicker=kicker, titular=titular, sub=sub, cat=cat,
                cierre=cierre_t, sub_cierre=sub_cierre, cta=cta, idxs=idxs,
                pies=pies or [], modo=modo,
                kicker_cierre=kicker_cierre or "Apardian Studio",
                intermedia=intermedia, laminas=laminas or len(idxs),
                mezcla=mezcla, reutiliza=reutiliza, fijas=fijas)


CARRUSELES = [
 C("01-una-boda-entera", "Bodas · Uruguay",
   "Casamientos",
   "Ceremonia, salón y fiesta. Todo lo que pasa en un día que dura uno solo.",
   ["bodas", "salones"], "Tu fecha todavía está libre",
   "Cobertura completa, todas las fotos sin tope y entrega en 10 días.",
   "RESERVÁ TU FECHA", [3, 7, 11, 2, 14, 5, 16, 9]),

 C("02-ocho-platos", "Fotografía gastronómica",
   "Platos que se venden solos",
   "Así se ve una carta cuando las fotos están hechas para vender.",
   "gastronomia", "Tu carta puede verse así",
   "Una jornada en tu local y tenés material para todo el año. Entrega en 7 días.",
   "COTIZÁ TU CARTA", [5, 12, 21, 30, 8, 40, 17, 44]),

 C("03-antes-y-despues", "Edición en Lightroom",
   "Antes y después",
   "La foto la sacaste bien. Esto es lo que falta para que se note.",
   "naturaleza", "Mandame tus fotos",
   "Edición por lote para fotógrafos. Tu lote listo en 72 horas.",
   "MANDAME TUS FOTOS", [9, 21, 4, 17, 28, 33, 12, 3], modo="antes", reutiliza=True),

 C("04-marcas-uruguayas", "Marcas · Uruguay",
   "Marcas uruguayas que fotografié",
   "Aceite de oliva, empanadas, alfajores y kamados. Producto real.",
   ["marcas"], "Tu producto es el que falta",
   "Packshot limpio, listo para tienda online, catálogo y redes.",
   "PEDIME UN PRESUPUESTO", [2, 7, 11, 5, 13, 0, 9, 4]),

 C("05-ocho-personas", "Retratos",
   "Nadie posó",
   "A todas les dije dos cosas y me callé. El resto lo hizo la luz.",
   "retratos", "Te toca a vos",
   "Book personal, marca personal o retrato para tu web.",
   "ESCRIBIME POR WHATSAPP", [4, 18, 29, 8, 22, 14, 26, 11],
   fijas=["horacio__IMG_6481.jpg", "v__114.jpg", "juan-luz__IMG_2643.jpg",
          "v__118.jpg", "v__119.jpg", "nw__IMG_6981.jpg",
          "v__116.jpg", "v__115.jpg"]),

 C("06-cuando-se-apagan", "Eventos y fiestas",
   "Lo que pasa cuando se apagan las luces",
   "La parte de la fiesta que nadie se acuerda al otro día.",
   "eventos", "La próxima puede ser la tuya",
   "Cobertura de toda la fiesta, sin tope de fotos y galería para los invitados.",
   "RESERVÁ TU FECHA", [6, 33, 48, 2, 19, 41, 27, 12]),

 C("07-salones-uruguay", "Salones y estancias",
   "Salones de Uruguay",
   "Cada lugar pide una luz distinta. Estas son las que encontré.",
   "salones", "¿Tenés un salón?",
   "Fotos del espacio montado, para tu web y para vender fechas.",
   "PEDIME UN PRESUPUESTO", [4, 7, 12, 1, 15, 9, 18, 3]),

 C("08-los-que-no-posan", "Animales",
   "Los que nunca posan",
   "No entienden la cámara y por eso salen mejor que nosotros.",
   "animales", "También hago esto",
   "Si tenés un animal en tu vida, merece una foto de verdad.",
   "ESCRIBIME POR WHATSAPP", [1, 6, 11, 3, 17, 9, 20, 14]),

 C("09-uruguay-punta-a-punta", "Naturaleza y viajes",
   "Uruguay de punta a punta",
   "Lo que veo cuando dejo de trabajar. Todo impreso queda mejor.",
   "naturaleza", "Colgá una en tu casa",
   "Copias numeradas, papel de archivo y marco de madera.",
   "QUIERO UN CUADRO", [3, 17, 28, 8, 22, 35, 12, 30]),

 C("10-musica-en-vivo", "Música",
   "Bandas que suenan antes de que aprietes play",
   "Poca luz, mucho movimiento y una sola oportunidad por tema.",
   "musica", "¿Tocás en vivo?",
   "Fotos de show para prensa, redes y tapa de disco.",
   "ESCRIBIME POR WHATSAPP", [1, 5, 9, 3, 7, 11, 2, 6]),

 C("11-hora-por-hora", "Bodas",
   "Lo que se repite en todas las bodas",
   "Y que nunca son iguales dos veces.",
   ["bodas", "salones"], "Contame tu fecha",
   "Te paso disponibilidad y presupuesto en el día.",
   "RESERVÁ TU FECHA", [11, 2, 16, 5, 9, 14, 7, 3]),

 C("12-del-deposito-a-la-tienda", "Producto",
   "Del depósito a la tienda",
   "Ocho productos que antes se vendían con una foto de celular.",
   ["marcas", "gastronomia"], "El tuyo puede ser el noveno",
   "Todos los productos que traigas, con recorte listo para tienda online.",
   "PEDIME UN PRESUPUESTO", [0, 5, 9, 13, 2, 7, 11, 4]),

 # Deportes solo tiene 7 fotos y cinco son autos en pista: no alcanza para un
 # carrusel propio sin repetir. Se arma uno de movimiento con deporte, musica y fiesta.
 C("13-el-instante", "Deporte · Música · Fiesta",
   "El instante que no se repite",
   "Tres mundos donde no podés pedir que lo repitan: la pista, el escenario y la fiesta.",
   ["deportes", "musica", "eventos"], "¿Tenés algo que pasa una sola vez?",
   "Cobertura de carrera, show o evento. Todas las fotos, entrega en 10 días.",
   "ESCRIBIME POR WHATSAPP", [0, 1, 2, 3, 4, 5, 6, 7]),

 C("14-que-hago", "Servicios",
   "Cuatro cosas que hago",
   "Foto, video, páginas web y edición en Lightroom. Todo desde Uruguay.",
   "eventos", "¿Cuál necesitás?",
   "Contame qué tenés en la cabeza y te digo cómo lo resolvemos.",
   "ESCRIBIME POR WHATSAPP", [6, 33, 2, 19, 41, 27, 12, 48],
   mezcla=["bodas", "gastronomia", "retratos", "marcas", "musica", "salones"],
   pies=["Fotografía · eventos, bodas, producto y retrato",
         "Video · reels, institucional y color grading",
         "Páginas web · diseño propio, no plantilla",
         "Edición en Lightroom · para otros fotógrafos",
         "Books y cuadros · para vos o para regalar",
         "Más de 80 proyectos entregados"]),

 C("15-como-trabajo", "Proceso",
   "Cómo trabajo",
   "Sin formularios, sin respuestas automáticas y sin desaparecer.",
   "gastronomia", "Empecemos",
   "Escribime por WhatsApp y en 24 horas te armo una propuesta.",
   "ESCRIBIME POR WHATSAPP", [30, 12, 21, 5, 44, 8, 17, 40],
   mezcla=["retratos", "gastronomia", "bodas", "marcas", "naturaleza", "eventos"],
   pies=["01 · Me escribís por WhatsApp, directo",
         "02 · Charlamos y entiendo qué necesitás",
         "03 · En 24 horas te paso propuesta y precio",
         "04 · Produzco y te muestro avances",
         "05 · Edito en Lightroom, una por una",
         "06 · Entrego en los formatos que necesites"]),
]


# ------------------------------------------------------------------ render
def slug_ok(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:40]


def main():
    os.makedirs(DEST, exist_ok=True)
    total_lam, indice = 0, []
    usadas = set()          # ninguna foto se repite entre carruseles
    for car in CARRUSELES:
        d_car = os.path.join(DEST, car["slug"])
        os.makedirs(d_car, exist_ok=True)
        n_lam = car.get("laminas") or len(car["idxs"])
        # ocho laminas seguidas del mismo tema aburren: se exige variedad
        import similitud as S
        from motor_ads import pool
        cats = car.get("mezcla") or (car["cat"] if isinstance(car["cat"], (list, tuple))
                                     else [car["cat"]])
        cands = []
        for k in cats:
            cands += pool().get(k) or []
        # en los carruseles de gente, las personas van primero
        gente_primero = any(k in cats for k in ("bodas", "eventos", "retratos", "musica", "empresas"))
        if car.get("fijas"):
            # elegidas a mano: el archivo de retratos son 4 sesiones y el
            # selector no distingue que 16 fotos son la misma persona
            idx = {os.path.basename(p): p for p in cands}
            rutas = [idx[n] for n in car["fijas"] if n in idx]
            n_lam = len(rutas)
            usadas.update(rutas)
            indice_ok = True
        else:
            rutas = S.una_por_escena(cands, n_lam, arranque=car["idxs"][0], size=POST,
                                     prefiere_gente=gente_primero,
                                     excluir=None if car.get("reutiliza") else usadas)
            if not car.get("reutiliza"):
                usadas.update(rutas)
        if len(rutas) < n_lam:
            # no hay material para tantas laminas: el carrusel se acorta.
            # Es mejor uno corto y variado que uno largo con la misma foto repetida.
            print(f"  {car['slug'][:2]}: solo {len(rutas)} laminas, el archivo no da para {n_lam}")
            n_lam = len(rutas)
        pies = car["pies"]
        for k in range(n_lam):
            n = k + 1
            if k == 0:
                im = tapa(rutas[0], car, n_lam)
            elif k == n_lam - 1:
                im = cierre(rutas[-1], car, n_lam)
            elif car["modo"] == "antes":
                im = antes_despues_lamina(rutas[k], n, n_lam,
                                          pies[k-1] if k-1 < len(pies) else None)
            else:
                im = foto_sola(rutas[k], n, n_lam,
                               pies[k-1] if k-1 < len(pies) else None)
            im.save(os.path.join(d_car, f"{n:02d}.jpg"), "JPEG", quality=90, optimize=True)
            total_lam += 1
        indice.append({"carrusel": car["slug"], "titular": car["titular"],
                       "laminas": n_lam, "cta": car["cta"]})
    json.dump(indice, open(os.path.join(os.path.dirname(DEST), "indice_carruseles.json"), "w"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"carruseles": len(CARRUSELES), "laminas": total_lam},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
