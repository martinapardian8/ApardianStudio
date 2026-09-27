"""Cose los tramos generados por capturas.js en una sola imagen por ancho y borra los temporales."""
import json, os, sys, glob
from PIL import Image
d = sys.argv[1] if len(sys.argv) > 1 else 'capturas'
for meta in glob.glob(os.path.join(d, '_*.json')):
    m = json.load(open(meta)); n = os.path.basename(meta)[1:-5]
    out = Image.new('RGB', (m['w'], m['total']), (18, 53, 36))
    for t in m['tramos']:
        im = Image.open(t['file']); out.paste(im, (0, t['y'])); os.remove(t['file'])
    os.remove(meta)
    out.save(os.path.join(d, f'{n}-completa.png'), optimize=True)
    print(n, out.size)
