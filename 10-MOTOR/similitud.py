# -*- coding: utf-8 -*-
"""Evita que una misma pieza muestre dos fotos casi iguales.

Usa un hash perceptual: se reduce la foto a una grilla en gris y se compara
cada celda contra la media. Dos fotos parecidas dan hashes parecidos.
"""
import os, json
from PIL import Image

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hashes.json")
_h = None
N = 12   # grilla de 12x12 = 144 bits


def _cache():
    global _h
    if _h is None:
        _h = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    return _h


def guardar():
    if _h is not None:
        json.dump(_h, open(CACHE, "w"))


def phash(ruta):
    c = _cache()
    if ruta in c:
        return c[ruta]
    try:
        im = Image.open(ruta).convert("L").resize((N, N), Image.LANCZOS)
    except Exception:
        c[ruta] = "0" * (N*N); return c[ruta]
    px = list(im.getdata())
    m = sum(px) / len(px)
    c[ruta] = "".join("1" if v > m else "0" for v in px)
    return c[ruta]


def distancia(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def distintas(cands, n, umbral=26, arranque=0):
    """Elige n fotos que no se parezcan entre si.

    umbral: cuantos bits de 144 tienen que diferir para considerarlas distintas.
    26 deja pasar variaciones del mismo lugar pero corta las casi identicas.
    """
    if not cands:
        return []
    orden = cands[arranque:] + cands[:arranque]
    eleg, hs = [], []
    for p in orden:
        h = phash(p)
        if all(distancia(h, o) >= umbral for o in hs):
            eleg.append(p); hs.append(h)
            if len(eleg) == n:
                return eleg
    # si el umbral no alcanza, se baja hasta completar antes que repetir a ciegas
    for u in (20, 15, 10, 4):
        for p in orden:
            if p in eleg:
                continue
            h = phash(p)
            if all(distancia(h, o) >= u for o in hs):
                eleg.append(p); hs.append(h)
                if len(eleg) == n:
                    return eleg
    for p in orden:
        if p not in eleg:
            eleg.append(p)
        if len(eleg) == n:
            break
    return eleg


def repetidas_en(rutas, umbral=26):
    """Control de calidad: pares demasiado parecidos dentro de una misma pieza."""
    mal = []
    for i in range(len(rutas)):
        for j in range(i+1, len(rutas)):
            d = distancia(phash(rutas[i]), phash(rutas[j]))
            if d < umbral:
                mal.append((os.path.basename(rutas[i]), os.path.basename(rutas[j]), d))
    return mal


# ---------------------------------------------------------------- variedad
# El hash perceptual no alcanza. Tres mesas montadas en tres salones distintos
# dan hashes muy diferentes y aun asi son "la misma foto" para quien mira.
# Lo que hay que variar es el TEMA: si hay gente, cuanta luz, que color domina.
import os as _os
from PIL import Image as _Image

_PERF = None
_PERF_CACHE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "perfiles.json")


def _perf_cache():
    global _PERF
    if _PERF is None:
        _PERF = json.load(open(_PERF_CACHE)) if _os.path.exists(_PERF_CACHE) else {}
    return _PERF


def guardar_perfiles():
    if _PERF is not None:
        json.dump(_PERF, open(_PERF_CACHE, "w"))


def perfil(ruta):
    """Firma tematica de una foto: (gente, brillo, color, prefijo, vertical)."""
    c = _perf_cache()
    if ruta in c:
        return tuple(c[ruta])
    from recorte import caras
    im = _Image.open(ruta).convert("RGB")
    w, h = im.size
    ch = im.resize((48, 48), _Image.LANCZOS)
    px = list(ch.getdata())
    r = sum(p[0] for p in px) / len(px)
    g = sum(p[1] for p in px) / len(px)
    b = sum(p[2] for p in px) / len(px)
    brillo = (r*0.299 + g*0.587 + b*0.114)

    cs = [f for f in caras(ruta) if f[4] >= 0.7]
    grandes = [f for f in cs if f[2]*f[3] > w*h*0.010]
    if grandes:      gente = "retrato"       # alguien es el sujeto
    elif len(cs) >= 3: gente = "grupo"       # varias personas chicas: escena social
    elif cs:         gente = "alguien"
    else:            gente = "sin_gente"

    if brillo < 70:    luz = "oscura"
    elif brillo < 125: luz = "media"
    else:              luz = "clara"

    calido = (r - b) / max(1.0, (r + b) / 2)
    if calido > 0.18:    color = "calido"
    elif calido < -0.10: color = "frio"
    else:                color = "neutro"

    pref = _os.path.basename(ruta).split("__")[0]
    vert = "v" if h > w else "h"
    p = (gente, luz, color, pref, vert)
    c[ruta] = list(p)
    return p


_VETADAS = None
def _vetadas(size):
    """Fotos que en ese formato no entran sin partir un rostro. No se usan."""
    global _VETADAS
    if _VETADAS is None:
        p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fotos_que_cortan.json")
        _VETADAS = json.load(open(p)) if _os.path.exists(p) else {}
    clave = "4:5" if size[1] > size[0] and size[1] / size[0] < 1.5 else "9:16"
    return set(_VETADAS.get(clave, []))


def variadas(cands, n, arranque=0, max_por_tema=1, size=None):
    """Elige n fotos que cuenten cosas distintas, no la misma tres veces.

    Prioriza cambiar de tema (gente / luz / color) y de sesion (prefijo).
    Recien si no alcanza el material afloja la exigencia.
    """
    if not cands:
        return []
    if size is not None:
        veto = _vetadas(size)
        limpias = [p for p in cands if p not in veto]
        if len(limpias) >= n:
            cands = limpias
    orden = cands[arranque:] + cands[:arranque]
    for tope in (max_por_tema, max_por_tema + 1, max_por_tema + 2, 99):
        for exigir_prefijo in (True, False):
            eleg, hs, temas, prefs = [], [], {}, {}
            for p in orden:
                ge, lz, co, pr, _ = perfil(p)
                tema = (ge, lz, co)
                if temas.get(tema, 0) >= tope:
                    continue
                if exigir_prefijo and prefs.get(pr, 0) >= 1:
                    continue
                h = phash(p)
                if any(distancia(h, o) < 20 for o in hs):
                    continue
                eleg.append(p); hs.append(h)
                temas[tema] = temas.get(tema, 0) + 1
                prefs[pr] = prefs.get(pr, 0) + 1
                if len(eleg) == n:
                    return eleg
    return distintas(cands, n, 20, arranque)


def temas_repetidos(rutas, tope=1):
    """Control de calidad: ¿esta pieza cuenta lo mismo dos veces?"""
    from collections import Counter
    c = Counter(perfil(p)[:3] for p in rutas)
    return [(t, k) for t, k in c.items() if k > tope]


# Prefijos que son pozos mezclados (muchas personas y lugares distintos).
# Todos los demas son una sesion con un solo cliente: de ahi entra una sola foto.
# Un prefijo con MUCHAS fotos suele ser un pozo mezclado (la web vieja, por
# ejemplo). Uno con pocas es una sola sesion de un solo cliente.
MEZCLADOS = {"v"}
MINIMO_MEZCLADO = 10


def una_por_escena(cands, n, arranque=0, size=None, prefiere_gente=False, excluir=None):
    """Elige n fotos de ESCENAS distintas. Si no hay, devuelve menos.

    Un carrusel con la misma sesion tres veces se lee como relleno. Antes que
    repetir, este selector devuelve una lista mas corta y el carrusel se acorta.

    Escena = misma sesion (prefijo del archivo) + mismo tema (gente/luz/color).
    Ademas se exige distancia de hash: dos tomas casi iguales de la misma
    sesion nunca entran juntas.
    """
    if not cands:
        return []
    if size is not None:
        veto = _vetadas(size)
        limpias = [p for p in cands if p not in veto]
        if len(limpias) >= 2:
            cands = limpias
    if excluir:
        libres = [p for p in cands if p not in excluir]
        if len(libres) >= 3:      # si casi no queda nada, se permite reutilizar
            cands = libres
    orden = cands[arranque:] + cands[:arranque]

    if prefiere_gente:
        # En bodas, fiestas o retratos el sujeto es la gente. Las fotos de
        # detalle acompañan, no llevan el carrusel: van al final de la cola.
        con = [p for p in orden if perfil(p)[0] != "sin_gente"]
        sin = [p for p in orden if perfil(p)[0] == "sin_gente"]
        orden = con + sin

    eleg, hs, escenas, temas = [], [], set(), {}
    for tope_sesion in (1, 2, 3):
        for p in orden:
            if p in eleg:
                continue
            ge, lz, co, pr, _ = perfil(p)
            h = phash(p)

            if ge == "sin_gente":
                # Paisaje, plato, salon: manda el parecido visual, pero ademas
                # no pueden entrar cuatro mesas montadas solo porque los
                # salones sean distintos. Dos por tipo de escena y basta.
                if any(distancia(h, o) < 30 for o in hs):
                    continue
                t = (ge, lz, co)
                if temas.get(t, 0) >= 2:
                    continue
                if temas.get(("_sesion_", pr), 0) >= 2:
                    continue          # dos por cliente y basta
                temas[t] = temas.get(t, 0) + 1
                temas[("_sesion_", pr)] = temas.get(("_sesion_", pr), 0) + 1
            else:
                # Con gente, la misma sesion es la misma escena: mismo fondo,
                # misma ropa, misma luz.
                # De una sesion de un solo cliente entra UNA foto: dos retratos
                # del mismo señor en la misma biblioteca son la misma persona,
                # aunque el hash diga que las imagenes difieren.
                # De una sesion pueden entrar hasta dos fotos, pero solo si se
                # ven claramente distintas. Medido sobre el archivo: dos tomas
                # del mismo señor en el mismo lugar quedan por debajo de 42.
                n_sesion = sum(1 for q in cands
                               if _os.path.basename(q).split("__")[0] == pr)
                mezclado = pr in MEZCLADOS and n_sesion >= MINIMO_MEZCLADO
                tope = tope_sesion if mezclado else (2 if n_sesion >= 6 else 1)
                esc = (pr, ge, lz)
                if esc in escenas:
                    continue
                if sum(1 for e in escenas if e[0] == pr) >= tope:
                    continue
                if any(distancia(h, o) < (40 if mezclado else 42) for o in hs):
                    continue
                escenas.add(esc)

            eleg.append(p); hs.append(h)
            if len(eleg) == n:
                return _sin_rachas(eleg)
    return _sin_rachas(eleg)


def _sin_rachas(rutas, maxi=2):
    """Reordena para que no haya tres fotos seguidas del mismo tipo.

    Cinco mesas montadas una atras de otra se leen como relleno aunque cada
    salon sea distinto. Se intercalan para que el carrusel respire.
    """
    if len(rutas) < 3:
        return rutas
    resto = list(rutas)
    salida, racha, ult = [], 0, None
    while resto:
        elegido = None
        for p in resto:
            t = perfil(p)[0]
            if t != ult or racha < maxi:
                elegido = p; break
        if elegido is None:
            elegido = resto[0]
        t = perfil(elegido)[0]
        racha = racha + 1 if t == ult else 1
        ult = t
        salida.append(elegido); resto.remove(elegido)
    return salida
