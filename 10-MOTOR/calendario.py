# -*- coding: utf-8 -*-
"""Calendario de contenido y ventas: 9 semanas, del 19/10 al 20/12/2026.

Una sola fuente: arma 08-CONTENIDO-INSTAGRAM/calendario.json (lo leen la app
centro de mando y el PDF) y 08-CONTENIDO-INSTAGRAM/CALENDARIO.md (para leer).

Ritmo: lunes carrusel collage (lo mas fuerte), miercoles y viernes las
publicaciones ya armadas en 00-SUBIR-EN-ORDEN, historias todos los dias de
semana, y cada semana un foco de venta que acompaña al carrusel.
"""
import os, json, datetime as dt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
INICIO = dt.date(2026, 10, 19)          # lunes
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

COLLAGE = "06-carruseles-collage"
# (carpeta, titulo, por que esa semana)
SEMANAS = [
    ("01-bodas-un-si", "Un sí dura un segundo",
     "Las parejas del verano 26/27 están cerrando fotógrafo ahora.",
     "Bodas", "Contactar 10 salones y wedding planners para alianzas; responder toda consulta de fecha en menos de 1 h.",
     "P1 respuesta rápida + P2 seguimiento de presupuestos (WhatsApp Business)"),
    ("02-gastronomia-cuatro-fotos", "La gente come con los ojos",
     "Restaurantes y paradores arman la carta de verano en noviembre.",
     "Gastronomía", "Correr el prospector con 'restaurantes' en Pocitos, Punta Carretas, Punta del Este y La Barra; 5 DMs a locales sin fotos propias.",
     "P3 prospección B2B: armar flujos 01–03, calentar el dominio de envío"),
    ("06-edicion-vos-disparas", "Vos disparás. Yo edito.",
     "Plena temporada de bodas: los fotógrafos están tapados de edición.",
     "Edición Lightroom", "Escribir a 15 fotógrafos de bodas (UY, AR, ES, MX) con la plantilla en su idioma; ofrecer prueba con un lote chico pago.",
     "P5 pedido de reseñas a los últimos 10 clientes"),
    ("04-fin-de-anio", "La fiesta de fin de año pasa una vez",
     "Las empresas reservan la fiesta de diciembre a principios de noviembre.",
     "Eventos y empresas", "Mail a 20 áreas de RR. HH. y comunicación (flujo 03, rubro empresas); reactivar clientes de eventos 2025.",
     "P6 reactivación de clientes viejos (fin de año)"),
    ("03-marca-personal-cinco-usos", "Tu marca personal no entra en una selfie",
     "Cierre de año: profesionales actualizan web y LinkedIn para enero.",
     "Retrato / marca personal", "10 DMs a profesionales con fotos viejas en LinkedIn; proponer sesión de una mañana.",
     "P7 publicación programada (Meta Business Suite)"),
    ("07-web-tu-instagram-no-es-tu-web", "Tu Instagram no es tu página web",
     "Black Friday (27/11): los negocios que venden por Instagram sienten el límite.",
     "Páginas web", "Auditor n8n sobre negocios con solo Instagram o web vieja; 10 mails con la mejora concreta.",
     "P3 en marcha: revisar puntajes y respuestas de la semana"),
    ("08-cuadros-regala-un-lugar", "Regalá un lugar",
     "Compras de Navidad: el cuadro es regalo y deco a la vez.",
     "Cuadros", "Historias con precios y tamaños reales (los pone Martin); fijar fecha límite de pedidos para llegar al 24.",
     "P4 prospección de fotógrafos en EN/PT"),
    ("09-musica-de-la-idea-al-master", "La música también la hago",
     "Se lanza la sección de producción musical en la web.",
     "Producción musical", "Compartir el EP; escribir a 10 bandas/solistas que tocaron en vivo este año; ofrecer videoclip + mix.",
     "P8 reporte semanal de métricas (lunes 9:00)"),
    ("05-producto-del-olivo-a-la-mesa", "Un producto tiene una historia entera",
     "Las marcas planifican el contenido de verano y la tienda online de enero.",
     "Producto / marcas", "Prospector con 'marcas uruguayas', 'tiendas online', 'productores'; proponer sesión de origen + packshot.",
     "Revisar todo el sistema: qué canal trajo más consultas (APRENDIZAJES.md)"),
]


def main():
    orden = json.load(open(os.path.join(IG, "00-SUBIR-EN-ORDEN", "orden.json")))
    hist = sorted(f for f in os.listdir(os.path.join(IG, "04-historias-organicas"))
                  if f.endswith(".jpg") and not f.startswith("00_"))
    titulos = {h["archivo"]: h["titular"] for h in
               json.load(open(os.path.join(IG, "indice_historias.json")))}
    videos = sorted(f for f in os.listdir(os.path.join(IG, "05-videos")) if f.endswith("_feed.mp4"))
    mundo = json.load(open(os.path.join(IG, "08-tus-fotos-en-el-mundo", "indice.json")))
    # orden de la serie segun el foco de cada semana
    orden_mundo = [2, 6, 4, 10, 1, 12, 11, 3, 8]
    dias, k_hist, k_orden, k_video = [], 0, 0, 0
    for s, (slug, tit, porque, vertical, venta, auto) in enumerate(SEMANAS):
        lunes = INICIO + dt.timedelta(weeks=s)
        for d in range(7):
            f = lunes + dt.timedelta(days=d)
            items = []
            if d == 0:
                items.append({"tipo": "Carrusel collage", "hora": "19:30", "titulo": tit,
                              "pieza": f"{COLLAGE}/{slug}", "nota": porque})
            if d in (2, 4):
                # las publicaciones que se sacaron (antes/despues simulado) ya no estan
                while k_orden < len(orden) and not os.path.isdir(
                        os.path.join(IG, "00-SUBIR-EN-ORDEN", f"{orden[k_orden]['n']:02d}")):
                    k_orden += 1
                if k_orden < len(orden):
                    o = orden[k_orden]; k_orden += 1
                    items.append({"tipo": o["tipo"], "hora": "19:30", "titulo": o["titulo"],
                                  "pieza": f"00-SUBIR-EN-ORDEN/{o['n']:02d}",
                                  "nota": "Publicación ya armada (si ya la subiste, saltala)."})
                elif k_video < len(videos):
                    v = videos[k_video]; k_video += 1
                    items.append({"tipo": "Reel de 6 segundos", "hora": "19:30",
                                  "titulo": v.split("_", 2)[2].replace("_feed.mp4", "").replace("-", " ").capitalize(),
                                  "pieza": f"05-videos/{v}", "nota": "Video animado de un aviso."})
            if d < 5 and k_hist < len(hist):
                items.append({"tipo": "Historia", "hora": "12:30", "titulo": titulos.get(hist[k_hist], hist[k_hist][4:-4].split("_", 1)[-1].replace("-", " ")),
                              "pieza": f"04-historias-organicas/{hist[k_hist]}", "nota": ""})
                k_hist += 1
            if d == 0:
                items.append({"tipo": "Historia", "hora": "20:00", "titulo": "Nuevo carrusel: compartilo en historias",
                              "pieza": f"{COLLAGE}/{slug}/01.jpg", "nota": "Con sticker de enlace a WhatsApp."})
            if d == 1:
                items.append({"tipo": "Venta", "hora": "10:00", "titulo": f"Foco de la semana: {vertical}",
                              "pieza": "", "nota": venta})
            if d == 3:
                items.append({"tipo": "Reel", "hora": "19:30", "titulo": "Reel del carrusel: " + tit,
                              "pieza": f"07-reels-collage/{slug}.mp4",
                              "nota": "Ponele un tema tuyo de fondo."})
            if d == 5 and s < len(orden_mundo):
                m = next(x for x in mundo if x["n"] == orden_mundo[s])
                items.append({"tipo": "Tus fotos en el mundo", "hora": "11:00", "titulo": m["frase"],
                              "pieza": f"08-tus-fotos-en-el-mundo/{m['archivo']}",
                              "nota": m["lugar"] + ". Es un montaje: decilo en el pie."})
            if d == 3:
                items.append({"tipo": "Automatización", "hora": "10:00", "titulo": auto,
                              "pieza": "11-AUTOMATIZACION/README.md", "nota": ""})
            if d == 4:
                items.append({"tipo": "Venta", "hora": "17:00", "titulo": "Seguimiento de presupuestos y leads",
                              "pieza": "09-ESTUDIO/clientes.md",
                              "nota": "Todo presupuesto sin respuesta hace 2+ días recibe un mensaje."})
            if items:
                items.sort(key=lambda it: it["hora"])
                dias.append({"fecha": f.isoformat(), "dia": DIAS[d], "semana": s + 1,
                             "vertical": vertical, "items": items})
    data = {"desde": INICIO.isoformat(), "hasta": (INICIO + dt.timedelta(weeks=len(SEMANAS), days=-1)).isoformat(),
            "semanas": [{"n": i + 1, "lunes": (INICIO + dt.timedelta(weeks=i)).isoformat(),
                         "carrusel": t, "pieza": f"{COLLAGE}/{sl}", "porque": p, "vertical": v,
                         "venta": ve, "automatizacion": a}
                        for i, (sl, t, p, v, ve, a) in enumerate(SEMANAS)],
            "dias": dias}
    json.dump(data, open(os.path.join(IG, "calendario.json"), "w"), ensure_ascii=False, indent=1)

    md = ["# Calendario de contenido y ventas",
          f"Del {INICIO.strftime('%d/%m')} al {data['hasta'][8:10]}/{data['hasta'][5:7]} de 2026. "
          "Generado por `10-MOTOR/calendario.py` (no se edita a mano).", "",
          "Ritmo: **lunes** carrusel collage · **jueves** su reel · **sábado** Tus fotos en el mundo · **miércoles y viernes** publicaciones ya armadas · "
          "**historias** de lunes a viernes · **martes** foco de venta · **jueves** una automatización · "
          "**viernes** seguimiento de presupuestos.", ""]
    for sem in data["semanas"]:
        md += [f"## Semana {sem['n']} · {dt.date.fromisoformat(sem['lunes']).strftime('%d/%m')} — {sem['vertical']}",
               f"**Carrusel:** {sem['carrusel']} (`{sem['pieza']}`). {sem['porque']}",
               f"**Venta:** {sem['venta']}",
               f"**Automatización:** {sem['automatizacion']}", "",
               "| Día | Hora | Qué | Pieza |", "|---|---|---|---|"]
        for d in [x for x in dias if x["semana"] == sem["n"]]:
            for it in d["items"]:
                md.append(f"| {d['dia']} {d['fecha'][8:10]}/{d['fecha'][5:7]} | {it['hora']} | "
                          f"{it['tipo']}: {it['titulo']} | " + (f"`{it['pieza']}`" if it['pieza'] else "—") + " |")
        md.append("")
    open(os.path.join(IG, "CALENDARIO.md"), "w").write("\n".join(md))
    print(json.dumps({"dias": len(dias), "items": sum(len(d["items"]) for d in dias)}))


if __name__ == "__main__":
    main()
