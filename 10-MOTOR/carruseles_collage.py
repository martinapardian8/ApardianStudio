# -*- coding: utf-8 -*-
"""Los carruseles collage: cada uno es un lienzo continuo cortado en laminas.

python3 10-MOTOR/carruseles_collage.py            # todos
python3 10-MOTOR/carruseles_collage.py bodas      # uno solo

Sale a 08-CONTENIDO-INSTAGRAM/06-carruseles-collage/<slug>/NN.jpg y un
_panorama.jpg para ver el carrusel entero de un vistazo.
"""
import sys, json, os
from collage import *

WA = "+598 91 962 962"
X = Lienzo.X


# =================================================================== 01 bodas
def bodas():
    L = Lienzo(6, "hueso", tinte=(242, 236, 229))
    # 1 · la mano sostiene la copia: la foto de la pareja en la rambla
    q = L.montar_en_copias("mano_foto.jpg", [F("bodas", "portfolio__IMG_8771.jpg")],
                           0, 0, LAM, ALTO)[0]
    L.etiqueta("Bodas · temporada 26/27", M, 74)
    L.titulo("Un sí dura un segundo.", M, 112, LAM - 2 * M, 104, max_lineas=2)
    L.texto("La foto, toda la vida.", M, 1010, 420, 38, NEGRO, "Medium")
    L.deslizar(0, y=ALTO - 96, claro=False)
    p0 = (q[1][0] - 40, q[1][1] + 34)

    # 2 · la ceremonia
    a = L.foto(F("bodas", "nw__IMG_9717.jpg"), X(1, .43), 400, 700, 470, rot=-3.5)
    L.papel(X(1, .25), 745, 440, 230, 4, "La ceremonia", k=2, px=58, sub="11:00 · iglesia")
    b = L.foto(F("bodas", "portfolio__IMG_9601.jpg"), X(1, .62), 1020, 610, 407, rot=2.5)
    L.cinta_en(b, .5, 0, 190, rot=-6, k=4)

    # 3 · el salon (cruza a la lamina 4)
    c = L.foto(F("bodas", "v__4.jpg"), X(2, .34), 560, 470, 640, rot=2)
    L.papel(X(2, .76), 330, 420, 230, -5, "El salón", k=1, px=62, sub="20:30 · la entrada")
    e = L.foto(F("salones", "golf-a__IMG_4684.jpg"), X(3, .0), 1050, 780, 440, rot=-2)
    L.cinta(X(3, .0) - 300, 1050 - 230, 170, 30, k=6)
    L.cinta(X(3, .0) + 320, 1050 - 240, 170, -24, k=7)

    # 4 · los detalles
    f = L.foto(F("bodas", "portfolio__IMG_9582.jpg"), X(3, .56), 420, 640, 427, rot=3)
    g = L.circulo(F("salones", "golf-b__IMG_0339.jpg"), X(3, .20), 560, 150)
    L.papel(X(3, .64), 830, 470, 250, -3, "Lo que\nnadie mira", k=3, px=52,
            sub="y después todos quieren")

    # 5 · la promesa
    x5 = X(4) + M
    L.etiqueta("Lo que incluye", x5, 150)
    L.titulo("Todas las fotos. Sin tope.", x5, 192, 880, 112, max_lineas=3)
    y = 560
    for n, t in (("01", "Ceremonia, salón y fiesta, de principio a fin."),
                 ("02", "Editadas una por una en Lightroom."),
                 ("03", "Entrega en 10 días como máximo.")):
        L.numero(n, x5, y, 64)
        L.texto(t, x5 + 110, y + 14, 700, 36, NEGRO, "Medium")
        y += 120
    h = L.foto(F("bodas", "nw__IMG_9726.jpg"), X(5, .02), 1060, 640, 427, rot=2.5)
    L.cinta_en(h, .5, 0, 180, rot=4, k=2)

    # 6 · el pedido
    x6 = X(5) + M
    L.etiqueta("Fechas de verano", x6, 150)
    L.titulo("Quedan pocas.", x6, 192, 880, 140, max_lineas=2)
    L.texto("Contame tu fecha y en el día te paso disponibilidad y presupuesto.",
            x6, 380, 760, 38, NEGRO, "Regular")
    L.etiqueta("Escribime por WhatsApp", x6 + 330, 560, NEGRO, 24)
    escribir(L.d, (x6 + 345, 600), WA, display(66), ROJO)
    L.firma(5, x=X(5, .66), y=ALTO - 150, escala=1.6)

    # el hilo: de la copia en la mano hasta el pedido
    pts = [p0, a.punto(.08, .06), a.punto(.93, .05), b.punto(.92, .08), c.punto(.5, .04),
           e.punto(.9, .06), f.punto(.1, .08), f.punto(.95, .92), (X(4, .12), 1110),
           h.punto(.92, .06), (x6 + 278, 588)]
    L.hilo(pts)
    for k, p in enumerate(pts):
        L.chinche(*p, k=k + 1)
    return L.guardar("01-bodas-un-si")


CAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capturas_web")


def cierre(L, i, kicker_t, titulo_t, texto_t, px=120, y_tel=None):
    """La ultima lamina: lo unico que pide algo. Devuelve donde clavar el hilo."""
    x = X(i) + M
    L.etiqueta(kicker_t, x, 150)
    alto = L.titulo(titulo_t, x, 192, LAM - 2 * M, px, max_lineas=3)
    y = 192 + alto + 40
    y += L.texto(texto_t, x, y, 800, 38, L.tinta, "Regular") + 70
    y = y_tel or y
    L.etiqueta("Escribime por WhatsApp", x + 110, y, L.tinta, 24)
    escribir(L.d, (x + 110, y + 40), WA, display(70), ROJO)
    L.firma(i, x=X(i, .66), y=ALTO - 150, escala=1.6)
    return (x + 50, y + 70)


def chinchar(L, pts, desde=1):
    L.hilo(pts)
    for k, p in enumerate(pts):
        L.chinche(*p, k=k + desde)


# =================================================================== 02 gastronomia
def gastronomia():
    L = Lienzo(6, "carbon")
    L.etiqueta("Gastronomía · antes del verano", M, 90)
    L.titulo("La gente come con los ojos.", M, 130, 900, 108, max_lineas=2)
    L.palabra_foto("Fuego", F("gastronomia", "nicol__IMG_5766.jpg"), M - 10, 420, 470)
    L.texto("Las 4 fotos que necesita tu carta.", M, 1010, 560, 40, HUESO, "Medium")
    L.deslizar(0)

    # 01 el plato
    a = L.foto(F("gastronomia", "sergio__IMG_7391.jpg"), X(1, .52), 640, 560, 760, rot=-2.5)
    L.papel(X(1, .24), 1130, 430, 230, 4, "01 · El plato", k=1, px=56, sub="lo que se pide")
    # 02 el proceso
    b = L.foto(F("gastronomia", "sergio__IMG_7377.jpg"), X(2, .30), 520, 470, 640, rot=3)
    c = L.foto(F("gastronomia", "sergio__IMG_7488.jpg"), X(2, .70), 830, 470, 640, rot=-3)
    L.papel(X(2, .26), 1110, 450, 230, -3, "02 · El proceso", k=2, px=56, sub="lo que da confianza")
    # 03 el lugar (cruza a la lamina 5)
    e = L.foto(F("gastronomia", "la-estacion__IMG_8063.jpg"), X(3, .55), 470, 840, 560, rot=2)
    f = L.foto(F("gastronomia", "ivanna-santiago__IMG_4815.jpg"), X(4, .02), 1020, 640, 380, rot=-2)
    L.papel(X(3, .28), 1020, 430, 230, 3, "03 · El lugar", k=3, px=58, sub="lo que hace volver")
    # 04 la gente
    g = L.foto(F("gastronomia", "nw__IMG_7064.jpg"), X(4, .62), 470, 470, 640, rot=-2)
    L.papel(X(4, .66), 1110, 430, 230, -4, "04 · La gente", k=1, px=58, sub="lo que te diferencia")

    fin = cierre(L, 5, "Una jornada en tu local", "Toda tu carta en un día.",
                 "No hace falta que cierres. Plato, proceso, lugar y gente. Entrega en 7 días.",
                 px=110)
    chinchar(L, [(X(0, .86), 300), a.punto(.9, .05), b.punto(.1, .05), c.punto(.9, .05),
                 e.punto(.1, .06), e.punto(.92, .06), g.punto(.5, .04), fin])
    return L.guardar("02-gastronomia-cuatro-fotos")


# =================================================================== 03 marca personal
def marca_personal():
    L = Lienzo(6, "hueso")
    L.etiqueta("Retrato · marca personal", M, 90)
    L.titulo("Tu marca personal no entra en una selfie.", M, 130, 620, 96, max_lineas=4)
    a = L.foto(F("retratos", "horacio__IMG_6071.jpg"), X(0, .70), 760, 470, 640, rot=3)
    L.texto("Una mañana de fotos. Cinco usos.", M, 1080, 520, 38, NEGRO, "Medium")
    L.deslizar(0, claro=False)

    b = L.foto(F("retratos", "horacio__IMG_6701.jpg"), X(1, .32), 560, 480, 650, rot=-3)
    L.papel(X(1, .30), 1110, 400, 220, 3, "Para tu web", k=1, px=58)
    c = L.foto(F("retratos", "horacio__IMG_6481.jpg"), X(1, .78), 760, 390, 530, rot=4)
    L.papel(X(1, .80), 1170, 400, 210, -4, "Para LinkedIn", k=2, px=54)

    d = L.foto(F("retratos", "horacio__IMG_6256.jpg"), X(2, .50), 600, 520, 700, rot=-2)
    L.papel(X(2, .52), 1140, 440, 220, 2, "Para el podcast", k=3, px=56)

    e = L.foto(F("retratos", "nw__IMG_6981.jpg"), X(3, .30), 600, 470, 640, rot=2.5)
    L.papel(X(3, .30), 1130, 420, 220, -3, "Para la prensa", k=1, px=56)
    f = L.foto(F("retratos", "horacio__IMG_6581.jpg"), X(3, .77), 760, 390, 530, rot=-3.5)
    L.papel(X(3, .78), 1170, 400, 210, 4, "Para tus redes", k=2, px=54)

    x4 = X(4) + M
    L.etiqueta("Cómo trabajo", x4, 150)
    L.titulo("Sin fondos de cartón.", x4, 192, 880, 112, max_lineas=2)
    y = 470
    for n, t in (("01", "Luz natural, tu ropa y tu lugar."),
                 ("02", "Te digo dos cosas y me callo. El resto lo hace la luz."),
                 ("03", "Todas las fotos que salgan bien, entrega en 10 días.")):
        L.numero(n, x4, y, 64)
        L.texto(t, x4 + 110, y + 14, 720, 36, NEGRO, "Medium")
        y += 130
    g = L.foto(F("retratos", "horacio__IMG_6614-2.jpg"), X(4, .55), 1060, 460, 306, rot=2)

    fin = cierre(L, 5, "Book o marca personal", "Te toca a vos.",
                 "Una mañana de fotos y tenés material para la web, las redes y la prensa.",
                 px=130)
    chinchar(L, [a.punto(.9, .04), b.punto(.1, .04), c.punto(.9, .05), d.punto(.5, .03),
                 e.punto(.1, .04), f.punto(.92, .05), f.punto(.95, .92), (X(4, .10), 1010),
                 g.punto(.08, .07), g.punto(.92, .07), fin])
    return L.guardar("03-marca-personal-cinco-usos")


# =================================================================== 04 fin de anio
def fin_de_anio():
    L = Lienzo(6, "carbon")
    L.montar_en_copias("fotos_negro_sueltas.jpg", [
        F("eventos", "leticia40__IMG_8126.jpg"), F("eventos", "la-condesa__IMG_3179.jpg"),
        F("eventos", "nw__IMG_9236.jpg"), F("eventos", "nicol__IMG_5832.jpg"),
        F("eventos", "leticia40__IMG_7766.jpg"), F("eventos", "nw__IMG_9199.jpg")],
        0, 0, LAM, ALTO, orden="lectura")
    L.etiqueta("Eventos · diciembre", M, 960, ROJO)
    L.titulo("La fiesta de fin de año pasa una vez.", M, 1000, LAM - 2 * M, 104,
             max_lineas=2, color=HUESO)
    L.deslizar(0, y=ALTO - 80)
    a = L.foto(F("salones", "la-condesa__IMG_3180.jpg"), X(1, .30), 380, 720, 480, rot=-3)
    L.papel(X(1, .72), 760, 420, 220, 4, "La pista", k=1, px=60, sub="23:40")
    b = L.foto(F("eventos", "leticia40__IMG_8208.jpg"), X(1, .48), 1060, 620, 413, rot=2)
    c = L.foto(F("eventos", "15-sol__IMG_8326.jpg"), X(2, .55), 470, 640, 427, rot=3)
    L.papel(X(2, .30), 880, 430, 220, -3, "Los abrazos", k=2, px=56, sub="01:15")
    e = L.foto(F("eventos", "caro60__IMG_0233.jpg"), X(3, .00), 1060, 640, 427, rot=-2)
    f = L.foto(F("eventos", "leticia40__IMG_8466.jpg"), X(3, .58), 420, 600, 400, rot=-3)
    L.papel(X(3, .72), 820, 420, 220, 3, "El final", k=3, px=60, sub="04:30")
    g = L.foto(F("eventos", "nicol__IMG_5857.jpg"), X(4, .40), 520, 600, 400, rot=3)
    x4 = X(4) + M
    L.texto("Que no quede solo en el grupo de WhatsApp con fotos borrosas.",
            x4, 900, 820, 44, HUESO, "Medium")

    fin = cierre(L, 5, "Empresas · cumpleaños · fin de año", "Diciembre se llena rápido.",
                 "Toda la fiesta, sin tope de fotos y galería para los invitados. Entrega en 10 días.",
                 px=104)
    chinchar(L, [(X(0, .93), 520), a.punto(.92, .05), b.punto(.9, .06), c.punto(.1, .06),
                 e.punto(.9, .05), f.punto(.1, .06), g.punto(.92, .06), fin])
    return L.guardar("04-fin-de-anio")


# =================================================================== 05 producto
def producto():
    L = Lienzo(6, "hueso")
    L.etiqueta("Fotografía de producto", M, 90)
    L.titulo("Un producto tiene una historia entera.", M, 130, 900, 100, max_lineas=3)
    a = L.foto(F("marcas", "v__83.jpg"), X(0, .60), 900, 640, 427, rot=-2.5)
    L.texto("Del olivo a la mesa, en cuatro capítulos.", M, 1200, 600, 34, NEGRO, "Medium")
    L.deslizar(0, claro=False)

    b = L.foto(F("marcas", "v__75.jpg"), X(1, .45), 420, 640, 427, rot=3)
    c = L.foto(F("marcas", "v__74.jpg"), X(1, .62), 900, 560, 373, rot=-2)
    L.papel(X(1, .22), 1180, 380, 210, -3, "01 · Origen", k=1, px=56)
    d = L.foto(F("marcas", "v__78.jpg"), X(2, .40), 470, 600, 400, rot=-3)
    L.papel(X(2, .34), 880, 400, 210, 3, "02 · Proceso", k=2, px=56)
    e = L.foto(F("marcas", "v__81.jpg"), X(3, .00), 1040, 620, 413, rot=2)
    f = L.foto(F("marcas", "v__82.jpg"), X(3, .55), 420, 600, 400, rot=3)
    L.papel(X(3, .66), 870, 420, 210, -3, "03 · Producto", k=3, px=56)
    g = L.foto(F("marcas", "v__80.jpg"), X(4, .45), 460, 620, 413, rot=-2)
    h = L.foto(F("marcas", "v__77.jpg"), X(4, .58), 950, 560, 373, rot=3)
    L.papel(X(4, .20), 1200, 360, 200, 4, "04 · Uso", k=1, px=56)

    fin = cierre(L, 5, "Marcas uruguayas", "No es solo el packshot.",
                 "Origen, proceso, producto y uso: el material completo para tu tienda, tu web y tus redes. Entrega en 5 días.",
                 px=110)
    chinchar(L, [a.punto(.92, .06), b.punto(.08, .06), c.punto(.92, .06), d.punto(.5, .04),
                 f.punto(.1, .06), e.punto(.92, .06), g.punto(.1, .06), h.punto(.92, .06), fin])
    return L.guardar("05-producto-del-olivo-a-la-mesa")


# =================================================================== 06 edicion
def edicion():
    L = Lienzo(6, "carbon")
    L.etiqueta("Para fotógrafos · edición en Lightroom", M, 90)
    L.titulo("Vos disparás. Yo edito.", M, 130, 900, 150, max_lineas=2)
    L.texto("Deslizá despacio: cada foto se arregla al pasar de una lámina a la otra.",
            M, 470, 460, 40, HUESO, "Medium")
    # cada copia esta rasgada justo en el corte de lamina
    a = L.antes_despues(F("naturaleza", "v__26.jpg"), X(1), 930, 900, 600, rot=0, k=3)
    b = L.antes_despues(F("salones", "golf-a__IMG_4658.jpg"), X(2), 430, 900, 600, rot=0, k=5)
    c = L.antes_despues(F("naturaleza", "v__63.jpg"), X(3), 930, 900, 600, rot=0, k=9)
    d = L.antes_despues(F("gastronomia", "sergio__IMG_7258.jpg"), X(4), 430, 900, 600, rot=0, k=11)
    L.papel(X(1, .28), 330, 420, 220, -3, "Culling", k=1, px=60, sub="elijo las que valen")
    L.papel(X(2, .28), 1050, 420, 220, 3, "Revelado", k=2, px=60, sub="con tu estilo")
    L.papel(X(3, .24), 330, 440, 220, -2, "Consistencia", k=3, px=50, sub="todo el lote igual")
    L.papel(X(4, .45), 1050, 420, 220, 2, "Exportado", k=1, px=56, sub="listo para entregar")

    fin = cierre(L, 5, "Desde cualquier país", "Tu lote en 72 horas.",
                 "Culling, revelado con tu preset y catálogo listo para exportar. Me decís cuántas fotos son y te paso precio en el día.",
                 px=118)
    chinchar(L, [(X(0, .62), 700), a.punto(.05, .03), a.punto(.95, .03), b.punto(.05, .04),
                 b.punto(.95, .04), c.punto(.05, .03), c.punto(.95, .03), d.punto(.05, .04),
                 d.punto(.95, .04), fin])
    return L.guardar("06-edicion-vos-disparas")


# =================================================================== 07 paginas web
def web():
    L = Lienzo(6, "hueso")
    qw = L.montar_en_copias("mano_celular.jpg", [os.path.join(CAP, "m_hero.png")],
                            0, 0, LAM, ALTO, sat=5, margen=1.0)[0]
    L.etiqueta("Páginas web", M, 74)
    L.titulo("Tu Instagram no es tu página web.", M, 112, LAM - 2 * M, 96, max_lineas=2)
    a = L.navegador(os.path.join(CAP, "d_hero.png"), X(1, .30), 960, 760, rot=-2)

    b = L.telefono(os.path.join(CAP, "m_galeria.png"), X(1, .72), 520, 820, rot=4)
    L.papel(X(1, .55), 1120, 440, 220, -3, "Anda en el celular", k=1, px=48)
    c = L.navegador(os.path.join(CAP, "d_galeria.png"), X(2, .52), 420, 900, rot=2)
    L.papel(X(2, .30), 900, 470, 230, 3, "Tu trabajo en grande", k=2, px=48,
            sub="no en un cuadradito")
    e = L.telefono(os.path.join(CAP, "m_contacto.png"), X(3, .05), 880, 760, rot=-4)
    L.papel(X(3, .55), 330, 470, 230, -2, "WhatsApp directo", k=3, px=50,
            sub="el cliente te escribe en un toque")
    f = L.navegador(os.path.join(CAP, "d_servicios.png"), X(3, .62), 980, 760, rot=-2)
    x4 = X(4) + M
    L.etiqueta("Lo que te llevás", x4, 150)
    L.titulo("Diseño propio. No plantilla.", x4, 192, 880, 108, max_lineas=3)
    y = 520
    for n, t in (("01", "Pensada para que te escriban, no solo para que te miren."),
                 ("02", "En español, inglés y portugués."),
                 ("03", "Un editor para cambiar textos y fotos sin llamarme.")):
        L.numero(n, x4, y, 64)
        L.texto(t, x4 + 110, y + 14, 720, 36, NEGRO, "Medium")
        y += 130
    g = L.telefono(os.path.join(CAP, "m_servicios.png"), X(4, .62), 1140, 520, rot=3)

    fin = cierre(L, 5, "Esta web la hice yo", "Te muestro cómo quedaría la tuya.",
                 "Escribime y en 24 horas te armo una propuesta con precio.",
                 px=104, y_tel=900)
    chinchar(L, [(qw[1][0] - 20, qw[1][1] + 30), a.punto(.06, .02), b.punto(.5, .02), c.punto(.95, .03), e.punto(.5, .02),
                 f.punto(.95, .03), (X(4, .20), 1000), g.punto(.5, .02), fin])
    return L.guardar("07-web-tu-instagram-no-es-tu-web")


# =================================================================== 08 cuadros
def cuadros():
    L = Lienzo(6, "hueso")
    L.etiqueta("Cuadros · para regalar", M, 90)
    L.titulo("Regalá un lugar.", M, 130, 900, 150, max_lineas=2)
    L.texto("Fotos de mi archivo, impresas y enmarcadas, listas para colgar.",
            M, 480, 620, 38, NEGRO, "Medium")
    L.deslizar(0, claro=False)
    # un tendedero rojo que cruza todo el carrusel: baja en la tapa para no
    # pisar el titulo y sube en el resto para que los cuadros respiren
    cuerda = [(-20, 790), (X(1, .15), 400), (X(2, .5), 430), (X(3, .5), 400),
              (X(4, .5), 430), (X(5, .3), 560)]
    L.hilo(cuerda, grosor=4, caida=0.03)
    L.chinche(*cuerda[-1], k=2)

    def altura(x):
        for (x0, y0), (x1, y1) in zip(cuerda, cuerda[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return cuerda[-1][1]

    cols = [
        (F("naturaleza", "nw__IMG_1996.jpg"), X(0, .64), 330, 440, -2),
        (F("naturaleza", "v__54.jpg"), X(1, .22), 330, 440, 3),
        (F("naturaleza", "v__26.jpg"), X(1, .78), 520, 346, -2),
        (F("naturaleza", "v__34.jpg"), X(2, .40), 340, 460, 2),
        (F("naturaleza", "v__59.jpg"), X(3, .05), 330, 440, -3),
        (F("naturaleza", "v__64.jpg"), X(3, .62), 520, 346, 2),
        (F("naturaleza", "nw__FullSizeRender_6.jpg"), X(4, .30), 320, 440, -2),
    ]
    for k, (ruta, cx, w, h, r) in enumerate(cols):
        top = altura(cx) + 20
        pz = L.marco(ruta, cx, top + (h + 120) // 2 + 14, w, h, rot=r, grosor=20, paspartu=40)
        x0, y0 = pz.punto(.5, 0)
        L.broche(x0, y0 - 6, 0, k=k + 1, tam=120)
    for (cx, t, k, rr) in ((X(1, .40), "Papel de archivo", 1, -3), (X(2, .62), "Marco de madera", 2, 3),
                           (X(3, .36), "Copia numerada", 3, -2), (X(4, .66), "Lista para colgar", 1, 2)):
        L.papel(cx, 1150, 420, 200, rr, t, k=k, px=46)
    cierre(L, 5, "Para Navidad", "Pedilo con tiempo.",
           "Elegís la foto, el tamaño y el marco, y te llega listo para colgar.",
           px=120, y_tel=760)
    return L.guardar("08-cuadros-regala-un-lugar")


# =================================================================== 09 musica
def musica():
    L = Lienzo(6, "carbon")
    qm = L.montar_en_copias("mano_foto_negro.jpg", [F("musica", "nw__IMG_7237.jpg")],
                            0, 0, LAM, ALTO)[0]
    L.etiqueta("Música · producción y video", M, 74)
    L.titulo("La música también la hago.", M, 112, LAM - 2 * M, 100, max_lineas=2, color=HUESO)
    L.texto("Pianista y productor. Trabajo en Ableton.", X(0, .42), 1110, 380, 36, HUESO, "Medium")
    L.deslizar(0, y=ALTO - 96)
    a = L.foto(F("musica", "nw__IMG_7233.jpg"), X(1, .14), 860, 560, 373, rot=-3)

    b = L.foto(F("musica", "la-estacion__IMG_8038.jpg"), X(1, .62), 420, 600, 400, rot=3)
    L.papel(X(1, .30), 820, 420, 220, -3, "Composición", k=1, px=56)
    c = L.foto(F("musica", "la-estacion__IMG_8044.jpg"), X(2, .40), 900, 640, 427, rot=-2)
    L.papel(X(2, .62), 330, 420, 220, 3, "Grabación", k=2, px=60)
    d = L.foto(F("musica", "la-estacion__IMG_8043.jpg"), X(3, .05), 430, 430, 580, rot=2)
    L.papel(X(3, .50), 860, 440, 220, -2, "Mix y mastering", k=3, px=50)
    e = L.foto(F("musica", "nw__IMG_7306.jpg"), X(4, .00), 1050, 640, 427, rot=3)
    f = L.foto(F("musica", "la-estacion__IMG_8091.jpg"), X(4, .55), 470, 470, 627, rot=-3)
    L.papel(X(4, .62), 1120, 400, 210, 3, "Videoclips", k=1, px=60)

    fin = cierre(L, 5, "Bandas · solistas · marcas", "Tu tema, de la idea al master.",
                 "Composición, grabación, mix, mastering y el videoclip para lanzarlo.",
                 px=104)
    chinchar(L, [(qm[1][0] - 36, qm[1][1] + 36), a.punto(.5, .05), b.punto(.92, .06), c.punto(.1, .06), d.punto(.5, .03),
                 e.punto(.92, .06), f.punto(.5, .03), fin])
    return L.guardar("09-musica-de-la-idea-al-master")


CARRUSELES = {"bodas": bodas, "gastronomia": gastronomia, "marca": marca_personal,
              "findeanio": fin_de_anio, "producto": producto, "edicion": edicion,
              "web": web, "cuadros": cuadros, "musica": musica}


def main(nombres):
    hechos = []
    for n in nombres or CARRUSELES:
        print("armando", n)
        hechos.append(CARRUSELES[n]())
    guardar_cache()
    print(json.dumps(hechos, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
