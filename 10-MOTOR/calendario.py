# -*- coding: utf-8 -*-
"""Calendario de contenido y ventas: 15 semanas, del 19/10/2026 al 31/01/2027.

Una sola fuente: arma 08-CONTENIDO-INSTAGRAM/calendario.json (lo leen la app
centro de mando y el PDF) y 08-CONTENIDO-INSTAGRAM/CALENDARIO.md (para leer).

Ritmo: un posteo de feed y una historia TODOS los dias. Lunes carrusel
(lo mas fuerte), jueves su reel, sabado "Tus fotos en el mundo". Desde el
2/11 (ESTETICA_IG.md: de cada 3 posteos, 2 fotos puras) martes, viernes y
domingo van fotos puras (10-fotos) y el miercoles una pieza armada
(00-SUBIR-EN-ORDEN o la campaña). Cada semana, un foco de venta.
"""
import os, sys, json, datetime as dt

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
    ("10-cuadros-un-viaje-que-se-cuelga", "Un viaje que se cuelga",
     "Última semana para regalos de Navidad, y Reyes el 6 de enero.",
     "Cuadros · Navidad y Reyes", "Historias con los cuadros y el plazo real de pedido (lo pone Martin); escribir a los clientes de 2025 con la idea de regalo.",
     "Radar: comprar el dominio para los mails y empezar a calentar la casilla (semana 1 de 2)"),
    ("11-eventos-el-verano-se-festeja", "El verano se festeja afuera",
     "Entre fiestas, la gente arma los cumpleaños y casamientos chicos de enero y febrero.",
     "Eventos de verano", "Mensaje a clientes de eventos 2025 (reactivación) y a 10 chacras y salones de jardín para alianzas.",
     "Radar: segunda semana de calentamiento; contestar el entrenamiento en el Centro"),
    ("12-gastronomia-carta-de-verano", "Tu carta de verano entra por los ojos",
     "Plena temporada en Punta del Este y José Ignacio: los paradores necesitan fotos ya.",
     "Gastronomía de temporada", "DMs a paradores y restaurantes de la costa con la carta vieja o sin fotos propias; ofrecer jornada en la semana.",
     "Radar arranca: 10 mails por día con las ofertas aprobadas"),
    ("13-bodas-entre-el-si-y-la-fiesta", "Entre el sí y la fiesta pasa todo",
     "Las parejas que se casan en otoño 2027 eligen fotógrafo en el verano.",
     "Bodas otoño 2027", "Escribir a 10 salones y wedding planners con el carrusel; responder toda consulta de fecha en menos de 1 h.",
     "Radar: 20 por día; leer el primer reporte semanal y ajustar ofertas"),
    ("14-edicion-en-enero-no-se-duerme", "En enero no se duerme",
     "Temporada alta de bodas en el hemisferio sur: los fotógrafos están tapados de edición.",
     "Edición Lightroom", "Radar con foco en fotógrafos de bodas (Argentina, México, EE.UU.); ofrecer lote de prueba chico pago.",
     "Radar: 35 por día; sumar búsquedas de fotógrafos si quedan pocos leads"),
    ("15-marca-360-una-marca-entera", "Una marca se ve igual en todos lados",
     "Fin de temporada: los negocios piensan en marzo y en cómo se ven el año que viene.",
     "Marca 360 y web", "Ofrecer marca 360 + web a los clientes de gastronomía y eventos del verano; Radar con foco en marcas chicas.",
     "Radar: 50 por día; qué país y qué rubro respondió mejor (APRENDIZAJES.md)"),
]


# campañas de 01-posteos-pauta que acompañan el foco de cada semana
CAMPANAS = [["bodas"], ["gastronomia"], ["edicion"], ["eventos", "empresas"], ["retratos"],
            ["web"], ["cuadros"], ["eventos", "empresas", "cuadros"], ["marcas"],
            ["cuadros"], ["eventos", "empresas"], ["gastronomia"], ["bodas"], ["edicion"], ["web", "marcas", "retratos"]]
# (la semana de musica no tiene piezas de pauta: el carrusel, su reel y el
# sabado ya son de musica; el resto del feed acompaña diciembre: fiestas y regalos)
# dias de la semana con un posteo de la cola (los otros tienen pieza fija)
DIAS_COLA = {1: "13:00", 2: "19:30", 4: "19:30", 6: "11:00"}


def _norm(t):
    import unicodedata, re
    t = unicodedata.normalize("NFD", t.lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in t if not unicodedata.combining(c))).strip()


def _titulo_archivo(f):
    return f[4:-4].split("_", 1)[-1].replace("_feed.mp4", "").replace("-", " ").capitalize()


def main():
    orden = json.load(open(os.path.join(IG, "00-SUBIR-EN-ORDEN", "orden.json")))
    # las publicaciones que se sacaron (antes/despues simulado) ya no estan
    # (y las carpetas que quedaron vacias). La 07 ("Platos que se venden solos")
    # no sale: Lupa la freno el 28/10 (repite el alfajor de tapa, dos fuegos y
    # cuatro fotos de las mismas empanadas); los platos ya estan en 10-fotos.
    SALTEAR = {7}
    orden = [o for o in orden if o["n"] not in SALTEAR]
    orden = [o for o in orden if os.path.isdir(os.path.join(IG, "00-SUBIR-EN-ORDEN", f"{o['n']:02d}"))
             and any(a.startswith("foto-") or a == "video.mp4"
                     for a in os.listdir(os.path.join(IG, "00-SUBIR-EN-ORDEN", f"{o['n']:02d}")))]
    hist = sorted(f for f in os.listdir(os.path.join(IG, "04-historias-organicas"))
                  if f.endswith(".jpg") and not f.startswith("00_"))
    titulos = {h["archivo"]: h["titular"] for h in
               json.load(open(os.path.join(IG, "indice_historias.json")))}
    pauta = {p["archivo"]: p for p in json.load(open(os.path.join(IG, "indice_pauta.json")))}
    videos = {f[:3]: f for f in os.listdir(os.path.join(IG, "05-videos")) if f.endswith("_feed.mp4")}
    mundo = json.load(open(os.path.join(IG, "08-tus-fotos-en-el-mundo", "indice.json")))
    # orden de la serie segun el foco de cada semana
    orden_mundo = [2, 6, 4, 10, 1, 12, 11, 3, 8, 5, 14, 13, 9, 15, 7]
    # lo armado para el verano (posteos de portfolio, historias 051+) sale
    # desde la semana 9: las semanas que ya estan en curso no cambian
    DESDE_NUEVO = "2026-12-14"

    # cola de posteos de pauta: un numero sale una sola vez (como video si lo
    # tiene, si no como foto) y no se repite lo que ya esta en 00-SUBIR
    ya = {_norm(o["titulo"]) for o in orden}
    cola_pauta = []
    for f in sorted(os.listdir(os.path.join(IG, "01-posteos-pauta"))):
        if not f.endswith(".jpg") or f.startswith("00_") or f not in pauta:
            continue
        p = pauta[f]
        if _norm(p["titular"]) in ya:
            continue
        v = videos.get(f[:3])
        cola_pauta.append({"campana": p["campana"], "n": f[:3],
                           "tipo": "Reel de 6 segundos" if v else "Posteo",
                           "titulo": p["titular"],
                           "pieza": f"05-videos/{v}" if v else f"01-posteos-pauta/{f}",
                           "nota": "Video animado de un aviso." if v else "Pieza de la campaña, con CTA."})
    # desde el 2/11, de cada 3 posteos al menos 2 son fotos puras (ESTETICA_IG.md):
    # martes, viernes y domingo van fotos de 10-fotos; el miercoles, una pieza armada
    DESDE_ESTETICA = "2026-11-02"
    fotos_ruta = os.path.join(IG, "10-fotos", "indice.json")
    cola_fotos = json.load(open(fotos_ruta, encoding="utf-8")) if os.path.exists(fotos_ruta) else []
    portfolio = os.path.join(IG, "09-posteos-portfolio", "indice.json")
    if os.path.exists(portfolio) and not cola_fotos:
        for p in json.load(open(portfolio, encoding="utf-8")):
            cola_pauta.append({"campana": p["campana"], "n": p["id"], "desde": DESDE_NUEVO,
                               "tipo": "Posteo", "titulo": p["titulo"],
                               "pieza": "09-posteos-portfolio/" + p["archivo"],
                               "nota": "Foto de portfolio, con el llamado a WhatsApp en el pie."})
    hist_pauta = [f for f in sorted(os.listdir(os.path.join(IG, "02-historias-pauta")))
                  if f.endswith(".jpg") and f in pauta]

    # una pieza de campaña sale una vez: en el feed o en historia, no en los dos
    # (las de 00-SUBIR cuentan como usadas: son la misma pieza con otro nombre)
    usados = {a[:3] for a, p in pauta.items() if _norm(p["titular"]) in ya}

    ultima_foto = {"campana": ""}

    def sacar_foto(campanas, fecha, primera_de_la_semana):
        # la primera de la semana acompaña el foco; las otras alternan temas
        criterios = [lambda c: c["campana"] != ultima_foto["campana"] and not choca("10-fotos/" + c["archivo"], fecha),
                     lambda c: not choca("10-fotos/" + c["archivo"], fecha), lambda c: True]
        if primera_de_la_semana:
            criterios.insert(0, lambda c: c["campana"] in campanas and not choca("10-fotos/" + c["archivo"], fecha))
        for quiero in criterios:
            for c in cola_fotos:
                if quiero(c):
                    cola_fotos.remove(c); ultima_foto["campana"] = c["campana"]
                    return c
        return None

    def sacar_pauta(campanas, fecha):
        for quiero in (lambda c: c["campana"] in campanas and c["n"] not in usados and not choca(c["pieza"], fecha),
                       lambda c: c["n"] not in usados and not choca(c["pieza"], fecha),
                       lambda c: c["n"] not in usados, lambda c: True):
            for c in cola_pauta:
                if c.get("desde", "") > fecha.isoformat():
                    continue
                if quiero(c):
                    cola_pauta.remove(c); usados.add(c["n"])
                    return c
        return None

    # historias de campaña con fecha adentro: despues de esto ya no dicen la verdad
    VENCE = {"007": "2027-01-01",         # "Quedan pocas fechas para el verano"
             "008": DESDE_NUEVO}          # cita de Sofia y Nicolas: hasta que Martin confirme que es real

    def sacar_hist_pauta(campanas, fecha, evitar=(), solo_libres=False):
        ruta = lambda f: f"02-historias-pauta/{f}"
        vigentes = [f for f in hist_pauta if fecha.isoformat() < VENCE.get(f[:3], "9999")]
        criterios = [lambda f: pauta[f]["campana"] in campanas and f[:3] not in usados and not choca(ruta(f), fecha),
                     lambda f: f[:3] not in usados and not choca(ruta(f), fecha)]
        if not solo_libres:
            criterios += [lambda f: f[:3] not in usados]
            if fecha.isoformat() < DESDE_NUEVO:      # desde la semana 9 no se repite una pieza ya usada
                criterios += [lambda f: f[:3] not in evitar]
        for quiero in criterios:
            for f in vigentes:
                if quiero(f):
                    hist_pauta.remove(f); usados.add(f[:3])
                    return f
        return None

    # ------------------------------------------------ que no se repita una foto
    # Lupa compara las fotos (aunque esten recortadas o con texto encima): una
    # pieza no entra si muestra la misma foto que otra a menos de 3 dias.
    # Primero se anotan las fijas (carrusel, reel, mundo) y despues cada dia
    # elige de la cola la primera que no choque. --rapido saltea la comparacion.
    colocadas = []
    for s, (slug, *_r) in enumerate(SEMANAS):
        lunes = INICIO + dt.timedelta(weeks=s)
        colocadas += [(lunes, f"{COLLAGE}/{slug}"), (lunes + dt.timedelta(days=3), f"07-reels-collage/{slug}.mp4")]
        if s < len(orden_mundo):
            m = next(x for x in mundo if x["n"] == orden_mundo[s])
            colocadas.append((lunes + dt.timedelta(days=5), f"08-tus-fotos-en-el-mundo/{m['archivo']}"))
    mirar = "--rapido" not in sys.argv
    if mirar:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import lupa
        from calendario_sheet import archivos_carpeta

    def archivos(pieza):
        if os.path.isdir(os.path.join(IG, pieza)):
            return archivos_carpeta(pieza)
        return [pieza]

    def _slug(pieza):
        return os.path.splitext(pieza.split("/")[1])[0]

    def choca(pieza, fecha):
        if not mirar:
            return False
        for f2, p2 in colocadas + [(fecha, it["pieza"]) for it in hoy if it["pieza"]]:
            if abs((f2 - fecha).days) < 3 and _slug(p2) != _slug(pieza):
                if any(lupa._misma(a, b) for a in archivos(pieza) for b in archivos(p2)):
                    return True
        return False

    # las semanas en curso no cambian: hasta FIJO se repite lo que ya decia
    # calendario.json (Martin ya lo esta subiendo) y esas piezas salen de las colas
    FIJO = DESDE_ESTETICA
    ruta_cal = os.path.join(IG, "calendario.json")
    viejo = ({x["fecha"]: x for x in json.load(open(ruta_cal, encoding="utf-8"))["dias"]}
             if os.path.exists(ruta_cal) else {})

    def consumir(pieza):
        base = os.path.basename(pieza)
        if pieza.startswith("00-SUBIR-EN-ORDEN/"):
            n = int(pieza.split("/")[1])
            for j in range(k_orden, len(orden)):
                if orden[j]["n"] == n:
                    orden.pop(j)
                    break
        elif pieza.startswith("04-historias-organicas/") and base in hist:
            hist.remove(base)
        elif pieza.startswith("02-historias-pauta/"):
            if base in hist_pauta:
                hist_pauta.remove(base)
            usados.add(base[:3])
        elif pieza.startswith(("01-posteos-pauta/", "05-videos/", "09-posteos-portfolio/")):
            for c in [c for c in cola_pauta if c["pieza"] == pieza]:
                cola_pauta.remove(c)
            if not pieza.startswith("09-"):
                usados.add(base[:3])
        elif pieza.startswith("10-fotos/"):
            for c in [c for c in cola_fotos if c["archivo"] == base]:
                cola_fotos.remove(c)

    dias, k_orden, hoy = [], 0, []
    for s, (slug, tit, porque, vertical, venta, auto) in enumerate(SEMANAS):
        lunes = INICIO + dt.timedelta(weeks=s)
        for d in range(7):
            f = lunes + dt.timedelta(days=d)
            if f.isoformat() < FIJO and f.isoformat() in viejo:
                items = [dict(it) for it in viejo[f.isoformat()]["items"]]
                for it in items:
                    consumir(it.get("pieza") or "")
                colocadas.extend((f, it["pieza"]) for it in items if it.get("pieza"))
                dias.append(dict(viejo[f.isoformat()], items=items))
                continue
            items, en_feed = [], set()
            hoy = items                      # choca() mira tambien lo del mismo dia
            # ---------------------------------------------------- feed: 1 por dia
            if d == 0:
                items.append({"tipo": "Carrusel", "hora": "19:30", "titulo": tit,
                              "pieza": f"{COLLAGE}/{slug}", "nota": porque})
            elif d == 3:
                items.append({"tipo": "Reel", "hora": "19:30", "titulo": "Reel del carrusel: " + tit,
                              "pieza": f"07-reels-collage/{slug}.mp4",
                              "nota": "Sale con el audio del archivo; si le querés poner un tema tuyo, subilo a mano."})
            elif d == 5 and s < len(orden_mundo):
                m = next(x for x in mundo if x["n"] == orden_mundo[s])
                items.append({"tipo": "Tus fotos en el mundo", "hora": "11:00", "titulo": m["frase"],
                              "pieza": f"08-tus-fotos-en-el-mundo/{m['archivo']}",
                              "nota": m["lugar"] + ". Es un montaje: decilo en el pie."})
            elif d in DIAS_COLA and f.isoformat() >= DESDE_ESTETICA and d != 2 and cola_fotos:
                c = sacar_foto(CAMPANAS[s], f, d == 1)
                items.append({"tipo": "Posteo", "hora": DIAS_COLA[d], "titulo": c["titulo"],
                              "pieza": "10-fotos/" + c["archivo"],
                              "nota": "Foto pura, sin texto encima: el llamado a WhatsApp va en el pie."})
            elif d in DIAS_COLA:
                hora = DIAS_COLA[d]
                if (d in (2, 4) or f.isoformat() >= DESDE_ESTETICA) and k_orden < len(orden):
                    # si la que sigue repite una foto cercana, se adelanta la proxima
                    for j in range(k_orden, min(k_orden + 3, len(orden))):
                        if not choca(f"00-SUBIR-EN-ORDEN/{orden[j]['n']:02d}", f):
                            orden.insert(k_orden, orden.pop(j))
                            break
                    o = orden[k_orden]; k_orden += 1
                    items.append({"tipo": o["tipo"], "hora": hora, "titulo": o["titulo"],
                                  "pieza": f"00-SUBIR-EN-ORDEN/{o['n']:02d}",
                                  "nota": "Publicación ya armada (si ya la subiste, saltala)."})
                else:
                    c = sacar_pauta(CAMPANAS[s], f)
                    if c:
                        en_feed.add(c["n"])
                        items.append({"tipo": c["tipo"], "hora": hora, "titulo": c["titulo"],
                                      "pieza": c["pieza"], "nota": c["nota"]})
            # ---------------------------------------------------- historia: 1 por dia
            # martes y viernes (dias de venta) una historia de campaña con CTA;
            # el resto, historias organicas (detras de escena, frases, fotos)
            h = None
            # las de pregunta tienen los botones dibujados: van a mano, con el
            # sticker de encuesta encima (la API no pone stickers), y ese dia
            # la historia automatica es la siguiente
            while d not in (1, 4) and hist and "_pregunta_" in hist[0]:
                q = hist.pop(0)
                items.append({"tipo": "Historia (a mano)", "hora": "18:00",
                              "titulo": titulos.get(q, _titulo_archivo(q)),
                              "pieza": f"04-historias-organicas/{q}",
                              "nota": "Subila desde la app y poné el sticker de encuesta sobre los botones dibujados."})
            hd = [x for x in hist if int(x[:3]) < 51 or f.isoformat() >= DESDE_NUEVO]
            if d not in (1, 4) and hd:
                # la proxima que no repita foto (las de pregunta se saltean aca)
                libres = [x for x in hd[:6] if "_pregunta_" not in x]
                h = next((x for x in libres if not choca(f"04-historias-organicas/{x}", f)),
                         libres[0] if libres else hd[0])
                hist.remove(h)
                items.append({"tipo": "Historia", "hora": "12:30",
                              "titulo": titulos.get(h, _titulo_archivo(h)),
                              "pieza": f"04-historias-organicas/{h}", "nota": ""})
            else:
                h = sacar_hist_pauta(CAMPANAS[s], f, en_feed, solo_libres=True)
                # si todas las de campaña repiten una foto cercana, va una organica que no repita
                org = None if h else next((x for x in hd if "_pregunta_" not in x
                                           and not choca(f"04-historias-organicas/{x}", f)), None)
                if org:
                    hist.remove(org)
                    items.append({"tipo": "Historia", "hora": "12:30",
                                  "titulo": titulos.get(org, _titulo_archivo(org)),
                                  "pieza": f"04-historias-organicas/{org}", "nota": ""})
                else:
                    h = h or sacar_hist_pauta(CAMPANAS[s], f, en_feed)
                if h:
                    items.append({"tipo": "Historia", "hora": "12:30", "titulo": pauta[h]["titular"],
                                  "pieza": f"02-historias-pauta/{h}",
                                  "nota": "Historia de la campaña de la semana, con CTA a WhatsApp."})
            if d == 0:
                items.append({"tipo": "Historia (a mano)", "hora": "20:00",
                              "titulo": "Nuevo carrusel: compartilo en historias",
                              "pieza": f"{COLLAGE}/{slug}/01.jpg",
                              "nota": "Desde la app, con sticker de enlace a WhatsApp (la API no pone stickers)."})
            # ---------------------------------------------------- ventas y sistema
            if d == 1:
                items.append({"tipo": "Venta", "hora": "10:00", "titulo": f"Foco de la semana: {vertical}",
                              "pieza": "", "nota": venta})
            if d == 3:
                items.append({"tipo": "Automatización", "hora": "10:00", "titulo": auto,
                              "pieza": "11-AUTOMATIZACION/README.md", "nota": ""})
            if d == 4:
                items.append({"tipo": "Venta", "hora": "17:00", "titulo": "Seguimiento de presupuestos y leads",
                              "pieza": "09-ESTUDIO/clientes.md",
                              "nota": "Todo presupuesto sin respuesta hace 2+ días recibe un mensaje."})
            if d == 6:
                items.append({"tipo": "Equipo", "hora": "18:00", "titulo": "Luz arma la semana que viene y Lupa la revisa",
                              "pieza": "09-ESTUDIO/EQUIPO.md",
                              "nota": "El lunes a las 10 te llegan a Telegram las piezas para aprobar."})
            colocadas.extend((f, it["pieza"]) for it in items
                             if it["tipo"] in ("Historia", "Posteo", "Reel de 6 segundos") or
                             it["pieza"].startswith("00-SUBIR-EN-ORDEN/"))
            if items:
                items.sort(key=lambda it: it["hora"])
                dias.append({"fecha": f.isoformat(), "dia": DIAS[d], "semana": s + 1,
                             "vertical": vertical, "items": items})
    # lo que Martin decidió con ✗ en el Centro y Luz resolvió (08-CONTENIDO-INSTAGRAM/ajustes.json):
    # {"quitar": ["<pieza>"], "reemplazos": {"<pieza vieja>": {"pieza": "...", "titulo": "...", "tipo": "Posteo"}}}
    # Una entrada vale para esa pieza en cualquier día; "fecha" la limita a un día.
    ruta_aj = os.path.join(IG, "ajustes.json")
    aj = json.load(open(ruta_aj, encoding="utf-8")) if os.path.exists(ruta_aj) else {}
    quitar, reemp = aj.get("quitar", []), aj.get("reemplazos", {})
    for d in dias:
        if d["fecha"] < FIJO:
            continue
        nuevos = []
        for it in d["items"]:
            q = next((x for x in quitar if (x if isinstance(x, str) else x.get("pieza")) == it.get("pieza") and
                      (isinstance(x, str) or x.get("fecha", d["fecha"]) == d["fecha"])), None)
            if q is not None:
                continue
            r = reemp.get(it.get("pieza"))
            if r and r.get("fecha", d["fecha"]) == d["fecha"]:
                it = dict(it, **{k: v for k, v in r.items() if k in ("pieza", "titulo", "tipo", "nota", "hora")})
            nuevos.append(it)
        d["items"] = nuevos

    feed = sum(1 for d in dias for it in d["items"] if it["tipo"] not in ("Historia", "Historia (a mano)", "Venta", "Automatización", "Equipo"))
    hist_n = sum(1 for d in dias for it in d["items"] if it["tipo"] == "Historia")
    sin_feed = [d["fecha"] for d in dias if not any(it["tipo"] not in ("Historia", "Historia (a mano)", "Venta", "Automatización", "Equipo") for it in d["items"])]
    sin_hist = [d["fecha"] for d in dias if not any(it["tipo"] == "Historia" for it in d["items"])]
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
          "Ritmo: **un posteo y una historia todos los días.** Feed: **lunes** carrusel · "
          "**jueves** su reel · **sábado** Tus fotos en el mundo · **martes, viernes y domingo** "
          "fotos puras · **miércoles** una pieza armada de la campaña. Historias a las 12:30 "
          "(martes y viernes, de campaña con CTA). Ventas: **martes** foco · **viernes** seguimiento. "
          "**Domingo** Luz arma la semana siguiente y Lupa la revisa.", ""]
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
    print(json.dumps({"dias": len(dias), "items": sum(len(d["items"]) for d in dias),
                      "feed": feed, "historias": hist_n, "dias_sin_feed": sin_feed,
                      "dias_sin_historia": sin_hist, "quedan_en_cola": len(cola_pauta),
                      "quedan_historias": len(hist) + len(hist_pauta)}))


if __name__ == "__main__":
    main()
