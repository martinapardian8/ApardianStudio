# -*- coding: utf-8 -*-
"""Historias 051 en adelante: verano 26/27 (fin de año, enero y febrero).

Mismas plantillas que historias.py (foto con frase, detras de escena, dato),
con fotos de Martin que no se usaron en las 50 primeras ni en los carruseles.
Sin preguntas: esas llevan la encuesta a mano y no salen solas.

python3 10-MOTOR/historias_verano.py                      # las que no salieron
python3 10-MOTOR/historias_verano.py --desde 2026-11-02   # solo las del calendario desde ese día

Solo fotos verticales a pantalla completa (Martin, 28/10/2026): si una de las
de abajo es horizontal, sale otra vertical del mismo tema (historias.elegir_foto).
"""
import os, re, json, unicodedata
import historias as H
from motor_ads import IMG, RAIZ, se_puede_escribir, registrar, opcion_desde

IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
DEST = os.path.join(IG, "04-historias-organicas")
INDICE = os.path.join(IG, "indice_historias.json")
PRIMERA = 51


def f(cat, nombre):
    return os.path.join(IMG, cat, "web", nombre)


HISTORIAS = [
    ("foto", f("naturaleza", "nw__IMG_2011_2.jpg"), dict(kicker="Fin de semana", titular="Hasta el faro y volver")),
    ("foto", f("naturaleza", "v__28.jpg"), dict(titular="Otra ciudad, la misma luz")),
    ("dato", None, dict(kicker="Cuadros", titular="Si no llega para Navidad, llega para Reyes",
                        sub="Fotos de mis viajes, impresas y enmarcadas. Escribime.", fondo="rojo")),
    ("foto", f("animales", "v__100.jpg"), dict(titular="Posó mejor que muchos")),
    ("foto", f("retratos", "juan-luz__IMG_2669.jpg"), dict(kicker="Retrato", titular="Una gorra, el sol y nada más")),
    ("detras", f("eventos", "v__11.jpg"), dict(kicker="Detrás de escena", titular="Fin de año: los chicos primero",
                                               sub="Me pongo a su altura y espero.")),
    ("foto", f("naturaleza", "v__53.jpg"), dict(titular="Agua quieta, verano largo")),
    ("dato", None, dict(kicker="Eventos", titular="¿Tenés fiesta en enero o febrero?",
                        sub="Escribime y te paso disponibilidad en el día.", fondo="negro")),
    ("foto", f("deportes", "v__86.jpg"), dict(titular="Un segundo antes")),
    ("foto", f("musica", "la-estacion__IMG_8039.jpg"), dict(kicker="En vivo", titular="El sonido también se ve")),
    ("foto", f("naturaleza", "v__55.jpg"), dict(titular="Hay colores que piden foto")),
    ("detras", f("gastronomia", "lokotas__IMG_7600.jpg"), dict(kicker="Detrás de escena", titular="La bandeja sale ahora",
                                                               sub="Hay diez segundos antes de que alguien la toque.")),
    ("dato", None, dict(kicker="Restaurantes", titular="La carta de verano se fotografía antes del verano",
                        sub="Una jornada en tu local. Entrega en 7 días.", fondo="hueso")),
    ("foto", f("empresas", "odontovita__IMG_4928.jpg"), dict(kicker="Empresas", titular="Hasta el catering sale en la foto")),
    ("foto", f("naturaleza", "v__61.jpg"), dict(titular="Vacaciones con la cámara encima")),
    ("foto", f("animales", "v__105.jpg"), dict(titular="Paciencia, mucha paciencia")),
    ("dato", None, dict(numero="72", kicker="Horas", titular="Tu lote, en plena temporada",
                        sub="Para fotógrafos que no llegan con la edición.", fondo="negro")),
    ("foto", f("retratos", "v__115.jpg"), dict(titular="Poca luz, mucha cara")),
    ("detras", f("eventos", "v__7.jpg"), dict(kicker="Detrás de escena", titular="En la fiesta de empresa también se juega",
                                              sub="Las mejores fotos salen cuando nadie posa.")),
    ("foto", f("naturaleza", "v__66.jpg"), dict(titular="Enero en modo lento")),
    ("foto", f("musica", "la-estacion__IMG_8079.jpg"), dict(kicker="Ensayo", titular="Antes de que se prendan las luces")),
    ("foto", f("empresas", "odontovita__IMG_5155.jpg"), dict(kicker="Empresas", titular="Fotos de equipo, sin cartón")),
    ("dato", None, dict(kicker="Marca 360", titular="Logo, colores, letras y plantillas",
                        sub="Tu marca, igual en todos lados.", fondo="hueso")),
    ("foto", f("retratos", "v__119.jpg"), dict(titular="Los chicos no posan: juegan")),
    ("foto", f("deportes", "v__89.jpg"), dict(titular="La foto es del que espera")),
    ("foto", f("animales", "v__109.jpg"), dict(titular="Campo abierto")),
    ("foto", f("animales", "nw__IMG_0653.jpg"), dict(titular="Retrato sin palabras")),
    ("foto", f("naturaleza", "v__29.jpg"), dict(titular="Lejos de todo")),
    ("foto", f("retratos", "horacio__IMG_6406.jpg"), dict(kicker="Retrato", titular="Trabajar con música")),
    ("foto", f("deportes", "v__87.jpg"), dict(titular="Todo pasa rápido")),
    ("foto", f("naturaleza", "v__41.jpg"), dict(titular="Nublado también sirve")),
    ("foto", f("animales", "v__102.jpg"), dict(titular="Nadie le dijo que posara")),
    ("foto", f("musica", "la-estacion__IMG_8052.jpg"), dict(kicker="Ensayo", titular="Sonido de sala")),
    ("foto", f("retratos", "v__116.jpg"), dict(titular="Luz de tarde")),
    ("foto", f("naturaleza", "v__62.jpg"), dict(titular="Otra ciudad desde arriba")),
    ("foto", f("deportes", "v__90.jpg"), dict(titular="A toda velocidad")),
    ("foto", f("animales", "v__107.jpg"), dict(titular="Mirá quién llegó")),
    ("foto", f("retratos", "juan-luz__IMG_2686.jpg"), dict(kicker="Retrato", titular="Con el agua de fondo")),
    ("foto", f("naturaleza", "v__56.jpg"), dict(titular="Tarde gris, foto linda")),
    ("dato", None, dict(kicker="Edición en Lightroom", titular="Mandame el lote y seguí disparando",
                        sub="Para fotógrafos en plena temporada. Escribime.", fondo="negro")),
    ("foto", f("naturaleza", "v__48.jpg"), dict(titular="El mar, de frente")),
    ("foto", f("musica", "la-estacion__IMG_8073.jpg"), dict(kicker="En la calle", titular="Música a cielo abierto")),
    ("dato", None, dict(kicker="Páginas web", titular="Tu web, pensada primero para el celular",
                        sub="Para negocios que abren en temporada. Escribime.", fondo="hueso")),
    ("foto", f("empresas", "odontovita__IMG_5182.jpg"), dict(kicker="Empresas", titular="La marca también sale en la foto")),
    ("foto", f("animales", "v__104.jpg"), dict(titular="Colores que no se inventan")),
    ("dato", None, dict(kicker="Marca 360", titular="Un manual para que tu marca no cambie de cara",
                        sub="Logo, colores, letras y plantillas, en un solo lugar.", fondo="rojo")),
    ("foto", f("retratos", "horacio__IMG_6496.jpg"), dict(kicker="Retrato", titular="Leer al sol")),
    ("foto", f("deportes", "v__88.jpg"), dict(titular="Debajo del muelle")),
]


# La foto de arriba es horizontal y la vertical que elegiría el motor no
# muestra lo que dice el texto: la elige Luz a mano. None: no hay una foto
# vertical de Martin que lo muestre y llene el 9:16; la historia no se rehace
# y Lupa la frena hasta que Martin decida (Martin, 28/10/2026).
VERTICAL = {
    51: None,                            # Hasta el faro: la única del faro es 3:4 (pierde 25 %)
    52: f("naturaleza", "v__55.jpg"),    # Otra ciudad: una calle, no el mar
    56: None,                            # Los chicos primero: no hay chicos en vertical
    60: None,                            # En vivo: no hay show en vivo vertical
    69: None,                            # Fiesta de empresa, nadie posa: las verticales son posadas
    70: f("naturaleza", "nw__FullSizeRender_6.jpg"),  # Enero en modo lento: mar quieto (la combi ya sale 3 veces)
    72: None,                            # Fotos de equipo: no hay equipo en vertical 9:16
    74: None,                            # Los chicos no posan: no hay chicos en vertical
    76: f("animales", "v__108.jpg"),     # Campo abierto: el caballo en el campo
    80: f("deportes", "v__90.jpg"),      # Todo pasa rápido: autos en derrape
}
H.VERTICAL.update(VERTICAL)


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:44]


def main(desde=None):
    """desde (AAAA-MM-DD): solo rehace las del calendario que salen ese día o
    después. Lo que ya salió no se toca nunca."""
    todo = json.load(open(INDICE, encoding="utf-8"))
    idx = [x for x in todo if x["n"] < PRIMERA]
    # el archivo conserva su nombre aunque cambie el texto: el calendario lo usa
    viejos = {x["n"]: x for x in todo if x["n"] >= PRIMERA}
    nombres = {x["archivo"] for x in viejos.values()}
    for x in os.listdir(DEST):
        if re.match(r"^\d{3}_", x) and int(x[:3]) >= PRIMERA and x not in nombres:
            os.remove(os.path.join(DEST, x))
    hechas = 0
    for k, (tipo, ruta, c) in enumerate(HISTORIAS):
        n = PRIMERA + k
        nom = viejos[n]["archivo"] if n in viejos else "%03d_%s_%s.jpg" % (n, tipo, slug(c["titular"]))
        destino = os.path.join(DEST, nom)
        if not se_puede_escribir(destino, desde):
            if n in viejos:
                idx.append(viejos[n])
            continue
        if tipo == "dato":
            ruta = H.foto_para_dato(c)
        # solo fotos verticales a pantalla completa (Martin, 28/10/2026)
        r = H.elegir_foto(ruta, destino, n)
        if r is None:
            print("  SIN FOTO VERTICAL %03d (%s): no se rehace, Lupa la frena" % (n, c["titular"]))
            if n in viejos:
                idx.append(viejos[n])
            continue
        im = H.dato(c, r) if tipo == "dato" else {"foto": H.foto_frase, "detras": H.detras}[tipo](r, c)
        im.save(destino, "JPEG", quality=90, optimize=True)
        registrar(destino, [r])
        hechas += 1
        idx.append({"n": n, "tipo": tipo, "titular": c["titular"], "archivo": nom,
                    "foto": os.path.relpath(r, RAIZ), "texto": H.texto_de(c)})
    json.dump(idx, open(INDICE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(hechas, "historias rehechas")


if __name__ == "__main__":
    import sys
    main(opcion_desde(sys.argv))
