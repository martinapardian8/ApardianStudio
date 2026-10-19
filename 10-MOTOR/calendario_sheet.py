# -*- coding: utf-8 -*-
"""Arma la planilla de aprobación de Instagram desde el calendario.

Lee 08-CONTENIDO-INSTAGRAM/calendario.json y escribe
11-AUTOMATIZACION/calendario_instagram.csv: una fila por publicación de feed
o reel, con los archivos en el orden en que se suben, la URL pública de cada
uno (apardianstudio.com/ig/...) y el pie de foto completo.

Esa planilla se importa a Google Sheets (hoja "Calendario") y es lo que leen
los flujos 07 (aprobación por Telegram) y 08 (publicador). Nada se publica si
la fila no dice "aprobado".

Las historias quedan afuera: la API de Instagram no programa historias para
una cuenta como la de Martin. Siguen siendo manuales (están en el calendario).

python3 10-MOTOR/calendario_sheet.py
"""
import os, re, csv, json, glob
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
SALIDA = os.path.join(RAIZ, "11-AUTOMATIZACION", "calendario_instagram.csv")
BASE_URL = "https://apardianstudio.com/ig/"
COLUMNAS = ["id", "fecha", "hora", "tipo", "titulo", "archivos", "urls", "pie",
            "primer_comentario", "estado", "aprobado_por", "aprobado_en",
            "publicado_en", "ig_media_id", "error"]
MAX_PIE = 2200          # límite de Instagram para el pie de foto
MAX_CARRUSEL = 10       # hojas por carrusel que acepta la API


def leer(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------ pies de foto
def pies_collage():
    """{'01': {'pie':..., 'comentario':...}} desde 06-carruseles-collage/00_COPYS.md"""
    md = leer(os.path.join(IG, "06-carruseles-collage", "00_COPYS.md"))
    out = {}
    for b in re.split(r"\n## ", md)[1:]:
        m = re.match(r"(\d\d) · ", b)
        if not m:
            continue
        pie = re.search(r"```\n(.*?)```", b, re.S)
        com = re.search(r"Primer comentario[^:]*: `(.+?)`", b)
        out[m.group(1)] = {"pie": pie.group(1).strip() if pie else "",
                           "comentario": com.group(1) if com else ""}
    return out


def pies_campana():
    """Pie base por campaña ('bodas', 'gastronomia'...) desde 00_PLAN.md."""
    md = leer(os.path.join(IG, "00_PLAN.md"))
    sec = md[md.index("## Pies de foto"):]
    out = {}
    for m in re.finditer(r"### (\w+)\n```\n(.*?)```", sec, re.S):
        out[m.group(1)] = m.group(2).strip()
    return out


def pie_mundo_base():
    md = leer(os.path.join(IG, "08-tus-fotos-en-el-mundo", "00_LEEME.md"))
    m = re.search(r"## Pie de foto base.*?```\n(.*?)```", md, re.S)
    return m.group(1).strip() if m else "{Frase del posteo}"


# ------------------------------------------------------------------ piezas
def archivos_carpeta(rel):
    """Archivos de una carpeta, en orden de subida, relativos a 08-CONTENIDO-INSTAGRAM."""
    d = os.path.join(IG, rel)
    if os.path.exists(os.path.join(d, "video.mp4")):
        return [rel + "/video.mp4"]
    fotos = sorted(glob.glob(os.path.join(d, "foto-*.jpg")),
                   key=lambda p: int(re.search(r"foto-(\d+)", p).group(1)))
    if not fotos:
        fotos = sorted(glob.glob(os.path.join(d, "[0-9][0-9].jpg")))
    return [os.path.relpath(p, IG) for p in fotos]


def tipo_de(archivos):
    if archivos and archivos[0].endswith(".mp4"):
        return "REEL"
    return "CAROUSEL" if len(archivos) > 1 else "IMAGE"


def fila(item, fecha, collage, campanas, mundo, base_mundo):
    """Devuelve la fila de la planilla o None si no es una publicación de feed/reel."""
    pieza, tipo_cal = item.get("pieza") or "", item["tipo"]
    if tipo_cal in ("Historia", "Venta", "Automatización") or not pieza:
        return None
    pie, comentario, archivos = "", "", []

    if pieza.startswith("06-carruseles-collage/"):
        slug = pieza.split("/")[1]
        archivos = archivos_carpeta(pieza)
        c = collage.get(slug[:2], {})
        pie, comentario = c.get("pie", ""), c.get("comentario", "")
    elif pieza.startswith("07-reels-collage/"):
        slug = os.path.basename(pieza)[:-4]
        archivos = [pieza]
        portada = "07-reels-collage/" + slug + "_portada.jpg"
        if os.path.exists(os.path.join(IG, portada)):
            archivos.append(portada)          # el publicador la usa como cover_url
        c = collage.get(slug[:2], {})
        pie, comentario = c.get("pie", ""), c.get("comentario", "")
    elif pieza.startswith("08-tus-fotos-en-el-mundo/"):
        archivos = [pieza]
        m = next((x for x in mundo if x["archivo"] == os.path.basename(pieza)), None)
        frase = m["frase"] if m else item.get("titulo", "")
        pie = base_mundo.replace("{Frase del posteo}", frase)
    elif pieza.startswith("00-SUBIR-EN-ORDEN/"):
        archivos = archivos_carpeta(pieza)
        cp = os.path.join(IG, pieza, "copy.txt")
        pie = leer(cp).strip() if os.path.exists(cp) else ""
    elif pieza.startswith("05-videos/"):
        archivos = [pieza]
        campana = os.path.basename(pieza).split("_")[1]
        pie = campanas.get(campana, "")
    else:
        return None

    faltan = [a for a in archivos if not os.path.exists(os.path.join(IG, a))]
    if not archivos or faltan:
        print("  OJO, faltan archivos para", pieza, faltan)
        return None
    tipo = tipo_de(archivos)
    error = ""
    if tipo == "CAROUSEL" and len(archivos) > MAX_CARRUSEL:
        error = "carrusel de más de %d hojas: la API no lo acepta" % MAX_CARRUSEL
    if len(pie) > MAX_PIE:
        error = (error + "; " if error else "") + "pie de más de %d caracteres" % MAX_PIE
    hhmm = item["hora"].replace(":", "")
    nombre = os.path.splitext(os.path.basename(pieza))[0].lower()
    if nombre.isdigit():                      # 00-SUBIR-EN-ORDEN/04 -> subir-04
        nombre = "subir-" + nombre
    ident = "%s-%s-%s" % (fecha, hhmm, re.sub(r"[^a-z0-9]+", "-", nombre).strip("-")[:40])
    return {
        "id": ident, "fecha": fecha, "hora": item["hora"], "tipo": tipo,
        "titulo": item.get("titulo", ""),
        "archivos": "|".join(archivos),
        "urls": "|".join(BASE_URL + quote(a) for a in archivos),
        "pie": pie, "primer_comentario": comentario,
        "estado": "error" if error else "pendiente",
        "aprobado_por": "", "aprobado_en": "", "publicado_en": "", "ig_media_id": "",
        "error": error,
    }


def main():
    cal = json.load(open(os.path.join(IG, "calendario.json"), encoding="utf-8"))
    collage, campanas = pies_collage(), pies_campana()
    mundo = json.load(open(os.path.join(IG, "08-tus-fotos-en-el-mundo", "indice.json"), encoding="utf-8"))
    base_mundo = pie_mundo_base()
    filas, historias = [], 0
    for d in cal["dias"]:
        for it in d["items"]:
            if it["tipo"] == "Historia":
                historias += 1
            f = fila(it, d["fecha"], collage, campanas, mundo, base_mundo)
            if f:
                filas.append(f)
    ids = [f["id"] for f in filas]
    assert len(ids) == len(set(ids)), "ids repetidos"
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    por_tipo = {}
    for f in filas:
        por_tipo[f["tipo"]] = por_tipo.get(f["tipo"], 0) + 1
    print(json.dumps({"filas": len(filas), "por_tipo": por_tipo,
                      "historias_manuales": historias,
                      "sin_pie": [f["id"] for f in filas if not f["pie"]],
                      "con_error": [f["id"] for f in filas if f["error"]]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
