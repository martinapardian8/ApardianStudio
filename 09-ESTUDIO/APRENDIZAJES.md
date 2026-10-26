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
- **El texto dice lo que muestra la foto** (24/10/2026). "Esta la saqué desde
  el piso" sobre una foto sacada de pie: no. Si no sabés cómo se sacó, no lo
  cuentes.
- **Sin "DESLIZÁ"** (26/10/2026). Ni flecha ni cartel de deslizar en los
  carruseles nuevos: Instagram ya muestra los puntitos.
- **Nada de testimonios inventados.** Una cita con nombre de cliente solo si
  el cliente la dijo y Martin lo confirma.

## Qué funciona
- (vacío — se llena con la operación real)

## Qué no funciona
- (vacío)

## Preguntas abiertas
- ¿Qué canal trae más consultas: Instagram, boca a boca o el sitio?
- ¿A qué precio cierra edición en Lightroom por foto y por lote?
