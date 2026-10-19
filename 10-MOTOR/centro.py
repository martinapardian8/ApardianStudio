# -*- coding: utf-8 -*-
"""Arma la app "Centro APARDIAN" (12-CENTRO/index.html + miniaturas).

Junta en una sola pagina el calendario (calendario.json), los carruseles
collage con sus textos (00_COPYS.md) y los guiones de venta (CM_VENTAS.md).
Lo que cambia con el uso (que se publico, los clientes) vive en la base de
datos del artifact, no en este archivo.

python3 10-MOTOR/centro.py
"""
import os, re, json, glob
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
COL = os.path.join(IG, "06-carruseles-collage")
OUT = os.path.join(RAIZ, "12-CENTRO")
PLANTILLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centro_plantilla.html")


def carruseles():
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
        os.makedirs(dst, exist_ok=True)
        lams = sorted(glob.glob(os.path.join(d, "[0-9][0-9].jpg")))
        for p in lams:
            im = Image.open(p).convert("RGB")
            im.thumbnail((432, 540), Image.LANCZOS)
            im.save(os.path.join(dst, os.path.basename(p)), quality=74, optimize=True)
        out.append({"slug": slug, "laminas": len(lams), **info})
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


def main():
    os.makedirs(OUT, exist_ok=True)
    datos = {"calendario": json.load(open(os.path.join(IG, "calendario.json"))),
             "carruseles": carruseles(), "guiones": guiones(),
             "whatsapp": "+598 91 962 962"}
    html = open(PLANTILLA).read().replace("/*__DATOS__*/null",
                                          json.dumps(datos, ensure_ascii=False))
    open(os.path.join(OUT, "index.html"), "w").write(html)
    n = sum(len(g["items"]) for g in datos["guiones"])
    print(json.dumps({"carruseles": len(datos["carruseles"]), "guiones": n,
                      "dias": len(datos["calendario"]["dias"])}))


if __name__ == "__main__":
    main()
