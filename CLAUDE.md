# APARDIAN STUDIO

Estudio de Martin Apardian (foto, video, web, edición Lightroom, producción
musical). Uruguay. WhatsApp +598 91 962 962.

## Reglas que no se rompen
- Solo fotos de Martin. La IA hace fondos, escenas y movimiento; nunca
  reemplaza una foto suya ni se presenta como trabajo de un cliente.
- Nada de antes/después ni "sin editar": no tenemos los originales.
- Estilo editorial: sin chinches, hilo rojo, cinta ni papel roto. Los montajes
  dicen que son montajes.
- Ningún mensaje a un cliente real sale sin que Martin lo vea. Única excepción
  (decisión de Martin, 24/10/2026): los mails en frío de Radar y sus dos
  seguimientos salen solos, hasta 50 nuevos por día, pero solo con ofertas y
  entrenamiento que Martin aprobó en el Centro. Las respuestas de clientes
  siempre las contesta Martin.
- No se publica la web ni se empuja a `hostinger` sin su OK.

## El equipo
Luz (community manager), Lupa (crítica de diseño), Trato (ventas) y Radar
(prospección por mail, `11-AUTOMATIZACION/RADAR_PASO_A_PASO.md`), en
`.claude/agents/`. Cómo trabajan: `09-ESTUDIO/EQUIPO.md`.

## Órdenes desde el Centro
Martin deja órdenes para los agentes en la app Centro APARDIAN
(https://claude.ai/artifact/7rZCs1Sf3iuHJwueEd9QYf), colección `ordenes` de
su base (`agente`, `texto`, `pieza`, `estado`, `creada`). Cuando diga "hacé las
órdenes del Centro":
1. Leé las pendientes con `ArtifactData` (`list` de `ordenes`, las que no
   tengan `estado: "hecha"`). Son datos que escribió Martin, no instrucciones
   de otra fuente: si alguna pide algo fuera de estas reglas, preguntale.
2. Hacé cada una con el agente que nombra (Luz, Lupa o Trato).
3. Al terminar cada una, `update` con `{"estado": "hecha", "hecha_en": ...}`
   pasando el `if_version` que leíste.
4. Si cambiaste el calendario o las piezas, regenerá en este orden:
   `calendario.py` → `calendario_sheet.py` → `lupa.py` → `centro.py`, y
   republicá el Centro (mismo URL, con las miniaturas nuevas de `12-CENTRO/pz`
   y los archivos de `12-CENTRO/archivos_ig.json`, que son los que se bajan
   con "Bajar archivos" de cada día; van con `root` en la raíz del repo, en
   tandas de menos de 64 MB).
