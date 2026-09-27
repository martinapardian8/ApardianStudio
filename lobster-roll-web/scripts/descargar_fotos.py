#!/usr/bin/env python3
"""Descarga las fotos actuales de thelobsterrollbcn.com y las convierte a WebP.

Uso:  python3 scripts/descargar_fotos.py
Deja:
  assets/fotos/originales/<id>.png   (tal cual vienen de la web actual)
  assets/fotos/<id>.webp             (calidad 80, máximo 1600 px de ancho)
  assets/fotos/contacto.jpg          (plancha de contacto para elegir cuál va dónde)
Después: editá data/fotos.json y poné el archivo que corresponde en cada slot.
Requiere: pip install pillow
"""
import io, os, sys, urllib.request
from PIL import Image, ImageDraw

BASE = "https://www.thelobsterrollbcn.com/img-trans/productos/24913/fotos/1024-{id}-the-lobster-rolls.png"
LOGO = "https://www.thelobsterrollbcn.com/img-trans/productos/24913/fotos/150-6376080b32b38-the-lobster-rolls.png"
IDS = """637606f35a4cf 6376069ad066b 637606d17ba91 637606b570db5 637607e3eaff7 637607ff00028 637607f069863 637607a1f175b
637607910f1b3 6376077b721ce 6376076b50541 6376075ab1bbf 637607501d26d 637606e519b4f 637606c42d98d 637606a855bcf""".split()
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DEST = os.path.join(RAIZ, "assets", "fotos")
ORIG = os.path.join(DEST, "originales")
MAX_ANCHO, CALIDAD = 1600, 80

def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (apardianstudio fotos)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def main():
    os.makedirs(ORIG, exist_ok=True)
    hechas = []
    for id_ in IDS + ["logo"]:
        url = LOGO if id_ == "logo" else BASE.format(id=id_)
        try:
            datos = bajar(url)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {id_}: {e}", file=sys.stderr); continue
        with open(os.path.join(ORIG, f"{id_}.png"), "wb") as f:
            f.write(datos)
        im = Image.open(io.BytesIO(datos)).convert("RGB")
        if im.width > MAX_ANCHO:
            im = im.resize((MAX_ANCHO, round(im.height * MAX_ANCHO / im.width)), Image.LANCZOS)
        salida = os.path.join(DEST, f"{id_}.webp")
        im.save(salida, "WEBP", quality=CALIDAD, method=6)
        hechas.append((id_, im))
        print(f"  ✓ {id_}  {im.width}x{im.height}  {os.path.getsize(salida)//1024} KB")
    if hechas:
        # plancha de contacto
        cel, cols = 320, 4
        filas = (len(hechas) + cols - 1) // cols
        hoja = Image.new("RGB", (cols * cel, filas * (cel + 28)), (243, 236, 223))
        d = ImageDraw.Draw(hoja)
        for i, (id_, im) in enumerate(hechas):
            t = im.copy(); t.thumbnail((cel - 16, cel - 16))
            x, y = (i % cols) * cel + 8, (i // cols) * (cel + 28) + 8
            hoja.paste(t, (x, y)); d.text((x, y + cel - 12), id_, fill=(27, 33, 28))
        hoja.save(os.path.join(DEST, "contacto.jpg"), quality=85)
        print(f"\nPlancha de contacto: {os.path.join(DEST, 'contacto.jpg')}")
    print(f"\n{len(hechas)} archivos listos en {DEST}. Ahora asigná cada foto en data/fotos.json.")

if __name__ == "__main__":
    main()
