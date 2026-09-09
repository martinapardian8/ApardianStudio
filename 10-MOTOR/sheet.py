import os, sys, json, glob
from PIL import Image, ImageDraw

OUT = "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/sheets"
BASE = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/03-FOTOS-OPTIMIZADAS"
os.makedirs(OUT, exist_ok=True)

def sheet(cat, slug, maxn=30, cols=6, cell=250):
    files = sorted(glob.glob(os.path.join(BASE, cat, "thumb", slug + "__*.jpg")))
    if not files:
        return None
    n = len(files)
    if n > maxn:
        step = n / maxn
        pick = [files[int(i*step)] for i in range(maxn)]
    else:
        pick = files
    rows = (len(pick) + cols - 1)//cols
    W, H = cols*cell, rows*cell
    canvas = Image.new("RGB", (W, H), (20,20,20))
    d = ImageDraw.Draw(canvas)
    mapping = []
    for i, f in enumerate(pick):
        try:
            im = Image.open(f); im.draft("RGB", (cell, cell)); im = im.convert("RGB")
        except Exception:
            continue
        w,h = im.size; s = cell/min(w,h)
        im = im.resize((max(1,int(w*s)), max(1,int(h*s))), Image.BILINEAR)
        w,h = im.size
        im = im.crop(((w-cell)//2, (h-cell)//2, (w-cell)//2+cell, (h-cell)//2+cell))
        x, y = (i % cols)*cell, (i//cols)*cell
        canvas.paste(im, (x,y))
        tag = str(i+1)
        d.rectangle([x+3,y+3,x+3+11*len(tag)+8,y+22], fill=(255,0,51))
        d.text((x+8,y+7), tag, fill=(255,255,255))
        mapping.append({"i": i+1, "file": os.path.basename(f)})
    p = os.path.join(OUT, f"{cat}__{slug}.jpg")
    canvas.save(p, quality=76)
    with open(os.path.join(OUT, f"{cat}__{slug}.json"), "w") as fh:
        json.dump(mapping, fh)
    return p, len(files), len(pick)

if __name__ == "__main__":
    cat, slug = sys.argv[1], sys.argv[2]
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    r = sheet(cat, slug, mx)
    print(json.dumps({"path": r[0], "total": r[1], "shown": r[2]}) if r else "SIN ARCHIVOS")
