# -*- coding: utf-8 -*-
"""Lupa, la crítica de diseño: revisión automática de cada pieza antes de que
llegue a Martin.

Revisa lo que se puede medir (archivos, medidas, peso, duración, pie de foto,
reglas de marca) y escribe la columna `revision` de la planilla:

    ok                      pasa; el flujo 07 se la manda a Martin
    ok · nota: ...          pasa, con algo para mirar
    frenado: ...            no llega a Martin hasta que se corrija
    frenado a mano: ...     lo frenó el agente Lupa mirándola; el script no lo
                            pisa (se borra a mano cuando está corregida)

Desde el 28/10/2026 también frena la foto que no llena un lienzo vertical
(4:5 o 9:16): foto horizontal, franjas, fondo desenfocado o marco alrededor
(foto_horizontal y franjas, más abajo).

Lo que no se mide (si la foto es de las mejores, si la semana se ve pareja en
la grilla) lo mira el agente Lupa (.claude/agents/lupa-critica-diseno.md) con
la hoja de contacto de la semana que arma este mismo script.

    python3 10-MOTOR/lupa.py                      # revisa toda la planilla
    python3 10-MOTOR/lupa.py --semana 2026-10-19  # además, hoja de contacto
    python3 10-MOTOR/lupa.py --sin-fotos          # sin comparar fotos (rápido)
"""
import os, re, sys, csv, json, datetime as dt
import numpy as np
from PIL import Image, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
CSV = os.path.join(RAIZ, "11-AUTOMATIZACION", "calendario_instagram.csv")
SALIDA = os.path.join(RAIZ, "06-NOTAS", "lupa")

MB = 1024 * 1024
# reglas de marca que frenan (ver 09-ESTUDIO/EQUIPO.md)
PROHIBIDO = [
    (r"antes\s*(y|/)\s*despu[eé]s", "habla de antes/después: no tenemos el original sin editar"),
    (r"sin\s+edit", "promete un 'sin editar' que no tenemos"),
]
CTA = re.compile(r"\+?598\s?9\d|whats ?app|wa\.me|escribime|link en (la )?bio", re.I)

# Lo que Martin enseñó (09-ESTUDIO/APRENDIZAJES.md, 24 y 26/10/2026): el texto
# de una pieza no nombra un lugar que no esté confirmado para ESA foto
# (10-MOTOR/fotos.json), y si habla de carta, platos o comida, la foto muestra
# comida, no un kamado ni un fuego.
LUGARES = re.compile(r"\b(uruguay\w*|montevideo|colonia|punta del este|jos[eé] ignacio|la barra|rambla|"
                     r"ciudad vieja|pocitos|carrasco|punta carretas|maldonado|rocha|canelones|pir[ií][aá]polis|"
                     r"cabo polonio|mallorca|palma|espa[ñn]a|barcelona|madrid|estambul|istanbul|turqu[ií]a|"
                     r"los [aá]ngeles|california|hollywood|venice|nueva york|new york|manhattan|central park|bear mountain|"
                     r"nueva jersey|new jersey|drach|buenos aires|argentina|latu)\b", re.I)
COMIDA_TXT = re.compile(r"\b(carta|men[uú]|platos?|comida|delivery|se come|hambre)\b", re.I)
_IDX = None


def _indice_piezas():
    """archivo publicado → {foto, texto} que escriben historias.py y generar_ads.py."""
    global _IDX
    if _IDX is None:
        _IDX = {}
        for nombre, carpetas in (("indice_historias.json", ["04-historias-organicas"]),
                                 ("indice_pauta.json", ["01-posteos-pauta", "02-historias-pauta"])):
            r = os.path.join(IG, nombre)
            if os.path.exists(r):
                for x in json.load(open(r, encoding="utf-8")):
                    for c in carpetas:
                        _IDX[c + "/" + x["archivo"]] = x
    return _IDX


def lugar_y_tema(archivos):
    """Frenos por lugar no confirmado o por foto que no muestra lo que dice el texto."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from motor_ads import ficha, COMIDA
    frenos = []
    for a in archivos:
        x = _indice_piezas().get(a)
        if not x or not x.get("foto"):
            continue
        fi, texto, foto = ficha(x["foto"]), x.get("texto", ""), os.path.basename(x["foto"])
        for m in dict.fromkeys(m.group(0) for m in LUGARES.finditer(texto)):
            if not (fi.get("confirmado") and m.lower()[:5] in fi.get("lugar", "").lower()):
                frenos.append(f'el texto dice "{m}" y la foto {foto} es de '
                              + (fi.get("lugar") or "un lugar sin confirmar") + ": preguntale a Martin dónde es")
        if COMIDA_TXT.search(texto) and fi.get("contenido") not in COMIDA:
            frenos.append(f"el texto habla de comida y la foto {foto} no muestra un plato"
                          + (f" (es {fi['contenido']})" if fi.get("contenido") else ""))
    return frenos


# ------------------------------------------------------------ foto horizontal en lienzo vertical
# Martin, 28/10/2026: "No me gusta que pongas una foto horizontal en un canva
# vertical". En un lienzo vertical (4:5 o 9:16) la foto lo llena de lado a
# lado: nada de foto chica sobre la misma foto desenfocada, franjas ni marco.
def _tramos(fila, minimo=20):
    """Máscara de los tramos largos y seguidos del salto (el borde de una foto
    es una línea entera; el de una línea de texto, no)."""
    f = fila.copy()
    f[1:-1] |= fila[:-2] & fila[2:]           # tapa huecos de un píxel
    out = np.zeros_like(f)
    i, n = 0, len(f)
    while i < n:
        if f[i]:
            j = i
            while j < n and f[j]:
                j += 1
            if j - i >= minimo:
                out[i:j] = True
            i = j
        else:
            i += 1
    return out


def franjas(im):
    """¿La foto quedó chica dentro del lienzo, con franjas, fondo desenfocado
    o marco alrededor? None si la foto llena el cuadro; si no, (nivel, dónde):
    'frenado' si hay franjas a los dos lados de la foto (arriba y abajo, o a
    los costados), 'nota' si hay una sola banda oscura y lisa cortada por una
    línea recta: puede ser una franja o un cielo detrás del texto, la mira Lupa.

    Cómo: busca líneas rectas de lado a lado (el borde de una foto pegada; el
    de una línea de texto o un horizonte natural se corta) y mira si del otro
    lado la imagen es lisa como un desenfoque o un color plano."""
    im = im.convert("L")
    W0, H0 = im.size
    w = 270
    h = max(8, int(round(H0 * w / W0)))
    chica = im.resize((w, h), Image.BILINEAR)
    g = np.asarray(chica, dtype=np.float32)
    lap = np.asarray(chica.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    lap[0, :] = lap[-1, :] = 0
    lap[:, 0] = lap[:, -1] = 0
    bandas = {}
    for eje in ("y", "x"):
        A = g if eje == "y" else g.T
        L = lap if eje == "y" else lap.T
        n, m = A.shape
        d = np.abs(A[2:, :] - A[:-2, :]) >= 8
        for i in range(len(d)):
            y = i + 1
            if y < 0.03 * n or y > 0.97 * n or d[i].mean() < 0.55:
                continue
            tramo = _tramos(d[i])
            if tramo.mean() < 0.55:
                continue
            for lado in ("antes", "despues"):
                if lado == "antes":
                    banda, bl, dentro = A[:y - 1, tramo], L[:y - 1, tramo], A[y + 1:y + 4, tramo]
                else:
                    banda, bl, dentro = A[y + 2:, tramo], L[y + 2:, tramo], A[max(0, y - 3):y, tramo]
                if len(banda) < 0.03 * n:
                    continue
                # el 30 % de las filas más lisas: el texto que va encima de la
                # franja no la esconde
                lisa = float(np.percentile((bl > 6).mean(axis=1), 30))
                if lisa >= 0.015:
                    continue
                # el borde de arriba de una línea de texto blanco no es una foto
                if float(dentro.mean()) > 215:
                    continue
                oscura = float(banda.mean()) < 90
                k = {("y", "antes"): "arriba", ("y", "despues"): "abajo",
                     ("x", "antes"): "a la izquierda", ("x", "despues"): "a la derecha"}[(eje, lado)]
                tam = len(banda) / n
                recta = float(tramo.mean())
                if k not in bandas or recta > bandas[k][2]:
                    bandas[k] = (tam, oscura and recta >= 0.6, recta)
    opuesto = {"arriba": "abajo", "abajo": "arriba",
               "a la izquierda": "a la derecha", "a la derecha": "a la izquierda"}
    # frena solo con franjas a los dos lados de la foto: una sola banda oscura
    # puede ser el degradado detrás del texto sobre un cielo con un borde recto
    # (un techo, el horizonte)
    fuertes = [(k, t) for k, (t, o, r) in bandas.items() if opuesto[k] in bandas]
    if fuertes:
        return "frenado", ", ".join(f"{k} ({int(round(t * 100))} %)" for k, t in fuertes)
    flojas = [(k, t) for k, (t, o, r) in bandas.items() if o]
    if flojas:
        return "nota", ", ".join(f"{k} ({int(round(t * 100))} %)" for k, t in flojas)
    return None


def _cuadros_video(ruta, n=3):
    """Tres cuadros del video (al 15, 50 y 85 %), como imágenes."""
    try:
        import cv2
    except ImportError:
        return []
    v = cv2.VideoCapture(ruta)
    total = int(v.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    out = []
    for t in (0.15, 0.5, 0.85)[:n]:
        v.set(cv2.CAP_PROP_POS_FRAMES, int(total * t))
        ok, im = v.read()
        if ok:
            out.append(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
    v.release()
    return out


_FOTOS_PIEZA = None
def _fotos_de_pieza(a):
    """Las fotos de Martin que muestra una pieza (de los índices del motor)."""
    global _FOTOS_PIEZA
    if _FOTOS_PIEZA is None:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from motor_ads import _fotos_por_pieza
            _FOTOS_PIEZA = _fotos_por_pieza()
        except Exception:
            _FOTOS_PIEZA = {}
    return _FOTOS_PIEZA.get(a, [])


def foto_horizontal(archivos):
    """(frenos, notas) por fotos que no llenan un lienzo vertical."""
    frenos, notas = [], []
    for a in archivos:
        if a.startswith("08-tus-fotos-en-el-mundo/"):
            continue          # los montajes ponen la foto en una escena a propósito
        r = os.path.join(IG, a)
        if not os.path.exists(r):
            continue
        nombre = os.path.basename(a)
        if a.endswith(".jpg"):
            im = Image.open(r)
            ims = [im] if im.height > im.width else []
        elif a.endswith(".mp4"):
            ims = [c for c in _cuadros_video(r) if c.height > c.width]
        else:
            ims = []
        if not ims:
            continue
        fuentes = _fotos_de_pieza(a)
        if fuentes and all("capturas_web" in f for f in fuentes):
            continue          # capturas de la web en el celular: llenan el cuadro, la página tiene sus bloques
        # lo que dice el índice: la foto de la pieza es horizontal o pierde
        # más del 22 % al llenar el cuadro
        try:
            from motor_ads import apta
            for f in fuentes:
                if a.endswith(".mp4") or not os.path.exists(f) or "capturas_web" in f:
                    continue        # las capturas de la web van por ventana, no son fotos
                if not apta(f, ims[0].size):
                    frenos.append(f"{nombre}: la foto {os.path.basename(f)} no llena el lienzo vertical "
                                  "(es horizontal, pierde más del 22 % o corta una cara)")
        except Exception:
            pass
        # lo que se ve: franjas o fondo desenfocado alrededor de la foto
        for im in ims:
            res = franjas(im)
            if res and res[0] == "frenado":
                frenos.append(f"{nombre}: la foto no llena el lienzo vertical, tiene franjas o fondo "
                              f"desenfocado {res[1]} (Martin: nunca una foto horizontal en un lienzo vertical)")
                break
            if res:
                notas.append(f"{nombre}: puede tener una franja {res[1]}; mirala")
                break
    return frenos, notas


def _video(ruta):
    """(ancho, alto, segundos) con OpenCV; None si no se puede leer."""
    try:
        import cv2
    except ImportError:
        return None
    v = cv2.VideoCapture(ruta)
    if not v.isOpened():
        return None
    w, h = int(v.get(cv2.CAP_PROP_FRAME_WIDTH)), int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps, n = v.get(cv2.CAP_PROP_FPS) or 0, v.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    v.release()
    return w, h, (n / fps if fps else 0)


def revisar(f, vistos=None, cercanas=None):
    """f: fila de la planilla (dict). vistos: {archivos: id} de las filas
    anteriores, para no repetir piezas; cercanas: {pieza: (fecha, id)}, para
    avisar si la misma pieza sale en feed e historia con días de diferencia.
    Devuelve el texto de `revision`."""
    frenos, notas = [], []
    tipo = f["tipo"]
    archivos = [a for a in f["archivos"].split("|") if a]
    pie = f.get("pie", "") or ""

    if not archivos:
        frenos.append("no tiene archivos")
    for a in archivos:
        if "_NO-PUBLICAR" in a or a.startswith("_"):
            frenos.append(f"{a} está en una carpeta que no se publica")
        r = os.path.join(IG, a)
        if not os.path.exists(r):
            frenos.append(f"falta {a}")
            continue
        peso = os.path.getsize(r)
        if a.endswith(".jpg"):
            if peso > 8 * MB:
                frenos.append(f"{os.path.basename(a)} pesa {peso / MB:.1f} MB (máximo 8)")
            w, h = Image.open(r).size
            p = w / h
            if tipo == "STORY":
                if abs(p - 9 / 16) > 0.02:
                    notas.append(f"{os.path.basename(a)} no es 9:16 ({w}×{h}): Instagram le pone bordes")
            elif not (0.79 <= p <= 1.92) and not (tipo == "REEL" and a.endswith("_portada.jpg")):
                frenos.append(f"{os.path.basename(a)} mide {w}×{h}: el feed acepta de 4:5 a 1,91:1")
            if w < 1080:
                notas.append(f"{os.path.basename(a)} tiene {w} px de ancho (ideal 1080)")
        elif a.endswith(".mp4"):
            lim = 100 if tipo == "STORY" else 300
            if peso > lim * MB:
                frenos.append(f"{os.path.basename(a)} pesa {peso / MB:.0f} MB (máximo {lim})")
            v = _video(r)
            if v:
                w, h, seg = v
                if tipo == "STORY" and seg > 60:
                    frenos.append(f"historia de {seg:.0f} s (máximo 60)")
                if tipo == "REEL" and not (3 <= seg <= 900):
                    frenos.append(f"reel de {seg:.1f} s (de 3 s a 15 min)")
                # el reel 4:5 se ve entero en el feed; en historias pide 9:16
                bien = [9 / 16] if tipo == "STORY" else [9 / 16, 4 / 5]
                if tipo in ("REEL", "STORY") and h and min(abs(w / h - b) for b in bien) > 0.02:
                    notas.append(f"video {w}×{h}, no es 9:16")
        else:
            frenos.append(f"{a}: solo se publican JPG y MP4")

    if tipo == "CAROUSEL":
        if not 2 <= len(archivos) <= 10:
            frenos.append(f"carrusel de {len(archivos)} hojas (de 2 a 10)")
        medidas = {Image.open(os.path.join(IG, a)).size for a in archivos
                   if a.endswith(".jpg") and os.path.exists(os.path.join(IG, a))}
        if len(medidas) > 1:
            frenos.append("las hojas del carrusel no miden todas igual: Instagram recorta las que no coinciden")

    if tipo != "STORY":
        if not pie.strip():
            frenos.append("no tiene pie de foto")
        if len(pie) > 2200:
            frenos.append(f"pie de {len(pie)} caracteres (máximo 2200)")
        n_hash = len(re.findall(r"#\w", pie))
        if n_hash > 30:
            frenos.append(f"{n_hash} hashtags (máximo 30)")
        elif n_hash > 8:
            notas.append(f"{n_hash} hashtags: con 3 a 5 alcanza")
        if pie and not CTA.search(pie):
            notas.append("el pie no lleva a WhatsApp")
        if any(a.startswith("08-tus-fotos-en-el-mundo/") for a in archivos) and "montaje" not in pie.lower():
            frenos.append("es un montaje y el pie no lo dice")
    for patron, motivo in PROHIBIDO:
        if re.search(patron, pie + " " + f.get("titulo", ""), re.I):
            frenos.append(motivo)
    frenos += lugar_y_tema(archivos)
    fr, no = foto_horizontal(archivos)
    frenos += fr
    notas += no

    if vistos is not None and f["archivos"]:
        if f["archivos"] in vistos and vistos[f["archivos"]] != f["id"]:
            frenos.append("repite una pieza que ya sale el " + vistos[f["archivos"]][:10])
        vistos.setdefault(f["archivos"], f["id"])

    if cercanas is not None:
        hoy = dt.date.fromisoformat(f["fecha"])
        for a in archivos:
            clave = re.sub(r"_(feed|historia)$", "", os.path.splitext(os.path.basename(a))[0])
            if not re.match(r"\d{3}_", clave):
                continue
            antes = cercanas.get(clave)
            if antes and antes[1] != f["id"] and abs((hoy - antes[0]).days) < 7:
                notas.append("la misma pieza salió el " + antes[0].strftime("%d/%m") + ": se ve repetido")
            cercanas[clave] = (hoy, f["id"])

    if frenos:
        return "frenado: " + "; ".join(dict.fromkeys(frenos))
    if notas:
        return "ok · nota: " + "; ".join(dict.fromkeys(notas))
    return "ok"


# ------------------------------------------------------------ misma foto
_DESC = {}


def _descriptores(rel):
    """Puntos SIFT de una imagen (o del cuadro 30 de un video), con el
    contraste parejo para que el velo oscuro del texto no la esconda."""
    if rel in _DESC:
        return _DESC[rel]
    import cv2
    r = os.path.join(IG, rel)
    im = None
    if rel.endswith(".mp4"):
        v = cv2.VideoCapture(r)
        v.set(cv2.CAP_PROP_POS_FRAMES, 30)
        ok, im = v.read()
    elif os.path.exists(r):
        im = cv2.imread(r)
    d = None
    if im is not None:
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        k = 480 / g.shape[1]
        g = cv2.resize(g, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        g = cv2.createCLAHE(3.0, (8, 8)).apply(g)
        k, ds = cv2.SIFT_create(3000).detectAndCompute(g, None)
        d = (k, ds, g.shape[0] * g.shape[1])
    _DESC[rel] = d
    return d


def _misma(a, b, umbral=60, cubre=0.15):
    """True si dos archivos muestran la misma foto, aunque estén recortados,
    con otro tamaño o con texto encima: muchos puntos que coinciden en
    geometría y que cubren buena parte de la imagen (si solo coinciden la
    etiqueta, los botones o el logo de la plantilla, cubren menos del 6 %)."""
    import cv2, numpy as np
    cv2.setRNGSeed(0)                 # FLANN arma arboles al azar: misma semilla, misma respuesta
    da, db = _descriptores(a), _descriptores(b)
    if not da or not db or da[1] is None or db[1] is None or len(da[0]) < 8 or len(db[0]) < 8:
        return False
    m = cv2.FlannBasedMatcher({"algorithm": 1, "trees": 4}, {"checks": 40}).knnMatch(da[1], db[1], k=2)
    g = [x[0] for x in m if len(x) == 2 and x[0].distance < 0.75 * x[1].distance]
    if len(g) < umbral:
        return False
    A = np.float32([da[0][x.queryIdx].pt for x in g])
    B = np.float32([db[0][x.trainIdx].pt for x in g])
    _, mask = cv2.findHomography(A, B, cv2.RANSAC, 5.0)
    if mask is None or int(mask.sum()) < umbral:
        return False
    # en cualquiera de las dos: la foto chica dentro de un aviso cubre poco
    # del aviso pero casi toda la otra imagen
    dentro = mask.ravel() == 1
    return max(cv2.contourArea(cv2.convexHull(A[dentro])) / da[2],
               cv2.contourArea(cv2.convexHull(B[dentro])) / db[2]) >= cubre


def fotos_repetidas(filas, dias=3):
    """{id: texto} para las piezas que muestran la misma foto que otra
    publicada con menos de `dias` días de diferencia (feed o historia)."""
    try:
        import cv2  # noqa: F401
    except ImportError:
        return {}
    orden = sorted(filas, key=lambda f: (f["fecha"], f["hora"]))
    out = {}
    for i, f in enumerate(orden):
        fi = dt.date.fromisoformat(f["fecha"])
        mias = [a for a in f["archivos"].split("|") if a and not a.endswith("_portada.jpg")]
        for g in orden[i + 1:]:
            if (dt.date.fromisoformat(g["fecha"]) - fi).days >= dias:
                break
            suyas = [a for a in g["archivos"].split("|") if a and not a.endswith("_portada.jpg")]
            # las hojas de un carrusel collage son cortes del mismo lienzo, y su
            # reel del jueves lo recorre a propósito
            def slug(x):
                return os.path.splitext(x.split("|")[0].split("/")[1])[0] if "/" in x else x
            if slug(f["archivos"]) == slug(g["archivos"]):
                continue
            if any(_misma(a, b) for a in mias for b in suyas):
                out.setdefault(g["id"], "misma foto que la pieza del " + fi.strftime("%d/%m") + " (" + f["titulo"][:40] + ")")
    return out


def hoja_de_contacto(filas, lunes):
    """Una imagen con la semana entera: arriba el feed como se vería en la
    grilla, abajo las historias. Para que Lupa y Martin la miren de una."""
    desde = dt.date.fromisoformat(lunes)
    dias = {(desde + dt.timedelta(days=i)).isoformat() for i in range(7)}
    sem = sorted((f for f in filas if f["fecha"] in dias), key=lambda f: (f["fecha"], f["hora"]))
    feed = [f for f in sem if f["tipo"] != "STORY"]
    hist = [f for f in sem if f["tipo"] == "STORY"]

    def primera(f):
        for a in f["archivos"].split("|"):
            r = os.path.join(IG, a)
            if a.endswith(".jpg") and os.path.exists(r):
                return Image.open(r).convert("RGB")
            if a.endswith(".mp4") and os.path.exists(r):
                try:
                    import cv2
                    v = cv2.VideoCapture(r)
                    v.set(cv2.CAP_PROP_POS_FRAMES, 30)
                    ok, im = v.read()
                    if ok:
                        return Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
                except ImportError:
                    pass
        return Image.new("RGB", (1080, 1350), (200, 200, 200))

    from PIL import ImageDraw, ImageFont
    try:
        letra = ImageFont.truetype(os.path.join(RAIZ, "10-MOTOR", "fuentes", "WorkSans.ttf"), 22)
    except OSError:
        letra = ImageFont.load_default()
    cw, ch, sw, sh, m = 300, 375, 170, 302, 24
    ancho = m + 7 * (cw + m)
    alto = m + ch + 70 + sh + 70
    lienzo = Image.new("RGB", (ancho, alto), (248, 247, 246))
    d = ImageDraw.Draw(lienzo)
    for i, f in enumerate(feed[:7]):
        im = primera(f)
        im = im.resize((cw, int(cw * im.height / im.width)))
        im = im.crop((0, max(0, (im.height - ch) // 2), cw, max(0, (im.height - ch) // 2) + ch))
        x = m + i * (cw + m)
        lienzo.paste(im, (x, m))
        color = (255, 0, 51) if f.get("revision", "").startswith("frenado") else (23, 23, 23)
        d.text((x, m + ch + 8), f"{f['fecha'][8:]}/{f['fecha'][5:7]} {f['hora']} · {f['tipo']}", fill=color, font=letra)
        d.text((x, m + ch + 36), f["titulo"][:26], fill=(90, 90, 90), font=letra)
    y = m + ch + 70
    for i, f in enumerate(hist[:7]):
        im = primera(f).resize((sw, sh))
        x = m + i * (cw + m) + (cw - sw) // 2
        lienzo.paste(im, (x, y))
        d.text((m + i * (cw + m), y + sh + 8), f"historia {f['fecha'][8:]}/{f['fecha'][5:7]}", fill=(23, 23, 23), font=letra)
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, f"semana-{lunes}.jpg")
    lienzo.save(ruta, quality=88)
    return ruta


def main():
    filas = list(csv.DictReader(open(CSV, encoding="utf-8")))
    columnas = list(filas[0].keys()) if filas else []
    if "revision" not in columnas:
        columnas.append("revision")
    vistos, cercanas, frenadas, con_nota = {}, {}, [], []
    activas = [f for f in filas if f.get("estado") not in ("publicado", "rechazado")]
    repetidas = fotos_repetidas(activas) if "--sin-fotos" not in sys.argv else {}
    for f in sorted(filas, key=lambda f: (f["fecha"], f["hora"])):
        if f.get("estado") in ("publicado", "rechazado"):
            vistos.setdefault(f["archivos"], f["id"])
            continue
        previa = f.get("revision", "") or ""
        auto = revisar(f, vistos, cercanas)
        if f["id"] in repetidas and not auto.startswith("frenado"):
            auto = ("ok · nota: " if auto == "ok" else auto + "; ") + repetidas[f["id"]]
        # el veto que puso el agente Lupa mirando la pieza no lo pisa el script
        f["revision"] = previa if previa.startswith("frenado a mano") else auto
        if f["revision"].startswith("frenado"):
            frenadas.append(f)
        elif "nota" in f["revision"]:
            con_nota.append(f)
    with open(CSV, "w", encoding="utf-8", newline="") as s:
        w = csv.DictWriter(s, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)

    md = ["# Revisión de Lupa", f"{dt.date.today().isoformat()} · {len(filas)} piezas en la planilla.", "",
          f"**Frenadas:** {len(frenadas)} · **Con nota:** {len(con_nota)} · "
          f"**Listas para Martin:** {len(filas) - len(frenadas)}", ""]
    if frenadas:
        md += ["## Frenadas (no llegan a Telegram hasta corregirlas)", ""]
        md += [f"- `{f['id']}` {f['titulo']}: {f['revision'][9:]}" for f in frenadas] + [""]
    if con_nota:
        md += ["## Pasan, con algo para mirar", ""]
        md += [f"- `{f['id']}` {f['titulo']}: {f['revision'].split('nota: ', 1)[1]}" for f in con_nota] + [""]
    os.makedirs(SALIDA, exist_ok=True)
    open(os.path.join(SALIDA, "REVISION.md"), "w", encoding="utf-8").write("\n".join(md))

    if "--semana" in sys.argv:
        lunes = sys.argv[sys.argv.index("--semana") + 1]
        print("hoja de contacto:", os.path.relpath(hoja_de_contacto(filas, lunes), RAIZ))
    print(json.dumps({"piezas": len(filas), "frenadas": len(frenadas), "con_nota": len(con_nota)}))


if __name__ == "__main__":
    main()
