# -*- coding: utf-8 -*-
"""El plan de octubre a diciembre de 2026 en un PDF (06-NOTAS/PLAN_APARDIAN_oct-dic-2026.pdf).

Arma un HTML con el sistema de marca y lo imprime con Chromium. Lee el
calendario de 08-CONTENIDO-INSTAGRAM/calendario.json, asi que si cambia el
calendario alcanza con volver a correrlo.
"""
import os, json, asyncio, html
from playwright.async_api import async_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(RAIZ, "10-MOTOR", "fuentes")
IG = os.path.join(RAIZ, "08-CONTENIDO-INSTAGRAM")
OUT = os.path.join(RAIZ, "06-NOTAS", "PLAN_APARDIAN_oct-dic-2026.pdf")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
e = html.escape


def img(ruta):
    return "file://" + os.path.join(RAIZ, ruta)


def fecha(iso):
    return iso[8:10] + "/" + iso[5:7]


def main():
    cal = json.load(open(os.path.join(IG, "calendario.json")))
    filas = "".join(
        f"<tr><td class='n'>{s['n']}</td><td>{fecha(s['lunes'])}</td><td><b>{e(s['vertical'])}</b><br>"
        f"<span class='m'>{e(s['carrusel'])}</span></td><td>{e(s['venta'])}</td><td>{e(s['automatizacion'])}</td></tr>"
        for s in cal["semanas"])
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(file://{F}/Anton-Regular.ttf)}}
@font-face{{font-family:Work;src:url(file://{F}/WorkSans.ttf);font-weight:100 900}}
@page{{size:A4;margin:16mm 15mm}}
:root{{--h:#F8F7F6;--n:#171717;--r:#FF0033;--m:#6E6863;--l:rgba(23,23,23,.15)}}
body{{font-family:Work,sans-serif;color:var(--n);font-size:10.5pt;line-height:1.5;margin:0}}
h1,h2,h3{{font-family:Anton,sans-serif;font-weight:400;text-transform:uppercase;line-height:.95;margin:0}}
h1{{font-size:54pt}} h2{{font-size:26pt;margin:0 0 10pt}} h3{{font-size:14pt;margin:14pt 0 6pt}}
.eti{{font-size:7.5pt;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--r)}}
.sec{{page-break-before:always}}
.portada{{box-sizing:border-box;height:262mm;background:var(--n);color:var(--h);margin:-16mm -15mm 0;padding:26mm 18mm;display:flex;flex-direction:column;justify-content:space-between}}
.portada h1{{font-size:68pt}} .portada .logo{{font-family:Anton;font-size:30pt}} .portada .logo i{{color:var(--r);font-style:normal}}
.portada p{{font-size:13pt;max-width:120mm;color:#D9D6D2}}
p{{margin:0 0 7pt}} .m{{color:var(--m)}}
table{{width:100%;border-collapse:collapse;font-size:8.6pt;margin:6pt 0 10pt}}
th{{text-align:left;font-size:7pt;letter-spacing:.14em;text-transform:uppercase;color:var(--m);border-bottom:1.5pt solid var(--n);padding:4pt 5pt}}
td{{border-bottom:.5pt solid var(--l);padding:5pt;vertical-align:top}}
td.n{{font-family:Anton;font-size:12pt;color:var(--r);width:12mm}}
img.w{{max-width:100%;max-height:222mm;display:block;margin:6pt auto 4pt}}
ul{{margin:0 0 8pt;padding-left:14pt}} li{{margin:0 0 3pt}}
.caja{{border-left:3pt solid var(--r);padding:6pt 10pt;background:#F1EFEC;margin:8pt 0}}
.dos{{display:grid;grid-template-columns:1fr 1fr;gap:10mm}}
.check li{{list-style:none;margin-left:-14pt}} .check li:before{{content:"☐  ";color:var(--r)}}
</style></head><body>

<div class="portada">
  <div class="logo">APARDIAN<i>.</i></div>
  <div><span class="eti">Plan · 19 de octubre al 20 de diciembre de 2026</span>
  <h1>Contenido,<br>ventas y<br>automatización.</h1></div>
  <p>Lo que se armó el 19 de octubre para que APARDIAN STUDIO publique con constancia, responda rápido y salga a buscar clientes, sin depender del boca a boca.</p>
</div>

<div class="sec">
<span class="eti">01 · Resumen</span><h2>Qué cambió hoy</h2>
<table><tr><th>Área</th><th>Qué hay ahora</th><th>Dónde está</th></tr>
<tr><td><b>Contenido</b></td><td>9 carruseles continuos en estilo editorial, 9 reels que los recorren, 12 posteos "Tus fotos en el mundo" y 4 animaciones de fotos tuyas.</td><td>08-CONTENIDO-INSTAGRAM/06, 07 y 08</td></tr>
<tr><td><b>Calendario</b></td><td>9 semanas, un posteo y una historia todos los días (63 + 63), sin repetir foto en menos de 3 días, más el foco de venta y la automatización de cada semana.</td><td>CALENDARIO.md y la app Centro</td></tr>
<tr><td><b>App Centro</b></td><td>Calendario con tildes, carruseles con sus textos para copiar, clientes y guiones de venta. Se usa desde el celular.</td><td>claude.ai (página privada)</td></tr>
<tr><td><b>Equipo</b></td><td>Tres agentes: Luz (community manager), Lupa (crítica de diseño, con veto) y Trato (ventas), con una escalera de confianza.</td><td>09-ESTUDIO/EQUIPO.md</td></tr>
<tr><td><b>Prospección</b></td><td>6 flujos de n8n: buscar negocios, auditar su web, redactar el mail, aprobar, seguir y clasificar respuestas.</td><td>11-AUTOMATIZACION</td></tr>
<tr><td><b>Instagram</b></td><td>Calendario de aprobación: Lupa revisa, aprobás por Telegram y un agente publica a la hora pactada, posteos e historias.</td><td>11-AUTOMATIZACION/INSTAGRAM_APROBACION.md</td></tr>
<tr><td><b>Web</b></td><td>Servicios rediseñado, sección nueva de Música con el EP FUGAZ y seguridad endurecida. Publicada.</td><td>05-WEB y apardianstudio.com</td></tr>
</table>
<div class="caja"><b>Regla de la casa, reforzada hoy:</b> solo fotos tuyas. La IA pone escenas, materiales y movimiento, nunca reemplaza una foto ni inventa un "antes". Todo lo que simulaba un antes/después quedó en <i>_NO-PUBLICAR-antes-simulado</i>.</div>
</div>

<div class="sec">
<span class="eti">02 · Contenido</span><h2>Carruseles continuos</h2>
<p>Cada carrusel es una sola imagen larga cortada en seis láminas: las fotos y los títulos pasan de una a otra, y eso obliga a deslizar. Lunes a las 19:30, uno por semana, y el jueves su reel.</p>
<img class="w" src="{img('08-CONTENIDO-INSTAGRAM/06-carruseles-collage/00_TODOS.jpg')}">
</div>

<div class="sec">
<span class="eti">02 · Contenido</span><h2>Tus fotos en el mundo</h2>
<p>Doce escenas con un cartel en blanco (Manhattan, Grand Central, Shibuya, Londres, París, Los Ángeles, la Rambla…) donde se monta una foto tuya sin retocarla. Las escenas quedan como plantillas: cualquier foto nueva entra sin gastar créditos. Van los sábados y el pie siempre aclara que es un montaje.</p>
<img class="w" src="{img('08-CONTENIDO-INSTAGRAM/08-tus-fotos-en-el-mundo/00_TODOS.jpg')}">
</div>

<div class="sec">
<span class="eti">03 · Calendario</span><h2>Nueve semanas, una idea por semana</h2>
<p><b>Un posteo y una historia todos los días.</b> Lunes carrusel · jueves su reel · sábado "Tus fotos en el mundo" · martes, miércoles, viernes y domingo publicaciones armadas y piezas de la campaña · historias a las 12:30 · martes foco de venta · viernes seguimiento · domingo Luz arma la semana siguiente.</p>
<table><tr><th>Sem.</th><th>Lunes</th><th>Tema y carrusel</th><th>Venta</th><th>Automatización</th></tr>{filas}</table>
</div>

<div class="sec">
<span class="eti">04 · Equipo</span><h2>Luz, Lupa y Trato</h2>
<table><tr><th>Agente</th><th>Qué hace</th><th>Nunca</th></tr>
<tr><td><b>Luz</b> · community manager</td><td>Un posteo y una historia por día. Arma la semana el domingo, elige fotos, escribe pies, genera piezas nuevas con el motor.</td><td>Publicar sola. Fotos que no son tuyas.</td></tr>
<tr><td><b>Lupa</b> · crítica de diseño</td><td>Revisa todo antes de que te llegue: medidas, peso, pie, marca, fotos repetidas aunque estén recortadas. Tiene veto.</td><td>Dejar pasar algo "porque ya está hecho".</td></tr>
<tr><td><b>Trato</b> · ventas</td><td>Consultas, presupuestos, seguimientos, prospección y el reporte del lunes.</td><td>Escribirle a un cliente sin que lo veas.</td></tr></table>
<p><b>Escalera de confianza:</b> hoy aprobás todo por Telegram → 4 semanas sin rechazos de diseño: aprobás la semana de una vez → 8 semanas: las historias orgánicas salen solas → precios, clientes y lo nuevo pasan siempre por vos.</p>
<h3>Trato: cómo vende</h3>
<div class="dos"><div>
<h3>El embudo</h3>
<ul><li><b>Atención:</b> carrusel, reel, aviso o mail.</li><li><b>Interés:</b> perfil y web con WhatsApp a un toque.</li><li><b>Conversación:</b> respuesta en menos de 1 hora y 3 preguntas para calificar.</li><li><b>Presupuesto:</b> en 24 horas, en una página.</li><li><b>Cierre:</b> seguimiento a los 2 y 5 días.</li><li><b>Reseña y referido:</b> a los 3 días de entregar.</li></ul>
<h3>Rutina diaria · 30 minutos</h3>
<ul><li>0–10: responder todo.</li><li>10–15: pipeline, a quién le toca seguimiento.</li><li>15–25: 10 interacciones de verdad con cuentas objetivo.</li><li>25–30: 5 mensajes de prospección personalizados.</li></ul>
</div><div>
<h3>KPIs de cada semana</h3>
<ul><li>Consultas nuevas y de qué canal vienen.</li><li>Tiempo medio de respuesta (meta: menos de 1 h).</li><li>Respuestas a la prospección.</li><li>Presupuestos, cierres, tasa de cierre y ticket.</li><li>Reseñas nuevas.</li></ul>
<p class="m">Las metas se fijan después de 4 semanas de medir: no hay datos históricos y no se inventan.</p>
<h3>Guiones</h3>
<p>Primer contacto por rubro, bienvenida, "¿cuánto sale?", seguimientos y las cuatro objeciones típicas. Están en la app Centro, con botón para copiar.</p>
</div></div>
</div>

<div class="sec">
<span class="eti">05 · Automatización</span><h2>Qué automatizar primero</h2>
<table><tr><th>P</th><th>Idea</th><th>Por qué</th><th>Semana</th></tr>
<tr><td class="n">1</td><td><b>Respuesta rápida a consultas</b></td><td>Quien responde primero suele cerrar. Cuida la plata más cercana.</td><td>1</td></tr>
<tr><td class="n">2</td><td><b>Seguimiento de presupuestos</b></td><td>Recupera cierres que hoy se enfrían. Costo cero.</td><td>1</td></tr>
<tr><td class="n">3</td><td><b>Prospección + auditoría + mail</b></td><td>Flujo constante de clientes nuevos: restaurantes, marcas, salones, inmobiliarias.</td><td>2–3</td></tr>
<tr><td class="n">4</td><td><b>Fotógrafos para edición Lightroom</b></td><td>El servicio que más escala, en ES, EN y PT.</td><td>4</td></tr>
<tr><td class="n">5</td><td><b>Pedido de reseñas</b></td><td>Prueba social con nombre y apellido.</td><td>2</td></tr>
<tr><td class="n">6</td><td><b>Reactivación de clientes</b></td><td>Más de 80 proyectos entregados: el cliente más barato de volver a cerrar.</td><td>3</td></tr>
<tr><td class="n">7</td><td><b>Publicación con aprobación</b></td><td>Aprobás cada posteo por Telegram y n8n lo publica en Instagram a su hora.</td><td>2</td></tr>
<tr><td class="n">8</td><td><b>Reporte semanal</b></td><td>Saber qué canal trae consultas y dónde poner tiempo y plata.</td><td>4</td></tr>
</table>
<h3>Cómo funciona la prospección</h3>
<p>Prospector (Google Maps) → Auditor (mira la web y encuentra un problema con evidencia) → Redactor (mail corto, con clase) → <b>tu aprobación</b> → envío → seguimiento a los 4 y 9 días → clasificador de respuestas → planilla de clientes. Ningún mail sale sin que lo veas. Cumple la Ley 18.331: solo datos públicos de empresas, baja en un clic y máximo dos seguimientos.</p>
</div>

<div class="sec">
<span class="eti">06 · Web</span><h2>Lo nuevo de apardianstudio.com</h2>
<img class="w" src="{img('06-NOTAS/vista-previa/servicios_pc_reposo.jpg')}">
<p><b>Servicios</b> pasa a ser un índice editorial de 5 filas (Video, Fotografía, Lightroom, Páginas web y Música). Cada fila muestra trabajo real tuyo. <b>Música</b> es una sección nueva: composición, grabación, mix y mastering y videoclip, con el EP <b>FUGAZ</b> de Spotify y un fondo animado.</p>
<h3>Seguridad</h3>
<ul><li>No hay claves expuestas: el Agente IA no llama a ninguna IA.</li><li><b>Arreglado:</b> la carpeta /.git podía quedar a la vista desde el navegador.</li><li>Fuentes servidas desde el sitio, CSP más estricta, sin embebidos de terceros salvo Spotify, security.txt, robots y sitemap.</li></ul>
<p class="m">Todo esto está en vista previa: se activa cuando subas el build a la rama hostinger.</p>
</div>

<div class="sec">
<span class="eti">07 · Lo que falta</span><h2>Lo que solo podés hacer vos</h2>
<ul class="check">
<li>Confirmar que FUGAZ es el EP a mostrar, y pasar fotos tuyas en el piano si las tenés.</li>
<li>Instagram: cuenta profesional vinculada a una página de Facebook y app de Meta para la publicación con aprobación.</li>
<li>n8n: crear la cuenta y cargar credenciales (Anthropic, Google Places, Sheets, Gmail, Telegram).</li>
<li>Dominio de correo: SPF, DKIM y DMARC antes del primer mail en frío.</li>
<li>2FA en Hostinger, GitHub y Google; contraseñas únicas; repositorio privado.</li>
<li>Bajar de la app de Higgsfield las cuatro animaciones (fuego, bolas de espejos, velero y velas).</li>
<li>Opcional: agregar d8j0ntlcm91z4.cloudfront.net a los dominios permitidos de la sesión para bajar las generaciones directo.</li>
</ul>
<h3>Créditos de Higgsfield</h3>
<p>298,75 al empezar el día → 197,75 al cierre. Se gastó en plantillas que se reutilizan (papeles, mockups, 12 escenas), 4 animaciones de fotos tuyas y el fondo de la sección de música.</p>
</div>
</body></html>"""
    tmp = os.path.join(RAIZ, "06-NOTAS", "_plan.html")
    open(tmp, "w").write(doc)

    async def imprimir():
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path=CHROME)
            pg = await b.new_page()
            await pg.goto("file://" + tmp, wait_until="load")
            await pg.wait_for_timeout(500)
            await pg.pdf(path=OUT, format="A4", print_background=True, prefer_css_page_size=True)
            await b.close()
    asyncio.run(imprimir())
    os.remove(tmp)
    print(OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
