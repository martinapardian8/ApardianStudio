# -*- coding: utf-8 -*-
"""150 piezas nuevas para la carpeta de marca, compuestas con las fotos de Martin.

No usa creditos: el motor arma cada pieza con el sistema visual sobre sus fotos
reales. Sale a 03-flyers, 06-posteos y 07-historias.
"""
import os, re, unicodedata, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_ads import *
import plantillas_ads as P
import similitud as S

BASE = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/04-VIDEOS-IA/contenido ia/marca"

CTA = {"wpp": "ESCRIBIME POR WHATSAPP", "fecha": "RESERVÁ TU FECHA",
       "ver": "MIRÁ EL PORTFOLIO", "presu": "PEDIME UN PRESUPUESTO",
       "carta": "COTIZÁ TU CARTA", "edit": "MANDAME TUS FOTOS",
       "web": "QUIERO MI WEB", "cuadro": "QUIERO UN CUADRO"}


def p(cat, plant, tit, sub, cta, kick=None, **extra):
    d = {"_cat": cat, "_plant": plant, "titular": tit, "sub": sub,
         "cta": CTA[cta], "kicker": kick or ""}
    d.update(extra)
    return d


# ---------------------------------------------------------------- 50 posteos
POSTEOS = [
 # --- bodas ---------------------------------------------------------------
 p("bodas","titular_sobre_foto","No se puede repetir el día","Por eso llego temprano y me voy último.","fecha","Bodas"),
 p("bodas","barra_inferior","La foto que va a colgar tu vieja","Una sola, pero tiene que ser esa.","fecha","Bodas · Uruguay"),
 p("bodas","mitad_color","Vas a estar nervioso y está bien","Mi trabajo es que eso no se note en las fotos.","fecha","Bodas", fondo="negro"),
 p("bodas","marco_hueso","Los que miran de lejos","Tus abuelos, tus amigos, el que llora en la última fila.","ver","Bodas"),
 p("bodas","franja_roja","Diciembre y enero se llenan primero","Consultá tu fecha ahora y te contesto hoy.","fecha"),
 p("bodas","cita","Pensábamos que iba a ser incómodo y ni lo vimos trabajar","Sofía y Nicolás · Colonia","fecha"),
 p("salones","lista_servicio","Todo el día","","presu","Qué incluye",
   items=["Desde los preparativos hasta el final","Todas las fotos, sin tope",
          "Editadas una por una","Entrega en 10 días"]),
 # --- gastronomia ---------------------------------------------------------
 p("gastronomia","titular_sobre_foto","Tu carta es tu vendedor","Y hoy está trabajando con fotos de celular.","carta","Gastronomía"),
 p("gastronomia","antes_despues","Misma cocina, otra foto","Lo que cambia es quién la saca y cómo se revela.","carta","Antes y después"),
 p("gastronomia","mitad_color","Nadie pide algo que se ve feo","Aunque esté riquísimo.","carta","Para tu local", fondo="rojo"),
 p("gastronomia","barra_inferior","El plato se enfría en tres minutos","Por eso la luz tiene que estar armada antes.","carta","Cómo trabajo"),
 p("gastronomia","marco_hueso","Producto envasado","Etiqueta, catálogo y tienda online en la misma jornada.","presu","Packaging"),
 p("gastronomia","franja_roja","Toda la carta en una jornada","No hace falta que cierres el local.","carta"),
 p("gastronomia","grilla_cuatro","Parrilla, panadería y cafetería","Todo fotografiado en el local del cliente.","ver","Gastronomía"),
 # --- edicion -------------------------------------------------------------
 p("naturaleza","antes_despues","No es un filtro","Se trabaja cada zona por separado. No hay botón que lo haga.","edit","Edición en Lightroom"),
 p("retratos","titular_sobre_foto","Volviste con 900 fotos","Y no tenés la semana para editarlas.","edit","Para fotógrafos"),
 p("eventos","barra_inferior","Cobrá antes","Si entregás en tres días en vez de tres semanas, cobrás antes.","edit","Post producción"),
 p("gastronomia","antes_despues","La comida se edita distinto","Si te pasás de saturación, deja de dar hambre.","edit","Edición"),
 p("retratos","antes_despues","La piel no se plancha","Se corrige el tono y se deja la textura.","edit","Retoque"),
 p("eventos","franja_roja","Tu lote en 72 horas","Bodas, eventos y sesiones de producto.","edit"),
 p("naturaleza","lista_servicio","Edición por lote","Trabajo con tu catálogo. No perdés tu flujo.","edit","Cómo trabajamos",
   items=["Culling: te dejo las que sirven","Revelado con tu preset o el mío",
          "Retoque de piel si hace falta","Catálogo listo para exportar"]),
 # --- marcas --------------------------------------------------------------
 p("marcas","marco_hueso","Tu producto en la góndola de al lado","La foto decide antes que el precio.","presu","Producto"),
 p("marcas","titular_sobre_foto","Fondo blanco de verdad","Blanco puro, sin gris ni celeste. Lo que pide una tienda online.","presu","Packshot"),
 p("marcas","mitad_color","La misma botella, otra marca","Lo que cambia no es el producto, es cómo lo contás.","presu","Marcas", fondo="hueso"),
 p("marcas","grilla_cuatro","Marcas uruguayas","Aceite, dulces, empanadas y kamados.","ver","Trabajos"),
 p("marcas","barra_inferior","Cuarenta tomas para elegir una","Así se hace un packshot que aguanta el zoom.","presu","Detrás de escena"),
 p("marcas","lista_servicio","Sesión de producto","Podés mandarme el producto o voy yo.","presu","Qué incluye",
   items=["Todos los productos que traigas","Fondo blanco y ambientado",
          "Recorte listo para tienda","Entrega en 5 días"]),
 # --- web -----------------------------------------------------------------
 p("empresas","titular_sobre_foto","En Google te busca el que no te conoce","En Instagram te encuentra el que ya te conocía.","web","Páginas web"),
 p("salones","mitad_color","Si carga lento, ya se fue","La mitad te mira desde el celular, en la calle.","web","Web", fondo="negro"),
 p("empresas","lista_servicio","Una web completa","Con editor para que la cambies vos.","web","Qué te entrego",
   items=["Diseño propio, no plantilla","Anda en celular y computadora",
          "Botón de WhatsApp directo","Te enseño a editarla"]),
 p("salones","franja_roja","Tu web andando en una semana","Vos me pasás el contenido, yo la publico.","web"),
 p("empresas","cita","Le mandé el logo un lunes y el viernes estaba online","Cliente de página web · Montevideo","web"),
 # --- retratos y books ----------------------------------------------------
 p("retratos","marco_hueso","Un book que no parece de estudio","Luz natural, tu ropa, tu lugar.","wpp","Books"),
 p("retratos","titular_sobre_foto","La foto de tu perfil es de hace seis años","Se nota.","presu","Marca personal"),
 p("retratos","mitad_color","Si vendés vos, la cara importa","Para tu web, tu LinkedIn o tu estudio.","wpp","Retrato", fondo="hueso"),
 p("retratos","barra_inferior","No hace falta que sepas posar","Para eso estoy yo. Te guío toda la sesión.","presu","Cómo es"),
 p("retratos","cita","Odiaba las fotos mías hasta esta sesión","Book personal · Montevideo","wpp"),
 p("retratos","lista_servicio","Book personal","Te guío toda la sesión.","presu","Cómo es una sesión",
   items=["Dos horas, los cambios que quieras","Todas las fotos que salgan bien",
          "Locación a elección","Entrega en 10 días"]),
 # --- eventos -------------------------------------------------------------
 p("eventos","titular_sobre_foto","A las dos de la mañana casi nadie sigue laburando","Yo sí. Ahí salen las mejores.","fecha","Eventos"),
 p("eventos","barra_inferior","Si me notás, algo hice mal","Me muevo rápido y en silencio.","ver","Cómo trabajo"),
 p("eventos","grilla_cuatro","Quince años y cumpleaños","Cobertura de toda la noche, sin tope de fotos.","fecha","Fiestas"),
 p("eventos","franja_roja","Fin de año se reserva en septiembre","Consultá tu fecha.","fecha"),
 p("salones","mitad_color","Vacío a las cinco, lleno a las nueve","Fotografiar un salón montado es otro laburo.","presu","Salones", fondo="negro"),
 # --- cuadros y varios ----------------------------------------------------
 p("naturaleza","marco_hueso","De la cámara a la pared","Impresión y enmarcado listo para colgar.","cuadro","Cuadros"),
 p("naturaleza","titular_sobre_foto","Una foto en el teléfono no decora nada","Elegís tamaño y marco, y te llega listo.","cuadro","Cuadros"),
 p("naturaleza","mitad_color","Uruguay impreso en grande","Copias numeradas y papel de archivo.","cuadro","Obra", fondo="hueso"),
 p("animales","barra_inferior","Los que nunca posan","Y por eso salen mejor que nosotros.","wpp","Animales"),
 p("empresas","titular_sobre_foto","Tu equipo no son modelos de banco de imágenes","Gente real trabajando.","presu","Corporativo"),
 p("musica","barra_inferior","Tres canciones y se acabó la luz","No podés pedirle a la banda que repita el tema.","wpp","Música"),
 p("deportes","titular_sobre_foto","No hay segunda toma","Deporte es la única disciplina donde no podés pedir que lo repitan.","wpp","Deportes"),
]

# ---------------------------------------------------------------- 50 historias
HISTORIAS = [
 p("bodas","titular_sobre_foto","Sábado de casamiento","Ya está la galería.","fecha","Recién entregado"),
 p("bodas","barra_inferior","La espera antes de entrar","Es el momento más nervioso del día.","fecha","Bodas"),
 p("bodas","mitad_color","Quedan fechas para el verano","Escribime y te paso disponibilidad.","fecha","Agenda", fondo="rojo"),
 p("bodas","marco_hueso","Ceremonia","Todo el día, sin tope de fotos.","fecha","Bodas"),
 p("salones","titular_sobre_foto","El salón antes de que entre nadie","Media hora de silencio y después no para más.","presu","Salones"),
 p("gastronomia","barra_inferior","Ocho horas en la cocina","Vale cada minuto cuando ves la carta terminada.","carta","Hoy"),
 p("gastronomia","antes_despues","Antes y después","Misma comida, otra foto.","carta","Edición"),
 p("gastronomia","mitad_color","Si no da hambre, no vende","Así de simple.","carta","Gastronomía", fondo="negro"),
 p("gastronomia","titular_sobre_foto","El humo dura diez segundos","Hay que estar listo antes.","carta","Detrás de escena"),
 p("gastronomia","marco_hueso","Producto envasado","Para etiqueta, catálogo y tienda.","presu","Packaging"),
 p("naturaleza","antes_despues","Esto es revelado","No hay botón que lo haga.","edit","Lightroom"),
 p("retratos","antes_despues","La piel no se plancha","Se corrige el tono, se deja la textura.","edit","Retoque"),
 p("eventos","antes_despues","Poca luz no es excusa","El ruido se trabaja, no se tapa.","edit","Edición"),
 p("marcas","antes_despues","Fondo blanco de verdad","Es lo que pide una tienda online.","presu","Packshot"),
 p("retratos","titular_sobre_foto","Sacás 800 fotos por evento","Y las editás de a una. Pará.","edit","Para fotógrafos"),
 p("eventos","barra_inferior","Entregá en tres días","Te libero la semana de edición.","edit","Post producción"),
 p("naturaleza","franja_roja","Tu lote en 72 horas","Para fotógrafos y para marcas.","edit"),
 p("marcas","marco_hueso","Tu producto merece esto","Packshot limpio, listo para vender.","presu","Producto"),
 p("marcas","titular_sobre_foto","Nadie compra lo que se ve mal","Aunque sea bueno.","presu","Marcas"),
 p("marcas","mitad_color","Todos los productos que traigas","Sin tope. Entrega en 5 días.","presu","Sesión", fondo="hueso"),
 p("empresas","titular_sobre_foto","Tu Instagram no es tu web","El cliente que te busca en Google no te encuentra.","web","Páginas web"),
 p("salones","mitad_color","Rápida en el celular","O no sirve.","web","Web", fondo="negro"),
 p("empresas","barra_inferior","Te dejo un editor","Cambiás textos y fotos sin llamarme.","web","Páginas web"),
 p("salones","franja_roja","Tu web en una semana","Vos me pasás el contenido.","web"),
 p("retratos","marco_hueso","Un book que no parece de estudio","Luz natural, tu ropa, tu lugar.","wpp","Books"),
 p("retratos","titular_sobre_foto","Le dije dos cosas y me callé","El resto lo hizo la luz.","presu","Retrato"),
 p("retratos","mitad_color","Para tu web o tu LinkedIn","Si vendés vos, la cara importa.","wpp","Marca personal", fondo="hueso"),
 p("retratos","barra_inferior","No sabés posar y está bien","Para eso estoy yo.","presu","Cómo es"),
 p("eventos","titular_sobre_foto","La fiesta empieza a las dos","Ahí salen las mejores.","fecha","Anoche"),
 p("eventos","barra_inferior","Del primer nervio al último brindis","Cobertura completa.","fecha","Eventos"),
 p("eventos","mitad_color","Quince años","Sin tope de fotos, entrega en 10 días.","fecha","Fiestas", fondo="rojo"),
 p("eventos","franja_roja","Reservá con tiempo","Fin de año se llena en septiembre.","fecha"),
 p("salones","marco_hueso","Salones de Uruguay","Fotos del espacio montado para tu web.","presu","Salones"),
 p("naturaleza","titular_sobre_foto","Salí a caminar y volví con esto","Uruguay tiene lugares que no están en ninguna guía.","cuadro","Fin de semana"),
 p("naturaleza","marco_hueso","Colgá tu mejor foto","Impresión y marco listo.","cuadro","Cuadros"),
 p("naturaleza","mitad_color","Copias numeradas","Papel de archivo y marco de madera.","cuadro","Obra", fondo="hueso"),
 p("naturaleza","barra_inferior","Nadie en kilómetros","Y eso también es Uruguay.","cuadro","Paisaje"),
 p("animales","titular_sobre_foto","Me miró y se fue","Nunca posan y siempre miran.","wpp","Animales"),
 p("animales","barra_inferior","No se movió en veinte minutos","Y salió mejor que yo.","wpp","Animales"),
 p("animales","marco_hueso","También hago esto","Si tenés un animal en tu vida, merece una foto de verdad.","wpp","Animales"),
 p("musica","titular_sobre_foto","Poca luz y una sola pasada","No se puede repetir el tema.","wpp","En vivo"),
 p("musica","barra_inferior","Fotos de show","Para prensa, redes y tapa de disco.","wpp","Música"),
 p("musica","mitad_color","¿Tocás en vivo?","Escribime antes de la próxima fecha.","wpp","Música", fondo="negro"),
 p("deportes","titular_sobre_foto","No hay segunda toma","El instante que no se repite.","wpp","Deportes"),
 p("empresas","marco_hueso","Retratos de equipo","Gente real trabajando, no modelos.","presu","Corporativo"),
 p("empresas","titular_sobre_foto","Una jornada en tu oficina","Sin frenar la operación.","presu","Empresas"),
 p("empresas","barra_inferior","Fotos del espacio y del proceso","Para web, redes y prensa.","presu","Corporativo"),
 p("gastronomia","franja_roja","Cambiá las fotos de tu carta","Y mirá qué pasa con el ticket promedio.","carta"),
 p("bodas","franja_roja","Contame tu fecha","Te contesto hoy mismo.","fecha"),
 p("retratos","franja_roja","Te toca a vos","Book, marca personal o retrato para tu web.","wpp"),
]

# ---------------------------------------------------------------- 50 flyers
FLYERS = [
 p(c, pl, t, s, ct, k, **e) for (c, pl, t, s, ct, k, e) in [
 ("bodas","titular_sobre_foto","Bodas","Cobertura completa, entrega en 10 días.","fecha","Servicio",{}),
 ("gastronomia","titular_sobre_foto","Gastronomía","Toda la carta en una jornada.","carta","Servicio",{}),
 ("retratos","titular_sobre_foto","Retratos","Books, marca personal y corporativo.","presu","Servicio",{}),
 ("marcas","titular_sobre_foto","Producto","Packshot listo para vender.","presu","Servicio",{}),
 ("eventos","titular_sobre_foto","Eventos","Quince años, cumpleaños y empresa.","fecha","Servicio",{}),
 ("naturaleza","titular_sobre_foto","Cuadros","De la cámara a la pared.","cuadro","Servicio",{}),
 ("empresas","titular_sobre_foto","Páginas web","Diseño propio, no plantilla.","web","Servicio",{}),
 ("naturaleza","titular_sobre_foto","Edición en Lightroom","Para otros fotógrafos.","edit","Servicio",{}),
 ("musica","titular_sobre_foto","Música en vivo","Prensa, redes y tapa de disco.","wpp","Servicio",{}),
 ("animales","titular_sobre_foto","Animales","Los que nunca posan.","wpp","Servicio",{}),
 ("salones","mitad_color","Salones","Fotos del espacio montado.","presu","Servicio",{"fondo":"negro"}),
 ("deportes","mitad_color","Deportes","El instante que no se repite.","wpp","Servicio",{"fondo":"negro"}),
 ("bodas","mitad_color","Reservá tu fecha","Diciembre y enero se llenan primero.","fecha","Agenda",{"fondo":"rojo"}),
 ("gastronomia","mitad_color","Cotizá tu carta","Una jornada en tu local.","carta","Agenda",{"fondo":"rojo"}),
 ("retratos","mitad_color","Agendá tu book","Dos horas, todas las fotos.","presu","Agenda",{"fondo":"rojo"}),
 ("marcas","marco_hueso","Marcas uruguayas","Producto real de gente que labura acá.","ver","Portfolio",{}),
 ("bodas","marco_hueso","Casamientos","Ceremonia, salón y fiesta.","ver","Portfolio",{}),
 ("retratos","marco_hueso","Personas","Ninguna posó.","ver","Portfolio",{}),
 ("naturaleza","marco_hueso","Uruguay","Paisajes impresos en grande.","cuadro","Portfolio",{}),
 ("eventos","marco_hueso","Fiestas","Lo que pasa cuando se apagan las luces.","ver","Portfolio",{}),
 ("gastronomia","franja_roja","Fotos en una jornada","No hace falta que cierres.","carta",None,{}),
 ("bodas","franja_roja","Entrega en 10 días","Sin tope de cantidad de fotos.","fecha",None,{}),
 ("naturaleza","franja_roja","Tu lote en 72 horas","Edición para fotógrafos.","edit",None,{}),
 ("empresas","franja_roja","Tu web en una semana","Diseño propio, no plantilla.","web",None,{}),
 ("marcas","franja_roja","Entrega en 5 días","Producto con recorte listo.","presu",None,{}),
 ("gastronomia","antes_despues","Antes y después","Misma cocina, otra foto.","carta","Edición",{}),
 ("naturaleza","antes_despues","Esto cambia una edición","No es un filtro.","edit","Lightroom",{}),
 ("retratos","antes_despues","Retoque de piel","Se corrige el tono, se deja la textura.","edit","Lightroom",{}),
 ("eventos","antes_despues","Poca luz","El ruido se trabaja, no se tapa.","edit","Lightroom",{}),
 ("marcas","antes_despues","Fondo blanco","Lo que pide una tienda online.","presu","Packshot",{}),
 ("bodas","barra_inferior","Todo el día","Desde los preparativos hasta el final.","fecha","Bodas",{}),
 ("gastronomia","barra_inferior","Para carta y delivery","Listas para el menú y para las apps.","carta","Gastronomía",{}),
 ("retratos","barra_inferior","Luz natural","Tu ropa, tu lugar, sin fondos de cartón.","presu","Retratos",{}),
 ("marcas","barra_inferior","Catálogo completo","Todos los productos en una jornada.","presu","Producto",{}),
 ("eventos","barra_inferior","Toda la noche","Sin tope de fotos.","fecha","Eventos",{}),
 ("salones","barra_inferior","Tu salón en su mejor momento","Montado y con la luz armada.","presu","Salones",{}),
 ("empresas","barra_inferior","Equipo y espacio","Una jornada, sin frenar la operación.","presu","Corporativo",{}),
 ("musica","barra_inferior","En vivo","Poca luz y una sola oportunidad.","wpp","Música",{}),
 ("animales","barra_inferior","Sin poses","Los que nunca miran a cámara.","wpp","Animales",{}),
 ("naturaleza","barra_inferior","Paisaje uruguayo","Copias numeradas para colgar.","cuadro","Cuadros",{}),
 ("bodas","grilla_cuatro","Casamientos 2026","Ceremonia, salón y fiesta.","ver","Portfolio",{}),
 ("gastronomia","grilla_cuatro","Cartas fotografiadas","Parrilla, panadería y café.","ver","Portfolio",{}),
 ("marcas","grilla_cuatro","Producto uruguayo","Aceite, dulces y empanadas.","ver","Portfolio",{}),
 ("eventos","grilla_cuatro","Fiestas","Quince años y cumpleaños.","ver","Portfolio",{}),
 ("retratos","grilla_cuatro","Personas","Ocho luces distintas.","ver","Portfolio",{}),
 ("bodas","cita","Nos entregó todo en diez días","Sofía y Nicolás · Colonia","fecha",None,{}),
 ("gastronomia","cita","Cambiamos las fotos y subió el ticket","Cliente de gastronomía","carta",None,{}),
 ("retratos","cita","Odiaba las fotos mías hasta esta sesión","Book personal · Montevideo","wpp",None,{}),
 ("empresas","cita","El viernes ya estaba online","Cliente de página web","web",None,{}),
 ("naturaleza","cita","Lo colgamos en el living","Cuadro impreso · Montevideo","cuadro",None,{}),
]]

MULTI = {"grilla_cuatro": 4, "dos_fotos": 2}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii","ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+","-",t).strip("-").lower()[:42]


def rutas(plant, cat, i, size):
    n = MULTI.get(plant, 1)
    malas = S._vetadas(POST) | S._vetadas(STORY)
    if n == 1:
        r = foto(cat, i)
        if r in malas:
            for k in range(1, 25):
                a = foto(cat, i + k)
                if a not in malas: return a
        return r
    cands = [q for q in (pool().get(cat) or []) if q not in malas] or (pool().get(cat) or [])
    return S.variadas(cands, n, arranque=i, size=size)


def hacer(lista, carpeta, size, story, arranque=200):
    d = os.path.join(BASE, carpeta)
    os.makedirs(d, exist_ok=True)
    hechos = 0
    for i, c in enumerate(lista):
        plant = c["_plant"]
        fn = getattr(P, plant)
        cc = {k: v for k, v in c.items() if not k.startswith("_")}
        if not cc.get("kicker"): cc.pop("kicker", None)
        try:
            im = fn(size, story, rutas(plant, c["_cat"], arranque + i * 3, size), cc)
            im.save(os.path.join(d, f"{arranque+i:03d}_{slug(c['titular'])}.jpg"),
                    "JPEG", quality=90, optimize=True)
            hechos += 1
        except Exception as e:
            print(f"  fallo {carpeta} {i}: {type(e).__name__}: {e}")
    return hechos


if __name__ == "__main__":
    r = {}
    r["03-flyers"]    = hacer(FLYERS,    "03-flyers",    POST,  False, 200)
    r["06-posteos"]   = hacer(POSTEOS,   "06-posteos",   POST,  False, 300)
    r["07-historias"] = hacer(HISTORIAS, "07-historias", STORY, True,  400)
    S.guardar(); S.guardar_perfiles()
    import recorte; recorte.guardar_cache()
    print(json.dumps(r, ensure_ascii=False))
