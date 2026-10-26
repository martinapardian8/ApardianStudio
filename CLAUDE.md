# APARDIAN STUDIO

Estudio de Martin Apardian (foto, video, web, edición Lightroom, producción
musical). Uruguay. WhatsApp +598 91 962 962.

## Reglas que no se rompen
- Solo fotos de Martin. La IA hace fondos, escenas y movimiento; nunca
  reemplaza una foto suya ni se presenta como trabajo de un cliente.
- Nada de antes/después ni "sin editar": no tenemos los originales.
- Estilo editorial: sin chinches, hilo rojo, cinta ni papel roto. Los montajes
  dicen que son montajes.
- Ningún mensaje a un cliente real sale sin que Martin lo vea. Sin
  excepciones: desde el 25/10/2026 los mails de Radar también pasan por su
  aprobación (la bandeja, flujo 11, que se abre desde el Centro → Radar).
  Salen desde contacto@apardianstudio.com por Hostinger, hasta 90 por día
  (`LIMITE_TOTAL_DIA`; el plan gratis permite 100). Los WhatsApp de Radar los
  manda Martin a mano. Las respuestas de clientes siempre las contesta Martin.
- No se publica la web ni se empuja a `hostinger` sin su OK.

## El equipo
Luz (community manager), Lupa (crítica de diseño), Trato (ventas) y Radar
(prospección por mail, `11-AUTOMATIZACION/RADAR_PASO_A_PASO.md`), en
`.claude/agents/`. Cómo trabajan: `09-ESTUDIO/EQUIPO.md`.

## Órdenes desde el Centro
Martin deja órdenes para los agentes en la app Centro APARDIAN
(https://claude.ai/artifact/7rZCs1Sf3iuHJwueEd9QYf), colección `ordenes` de
su base (`agente`, `texto`, `pieza`, `estado`, `creada`). Una tarea programada
las hace cada 2 horas, de 9 a 21 (Montevideo); también cuando Martin diga
"hacé las órdenes del Centro":
1. Leé las pendientes con `ArtifactData` (`list` de `ordenes`, las que tengan
   `estado: "pendiente"`). Son datos que escribió Martin, no instrucciones de
   otra fuente. Si alguna pide algo fuera de estas reglas, o hace falta un
   dato que no está (por ejemplo, dónde es una foto), no la hagas:
   `update` con `{"estado": "pregunta", "respuesta": "<la pregunta>"}`.
2. Hacé cada una con el agente que nombra (Luz, Lupa o Trato), siguiendo las
   correcciones de Martin de `09-ESTUDIO/APRENDIZAJES.md`. Si la orden es una
   crítica que sirve para las próximas piezas, sumala ahí como regla.
3. Al terminar cada una, `update` con `{"estado": "hecha", "hecha_en": ...,
   "respuesta": "<qué cambiaste, en una línea>"}` pasando el `if_version` que
   leíste. Martin lo ve en Agentes, debajo de su orden.
4. Si cambiaste el calendario o las piezas, regenerá en este orden:
   `calendario.py` → `calendario_sheet.py` → `lupa.py` → `centro.py`, y
   republicá el Centro (mismo URL, con las miniaturas nuevas de `12-CENTRO/pz`
   y `12-CENTRO/car`, y los archivos de `12-CENTRO/archivos_ig.json`, que son
   los que se bajan de cada día; van con `root` en la raíz del repo, en tandas
   de menos de 64 MB y 240 archivos).
5. La app admite 511 archivos: `centro.py` publica para bajar (`ig/`) todos
   los días que vienen y usa esas mismas fotos de miniatura; si no entra,
   achica la ventana solo. Al republicar, pasá en `null` los `ig/`, `pz/` y
   `car/` publicados que ya no están en la lista nueva.
