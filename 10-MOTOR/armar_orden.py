# -*- coding: utf-8 -*-
"""Reordena la entrega por PUBLICACION, no por tipo de archivo.

Cada carpeta es una publicacion completa y lista: las imagenes en el orden en
que se suben, el pie de foto para copiar y la historia que la acompaña.
Martin abre la carpeta 01, sube lo que hay adentro, y listo.
"""
import os, json, shutil, glob

BASE = "/Users/martinapardian/Desktop/WEB APARDIANSTUDIO/08-CONTENIDO-INSTAGRAM"
DEST = os.path.join(BASE, "00-SUBIR-EN-ORDEN")

CARR = os.path.join(BASE, "03-carruseles")
POST = os.path.join(BASE, "01-posteos-pauta")
HORG = os.path.join(BASE, "04-historias-organicas")
VID  = os.path.join(BASE, "05-videos")


def buscar(carpeta, n):
    """Archivo que empieza con ese numero, ignorando los indices."""
    for p in sorted(glob.glob(os.path.join(carpeta, f"{n:03d}_*.jpg"))):
        return p
    return None


def carrusel(slug_ini):
    for d in sorted(os.listdir(CARR)):
        if d.startswith(slug_ini) and os.path.isdir(os.path.join(CARR, d)):
            return os.path.join(CARR, d)
    return None


# ---------------------------------------------------------------- el plan
# (dia, tipo, referencia, historia, titulo, copy)
FIRMA = "\n\nEscribime por WhatsApp desde el link de la bio.\n🌐 apardianstudio.com"

PUBS = [
{"n": 1, "cuando": "Hoy", "tipo": "carrusel", "ref": "05",
 "historia": 5, "titulo": "Nadie posó",
 "por_que": "Es el carrusel mas fuerte que tenes: ocho personas distintas, ocho "
            "luces distintas, todas bien compuestas. Para volver despues de un "
            "tiempo sin publicar conviene lo mas transversal, que le hable a "
            "cualquiera que te siga y no solo a los que se casan.",
 "copy": """Hacía rato que no subía nada acá. No porque no estuviera trabajando: justamente por eso.

Ocho personas, ocho luces. Ninguna posó.

A todas les dije dos cosas y me callé. El resto lo hace la luz y el tiempo que le des a alguien para que se olvide de que hay una cámara.

Hago books personales, retratos de marca y fotos para tu web o tu LinkedIn. Luz natural, tu ropa, tu lugar. Sin fondos de cartón.

Si te da vergüenza que te saquen fotos, esa es justamente mi especialidad. Y no te preocupes por posar: para eso estoy yo.""" + FIRMA,
 "hashtags": "#retrato #bookdefotos #marcapersonal #montevideo #fotografiaderetrato #fotografouruguay"},

{"n": 2, "cuando": "Miércoles", "tipo": "posteo", "ref": 9,
 "historia": 3, "titulo": "La gente pide con los ojos",
 "por_que": "Cambia de publico: despues de bodas conviene hablarle a los "
            "restaurantes, que compran todo el año y no solo en verano.",
 "copy": """La gente pide con los ojos.

Si la foto del plato no da hambre, no vende. Da igual lo bien que cocines: nadie pide algo que se ve mal en la carta.

Voy a tu local una jornada, fotografío todos los platos de la carta y te los entrego en 7 días, listos para el menú, para Instagram y para las apps de delivery. No hace falta que cierres.

¿Cuánto hace que no cambiás las fotos de tu carta?""" + FIRMA,
 "hashtags": "#fotografiagastronomica #montevideo #restaurantesuruguay #foodphotography #cartadigital #parrilla"},

{"n": 3, "cuando": "Viernes", "tipo": "video", "ref": "017_edicion_fotografias-vos-edito-yo_feed.mp4",
 "historia": 16, "titulo": "Fotografiás vos. Edito yo.",
 "por_que": "El video rinde mas que la imagen fija y este servicio es el unico "
            "que no depende de que el cliente este en Uruguay.",
 "copy": """Fotografiás vos. Edito yo.

Si sos fotógrafo y venís atrasado con una entrega, esta es para vos. Mandame el lote y te lo devuelvo revelado con tu estilo, no con el mío.

Culling, revelado con tu preset o con el mío, retoque de piel si hace falta y el catálogo listo para exportar. Tu lote en 72 horas.

Vos cubrís el próximo evento mientras yo te libero la semana de edición.""" + FIRMA,
 "hashtags": "#lightroom #edicionfotografica #fotografosuruguay #postproduccion #revelado"},

{"n": 4, "cuando": "Semana 2 · Lunes", "tipo": "carrusel", "ref": "01",
 "historia": 1, "titulo": "Casamientos",
 "por_que": "Septiembre es cuando se reservan las fechas de diciembre y enero. "
            "Va en la semana 2 y no en la 1 porque tu archivo de bodas tiene "
            "pocas fotos de novios y muchas de salon: el carrusel es correcto "
            "pero no es tu material mas fuerte.",
 "copy": """Casamientos.

La ceremonia, el salón antes de que entre nadie y la fiesta cuando ya no queda nadie sentado. Un día que dura uno solo y no vuelve.

Cubro bodas en todo el país. Todas las fotos, sin tope de cantidad, editadas una por una en Lightroom y entregadas en 10 días.

Si te casás este verano, diciembre y enero se llenan primero. Escribime y te paso disponibilidad hoy mismo.""" + FIRMA,
 "hashtags": "#fotografodebodas #casamientouruguay #bodasuruguay #montevideo #fotografiadebodas"},

{"n": 5, "cuando": "Semana 2 · Miércoles", "tipo": "posteo", "ref": 30,
 "historia": 14, "titulo": "Tu Instagram no es tu página web",
 "por_que": "Servicio nuevo y poco conocido entre los que te siguen. Vale "
            "presentarlo con un posteo propio.",
 "copy": """Tu Instagram no es tu página web.

Si el cliente te tiene que escribir para saber qué hacés y cuánto sale, ya lo perdiste. En Instagram te encuentra el que ya te conoce; en Google te encuentra el que te está buscando.

Diseño y programo páginas web. Diseño propio, no una plantilla. Anda rápido en el celular, tiene botón de WhatsApp directo, y te dejo un editor para que cambies textos y fotos vos, sin llamarme.

Esta misma cuenta tiene la suya: apardianstudio.com""" + FIRMA,
 "hashtags": "#diseñoweb #paginasweb #uruguay #emprendedoresuy #desarrolloweb"},

{"n": 6, "cuando": "Semana 2 · Viernes", "tipo": "carrusel", "ref": "03",
 "historia": 17, "titulo": "Antes y después",
 "por_que": "El antes y despues es el formato que mas se guarda y se comparte. "
            "Ademas educa sobre lo que cuesta una buena edicion.",
 "copy": """Antes y después.

A la izquierda, como sale de la cámara. A la derecha, después de revelarla.

No es un filtro. Se trabaja cada zona por separado: las luces, las sombras, el color de cada rango. No hay un botón que lo haga.

Esto es lo que pasa con tus fotos cuando me las mandás. Para fotógrafos y para marcas.""" + FIRMA,
 "hashtags": "#lightroom #antesydespues #edicionfotografica #fotografosuruguay #revelado"},

{"n": 7, "cuando": "Semana 3 · Lunes", "tipo": "carrusel", "ref": "02",
 "historia": 27, "titulo": "Platos que se venden solos",
 "por_que": "Vuelve a gastronomia con formato carrusel, que rinde mas que el "
            "posteo suelto de la semana 1.",
 "copy": """Platos que se venden solos.

Parrilla, panadería, cafetería y producto envasado. Todos fotografiados en el local del cliente, en una sola jornada de trabajo.

El plato se enfría en tres minutos, así que la luz tiene que estar armada antes de que salga de la cocina. Eso es el 80% del laburo.

Si tu carta todavía tiene fotos de celular, hablemos.""" + FIRMA,
 "hashtags": "#fotografiagastronomica #foodphotography #montevideo #restaurantesuruguay #parrilla"},

{"n": 8, "cuando": "Semana 3 · Miércoles", "tipo": "posteo", "ref": 4,
 "historia": 11, "titulo": "No es mi primera boda",
 "por_que": "Prueba social. Despues de tres semanas publicando conviene "
            "recordar que hay trayectoria detras.",
 "copy": """Más de 80 proyectos entregados.

Bodas, quince años, fiestas de empresa, marcas y páginas web. Ocho años haciendo esto en Uruguay.

No es mi primera boda ni mi primera carta ni mi primera web. Y se nota justamente en las cosas que no vas a ver: que llegue temprano, que tenga dos cámaras, que no desaparezca después de cobrar.

Si estás buscando a alguien para algo que pasa una sola vez, escribime.""" + FIRMA,
 "hashtags": "#fotografouruguay #montevideo #fotografodebodas #produccionaudiovisual"},

{"n": 9, "cuando": "Semana 3 · Viernes", "tipo": "carrusel", "ref": "04",
 "historia": 6, "titulo": "Marcas uruguayas que fotografié",
 "por_que": "Producto es el servicio que mas se vende por recomendacion entre "
            "emprendedores. Mostrar clientes reales lo dispara.",
 "copy": """Marcas uruguayas que fotografié.

Aceite de oliva, empanadas, alfajores, kamados. Producto real de gente que labura acá.

Un packshot no es sacarle una foto a la botella. Es fondo parejo, mismo tamaño en toda la línea y un recorte que la tienda online acepte sin quejarse.

Todos los productos que traigas, entrega en 5 días.""" + FIRMA,
 "hashtags": "#fotografiadeproducto #packshot #marcasuruguayas #emprendedoresuy #packaging"},

{"n": 10, "cuando": "Semana 4 · Lunes", "tipo": "carrusel", "ref": "06",
 "historia": 4, "titulo": "Lo que pasa cuando se apagan las luces",
 "por_que": "Fiestas y quince años. Empieza la temporada de fin de curso y "
            "las familias reservan con dos meses de anticipacion.",
 "copy": """Lo que pasa cuando se apagan las luces.

La fiesta empieza de verdad a las dos de la mañana, y ahí es cuando salen las mejores. El problema es que a esa hora casi nadie sigue laburando.

Yo sí. Me muevo rápido y en silencio: si me notás, algo hice mal.

Quince años, cumpleaños y fiestas de empresa. Cobertura de toda la noche, sin tope de fotos, entrega en 10 días.""" + FIRMA,
 "hashtags": "#quinceaños #fiestasuruguay #fotografodeeventos #montevideo #cumpleaños"},

{"n": 11, "cuando": "Semana 4 · Miércoles", "tipo": "video", "ref": "037_retratos_una-foto-tuya-que-no-te-da-verguenza-man_feed.mp4",
 "historia": 24, "titulo": "Una foto tuya que no te da vergüenza mandar",
 "por_que": "Video otra vez, y con el gancho mas humano de todos.",
 "copy": """Una foto tuya que no te da vergüenza mandar.

La que usás en LinkedIn es de hace seis años. La del sitio de tu estudio te la sacó un amigo con el celular. Y cada vez que te piden una foto, buscás diez minutos y mandás cualquiera.

Dos horas, los cambios de ropa que quieras, la locación que elijas. Te guío toda la sesión: no hace falta que sepas posar.

Todas las fotos que salgan bien, entrega en 10 días.""" + FIRMA,
 "hashtags": "#retrato #marcapersonal #linkedin #montevideo #bookdefotos"},

{"n": 12, "cuando": "Semana 4 · Viernes", "tipo": "carrusel", "ref": "15",
 "historia": 30, "titulo": "Cómo trabajo",
 "por_que": "Cierra el mes explicando el proceso. Es el posteo que convierte "
            "al que te viene siguiendo hace cuatro semanas y todavia no escribio.",
 "copy": """Cómo trabajo, en seis pasos.

Sin formularios, sin respuestas automáticas y sin desaparecer a mitad de camino.

Me escribís por WhatsApp, charlamos, y en 24 horas te paso una propuesta con precio cerrado. Después produzco, te muestro avances, edito en Lightroom una por una y entrego en los formatos que necesites.

El presupuesto que te paso es el que pagás. Sin costos escondidos y sin tope de cantidad de fotos.""" + FIRMA,
 "hashtags": "#fotografouruguay #montevideo #produccionaudiovisual #comotrabajo"},
]


def main():
    if os.path.exists(DEST):
        shutil.rmtree(DEST)
    os.makedirs(DEST)
    resumen = []

    for p in PUBS:
        nom = f"{p['n']:02d}-{p['cuando'].split('·')[-1].strip().lower().replace(' ','-')}"
        d = os.path.join(DEST, f"{p['n']:02d}")
        os.makedirs(d, exist_ok=True)
        archivos = []

        if p["tipo"] == "carrusel":
            src = carrusel(p["ref"])
            lam = sorted(q for q in glob.glob(os.path.join(src, "*.jpg"))
                         if not os.path.basename(q).startswith("00_"))
            for i, q in enumerate(lam, 1):
                dst = os.path.join(d, f"foto-{i}.jpg")
                shutil.copy2(q, dst); archivos.append(os.path.basename(dst))
        elif p["tipo"] == "posteo":
            q = buscar(POST, p["ref"])
            dst = os.path.join(d, "foto-1.jpg")
            shutil.copy2(q, dst); archivos.append("foto-1.jpg")
        else:  # video
            q = os.path.join(VID, p["ref"])
            dst = os.path.join(d, "video.mp4")
            shutil.copy2(q, dst); archivos.append("video.mp4")

        h = buscar(HORG, p["historia"])
        if h:
            shutil.copy2(h, os.path.join(d, "historia.jpg"))

        with open(os.path.join(d, "copy.txt"), "w") as f:
            f.write(p["copy"] + "\n\n" + p["hashtags"] + "\n")

        tipo_txt = {"carrusel": f"Carrusel de {len(archivos)} fotos",
                    "posteo": "Posteo de una foto",
                    "video": "Video de 6 segundos"}[p["tipo"]]
        with open(os.path.join(d, "LEEME.txt"), "w") as f:
            f.write(f"""PUBLICACIÓN {p['n']:02d} — {p['cuando']}
{p['titulo']}

QUÉ ES
{tipo_txt}.

QUÉ SUBIR, EN ESTE ORDEN
1. El posteo: {', '.join(archivos)}
   (subí las fotos en ese orden exacto, el carrusel cuenta una historia)
2. El pie de foto: abrí copy.txt, copiá todo y pegalo.
3. La historia: historia.jpg, subila el mismo día, un rato después del posteo.

POR QUÉ ESTA Y NO OTRA
{p['por_que']}
""")
        resumen.append({"n": p["n"], "cuando": p["cuando"], "titulo": p["titulo"],
                        "tipo": tipo_txt, "archivos": len(archivos)})

    json.dump(resumen, open(os.path.join(DEST, "orden.json"), "w"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"publicaciones": len(PUBS)}, ensure_ascii=False))
    return resumen


if __name__ == "__main__":
    main()
