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

DEST = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM", "04-historias-organicas")
M = 76
W, H = STORY
TOP, BOT = SAFE_STORY_TOP, H - SAFE_STORY_BOT


# ------------------------------------------------------------------ plantillas
# Todas con la foto de Martin como protagonista (pieza_foto, en motor_ads): a
# sangre si la proporción da, entera sobre negro si no. Pedido de Martin del
# 26/10/2026. Nada de antes/después: no tenemos los originales.
def foto_frase(ruta, c):
    """Foto y una sola línea. La más usada y la que menos molesta."""
    return pieza_foto(ruta, STORY, True, c)[0]


def detras(ruta, c):
    """Detrás de escena: la foto y qué pasaba cuando se sacó."""
    c = dict(c); c.setdefault("kicker", "Detrás de escena")
    return pieza_foto(ruta, STORY, True, c)[0]


def antes_historia(ruta, c):
    """Antes eran un antes/después; ahora la foto terminada y la explicación."""
    return pieza_foto(ruta, STORY, True, c)[0]


# Los datos también llevan una foto: el tema del dato elige la carpeta.
TEMA_DATO = [("cuadro", "naturaleza"), ("viaje", "naturaleza"), ("restaurante", "gastronomia"),
             ("carta", "gastronomia"), ("gastronom", "gastronomia"), ("evento", "eventos"),
             ("fiesta", "eventos"), ("boda", "bodas"), ("casa", "bodas"), ("retrato", "retratos"),
             ("animal", "animales"), ("marca", "marcas"), ("web", "empresas"), ("edici", "bodas"),
             ("lote", "bodas"), ("fotógraf", "bodas"), ("empresa", "empresas"), ("servicio", "retratos")]


def foto_para_dato(c):
    t = " ".join(str(c.get(k, "")) for k in ("kicker", "titular", "sub")).lower()
    cat = next((v for k, v in TEMA_DATO if k in t), "retratos")
    n = sum(ord(x) for x in c["titular"])
    return foto_de(cat, n, COMIDA if cat == "gastronomia" else None)


def dato(c, ruta=None):
    """Un dato o una frase, sobre una foto de Martin del mismo tema."""
    return pieza_foto(ruta or foto_para_dato(c), STORY, True, c)[0]


def pregunta(ruta, c):
    """La foto, la pregunta y dos opciones abajo (la encuesta se pone a mano)."""
    ops = c["opciones"][:2]
    im, fin = pieza_foto(ruta, STORY, True, {k: v for k, v in c.items() if k != "opciones"},
                         extra_abajo=len(ops) * 120 + 10)
    d = ImageDraw.Draw(im)
    y = fin + 4
    for op in ops:
        d.rounded_rectangle([M, y, W - M, y + 100], radius=50, fill=None, outline=HUESO, width=3)
        escribir(d, (W//2, y + 31), op, work(32, "SemiBold"), HUESO, 1.5, "c")
        y += 120
    return im


# ------------------------------------------------------------------ catalogo
def h(tipo, cat, idx, **c):
    c["_t"], c["_cat"], c["_i"] = tipo, cat, idx
    return c


HISTORIAS = [
 # --- oficio y trabajo reciente ---------------------------------------
 h("foto", "bodas", 3, kicker="Sábado pasado", titular="Todavía tengo arroz en la cámara",
   sub="Ya está la galería."),
 h("foto", "bodas", 12, kicker="Ceremonia", titular="La entrada que todos esperaban",
   sub="Un segundo que no se repite."),
 h("foto", "gastronomia", 5, kicker="Hoy", titular="Ocho horas para veinte platos",
   sub="Vale cada minuto cuando ves la carta terminada."),
 h("foto", "eventos", 33, kicker="Anoche", titular="La fiesta recién empieza a las dos",
   sub="Y ahí es cuando salen las mejores."),
 h("foto", "retratos", 18, kicker="Retrato", titular="Le dije dos cosas y me callé",
   sub="El resto lo hizo la luz de la ventana."),
 h("foto", "marcas", 7, kicker="Producto", titular="Cuarenta tomas para elegir una",
   sub="Las aceitunas caen una sola vez."),
 h("foto", "musica", 4, kicker="En vivo", titular="Poca luz y una sola pasada",
   sub="No podés pedirle a la banda que repita el tema."),
 h("foto", "animales", 6, kicker="Animales", titular="Este no entendió nada y salió mejor que yo"),
 h("foto", "naturaleza", 21, kicker="Fin de semana", titular="Salí a caminar y volví con esto",
   sub="Palma de Mallorca."),
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
 h("foto", "naturaleza", 3, titular="Lugares que no salen en la guía"),
 h("foto", "naturaleza", 35, titular="Nadie en kilómetros"),
 h("foto", "animales", 14, titular="Me miró y se fue"),
 h("foto", "animales", 20, titular="No se movió en veinte minutos"),
 h("foto", "gastronomia", 40, titular="Esto salió del horno hace un minuto"),
 h("foto", "gastronomia", 17, titular="Se ve como se come"),
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


def texto_de(c):
    return " · ".join(str(c[k]) for k in ("kicker", "titular", "sub") if c.get(k)) + \
        ("" if not c.get("opciones") else " · " + " / ".join(c["opciones"]))


def main():
    os.makedirs(DEST, exist_ok=True)
    INDICE = os.path.join(os.path.dirname(DEST), "indice_historias.json")
    viejo = {x["n"]: x for x in json.load(open(INDICE, encoding="utf-8"))} if os.path.exists(INDICE) else {}
    idx = []
    for i, c in enumerate(HISTORIAS, 1):
        t = c["_t"]
        cc = {k: v for k, v in c.items() if not k.startswith("_")}
        try:
            if t == "dato":
                r = foto_para_dato(cc)
                im = dato(cc, r)
            else:
                import similitud as S
                r = foto_de(c["_cat"], c["_i"], COMIDA if c["_cat"] == "gastronomia" else None)
                if r in S._vetadas(STORY):
                    for k in range(1, 20):
                        alt = foto_de(c["_cat"], c["_i"] + k, COMIDA if c["_cat"] == "gastronomia" else None)
                        if alt not in S._vetadas(STORY):
                            r = alt; break
                im = {"foto": foto_frase, "pregunta": pregunta,
                      "detras": detras, "antes": antes_historia}[t](r, cc)
            # el archivo conserva su nombre aunque cambie el texto: el calendario lo usa
            nom = viejo[i]["archivo"] if i in viejo else f"{i:03d}_{t}_{slug_ok(c['titular'])}.jpg"
            im.save(os.path.join(DEST, nom), "JPEG", quality=90, optimize=True)
            idx.append({"n": i, "tipo": t, "titular": c["titular"], "archivo": nom,
                        "foto": os.path.relpath(r, RAIZ), "texto": texto_de(cc)})
        except Exception as e:
            print(f"  FALLO {i:03d} {t}: {type(e).__name__}: {e}")
    # las historias del verano (51 en adelante) las arma historias_verano.py
    idx += [x for n, x in sorted(viejo.items()) if n > len(HISTORIAS)]
    json.dump(idx, open(INDICE, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"historias": len(os.listdir(DEST))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
