import os, json, shutil, glob, sys
from PIL import Image

PROJ  = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO"
OPT   = os.path.join(PROJ, "03-FOTOS-OPTIMIZADAS")
WEB   = os.path.join(PROJ, "05-WEB")
IMG   = os.path.join(WEB, "img")
SHEETS= "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/sheets"
PICKS = os.path.join(PROJ, "06-NOTAS", "picks.json")

# índice global: nombre de archivo -> carpeta que lo contiene
_INDEX = None
def index_archivo():
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for root, dirs, files in os.walk(OPT):
            if os.path.basename(root) != "web":
                continue
            carpeta = os.path.relpath(os.path.dirname(root), OPT)
            for f in files:
                if f.lower().endswith(".jpg"):
                    _INDEX.setdefault(f, carpeta)
    return _INDEX


def ingerir(drop_rel, destino_slug):
    """Toma las fotos crudas que Martin dejó en una carpeta suelta del proyecto
    y las deja optimizadas en 03-FOTOS-OPTIMIZADAS/<destino_slug>/{web,thumb}.
    Devuelve la lista de nombres de archivo listos para usar."""
    src = os.path.join(PROJ, drop_rel)
    if not os.path.isdir(src):
        return []
    ow = os.path.join(OPT, destino_slug, "web")
    ot = os.path.join(OPT, destino_slug, "thumb")
    os.makedirs(ow, exist_ok=True); os.makedirs(ot, exist_ok=True)
    listos = []
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        base = destino_slug[:4] + "__" + os.path.splitext(f)[0].replace(" ", "_") + ".jpg"
        dw, dt = os.path.join(ow, base), os.path.join(ot, base)
        if not (os.path.exists(dw) and os.path.exists(dt)):
            try:
                im = Image.open(os.path.join(src, f)).convert("RGB")
            except Exception as e:
                print("  no se pudo leer:", f, e); continue
            a = im.copy(); a.thumbnail((1800, 1800), Image.LANCZOS)
            a.save(dw, "JPEG", quality=82, optimize=True)
            b = im.copy(); b.thumbnail((700, 700), Image.LANCZOS)
            b.save(dt, "JPEG", quality=78, optimize=True)
        listos.append(base)
    if listos:
        global _INDEX
        _INDEX = None          # el índice global tiene que rehacerse
    return listos


def resolve(cat, slug, idxs):
    """Devuelve nombres de archivo a partir de los números de la hoja de contacto.
    Las hojas se buscan por slug, así el usuario puede reorganizar carpetas sin romper nada."""
    mp = os.path.join(SHEETS, f"{cat}__{slug}.json")
    if not os.path.exists(mp):
        cands = [f for f in os.listdir(SHEETS) if f.endswith(f"__{slug}.json")]
        if not cands:
            return []
        mp = os.path.join(SHEETS, cands[0])
    m = {e["i"]: e["file"] for e in json.load(open(mp))}
    return [m[i] for i in idxs if i in m]

def archive_count(cat, slug):
    return len(glob.glob(os.path.join(OPT, cat, "thumb", slug + "__*.jpg")))

def shape_of(path):
    """Cuadrada, alta o ancha según la proporción real de la foto."""
    try:
        w, h = Image.open(path).size
    except Exception:
        return ""
    r = w / h
    if r >= 1.45: return "wide"
    if r <= 0.72: return "tall"
    return ""

def main():
    cfg = json.load(open(PICKS))
    os.makedirs(IMG, exist_ok=True)
    data = {"hero": "", "works": [], "categories": []}

    for cat in cfg["categories"]:
        key = cat["key"]
        out_w = os.path.join(IMG, key, "web")
        out_t = os.path.join(IMG, key, "thumb")
        os.makedirs(out_w, exist_ok=True); os.makedirs(out_t, exist_ok=True)
        photos, arch = [], 0
        # carpeta suelta donde Martin tira fotos nuevas: se ingieren solas
        archivos = list(cat.get("files", []))
        if cat.get("drop"):
            nuevos = ingerir(cat["drop"], cat.get("drop_slug", key))
            archivos += [n for n in nuevos if n not in archivos]
        # fuente por lista explícita de archivos (las fotos que eligió Martin)
        for fn in archivos:
            frm = index_archivo().get(fn)
            if frm is None:
                print("  no encontrado:", fn); continue
            sw = os.path.join(OPT, frm, "web", fn)
            st = os.path.join(OPT, frm, "thumb", fn)
            if not (os.path.exists(sw) and os.path.exists(st)):
                print("  falta:", fn); continue
            shutil.copy2(sw, os.path.join(out_w, fn)); shutil.copy2(st, os.path.join(out_t, fn))
            photos.append({"web": f"img/{key}/web/{fn}", "thumb": f"img/{key}/thumb/{fn}", "shape": shape_of(sw)})
            arch += 1

        for src in cat.get("sources", []):
            slug = src["slug"]
            frm = src.get("from", key)          # carpeta física donde quedaron los archivos
            arch += archive_count(frm, slug)
            for fn in resolve(frm, slug, src["pick"]):
                sw = os.path.join(OPT, frm, "web", fn)
                st = os.path.join(OPT, frm, "thumb", fn)
                if not (os.path.exists(sw) and os.path.exists(st)):
                    continue
                shutil.copy2(sw, os.path.join(out_w, fn))
                shutil.copy2(st, os.path.join(out_t, fn))
                photos.append({
                    "web":   f"img/{key}/web/{fn}",
                    "thumb": f"img/{key}/thumb/{fn}",
                    "shape": shape_of(sw),
                })
        if not photos and not cat.get("soon"):
            print("  seccion sin fotos, no se publica:", key); continue
        data["categories"].append({
            "key": key, "name": cat["name"], "phrase": cat["phrase"],
            "soon": cat.get("soon", False), "soonText": cat.get("soonText", ""),
            "archive": arch, "photos": photos,
        })

    for w in cfg.get("works", []):
        # la tarjeta puede indicar el archivo directo, o resolverse por hoja de contacto
        if w.get("file"):
            fn = w["file"]
            frm = index_archivo().get(fn)
            if frm is None:
                print("  tarjeta sin archivo:", fn); continue
        else:
            frm = w.get("from", w["cat"])
            r = resolve(frm, w["slug"], [w["pick"]])
            if not r: continue
            fn = r[0]
        sw = os.path.join(OPT, frm, "web", fn)
        st = os.path.join(OPT, frm, "thumb", fn)
        os.makedirs(os.path.join(IMG, "works"), exist_ok=True)
        shutil.copy2(sw, os.path.join(IMG, "works", fn))
        shutil.copy2(st, os.path.join(IMG, "works", "t_" + fn))
        data["works"].append({
            "title": w["title"], "meta": w["meta"], "chip": w["chip"],
            "chipDark": w.get("chipDark", False),
            "web": f"img/works/{fn}", "thumb": f"img/works/t_{fn}",
        })

    # --- videos IA ---
    AI = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/contenido ia"
    SRCJ = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/origen"
    vids = cfg.get("videos", {})
    if vids:
        os.makedirs(os.path.join(IMG, "video"), exist_ok=True)
        by_cat = {c["key"]: c for c in data["categories"]}
        for catkey, items in vids.items():
            for it in items:
                mp4 = os.path.join(AI, it["file"])
                if not os.path.exists(mp4):
                    continue
                shutil.copy2(mp4, os.path.join(IMG, "video", it["file"]))
                # poster desde la imagen de origen
                poster_name = it["file"].replace(".mp4", "_poster.jpg")
                srcimg = os.path.join(SRCJ, it["poster"])
                if os.path.exists(srcimg):
                    im = Image.open(srcimg).convert("RGB")
                    im.thumbnail((900, 900), Image.LANCZOS)
                    im.save(os.path.join(IMG, "video", poster_name), quality=76, optimize=True)
                entry = {
                    "web":   f"img/video/{it['file']}",
                    "thumb": f"img/video/{poster_name}",
                    "video": f"img/video/{it['file']}",
                    "shape": it.get("shape", ""),
                }
                if catkey in by_cat:
                    by_cat[catkey]["photos"].insert(it.get("at", 0), entry)

    # fondo animado de sección
    sb = cfg.get("section_bg")
    if sb:
        mp4 = os.path.join(AI, sb["file"])
        if os.path.exists(mp4):
            os.makedirs(os.path.join(IMG, "video"), exist_ok=True)
            shutil.copy2(mp4, os.path.join(IMG, "video", sb["file"]))
            pn = sb["file"].replace(".mp4", "_poster.jpg")
            src = os.path.join(SRCJ, sb["poster"])
            if os.path.exists(src):
                im = Image.open(src).convert("RGB"); im.thumbnail((1600, 1600), Image.LANCZOS)
                im.save(os.path.join(IMG, "video", pn), quality=74, optimize=True)
            data["sectionBg"] = {"video": f"img/video/{sb['file']}", "poster": f"img/video/{pn}"}

    hv = cfg.get("hero_video")
    if hv and os.path.exists(os.path.join(AI, hv)):
        os.makedirs(os.path.join(IMG, "video"), exist_ok=True)
        shutil.copy2(os.path.join(AI, hv), os.path.join(IMG, "video", hv))
        data["heroVideo"] = f"img/video/{hv}"

    h = cfg.get("hero")
    if h:
        hf = h.get("from", h["cat"])
        fn = resolve(hf, h["slug"], [h["pick"]])
        if fn:
            fn = fn[0]
            shutil.copy2(os.path.join(OPT, hf, "web", fn), os.path.join(IMG, "hero.jpg"))
            data["hero"] = "img/hero.jpg"

    with open(os.path.join(WEB, "js", "data.js"), "w") as f:
        f.write("window.SITE_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")

    tot = sum(len(c["photos"]) for c in data["categories"])
    print(json.dumps({"categorias": len(data["categories"]), "fotos_publicadas": tot,
                      "trabajos": len(data["works"]), "hero": bool(data["hero"])}, ensure_ascii=False))

main()
