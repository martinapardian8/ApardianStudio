# -*- coding: utf-8 -*-
"""Suma los textos de i18n_extra.json al diccionario del sitio.

armar_i18n.py arma js/i18n_dict.js desde un workflow de traducción que vive
en la Mac. Este script hace lo mínimo sin depender de eso: agrega o pisa
claves sueltas (es/en/pt), las frases de WhatsApp, y corre en +1 los números
de las secciones que quedaron después de Música. Se puede correr varias veces.
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(os.path.dirname(AQUI), "05-WEB")
DIC = os.path.join(WEB, "js", "i18n_dict.js")
ES = os.path.join(AQUI, "i18n_es.json")
EXTRA = json.load(open(os.path.join(AQUI, "i18n_extra.json"), encoding="utf-8"))

js = open(DIC, encoding="utf-8").read()
a = js.index("window.APARDIAN_I18N = ") + len("window.APARDIAN_I18N = ")
b = js.index(";\nwindow.APARDIAN_I18N_GEN")
dic = json.loads(js[a:b])
es = json.load(open(ES, encoding="utf-8"))

# los números de sección: solo se corren si todavía tienen el número viejo
viejos = {"lbl016": "05", "lbl017": "06", "lbl018": "07", "lbl019": "08", "lbl020": "09"}
for k in EXTRA.get("renumerar", []):
    for d in (dic["en"], dic["pt"], es):
        v = d.get(k)
        if v and v.startswith(viejos[k] + " "):
            d[k] = "%02d" % (int(viejos[k]) + 1) + v[2:]

for k, t in EXTRA["claves"].items():
    es[k] = t["es"]
    dic["en"][k] = t["en"]
    dic["pt"][k] = t["pt"]

js = js[:a] + json.dumps(dic, ensure_ascii=False, indent=1) + js[b:]

# frases de WhatsApp: se insertan dentro de cada idioma de APARDIAN_I18N_WA
for frase, t in EXTRA.get("whatsapp", {}).items():
    for code in ("en", "pt"):
        if json.dumps(frase, ensure_ascii=False) in js.split("window.APARDIAN_I18N_WA")[1].split(code + ": {")[1].split("}")[0]:
            continue
        m = re.search(r"(window\.APARDIAN_I18N_WA = \{.*?\n  " + code + r": \{\n)", js, re.S)
        ins = "    %s: %s,\n" % (json.dumps(frase, ensure_ascii=False), json.dumps(t[code], ensure_ascii=False))
        js = js[:m.end()] + ins + js[m.end():]

open(DIC, "w", encoding="utf-8").write(js)
json.dump(es, open(ES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("claves en:", len(dic["en"]), "pt:", len(dic["pt"]), "es:", len(es))
