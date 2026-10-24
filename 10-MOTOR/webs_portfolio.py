# -*- coding: utf-8 -*-
"""Capturas de las webs que hizo Martin, listas para la fila "Webs que hice".

Lee 05-WEB/img/webs/webs.json (un proyecto por entrada) y escribe, para cada
uno, <slug>_pc.jpg (1440x900) y <slug>_cel.jpg (390x844 a 2x) en 05-WEB/img/webs/.

De dónde sale cada captura, en este orden:
1. "fuentes": capturas que manda Martin, en 06-NOTAS/webs-fuentes/<slug>/
   escritorio.(png|jpg) y celular.(png|jpg). Esa carpeta NO va a la web ni a
   GitHub (.gitignore): ahí están los originales con el nombre del cliente.
2. "url": se saca con Playwright (solo webs que hizo Martin; si la red de la
   sesión no llega al sitio, se avisa y no se inventa nada).
3. Si no hay ninguna de las dos, sale una lámina "captura pendiente", gris y
   evidente, para ver cómo queda el armado. Esa lámina no se publica.

Clientes confidenciales: "tapar" dice qué zonas cubrir en cada captura, en
píxeles de la imagen original: {"pc": [[x, y, ancho, alto, "texto"], ...]}.
"texto" puede ser "LOREM IPSUM" (va con el color de fondo de la zona y la
letra en contraste), "logo" (bloque gris con la palabra LOGO) o "blur"
(desenfoque, para textos chicos). La barra del navegador del armado nunca
muestra el dominio real de un cliente confidencial.

    python3 10-MOTOR/webs_portfolio.py            # todas
    python3 10-MOTOR/webs_portfolio.py lobster    # una
"""
import os, sys, json, glob, subprocess, time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(RAIZ, "05-WEB")
DIR = os.path.join(WEB, "img", "webs")
FUENTES = os.path.join(RAIZ, "06-NOTAS", "webs-fuentes")
ANTON = os.path.join(RAIZ, "10-MOTOR", "fuentes", "Anton-Regular.ttf")
WORK = os.path.join(RAIZ, "10-MOTOR", "fuentes", "WorkSans.ttf")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PC, CEL = (1440, 900), (780, 1688)


def _fuente(ruta, tam):
    try:
        return ImageFont.truetype(ruta, tam)
    except OSError:
        return ImageFont.load_default()


def tapar(im, cajas):
    """Cubre el nombre o el logo del cliente. Devuelve una imagen nueva."""
    im = im.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    for c in cajas:
        x, y, w, h = [int(v) for v in c[:4]]
        modo = c[4] if len(c) > 4 else "LOREM IPSUM"
        zona = im.crop((x, y, x + w, y + h))
        if modo == "blur":
            im.paste(zona.filter(ImageFilter.GaussianBlur(max(6, h // 3))), (x, y))
            continue
        # el color de fondo es el del borde de la zona (no el del texto que tapa)
        borde = Image.new("RGB", (w, 2))
        borde.paste(zona.crop((0, 0, w, 1)), (0, 0)); borde.paste(zona.crop((0, h - 1, w, h)), (0, 1))
        fondo = tuple(int(v) for v in ImageStat.Stat(borde).median)
        lum = 0.299 * fondo[0] + 0.587 * fondo[1] + 0.114 * fondo[2]
        tinta = (23, 23, 23) if lum > 140 else (248, 247, 246)
        if modo == "logo":
            gris = (205, 203, 200) if lum > 140 else (70, 68, 66)
            d.rectangle((x, y, x + w, y + h), fill=fondo)
            m = max(2, h // 8)
            d.rounded_rectangle((x + m, y + m, x + w - m, y + h - m), radius=max(3, h // 6), fill=gris)
            f = _fuente(WORK, max(10, int(h * 0.32)))
            d.text((x + w / 2, y + h / 2), "LOGO", font=f, fill=tinta, anchor="mm")
            continue
        d.rectangle((x, y, x + w, y + h), fill=fondo)
        tam = max(10, int(h * 0.72))
        f = _fuente(ANTON, tam)
        while tam > 10 and d.textlength(modo, font=f) > w * 0.96:
            tam -= 2; f = _fuente(ANTON, tam)
        d.text((x + w / 2, y + h / 2), modo, font=f, fill=tinta, anchor="mm")
    return im


def pendiente(tam, rubro, cel=False):
    """Lámina gris que muestra dónde va la captura. Se ve que es un hueco."""
    w, h = tam
    im = Image.new("RGB", tam, (236, 234, 231))
    d = ImageDraw.Draw(im)
    k = 2 if cel else 1
    # barra de navegación con el lugar del logo
    d.rectangle((0, 0, w, 74 * k), fill=(248, 247, 246))
    d.rounded_rectangle((28 * k, 20 * k, 210 * k, 54 * k), radius=6 * k, fill=(214, 212, 209))
    d.text((119 * k, 37 * k), "LOREM IPSUM", font=_fuente(ANTON, 20 * k), fill=(120, 117, 114), anchor="mm")
    if not cel:
        for i in range(4):
            d.rounded_rectangle((w - 520 + i * 110, 31, w - 450 + i * 110, 43), radius=6, fill=(214, 212, 209))
    # bloques de contenido, claramente esquemáticos
    y0 = 74 * k + 40 * k
    d.rectangle((28 * k, y0, w - 28 * k, y0 + (300 if not cel else 220) * k), fill=(222, 220, 217))
    y = y0 + (330 if not cel else 250) * k
    cols = 1 if cel else 3
    cw = (w - 56 * k - (cols - 1) * 20 * k) // cols
    for c in range(cols):
        x = 28 * k + c * (cw + 20 * k)
        d.rectangle((x, y, x + cw, y + 160 * k), fill=(222, 220, 217))
    f = _fuente(WORK, 15 * k)
    d.text((w / 2, y0 + (150 if not cel else 110) * k), "CAPTURA PENDIENTE · " + rubro.upper(),
           font=f, fill=(140, 137, 134), anchor="mm")
    return im


def capturar(url, destino_pc, destino_cel, local=False):
    """Saca escritorio y celular con Playwright. Devuelve (ok, motivo)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "falta playwright"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME)
            for vp, dsf, dst in (({"width": 1440, "height": 900}, 1, destino_pc),
                                 ({"width": 390, "height": 844}, 2, destino_cel)):
                pg = b.new_page(viewport=vp, device_scale_factor=dsf, locale="es-UY")
                pg.goto(url, wait_until="load", timeout=45000)
                pg.wait_for_timeout(2500)
                if local:
                    # la web de Apardian abre con una puerta de entrada: se saca para la foto
                    pg.evaluate("""() => { const l = document.getElementById('loader'); if (l) l.remove();
                                         document.body.classList.remove('locked'); window.scrollTo(0, 0); }""")
                    pg.wait_for_timeout(1500)
                pg.screenshot(path=dst, type="jpeg", quality=86)
                pg.close()
            b.close()
        return True, ""
    except Exception as e:
        return False, str(e).splitlines()[0][:160]


def armar(p):
    slug = p["slug"]
    out_pc, out_cel = os.path.join(DIR, slug + "_pc.jpg"), os.path.join(DIR, slug + "_cel.jpg")
    fuentes = os.path.join(FUENTES, slug)
    def buscar(nombre):
        for ext in ("png", "jpg", "jpeg", "webp"):
            r = os.path.join(fuentes, nombre + "." + ext)
            if os.path.exists(r):
                return r
        return None
    pc, cel = buscar("escritorio"), buscar("celular")
    origen = "fuentes"
    if not (pc and cel) and p.get("url"):
        os.makedirs(fuentes, exist_ok=True)
        srv = None
        url = p["url"]
        if url == "local":
            srv = subprocess.Popen([sys.executable, "-m", "http.server", "8791", "-d", WEB],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1); url = "http://127.0.0.1:8791/index.html"
        ok, motivo = capturar(url, os.path.join(fuentes, "escritorio.jpg"), os.path.join(fuentes, "celular.jpg"),
                              local=p["url"] == "local")
        if srv:
            srv.terminate()
        if ok:
            pc, cel, origen = buscar("escritorio"), buscar("celular"), "url"
        else:
            print("  %s: no se pudo capturar %s (%s)" % (slug, p["url"], motivo))
    if pc and cel:
        tap = p.get("tapar", {})
        a = tapar(Image.open(pc), tap.get("pc", [])) if p.get("confidencial") else Image.open(pc).convert("RGB")
        b = tapar(Image.open(cel), tap.get("cel", [])) if p.get("confidencial") else Image.open(cel).convert("RGB")
        a = a.resize((PC[0], int(a.height * PC[0] / a.width))).crop((0, 0) + PC)
        b = b.resize((CEL[0], int(b.height * CEL[0] / b.width))).crop((0, 0) + CEL)
    else:
        a, b, origen = pendiente(PC, p["rubro"]), pendiente(CEL, p["rubro"], cel=True), "pendiente"
    os.makedirs(DIR, exist_ok=True)
    a.save(out_pc, quality=84, optimize=True, progressive=True)
    b.save(out_cel, quality=84, optimize=True, progressive=True)
    return origen


def main():
    cfg = json.load(open(os.path.join(DIR, "webs.json"), encoding="utf-8"))
    solo = sys.argv[1:]
    res = {}
    for p in cfg["proyectos"]:
        if solo and not any(s in p["slug"] for s in solo):
            continue
        res[p["slug"]] = armar(p)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
