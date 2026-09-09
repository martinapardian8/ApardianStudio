# -*- coding: utf-8 -*-
"""Campañas de pauta para APARDIAN STUDIO.

Cada pieza esta pensada como un aviso pago: un publico, un gancho, una oferta
y un solo boton. El texto esta escrito en la voz de Martin: voseo, directo,
sin adornos.

Estructura: (campaña, plantilla, categoria_de_foto, indice, copy)
"""

# ---- llamadas a la accion, cortas y en imperativo -------------------------
CTA_WPP   = "ESCRIBIME POR WHATSAPP"
CTA_FECHA = "RESERVÁ TU FECHA"
CTA_VER   = "MIRÁ EL PORTFOLIO"
CTA_PRESU = "PEDIME UN PRESUPUESTO"
CTA_CARTA = "COTIZÁ TU CARTA"
CTA_EDIT  = "MANDAME TUS FOTOS"
CTA_WEB   = "QUIERO MI WEB"


def P(camp, plant, cat, idx, **c):
    c["_camp"], c["_plant"], c["_cat"], c["_idx"] = camp, plant, cat, idx
    return c


# =========================================================================
# 1. BODAS — publico: parejas comprometidas, 25 a 40, Uruguay
# =========================================================================
BODAS = [
 P("bodas", "titular_sobre_foto", "bodas", 3,
   kicker="Fotografía de bodas · Uruguay",
   titular="Tu casamiento pasa una sola vez",
   sub="Cobertura completa, selección y edición en Lightroom. Entrega en 10 días.",
   cta=CTA_FECHA),
 P("bodas", "barra_inferior", "bodas", 7,
   kicker="Bodas · Montevideo y Punta del Este",
   titular="Dentro de diez años, esto es lo que te va a quedar",
   sub="No poses armadas. El día como pasó, contado en fotos.",
   cta=CTA_VER),
 P("bodas", "lista_servicio", "bodas", 11,
   kicker="Qué incluye",
   titular="Una boda completa",
   items=["Cobertura de todo el día", "Todas las fotos, sin tope de cantidad",
          "Editadas una por una en Lightroom", "Entrega en 10 días"],
   sub="Sin tope de fotos y sin costos escondidos. El presupuesto que te paso es el que pagás.",
   cta=CTA_PRESU),
 P("bodas", "prueba_social", "bodas", 2,
   numero="80", kicker="Proyectos entregados",
   titular="No es mi primera boda",
   sub="Más de 80 trabajos entregados entre bodas, fiestas y marcas.",
   cta=CTA_FECHA),
 P("bodas", "grilla_cuatro", "bodas", 0,
   kicker="Bodas 2026",
   titular="Así se ve un casamiento bien fotografiado",
   sub="Ceremonia, fiesta y los momentos que nadie más vio.",
   cta=CTA_VER),
 P("bodas", "oferta_numero", "bodas", 14,
   numero="10", kicker="Días de entrega",
   titular="Tus fotos en diez días",
   sub="Sin esperar seis meses. Todas, editadas en Lightroom una por una.",
   cta=CTA_FECHA),
 P("bodas", "mitad_color", "bodas", 5, fondo="negro",
   kicker="Temporada 2026",
   titular="Quedan pocas fechas para el verano",
   sub="Las de diciembre y enero se llenan primero. Consultá la tuya.",
   cta=CTA_FECHA),
 P("bodas", "cita", "bodas", 16,
   titular="Nos entregó todas las fotos en diez días y quedamos mudos",
   sub="Sofía y Nicolás · Casamiento en Colonia",
   cta=CTA_FECHA),
]

# =========================================================================
# 2. GASTRONOMÍA — publico: dueños de restaurantes, parrillas, cafés
# =========================================================================
GASTRO = [
 P("gastronomia", "titular_sobre_foto", "gastronomia", 5,
   kicker="Fotografía gastronómica",
   titular="La gente pide con los ojos",
   sub="Si la foto no da hambre, no vende. Así de simple.",
   cta=CTA_CARTA),
 P("gastronomia", "antes_despues", "gastronomia", 12,
   kicker="Foto de celular vs. foto tuya",
   titular="El mismo plato. Otra carta.",
   sub="Misma comida, misma cocina. Cambia quién la fotografía.",
   cta=CTA_CARTA),
 P("gastronomia", "barra_inferior", "gastronomia", 21,
   kicker="Cartas · Delivery · Redes",
   titular="Tu carta se vende sola cuando la foto acompaña",
   sub="Fotos listas para el menú, para Instagram y para las apps de delivery.",
   cta=CTA_PRESU),
 P("gastronomia", "lista_servicio", "gastronomia", 30,
   kicker="Sesión de carta",
   titular="Qué te llevás",
   items=["Todos los platos de tu carta", "Fondo neutro y ambientado",
          "Formato para carta y para redes", "Entrega en 7 días"],
   sub="Vamos a tu local. No hace falta que cierres.",
   cta=CTA_CARTA),
 P("gastronomia", "franja_roja", "gastronomia", 8,
   titular="Fotos de tu carta en una jornada",
   sub="Una mañana de trabajo y tenés material para todo el año.",
   cta=CTA_WPP),
 P("gastronomia", "grilla_cuatro", "gastronomia", 1,
   kicker="Gastronomía",
   titular="Comida que se ve como se come",
   sub="Parrilla, panadería, cafetería y producto envasado.",
   cta=CTA_VER),
 P("gastronomia", "mitad_color", "gastronomia", 40, fondo="rojo",
   kicker="Para tu local",
   titular="Nadie pide un plato que se ve mal",
   sub="Cambiá las fotos de tu carta y mirá qué pasa con el ticket promedio.",
   cta=CTA_CARTA),
 P("gastronomia", "marco_hueso", "gastronomia", 17,
   kicker="Producto y packaging",
   titular="Tu producto, como se merece",
   sub="Packshot limpio para etiqueta, catálogo y tienda online.",
   cta=CTA_PRESU),
]

# =========================================================================
# 3. EDICIÓN EN LIGHTROOM — publico: otros fotógrafos. El servicio escalable.
# =========================================================================
EDICION = [
 P("edicion", "antes_despues", "naturaleza", 9,
   kicker="Edición en Lightroom",
   titular="Fotografiás vos. Edito yo.",
   sub="Mandame el raw y te lo devuelvo revelado con tu estilo, no con el mío.",
   cta=CTA_EDIT),
 P("edicion", "titular_sobre_foto", "retratos", 14,
   kicker="Para fotógrafos",
   titular="Sacás 800 fotos y las editás de a una",
   sub="Pará. Esa parte te la puedo hacer yo mientras vos cubrís el próximo evento.",
   cta=CTA_EDIT),
 P("edicion", "barra_inferior", "eventos", 23,
   kicker="Post producción",
   titular="Entregá en tres días, no en tres semanas",
   sub="Te libero la semana de edición. Vos cobrás antes y tomás más trabajos.",
   cta=CTA_EDIT),
 P("edicion", "lista_servicio", "gastronomia", 44,
   kicker="Cómo trabajamos",
   titular="Edición por lote",
   items=["Culling: te dejo solo las que sirven", "Revelado con tu preset o con el mío",
          "Retoque de piel si hace falta", "Catálogo listo para exportar"],
   sub="Trabajo con tu catálogo de Lightroom. No perdés tu flujo.",
   cta=CTA_EDIT),
 P("edicion", "antes_despues", "eventos", 41,
   kicker="Antes y después",
   titular="Esto es lo que cambia una buena edición",
   sub="Misma foto. Una sale de la cámara, la otra sale a publicarse.",
   cta=CTA_EDIT),
 P("edicion", "oferta_numero", "retratos", 26,
   numero="72", kicker="Horas",
   titular="Tu lote editado en 72 horas",
   sub="Para bodas, eventos y sesiones de producto.",
   cta=CTA_EDIT),
 P("edicion", "franja_roja", "naturaleza", 21,
   titular="La foto la sacaste bien. Ahora que se note.",
   sub="Edición en Lightroom para fotógrafos y para marcas.",
   cta=CTA_EDIT),
]

# =========================================================================
# 4. MARCAS Y PRODUCTO — publico: emprendedores y marcas chicas
# =========================================================================
MARCAS = [
 P("marcas", "marco_hueso", "marcas", 2,
   kicker="Fotografía de producto",
   titular="Tu producto merece una foto que lo venda",
   sub="Packshot limpio, listo para Mercado Libre, tienda online y catálogo.",
   cta=CTA_PRESU),
 P("marcas", "titular_sobre_foto", "marcas", 7,
   kicker="Marcas · Uruguay",
   titular="Nadie compra lo que no se ve bien",
   sub="Fotos de producto que aguantan la ampliación y el zoom.",
   cta=CTA_WPP),
 P("marcas", "grilla_cuatro", "marcas", 0,
   kicker="Trabajos de marca",
   titular="Aceite, dulces, empanadas y kamados",
   sub="Producto real de clientes reales, fotografiado en Uruguay.",
   cta=CTA_VER),
 P("marcas", "antes_despues", "marcas", 11,
   kicker="Foto de catálogo",
   titular="La misma botella, otra marca",
   sub="Lo que cambia no es el producto. Es cómo lo contás.",
   cta=CTA_PRESU),
 P("marcas", "lista_servicio", "marcas", 5,
   kicker="Sesión de producto",
   titular="Qué incluye",
   items=["Todos los productos que traigas", "Fondo blanco y fondo ambientado",
          "Recorte listo para tienda online", "Entrega en 5 días"],
   sub="Podés mandarme el producto o voy yo a tu depósito.",
   cta=CTA_PRESU),
 P("marcas", "mitad_color", "marcas", 13, fondo="hueso",
   kicker="Para tu tienda online",
   titular="Fondo blanco, sin sorpresas",
   sub="Recortado, parejo y con el mismo tamaño en toda la línea.",
   cta=CTA_PRESU),
]

# =========================================================================
# 5. PÁGINAS WEB — publico: negocios que venden solo por Instagram
# =========================================================================
WEB = [
 P("web", "titular_sobre_foto", "empresas", 1,
   kicker="Diseño y venta de páginas web",
   titular="Tu Instagram no es tu página web",
   sub="Si el cliente te tiene que escribir para saber el precio, ya lo perdiste.",
   cta=CTA_WEB),
 P("web", "mitad_color", "salones", 4, fondo="negro",
   kicker="Páginas web",
   titular="Rápida en el celular o no sirve",
   sub="La mitad de tus clientes te va a mirar desde el teléfono, en la calle.",
   cta=CTA_WEB),
 P("web", "lista_servicio", "empresas", 3,
   kicker="Qué te entrego",
   titular="Una web completa",
   items=["Diseño propio, no una plantilla", "Andando en celular y computadora",
          "Botón de WhatsApp directo", "Te enseño a editarla vos"],
   sub="Con un editor visual para que cambies textos y fotos sin llamarme.",
   cta=CTA_WEB),
 P("web", "oferta_numero", "salones", 9,
   numero="7", kicker="Días",
   titular="Tu web andando en una semana",
   sub="Vos me pasás el contenido, yo la construyo y la publico.",
   cta=CTA_WEB),
 P("web", "dos_fotos", "salones", 12,
   kicker="Foto + web, juntos",
   titular="Las fotos y el lugar donde se muestran",
   sub="Hago las dos cosas, así no tenés que coordinar entre dos proveedores.",
   cta=CTA_WEB),
 P("web", "cita", "empresas", 5,
   titular="Le mandé el logo un lunes y el viernes ya estaba online",
   sub="Cliente de página web · Montevideo",
   cta=CTA_WEB),
]

# =========================================================================
# 6. RETRATOS Y BOOKS — publico: personas, modelos, profesionales
# =========================================================================
RETRATOS = [
 P("retratos", "marco_hueso", "retratos", 4,
   kicker="Books y retratos",
   titular="Un book que no parece de estudio",
   sub="Luz natural, tu ropa, tu lugar. Sin fondos de cartón.",
   cta=CTA_WPP),
 P("retratos", "titular_sobre_foto", "retratos", 18,
   kicker="Retrato",
   titular="Una foto tuya que no te da vergüenza mandar",
   sub="Para LinkedIn, para la web de tu estudio o para vos.",
   cta=CTA_PRESU),
 P("retratos", "mitad_color", "retratos", 29, fondo="hueso",
   kicker="Marca personal",
   titular="Si vendés vos, la cara importa",
   sub="Sesión de retrato para profesionales, artistas y emprendedores.",
   cta=CTA_WPP),
 P("retratos", "lista_servicio", "retratos", 8,
   kicker="Book personal",
   titular="Cómo es una sesión",
   items=["Dos horas, los cambios que quieras", "Todas las fotos que salgan bien",
          "Locación a elección", "Entrega en 10 días"],
   sub="Te guío durante toda la sesión. No hace falta que sepas posar.",
   cta=CTA_PRESU),
 P("retratos", "cita", "retratos", 22,
   titular="Odiaba las fotos mías hasta esta sesión",
   sub="Book personal · Montevideo",
   cta=CTA_WPP),
]

# =========================================================================
# 7. EVENTOS Y FIESTAS — publico: quinces, cumpleaños, empresas
# =========================================================================
EVENTOS = [
 P("eventos", "titular_sobre_foto", "eventos", 6,
   kicker="Eventos y fiestas",
   titular="La fiesta dura una noche",
   sub="Cobertura completa, del primer nervio al último brindis.",
   cta=CTA_FECHA),
 P("eventos", "barra_inferior", "eventos", 33,
   kicker="Quince años · Cumpleaños · Corporativo",
   titular="El día entero, sin que nadie note que estoy",
   sub="Me muevo rápido y en silencio. Vos disfrutás, yo trabajo.",
   cta=CTA_VER),
 P("eventos", "grilla_cuatro", "eventos", 2,
   kicker="Fiestas",
   titular="Lo que pasa cuando se apagan las luces",
   sub="Baile, brindis y las caras que nadie más vio.",
   cta=CTA_VER),
 P("eventos", "franja_roja", "eventos", 48,
   titular="Reservá con tiempo",
   sub="Las fechas de fin de año se llenan en septiembre.",
   cta=CTA_FECHA),
 P("eventos", "lista_servicio", "salones", 7,
   kicker="Cobertura de evento",
   titular="Qué incluye",
   items=["Cobertura de toda la fiesta", "Todas las fotos, sin tope de cantidad",
          "Galería online para los invitados", "Entrega en 10 días"],
   sub="Salones, estancias y casas particulares en todo el país.",
   cta=CTA_PRESU),
]

# =========================================================================
# 8. CUADROS — publico: decoración, regalo, gente que ya tiene la foto
# =========================================================================
CUADROS = [
 P("cuadros", "marco_hueso", "naturaleza", 3,
   kicker="Cuadros",
   titular="Colgá tu mejor foto",
   sub="Impresión y enmarcado listo para colgar. Tuya o de mi archivo.",
   cta=CTA_WPP),
 P("cuadros", "mitad_color", "naturaleza", 17, fondo="hueso",
   kicker="De la cámara a la pared",
   titular="Una foto en el teléfono no decora nada",
   sub="Elegís el tamaño y el marco, y te llega listo.",
   cta=CTA_PRESU),
 P("cuadros", "titular_sobre_foto", "naturaleza", 28,
   kicker="Obra para tu casa",
   titular="Paisajes de Uruguay, impresos en grande",
   sub="Copias numeradas, papel de archivo y marco de madera.",
   cta=CTA_VER),
]

# =========================================================================
# 9. EMPRESAS — publico: recursos humanos y comunicación
# =========================================================================
EMPRESAS = [
 P("empresas", "titular_sobre_foto", "empresas", 0,
   kicker="Fotografía corporativa",
   titular="Fotos de tu equipo que no parecen de banco de imágenes",
   sub="Gente real trabajando, no modelos sonriendo frente a una notebook.",
   cta=CTA_PRESU),
 P("empresas", "lista_servicio", "empresas", 4,
   kicker="Sesión en tu empresa",
   titular="Qué te llevás",
   items=["Retratos de todo el equipo", "Fotos del espacio y del proceso",
          "Sin tope de cantidad", "Entrega en 10 días"],
   sub="Una jornada en tu oficina o planta. Sin frenar la operación.",
   cta=CTA_PRESU),
]

TODO = BODAS + GASTRO + EDICION + MARCAS + WEB + RETRATOS + EVENTOS + CUADROS + EMPRESAS

if __name__ == "__main__":
    import collections
    c = collections.Counter(x["_camp"] for x in TODO)
    t = collections.Counter(x["_plant"] for x in TODO)
    print("piezas base:", len(TODO))
    print("por campaña:", dict(c))
    print("por plantilla:", dict(t))
