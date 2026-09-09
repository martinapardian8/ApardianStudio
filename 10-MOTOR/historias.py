# -*- coding: utf-8 -*-
"""50 historias organicas para APARDIAN STUDIO.

No son avisos: no piden nada de entrada. Sirven para sostener la cuenta entre
campaña y campaña, mostrar oficio y dar pie a que la gente conteste.
Todas en 9:16 con los margenes seguros de Instagram respetados.
"""
import os, re, unicodedata, json
from PIL import Image, ImageDraw
from motor_ads import *
import plantillas_ads as PL

DEST = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/08-CONTENIDO-INSTAGRAM/04-historias-organicas"
M = 76
W, H = STORY
TOP, BOT = SAFE_STORY_TOP, H - SAFE_STORY_BOT


# ------------------------------------------------------------------ plantillas
def foto_frase(ruta, c):
    """Foto a sangre y una sola linea. La mas usada y la que menos molesta."""
    im = cargar(ruta, STORY, foco=0.42)
    im = velo_banda(im, BOT - 420, H, objetivo=50, pluma=260, piso=0.38)
    d = ImageDraw.Draw(im)
    y = BOT - 360
    if c.get("kicker"):
        kicker(d, M, y, c["kicker"], HUESO); y += 26 + 18
    y += titular(d, c["titular"], M, y, W - 2*M, 104, HUESO) + 24
    if c.get("sub"):
        parrafo(d, c["sub"], M, y, W - 2*M - 60, 31, (220, 218, 215))
    firma(d, M, BOT - 40, 1.0, True)
    return im


def dato(c):
    """Fondo plano y un dato. Corta el ritmo entre fotos."""
    fondo = c.get("fondo", "negro")
    col = {"negro": CARBON, "rojo": ROJO, "hueso": HUESO}[fondo]
    im = Image.new("RGB", STORY, col)
    d = ImageDraw.Draw(im)
    tinta = NEGRO if fondo == "hueso" else HUESO
    acento = ROJO if fondo == "hueso" else HUESO
    y = TOP + 180
    if c.get("numero"):
        y += numeral(d, c["numero"], M, y, 260, tinta) + 26
    if c.get("kicker"):
        kicker(d, M, y, c["kicker"], acento); y += 26 + 22
    y += titular(d, c["titular"], M, y, W - 2*M, 112, tinta) + 28
    if c.get("sub"):
        parrafo(d, c["sub"], M, y, W - 2*M - 50, 32,
                (72, 70, 68) if fondo == "hueso" else (216, 214, 211))
    firma(d, M, BOT - 40, 1.0, fondo != "hueso")
    return im


def pregunta(ruta, c):
    """Foto arriba y dos opciones abajo. Para poner la encuesta encima."""
    im = Image.new("RGB", STORY, CARBON)
    hf = int(H * 0.46)
    im.paste(cargar(ruta, (W, hf), foco=0.42), (0, TOP - 40))
    d = ImageDraw.Draw(im)
    y = TOP - 40 + hf + 60
    y += titular(d, c["titular"], M, y, W - 2*M, 96, HUESO) + 40
    for op in c["opciones"][:2]:
        d.rounded_rectangle([M, y, W - M, y + 108], radius=54,
                            fill=None, outline=HUESO, width=3)
        escribir(d, (W//2, y + 34), op, work(34, "SemiBold"), HUESO, 1.5, "c")
        y += 128
    if c.get("sub"):
        parrafo(d, c["sub"], M, y + 12, W - 2*M - 40, 29, (178, 176, 173))
    firma(d, M, BOT - 40, 1.0, True)
    return im


def detras(ruta, c):
    """Marco hueso con la foto adentro. Se lee como una polaroid editorial."""
    im = Image.new("RGB", STORY, HUESO)
    d = ImageDraw.Draw(im)
    mm = 88
    fw = W - 2*mm
    fh = int(fw * 1.16)
    yf = TOP + 40
    im.paste(cargar(ruta, (fw, fh), foco=0.45), (mm, yf))
    y = yf + fh + 46
    kicker(d, mm, y, c.get("kicker", "Detrás de escena"), ROJO); y += 26 + 16
    y += titular(d, c["titular"], mm, y, fw, 84, NEGRO) + 22
    if c.get("sub"):
        parrafo(d, c["sub"], mm, y, fw, 29, (78, 76, 74))
    firma(d, W - mm, BOT - 40, 1.0, False, "r")
    return im


def antes_historia(ruta, c):
    """Antes y despues en vertical, para el servicio de edicion."""
    im = Image.new("RGB", STORY, CARBON)
    alto = int(H * 0.56)
    base = cargar(ruta, (W, alto), foco=0.45)
    mix = Image.new("RGB", (W, alto))
    mix.paste(aplanar(base).crop((0, 0, W//2, alto)), (0, 0))
    mix.paste(realzar(base).crop((W//2, 0, W, alto)), (W//2, 0))
    yf = TOP - 30
    im.paste(mix, (0, yf))
    d = ImageDraw.Draw(im)
    d.rectangle([W//2 - 2, yf, W//2 + 2, yf + alto], fill=ROJO)
    et = work(24, "SemiBold")
    for txt, cx in (("ANTES", W//4), ("DESPUÉS", 3*W//4)):
        w = ancho(d, txt, et, 5) + 44
        d.rectangle([cx - w//2, yf + alto - 62, cx + w//2, yf + alto - 16], fill=CARBON)
        escribir(d, (cx, yf + alto - 54), txt, et, HUESO, 5, "c")
    y = yf + alto + 52
    y += titular(d, c["titular"], M, y, W - 2*M, 92, HUESO) + 24
    if c.get("sub"):
        parrafo(d, c["sub"], M, y, W - 2*M - 50, 30, (214, 212, 209))
    firma(d, M, BOT - 40, 1.0, True)
    return im


# ------------------------------------------------------------------ catalogo
def h(tipo, cat, idx, **c):
    c["_t"], c["_cat"], c["_i"] = tipo, cat, idx
    return c


HISTORIAS = [
 # --- oficio y trabajo reciente ---------------------------------------
 h("foto", "bodas", 3, kicker="Sábado pasado", titular="Todavía tengo arroz en la cámara",
   sub="Casamiento en Colonia. Ya está la galería."),
 h("foto", "bodas", 11, kicker="Ceremonia", titular="Esta la saqué desde el piso",
   sub="A veces el mejor lugar es el peor lugar."),
 h("foto", "gastronomia", 5, kicker="Hoy", titular="Ocho horas para veinte platos",
   sub="Vale cada minuto cuando ves la carta terminada."),
 h("foto", "eventos", 33, kicker="Anoche", titular="La fiesta recién empieza a las dos",
   sub="Y ahí es cuando salen las mejores."),
 h("foto", "retratos", 18, kicker="Retrato", titular="Le dije dos cosas y me callé",
   sub="El resto lo hizo la luz de la ventana."),
 h("foto", "marcas", 7, kicker="Producto", titular="Cuarenta tomas para elegir una",
   sub="Así se hace un packshot que aguanta el zoom."),
 h("foto", "musica", 4, kicker="En vivo", titular="Poca luz y una sola pasada",
   sub="No podés pedirle a la banda que repita el tema."),
 h("foto", "animales", 6, kicker="Animales", titular="Este no entendió nada y salió mejor que yo"),
 h("foto", "naturaleza", 21, kicker="Fin de semana", titular="Salí a caminar y volví con esto",
   sub="Uruguay tiene lugares que no aparecen en ninguna guía."),
 h("foto", "salones", 9, kicker="Salón", titular="Vacío a las cinco, lleno a las nueve",
   sub="Fotografiar un salón montado es otro laburo."),

 # --- datos y numeros ---------------------------------------------------
 h("dato", None, 0, numero="80", kicker="Proyectos entregados",
   titular="Ochenta y sigo contando", sub="Bodas, fiestas, marcas y páginas web.", fondo="negro"),
 h("dato", None, 0, numero="10", kicker="Días",
   titular="Ese es mi plazo de entrega", sub="Sin excepciones y sin tope de cantidad de fotos.", fondo="negro"),
 h("dato", None, 0, numero="4", kicker="Servicios",
   titular="Foto, video, web y edición", sub="Todo lo hago yo. No tercerizo.", fondo="rojo"),
 h("dato", None, 0, kicker="Dato",
   titular="El 70% te va a mirar desde el celular",
   sub="Por eso todo lo que entrego está pensado en vertical también.", fondo="hueso"),
 h("dato", None, 0, numero="72", kicker="Horas",
   titular="Lo que tardo en editar un lote", sub="Para fotógrafos que no llegan con la entrega.", fondo="negro"),

 # --- educativo: posiciona el servicio de edicion ------------------------
 h("antes", "naturaleza", 9, titular="Esto es revelado, no filtro",
   sub="Se trabaja cada zona por separado. No hay un botón que lo haga."),
 h("antes", "gastronomia", 12, titular="La comida se edita distinto",
   sub="Si te pasás de saturación, deja de dar hambre."),
 h("antes", "retratos", 14, titular="La piel no se plancha",
   sub="Se corrige el tono y se deja la textura. Si no, parece plástico."),
 h("antes", "eventos", 41, titular="Poca luz no es excusa",
   sub="El ruido se trabaja, no se tapa."),
 h("antes", "marcas", 11, titular="Fondo blanco de verdad",
   sub="Blanco puro, sin gris ni celeste. Es lo que pide una tienda online."),

 # --- preguntas para que contesten --------------------------------------
 h("pregunta", "bodas", 7, titular="¿Ceremonia de día o de noche?",
   opciones=["DE DÍA", "DE NOCHE"], sub="Contestá acá arriba, tengo curiosidad."),
 h("pregunta", "gastronomia", 21, titular="¿Qué foto te da más hambre?",
   opciones=["LA DE LA IZQUIERDA", "LA DE LA DERECHA"]),
 h("pregunta", "naturaleza", 28, titular="¿Color o blanco y negro?",
   opciones=["COLOR", "BLANCO Y NEGRO"], sub="Es la discusión eterna."),
 h("pregunta", "retratos", 22, titular="¿Posás o te da vergüenza?",
   opciones=["POSO SIN PROBLEMA", "ME MUERO DE VERGÜENZA"],
   sub="Si elegiste la segunda, esa es mi especialidad."),
 h("pregunta", "eventos", 19, titular="¿Foto o video en tu fiesta?",
   opciones=["FOTO", "LAS DOS COSAS"]),

 # --- detras de escena ---------------------------------------------------
 h("detras", "bodas", 16, kicker="Detrás de escena", titular="Dos cámaras y ningún plan B",
   sub="Por eso siempre llevo dos cuerpos y cuatro baterías."),
 h("detras", "gastronomia", 30, kicker="Detrás de escena", titular="El plato se enfría en tres minutos",
   sub="Hay que tener la luz armada antes de que salga de la cocina."),
 h("detras", "marcas", 2, kicker="Detrás de escena", titular="El fondo blanco no es una pared blanca",
   sub="Es papel, dos luces y mucha paciencia."),
 h("detras", "retratos", 8, kicker="Detrás de escena", titular="Trabajo casi siempre con luz de ventana",
   sub="Es gratis y es la mejor que hay."),
 h("detras", "eventos", 27, kicker="Detrás de escena", titular="Me muevo rápido y en silencio",
   sub="Si me notás, algo hice mal."),

 # --- frases de marca ----------------------------------------------------
 h("dato", None, 0, titular="El instante que no se repite",
   sub="Es literal. Por eso llego temprano y me voy último.", fondo="negro"),
 h("dato", None, 0, titular="Lo que entra por los ojos antes que por la boca",
   sub="Gastronomía.", fondo="rojo"),
 h("dato", None, 0, titular="Una persona, sin pose y sin apuro",
   sub="Retratos.", fondo="hueso"),
 h("dato", None, 0, titular="Los que nunca posan y siempre miran",
   sub="Animales.", fondo="negro"),
 h("dato", None, 0, titular="Dos personas y todo el resto de la vida esperando",
   sub="Bodas.", fondo="negro"),

 # --- foto suelta con frase corta ---------------------------------------
 h("foto", "naturaleza", 3, titular="Uruguay también es esto"),
 h("foto", "naturaleza", 35, titular="Nadie en kilómetros"),
 h("foto", "animales", 14, titular="Me miró y se fue"),
 h("foto", "animales", 20, titular="No se movió en veinte minutos"),
 h("foto", "gastronomia", 40, titular="Esto salió del horno hace un minuto"),
 h("foto", "gastronomia", 17, titular="Producto uruguayo, foto uruguaya"),
 h("foto", "bodas", 5, titular="Se casaron con viento a favor"),
 h("foto", "eventos", 48, titular="Quince años, cero poses"),
 h("foto", "musica", 9, titular="Tres canciones y se acabó la luz"),
 h("foto", "salones", 4, titular="Mañana esto va a estar lleno"),
 h("foto", "deportes", 2, titular="No hay segunda toma"),
 h("foto", "retratos", 29, titular="Una foto que sí se puede mandar"),
 h("foto", "empresas", 1, titular="Fotos de equipo que no dan vergüenza"),

 # --- avisos suaves de disponibilidad -----------------------------------
 h("dato", None, 0, kicker="Agenda", titular="Quedan fechas para diciembre",
   sub="Escribime y te paso disponibilidad en el día.", fondo="rojo"),
 h("dato", None, 0, kicker="Para fotógrafos", titular="Tengo lugar para editar dos lotes esta semana",
   sub="Si venís atrasado con una entrega, escribime.", fondo="negro"),
]


def slug_ok(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:44]


def main():
    os.makedirs(DEST, exist_ok=True)
    idx = []
    for i, c in enumerate(HISTORIAS, 1):
        t = c["_t"]
        cc = {k: v for k, v in c.items() if not k.startswith("_")}
        try:
            if t == "dato":
                im = dato(cc)
            else:
                import similitud as S
                r = foto(c["_cat"], c["_i"])
                if r in S._vetadas(STORY):
                    for k in range(1, 20):
                        alt = foto(c["_cat"], c["_i"] + k)
                        if alt not in S._vetadas(STORY):
                            r = alt; break
                im = {"foto": foto_frase, "pregunta": pregunta,
                      "detras": detras, "antes": antes_historia}[t](r, cc)
            nom = f"{i:03d}_{t}_{slug_ok(c['titular'])}.jpg"
            im.save(os.path.join(DEST, nom), "JPEG", quality=90, optimize=True)
            idx.append({"n": i, "tipo": t, "titular": c["titular"], "archivo": nom})
        except Exception as e:
            print(f"  FALLO {i:03d} {t}: {type(e).__name__}: {e}")
    json.dump(idx, open(os.path.join(os.path.dirname(DEST), "indice_historias.json"), "w"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"historias": len(os.listdir(DEST))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
