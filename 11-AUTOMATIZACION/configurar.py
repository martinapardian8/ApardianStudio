# -*- coding: utf-8 -*-
"""Copia los flujos de n8n/ con los datos de Martin ya puestos en cada Config.

Los datos (ID de la planilla, chat de Telegram, clave, dirección de n8n) no
se guardan en el repo: se pasan en un JSON y los flujos completos salen a la
carpeta que se indique, lista para importar en n8n.

    python3 11-AUTOMATIZACION/configurar.py datos.json carpeta_de_salida/

datos.json: {"SHEET_ID": "...", "TELEGRAM_CHAT_ID": "...", "TOKEN": "...",
             "N8N": "https://xxx.app.n8n.cloud", "FECHA_INICIO": "AAAA-MM-DD",
             "FECHA_FIN": "AAAA-MM-DD"}  (FECHA_FIN es opcional: fin de la prueba)
"""
import json, os, sys, glob

AQUI = os.path.dirname(os.path.abspath(__file__))


def configurar(flujo, d):
    """Pone los valores en los nodos Config (Set) del flujo. Devuelve los cambios."""
    n8n = d.get("N8N", "").rstrip("/")
    valores = {
        "SHEET_ID": d.get("SHEET_ID"),
        "TELEGRAM_CHAT_ID": d.get("TELEGRAM_CHAT_ID"),
        "FECHA_INICIO": d.get("FECHA_INICIO"),
        "FECHA_FIN": d.get("FECHA_FIN"),
        "URL_BANDEJA": n8n and n8n + "/webhook/apardian-bandeja",
        "URL_APROBAR_IG": n8n and n8n + "/webhook/apardian-ig-aprobar",
    }
    cambios = 0
    for nodo in flujo["nodes"]:
        if nodo["type"] != "n8n-nodes-base.set":
            continue
        for a in nodo["parameters"].get("assignments", {}).get("assignments", []):
            if a["name"] == "TOKEN" and d.get("TOKEN"):
                a["value"] = d["TOKEN"]; cambios += 1
            elif valores.get(a["name"]):
                a["value"] = valores[a["name"]]; cambios += 1
    return cambios


def main(datos, salida):
    d = json.load(open(datos, encoding="utf-8"))
    os.makedirs(salida, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(AQUI, "n8n", "*.json"))):
        flujo = json.load(open(f, encoding="utf-8"))
        n = configurar(flujo, d)
        json.dump(flujo, open(os.path.join(salida, os.path.basename(f)), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(os.path.basename(f), n, "valores")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
