# -*- coding: utf-8 -*-
"""Arma la app "Centro APARDIAN" (12-CENTRO/index.html + miniaturas).

Junta en una sola pagina el calendario (calendario.json), cada pieza de
Instagram con su miniatura, su pie y lo que dijo Lupa (calendario_instagram.csv),
los carruseles collage con sus textos (00_COPYS.md), los guiones de venta
(CM_VENTAS.md) y las instrucciones de los tres agentes (.claude/agents), que
la app usa para que Luz, Lupa y Trato trabajen desde ahi. Lo que cambia con el
uso (que se publico, los clientes, las ordenes a los agentes) vive en la base
de datos del artifact, no en este archivo.

python3 10-MOTOR/centro.py
"""
import hashlib, os, re, csv, sys, json, glob, datetime as dt
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendario_sheet as hoja

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
COL = os.path.join(IG, "06-carruseles-collage")
OUT = os.path.join(RAIZ, "12-CENTRO")
PLANTILLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centro_plantilla.html")


def carruseles(publicados=frozenset()):
    copys = open(os.path.join(COL, "00_COPYS.md")).read()
    bloques = re.split(r"\n## ", copys)[1:]
    por_num = {}
    for b in bloques:
        cab = b.split("\n", 1)[0]
        m = re.match(r"(\d\d) · (.+?) — \"(.+)\"", cab)
        if not m:
            continue
        pie = re.search(r"```\n(.*?)```", b, re.S)
        para = re.search(r"Para: (.+)", b)
        coment = re.search(r"Primer comentario[^:]*: `(.+?)`", b)
        nota = re.search(r"\nNota[^:]*: (.+?)(?:\n\n|$)", b, re.S)
        por_num[m.group(1)] = {"vertical": m.group(2), "titulo": m.group(3),
                               "para": para.group(1) if para else "",
                               "pie": pie.group(1).strip() if pie else "",
                               "comentario": coment.group(1) if coment else "",
                               "nota": " ".join(nota.group(1).split()) if nota else ""}
    out = []
    for d in sorted(glob.glob(os.path.join(COL, "[0-9][0-9]-*"))):
        slug = os.path.basename(d)
        info = por_num.get(slug[:2], {})
        dst = os.path.join(OUT, "car", slug)
        lams = sorted(glob.glob(os.path.join(d, "[0-9][0-9].jpg")))
        srcs = []
        for p in lams:
            # si la lámina ya se publica para bajar (ig/), se muestra esa: no
            # gasta un archivo más del tope de la app
            ig = "ig/06-carruseles-collage/%s/%s" % (slug, os.path.basename(p))
            if ig in publicados:
                srcs.append(ig); continue
            os.makedirs(dst, exist_ok=True)
            im = Image.open(p).convert("RGB")
            im.thumbnail((432, 540), Image.LANCZOS)
            im.save(os.path.join(dst, os.path.basename(p)), quality=74, optimize=True)
            srcs.append("car/%s/%s" % (slug, os.path.basename(p)))
        out.append({"slug": slug, "laminas": len(lams), "srcs": srcs, **info})
    # las miniaturas que ya no hacen falta se borran
    usados = {x for c in out for x in c["srcs"] if x.startswith("car/")}
    for raiz, _, fs in os.walk(os.path.join(OUT, "car")):
        for f in fs:
            r = os.path.relpath(os.path.join(raiz, f), OUT).replace(os.sep, "/")
            if r not in usados:
                os.remove(os.path.join(raiz, f))
    return out


def guiones():
    md = open(os.path.join(RAIZ, "09-ESTUDIO", "CM_VENTAS.md")).read()
    sec = md[md.index("## 3. Guiones por servicio"):md.index("## 4. WhatsApp Business")]
    grupos, actual = [], None
    for linea in sec.split("\n"):
        if linea.startswith("### "):
            actual = {"grupo": re.sub(r"^### [\d.]+ ", "", linea).strip(), "items": []}
            grupos.append(actual)
        elif actual is None:
            continue
        elif linea.startswith("**") and linea.rstrip().endswith("**"):
            actual["items"].append({"nombre": linea.strip("* \n"), "texto": "", "nota": ""})
        elif linea.startswith("> "):
            if not actual["items"] or actual["items"][-1]["texto"] and actual["items"][-1].get("_cerrado"):
                actual["items"].append({"nombre": "", "texto": "", "nota": ""})
            it = actual["items"][-1]
            it["texto"] = (it["texto"] + " " + linea[2:].strip()).strip()
        elif linea.startswith("(") and actual["items"]:
            actual["items"][-1]["nota"] = linea.strip("() ")
            actual["items"][-1]["_cerrado"] = True
        elif linea.strip() == "" and actual["items"] and actual["items"][-1]["texto"]:
            actual["items"][-1]["_cerrado"] = True
    for g in grupos:
        g["items"] = [{k: v for k, v in it.items() if not k.startswith("_")}
                      for it in g["items"] if it["texto"]]
    return [g for g in grupos if g["items"]]


def miniatura(rel, destino, ancho):
    """Primera imagen (o un cuadro del video) de una pieza, chica, para la app."""
    r = os.path.join(IG, rel)
    if rel.endswith(".mp4"):
        import cv2
        v = cv2.VideoCapture(r)
        v.set(cv2.CAP_PROP_POS_FRAMES, 30)
        ok, im = v.read()
        if not ok:
            return False
        im = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    else:
        im = Image.open(r).convert("RGB")
    im.thumbnail((ancho, ancho * 2), Image.LANCZOS)
    im.save(destino, quality=72, optimize=True, progressive=True)
    return True


def piezas(cal):
    """Una entrada por posteo o historia del calendario, con el id de la
    planilla, la tarea del calendario a la que corresponde y su miniatura."""
    revision = {}
    if os.path.exists(hoja.SALIDA):
        revision = {r["id"]: r.get("revision", "") for r in csv.DictReader(open(hoja.SALIDA, encoding="utf-8"))}
    collage, campanas = hoja.pies_collage(), hoja.pies_campana()
    mundo = json.load(open(os.path.join(IG, "08-tus-fotos-en-el-mundo", "indice.json"), encoding="utf-8"))
    base_mundo = hoja.pie_mundo_base()
    dst = os.path.join(OUT, "pz")
    os.makedirs(dst, exist_ok=True)
    out = []
    for d in cal["dias"]:
        for i, it in enumerate(d["items"]):
            f = hoja.fila(it, d["fecha"], collage, campanas, mundo, base_mundo)
            if not f:
                continue
            archivos = f["archivos"].split("|")
            principal = archivos[0]
            nombre = f["id"] + ".jpg"
            # en la ventana, la miniatura es la misma foto que se baja (ig/):
            # así no se gasta un archivo más del tope de la app
            foto = next((x for x in archivos if x.lower().endswith((".jpg", ".jpeg"))), None)
            if en_ventana(d["fecha"]) and foto:
                img = "ig/" + foto
            else:
                img = "pz/" + nombre
                if not os.path.exists(os.path.join(dst, nombre)):
                    miniatura(principal, os.path.join(dst, nombre), 240 if f["tipo"] == "STORY" else 360)
            # los archivos en el orden en que se suben, para guardarlos de a uno en el celular
            hojas = [x for x in archivos if not x.endswith("_portada.jpg")]
            base = "apardian-%s-%s" % (d["fecha"][8:10] + d["fecha"][5:7], "historia" if f["tipo"] == "STORY" else "posteo")
            bajar = [{"src": "ig/" + x, "nombre": base + ("-%02d" % k if len(hojas) > 1 else "") + os.path.splitext(x)[1]}
                     for k, x in enumerate(hojas, 1)]
            bajar += [{"src": "ig/" + x, "nombre": base + "-tapa.jpg"} for x in archivos if x.endswith("_portada.jpg")]
            if not en_ventana(d["fecha"]):
                bajar = []
            # la versión cambia si Luz rehace la pieza (otros archivos, otro peso u otro pie):
            # el Centro vuelve a pedir ✓ o ✗
            firma = f["archivos"] + "|" + f["pie"] + "|" + "|".join(str(os.path.getsize(os.path.join(IG, a))) for a in archivos)
            out.append({"id": f["id"], "cal": d["fecha"] + "-" + str(i), "fecha": d["fecha"], "hora": f["hora"], "bajar": bajar,
                        "archivos": f["archivos"], "urls": f["urls"], "ver": hashlib.sha1(firma.encode()).hexdigest()[:10],
                        "tipo": f["tipo"], "titulo": f["titulo"], "pie": f["pie"],
                        "comentario": f["primer_comentario"], "hojas": len([a for a in archivos if not a.endswith("_portada.jpg")]),
                        "pieza": it["pieza"], "nota": it.get("nota", ""),
                        "revision": revision.get(f["id"], ""), "img": img})
    # las miniaturas de piezas que ya no estan en el calendario (o que ya se
    # muestran con la foto de ig/) se borran
    vigentes = {os.path.basename(p["img"]) for p in out if p["img"].startswith("pz/")}
    for x in os.listdir(dst):
        if x not in vigentes:
            os.remove(os.path.join(dst, x))
    return out


# La app tiene un tope de 511 archivos. Los de bajar (fotos y videos en tamaño
# real) se publican para todos los días que vienen: la ventana arranca ayer y
# llega hasta el final del calendario. Si un día no entra todo, main() la
# achica de a una semana hasta que entre (TOPE_ARCHIVOS).
VENTANA_DIAS = int(os.environ.get("CENTRO_VENTANA") or 400)
TOPE_ARCHIVOS = 490
DESDE = os.environ.get("CENTRO_DESDE") or dt.date.today().isoformat()


def en_ventana(fecha):
    d0 = dt.date.fromisoformat(DESDE)
    return d0 - dt.timedelta(days=1) <= dt.date.fromisoformat(fecha) <= d0 + dt.timedelta(days=VENTANA_DIAS)


DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _sin_tildes(t):
    # los nombres dentro del ZIP van sin tildes: así se leen igual en Mac y Windows
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t) if not unicodedata.combining(c))


def _limpio(t, largo=48):
    t = _sin_tildes(t)
    t = re.sub(r'[\\/:*?"<>|\n]+', " ", t).strip().rstrip(".")
    return (t[:largo].rstrip() + "…") if len(t) > largo else t


def archivos_por_dia(cal):
    """Qué va en la carpeta de cada día: una subcarpeta por pieza con los
    archivos en el orden en que se suben (01.jpg, 02.jpg… o el video) y el pie
    en pie.txt. La app arma el ZIP en el navegador con esta lista; los
    archivos se publican en ig/ con la misma ruta que en 08-CONTENIDO-INSTAGRAM
    (ver archivos_ig). Al bajarlo, Safari lo abre solo y queda la carpeta."""
    collage, campanas = hoja.pies_collage(), hoja.pies_campana()
    mundo = json.load(open(os.path.join(IG, "08-tus-fotos-en-el-mundo", "indice.json"), encoding="utf-8"))
    base_mundo = hoja.pie_mundo_base()
    out = {}
    for d in cal["dias"]:
        if not en_ventana(d["fecha"]):
            continue
        filas = [f for it in d["items"] for f in [hoja.fila(it, d["fecha"], collage, campanas, mundo, base_mundo)] if f]
        if not filas:
            continue
        fecha = dt.date.fromisoformat(d["fecha"])
        raiz = "APARDIAN %s %s" % (fecha.strftime("%d-%m"), _sin_tildes(DIAS_ES[fecha.weekday()]))
        items, peso = [], 0
        for i, f in enumerate(sorted(filas, key=lambda f: (f["tipo"] == "STORY", f["hora"])), 1):
            tipo = {"STORY": "Historia", "IMAGE": "Posteo", "CAROUSEL": "Carrusel", "REEL": "Reel"}[f["tipo"]]
            carpeta = "%s/%d %s %s - %s/" % (raiz, i, tipo, f["hora"].replace(":", "."), _limpio(f["titulo"]))
            archivos = f["archivos"].split("|")
            hojas = [a for a in archivos if not a.endswith("_portada.jpg")]
            for k, a in enumerate(hojas, 1):
                ext = os.path.splitext(a)[1]
                nom = ("%02d%s" % (k, ext)) if len(hojas) > 1 else (tipo.lower() + ext)
                items.append({"ruta": carpeta + nom, "src": "ig/" + a})
                peso += os.path.getsize(os.path.join(IG, a))
            for a in archivos:
                if a.endswith("_portada.jpg"):
                    items.append({"ruta": carpeta + "tapa del reel.jpg", "src": "ig/" + a})
                    peso += os.path.getsize(os.path.join(IG, a))
            if f["pie"]:
                texto = f["pie"] + ("\n\n— Primer comentario (fijalo):\n" + f["primer_comentario"] if f["primer_comentario"] else "") + "\n"
            else:
                texto = "Historia: no lleva pie. Sale a las " + f["hora"] + ".\n"
            items.append({"ruta": carpeta + "pie.txt", "texto": texto})
        out[d["fecha"]] = {"nombre": raiz + ".zip", "kb": peso // 1024, "items": items}
    return out


def archivos_ig(dias):
    """{ruta publicada: ruta en el repo} de todos los archivos que bajan los días."""
    return {it["src"]: "08-CONTENIDO-INSTAGRAM/" + it["src"][3:]
            for d in dias.values() for it in d["items"] if "src" in it}


def leer(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()


def agentes():
    """Instrucciones de cada agente (sin el encabezado) y lo que tienen que
    saber del negocio. La app se las pasa a Claude en cada pedido."""
    def cuerpo(rel):
        t = leer(rel)
        return t.split("---", 2)[2].strip() if t.startswith("---") else t
    base = "\n\n".join(leer(r) for r in ["09-ESTUDIO/NEGOCIO.md", "09-ESTUDIO/MARCA.md", "09-ESTUDIO/APRENDIZAJES.md"])
    base += ("\n\nTambién vende producción musical (composición, grabación, mix, mastering y videoclip; "
             "Martin es pianista y productor, trabaja en Ableton; su último EP es FUGAZ, en Spotify como Marto Apardian) "
             "y cuadros (fotos de su archivo impresas, con marco).")
    return {
        "luz": cuerpo(".claude/agents/luz-community-manager.md") + "\n\n" + base,
        "lupa": cuerpo(".claude/agents/lupa-critica-diseno.md") + "\n\n" + base,
        "trato": cuerpo(".claude/agents/trato-ventas.md") + "\n\n" + base + "\n\n" + leer("09-ESTUDIO/CM_VENTAS.md"),
        "radar": cuerpo(".claude/agents/radar-prospeccion.md") + "\n\n" + base +
                 "\n\n=== Cómo escribe los mails (el mismo texto que usa n8n) ===\n" + leer("11-AUTOMATIZACION/prompts/redactor.md"),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    global VENTANA_DIAS
    cal = json.load(open(os.path.join(IG, "calendario.json")))
    while True:
        dias = archivos_por_dia(cal)
        ig = archivos_ig(dias)
        pzs, cars = piezas(cal), carruseles(frozenset(ig))
        total = len(ig) + sum(p["img"].startswith("pz/") for p in pzs) + \
            sum(x.startswith("car/") for c in cars for x in c["srcs"]) + 1
        if total <= TOPE_ARCHIVOS or VENTANA_DIAS <= 14:
            break
        VENTANA_DIAS -= 7
    print("archivos de la app:", total, "· ventana de", VENTANA_DIAS, "días")
    datos = {"calendario": cal, "piezas": pzs, "zips": dias,
             "carruseles": cars, "guiones": guiones(),
             "agentes": agentes(), "whatsapp": "+598 91 962 962"}
    html = open(PLANTILLA).read().replace("/*__DATOS__*/null",
                                          json.dumps(datos, ensure_ascii=False))
    open(os.path.join(OUT, "index.html"), "w").write(html)
    # lo que hay que publicar junto a la página para que se puedan bajar los días
    json.dump(ig, open(os.path.join(OUT, "archivos_ig.json"), "w"), ensure_ascii=False, indent=0)
    n = sum(len(g["items"]) for g in datos["guiones"])
    print(json.dumps({"carruseles": len(datos["carruseles"]), "guiones": n,
                      "dias": len(datos["calendario"]["dias"]), "piezas": len(datos["piezas"]),
                      "kb_html": os.path.getsize(os.path.join(OUT, "index.html")) // 1024}))


if __name__ == "__main__":
    main()
