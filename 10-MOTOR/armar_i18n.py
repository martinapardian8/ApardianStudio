# -*- coding: utf-8 -*-
"""Arma js/i18n_dict.js desde el resultado del workflow de traducción."""
import json, os, sys, re, html
J="/Users/martinapardian/.claude/projects/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/subagents/workflows/wf_48502fe4-97e/journal.jsonl"
SRC="/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/scratchpad/i18n_es.json"
WEB="/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/05-WEB/"
es=json.load(open(SRC))
gen_es=es["__generados__"]
res={}
OUT="/private/tmp/claude-501/-Users-martinapardian-Desktop/6cbae816-aae6-425b-87d6-b223b386128b/tasks/wcaknbx9q.output"
FUENTE=sys.argv[1] if len(sys.argv)>1 else OUT      # también sirve un json {"result":[{code,traducciones}]}
for item in json.load(open(FUENTE,encoding="utf-8"))["result"]:
    res[item["code"]]=item["traducciones"]
salida={"en":{}, "pt":{}}; gen={"en":{}, "pt":{}}; faltan={}
for code in ("en","pt"):
    t=res.get(code) or res.get("_t_"+code) or {}
    if not t: print("SIN traducción", code); continue
    faltan[code]=[k for k in es if k!="__generados__" and not t.get(k)]
    for k,v in es.items():
        if k=="__generados__": continue
        tv=t.get(k)
        if tv: salida[code][k]=tv
    g=t.get("__generados__") or []
    if len(g)!=len(gen_es): print("generados: largo distinto", code, len(g), len(gen_es))
    for a,b in zip(gen_es,g):
        if b: gen[code][a]=html.unescape(b)   # van como texto, no como HTML
    # plantillas para los chips numéricos y el contador de la galería
    n_es=[x for x in gen_es if re.match(r'^\d+ fotos$',x)]
    if n_es:
        ejemplo=gen[code].get(n_es[0],"")
        m=re.match(r'^(\d+)\s*(.*)$',ejemplo)
        if m: gen[code]["{n} fotos"]="{n} "+m.group(2)
    k="Selección de {n} fotos · archivo del proyecto: {m}"
    if k in gen[code]: pass
js="/* Diccionarios de idiomas, generados por 10-MOTOR/armar_i18n.py desde las traducciones revisadas. */\n"
js+="window.APARDIAN_I18N = "+json.dumps(salida,ensure_ascii=False,indent=1)+";\n"
js+="window.APARDIAN_I18N_GEN = "+json.dumps(gen,ensure_ascii=False,indent=1)+";\n"
wa=open(WEB+"js/i18n_dict.js",encoding="utf-8").read()
wa=wa[wa.index("window.APARDIAN_I18N_WA"):]
js+=wa
open(WEB+"js/i18n_dict.js","w",encoding="utf-8").write(js)
print("claves en:",len(salida["en"]),"pt:",len(salida["pt"]),"| generados en:",len(gen["en"]),"pt:",len(gen["pt"]))
print("faltan:", {k:v[:8] for k,v in faltan.items()})
