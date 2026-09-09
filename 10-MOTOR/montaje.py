import os, subprocess, sys, json, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D   = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/contenido ia/reel"
TMP = "/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/segs"
OUT = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/contenido ia/00_REEL_HERO.mp4"
os.makedirs(TMP, exist_ok=True)

# (archivo, desde, duracion) — el orden es el guion del reel
PLAN = [
 ("h01_manejando.mp4",     0.9, 0.90),   # ruta
 ("h06_pinguino.mp4",      0.9, 0.85),   # bajo el agua
 ("r00_fuego.mp4",         1.1, 0.85),   # fuego
 ("h03_novios_rambla.mp4", 0.9, 0.95),   # boda
 ("n10_guitarra.mp4",      0.9, 0.85),   # escenario
 ("n01_acantilado.mp4",    0.9, 0.90),   # mar
 ("n08_costillar.mp4",     0.9, 0.80),   # carne
 ("r07_bolas.mp4",         1.2, 0.90),   # fiesta
 ("h05_caballo.mp4",       0.9, 0.85),   # campo
 ("h09_retrato_bn.mp4",    0.9, 0.95),   # retrato en blanco y negro
 ("n14_flores.mp4",        0.9, 0.85),   # salon
 ("h08_estambul.mp4",      0.9, 0.90),   # ciudad
 ("r02_pizza.mp4",         1.0, 0.80),   # pizza
 ("h04_entrada_novia.mp4", 0.9, 0.95),   # iglesia
 ("n03_bahia.mp4",         0.9, 0.85),   # agua
 ("h02_cantante.mp4",      0.9, 0.90),   # concierto
 ("n06_perro.mp4",         0.9, 0.85),   # perro
 ("r04_kamado.mp4",        1.3, 0.80),   # producto
 ("r09_juanluz.mp4",       1.0, 0.90),   # retrato de marca, cielo limpio
 ("n04_faro.mp4",          0.9, 0.85),   # faro
 ("r06_manos.mp4",         1.2, 0.80),   # manos
 ("h07_guacamayo.mp4",     0.9, 0.85),   # guacamayo
 ("r08_salon.mp4",         1.2, 0.90),   # salon
 ("n05_playa.mp4",         0.9, 0.85),   # costa
 ("r01_chef.mp4",          1.3, 0.90),   # el chef
 ("n07_perro2.mp4",        0.9, 0.85),   # perro 2
 ("r03_alitas.mp4",        1.2, 0.80),   # cenital
 ("n02_palmeras.mp4",      0.9, 0.90),   # palmeras
 ("n12_banda.mp4",         0.9, 0.85),   # banda
 ("r05_tabla.mp4",         1.2, 0.85),   # tabla
 ("h04b_cierre.mp4",       0.0, 0.00),   # placeholder
]
PLAN = [x for x in PLAN if x[2] > 0]
PLAN.append(("r10_boda.mp4", 1.3, 1.30))   # cierra con la boda

VF = ("scale=1920:1080:force_original_aspect_ratio=increase,"
      "crop=1920:1080,fps=30,setsar=1,eq=contrast=1.05:saturation=1.06")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:", " ".join(cmd[:6]), r.stderr[-400:])
    return r.returncode == 0

segs, faltan = [], []
for i, (fn, ss, dur) in enumerate(PLAN):
    src = os.path.join(D, fn)
    if not os.path.exists(src):
        faltan.append(fn); continue
    dst = os.path.join(TMP, f"seg{i:02d}.mp4")
    ok = run([FF, "-y", "-ss", str(ss), "-t", str(dur), "-i", src,
              "-vf", VF, "-an", "-c:v", "libx264", "-preset", "medium",
              "-crf", "20", "-pix_fmt", "yuv420p", dst])
    if ok: segs.append(dst)

if faltan: print("faltan todavia:", faltan)
if not segs:
    print("sin material"); sys.exit(1)

lst = os.path.join(TMP, "lista.txt")
with open(lst, "w") as f:
    for s in segs: f.write(f"file '{s}'\n")

run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
     "-c:v", "libx264", "-preset", "slow", "-crf", "21",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT])

size = os.path.getsize(OUT)//1024
dur = subprocess.run([FF, "-i", OUT], capture_output=True, text=True).stderr
import re
m = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", dur)
print(json.dumps({"planos": len(segs), "faltan": faltan,
                  "duracion": m.group(1) if m else "?", "peso_kb": size,
                  "salida": OUT}, ensure_ascii=False))
