# Aprendizajes del estudio

Este archivo es la memoria del equipo. Cada agente lo lee antes de trabajar
y el agente `jefe` lo actualiza al cierre del día.

Regla: solo entra acá lo que se probó y dio resultado (o falló claramente).
Nada de teoría.

## Lo que Martin corrigió (reglas para todo lo que se genere)

Cada crítica de Martin entra acá y se convierte en una regla. Vale para Luz,
Lupa, los scripts de 10-MOTOR y cualquier pedido a Higgsfield. Lupa frena lo
que no la cumple.

- **La foto es la protagonista** (26/10/2026). En cada posteo e historia, la
  fotografía de Martin manda: el texto va chico y al pie, con la estética de la
  web (negro, Anton, el punto rojo). Nada de medias pantallas negras con la
  foto chiquita. En el código: `pieza_foto()` en `10-MOTOR/motor_ads.py`.
- **No recortar mal** (26/10/2026). Si para llenar el cuadro hay que perder
  más del 22 % de la foto, se muestra entera, de lado a lado. Un brazo suelto o
  medio producto es una pieza fallida. Lo mismo para lo que se pida a
  Higgsfield: la foto de Martin se pone entera, nunca recortada para que entre.
- **Nunca inventar el lugar** (25 y 26/10/2026). Una foto de Palma de Mallorca
  salió con "Uruguay tiene lugares…". El texto solo nombra un lugar si está
  confirmado para ESA foto en `10-MOTOR/fotos.json`. Si hace falta el lugar y
  no está, se le pregunta a Martin antes. Casi toda la carpeta `naturaleza`
  son viajes (Mallorca, Estambul, Los Ángeles): no es Uruguay.
- **El tema manda la foto** (24 y 25/10/2026). Si el texto habla de carta,
  platos o comida, la foto muestra un plato o comida preparándose, no un
  kamado ni un fuego (`contenido` en `fotos.json`).
- **Carta = plato servido** (28/10/2026). Una pieza que habla de "sesión de
  carta" o de "tu carta" lleva un plato terminado (`contenido: plato`) o la
  carta misma, nunca gente preparando (un alfajor bañándose en chocolate no es
  una carta). En `campanas.py` se fija la foto con `_foto=` en la pieza.
- **El texto dice lo que muestra la foto** (24/10/2026). "Esta la saqué desde
  el piso" sobre una foto sacada de pie: no. Si no sabés cómo se sacó, no lo
  cuentes.
- **Sin "DESLIZÁ"** (26/10/2026). Ni flecha ni cartel de deslizar en los
  carruseles nuevos: Instagram ya muestra los puntitos.
- **Nunca una foto horizontal en un lienzo vertical** (28/10/2026). "No me
  gusta que pongas una foto horizontal en un canva vertical." Historias, reels
  (9:16) y posteos o carruseles 4:5 llevan solo fotos verticales, a pantalla
  completa. Nada de foto chica con fondo desenfocado, franjas ni marcos. Una
  foto horizontal va en un posteo horizontal o no va. Lupa lo frena.
- **Los textos, con la voz de Martin** (28/10/2026). "Los textos tampoco me
  convencen, yo no escribo así. Quiero vender, pero con mi manera." Antes de
  escribir un titular, un pie o una historia, Luz lee `09-ESTUDIO/VOZ_MARTIN.md`
  (cómo escribe él, con ejemplos suyos) y escribe así. Cada texto que Martin
  corrige desde el Centro entra ahí como ejemplo.
- **Aprobación en el Centro** (28/10/2026). Cada posteo e historia del
  calendario tiene ✓ y ✗. Si Martin marca ✗, antes de borrar nada se le
  pregunta si quiere mejorar algo puntual, reemplazarla por otra mejor o
  eliminarla, y Luz hace eso (orden del Centro).
- **OK fijo de Martin para subir /ig** (28/10/2026, en el chat: "si a el OK
  fijo"). Las piezas de Instagram nuevas o rehechas se pueden subir a
  apardianstudio.com/ig sin pedirle permiso cada vez: se actualiza la rama
  `hostinger` copiando SOLO la carpeta `ig/` (con `10-MOTOR/preparar_ig.sh`).
  El resto del sitio sigue necesitando su "publicá la web".
- **Sin marcas de clientes sin permiso** (28/10/2026). Martin pidió sacar la
  foto con el cartel de OdontoVita del carrusel de fin de año. Una foto donde
  se ve el nombre, el logo o el cartel de un cliente no va en el contenido
  salvo que Martin confirme que tiene permiso.
- **Nada de testimonios inventados.** Una cita con nombre de cliente solo si
  el cliente la dijo y Martin lo confirma.
- **A un animal no se le inventa lo que pensó** (28/10/2026, orden del Centro:
  "es una perra y no me gusta el titular"). Nada de "este no entendió nada":
  si no sabés si es macho o hembra, no lo digas, y no le pongas pensamientos
  ni chistes. El texto dice lo que se ve.
- **Texto que no tenga que ver con la foto, no va** (28/10/2026: "no tiene
  sentido el texto en esta foto, eso fue la feria del alfajor en el Latu").
  "El fondo blanco no es una pared blanca" sobre un alfajor partido en una
  feria: no. Si no sabés qué pasaba cuando se sacó, el texto describe la
  foto y nada más.
- **El motivo, al medio** (28/10/2026: "centrá la foto bien en el medio, el
  barco", "ajustar el centro de mesa", "que se vea la marca del aceite"). El
  barco, el centro de mesa, la etiqueta del producto quedan centrados y
  enteros en el cuadro; el recorte automático no alcanza. En el código:
  `encuadrar()` en `10-MOTOR/motor_ads.py` (con `ENCUADRE` en `historias.py`
  y `generar_ads.py`) y el foco `"foto.jpg#fx,fy"` en `mundo.py`.
- **Las fotos torcidas se enderezan** (28/10/2026: "enderezarla"). Si el
  horizonte, una viga o una columna están inclinados, se gira la foto lo
  justo antes de armar la pieza (`encuadrar(..., girar=)`), sin dejar
  esquinas vacías.
- **Montajes horizontales, posteo horizontal** (28/10/2026: "foto horizontal
  en formato vertical no"). Las escenas horizontales de "Tus fotos en el
  mundo" salen en su proporción (1080 de ancho, hasta 1,91:1), a sangre, sin
  fondo negro ni franjas (`pieza_horizontal()` en `mundo.py`).

## Qué funciona
- (vacío — se llena con la operación real)

## Qué no funciona
- (vacío)

## Preguntas abiertas
- ¿Qué canal trae más consultas: Instagram, boca a boca o el sitio?
- ¿A qué precio cierra edición en Lightroom por foto y por lote?
