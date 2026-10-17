#!/usr/bin/env bash
# Vuelve a bajar las fuentes de Google Fonts como woff2 (subsets latin + latin-ext) y regenera css/fonts.css.
# Uso: bash scripts/fuentes.sh
set -euo pipefail
cd "$(dirname "$0")/.."
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
URL="https://fonts.googleapis.com/css2?family=Gloock&family=Anton&family=Oswald:wght@400..700&family=Figtree:ital,wght@0,300..800;1,400&display=swap"
mkdir -p assets/fonts
curl -sS -A "$UA" "$URL" -o /tmp/google-fonts.css
python3 - <<'PY'
import re, urllib.request, os
css = open('/tmp/google-fonts.css').read()
out = []
for subset, body in re.findall(r'/\* (\w[\w-]*) \*/\s*@font-face \{(.*?)\}', css, re.S):
    if subset not in ('latin', 'latin-ext') and not (fam == 'Oswald' and subset.startswith('cyrillic')): continue
    fam = re.search(r"font-family: '([^']+)'", body).group(1)
    style = re.search(r"font-style: (\w+)", body).group(1)
    weight = re.search(r"font-weight: ([\d ]+)", body).group(1)
    url = re.search(r"url\((https://[^)]+)\)", body).group(1)
    ur = re.search(r"unicode-range: ([^;]+);", body).group(1)
    name = f"{fam.lower().replace(' ', '-')}-{style}-{weight.replace(' ', '-')}-{subset}.woff2"
    open(os.path.join('assets/fonts', name), 'wb').write(urllib.request.urlopen(url).read())
    out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};font-display:swap;src:url(../assets/fonts/{name}) format('woff2');unicode-range:{ur};}}")
open('css/fonts.css', 'w').write("/* Fuentes autoalojadas (Google Fonts, licencia OFL). Regenerar con scripts/fuentes.sh */\n" + "\n".join(out) + "\n")
print(len(out), 'caras')
PY
