# El equipo de APARDIAN STUDIO

Tres agentes que mantienen vivo el Instagram y lo convierten en trabajo. Viven
en `.claude/agents/` y se llaman por el nombre ("Luz, armá la semana que viene",
"Lupa, revisá esto", "Trato, ¿a quién le toca seguimiento hoy?").

| | Quién | Qué hace | Qué no hace nunca |
|---|---|---|---|
| ☀️ | **Luz** · community manager | Un posteo y una historia por día, los siete días. Arma la semana, elige fotos, escribe pies, genera piezas nuevas con el motor cuando se acaba lo armado. | Publicar sola. Usar fotos que no son tuyas. Antes/después. |
| 🔍 | **Lupa** · crítica de diseño | Revisa cada pieza antes de que llegue a vos: medidas, peso, pie, reglas de marca y, mirándola, si está a la altura. Detecta la misma foto repetida aunque esté recortada o con texto. **Tiene veto.** | Dejar pasar algo "porque ya está hecho". Rehacer piezas (eso es de Luz). |
| 🤝 | **Trato** · ventas | Convierte consultas en presupuestos y presupuestos en trabajos. Seguimientos, prospección, pipeline, reporte semanal. Le cuenta a Luz qué pregunta la gente. | Mandarle algo a un cliente sin que vos lo veas. Inventar precios. |

Vos sos el cuarto: **aprobás**. Sin tu "Aprobar" en Telegram no sale nada.

## Cómo sale un posteo

```
 Luz arma la semana ──▶ Lupa revisa ──▶ frenado ──▶ vuelve a Luz
   (domingo 18:00)         │
                           ▼ ok
              Telegram, 10:00 del día anterior:
              imagen + pie + nota de Lupa
                           │
               Aprobar ────┴──── No publicar
                  │                   │
                  ▼                   ▼
      el flujo 08 lo publica     no sale nunca
      a la hora del calendario
                  │
                  ▼
      Te avisa con el link. Trato atiende lo que llegue.
```

## El ritmo (del 19/10 al 20/12/2026, y después sigue Luz)

**Todos los días, un posteo de feed y una historia.** Son 63 posteos y 63
historias en el calendario, que se publican solos después de tu aprobación.

| Día | Feed | Historia (12:30) | Además |
|---|---|---|---|
| Lunes | Carrusel collage, 19:30 | Orgánica | Compartís el carrusel en historias a mano, con el link a WhatsApp (20:00) |
| Martes | Pieza de la campaña de la semana, 13:00 | De campaña, con CTA | Trato: foco de venta |
| Miércoles | Publicación ya armada o de campaña, 19:30 | Orgánica | |
| Jueves | Reel del carrusel, 19:30 | Orgánica | Una automatización nueva |
| Viernes | Publicación ya armada o de campaña, 19:30 | De campaña, con CTA | Trato: seguimiento de presupuestos |
| Sábado | Tus fotos en el mundo, 11:00 | Orgánica | |
| Domingo | Pieza de campaña, 11:00 | Orgánica | Luz arma la semana siguiente y Lupa la revisa |

Algunas historias van **a mano** porque la API de Instagram no pone stickers:
la del lunes con el link y las de pregunta (llevan la encuesta encima de los
botones dibujados). Figuran en el calendario como *Historia (a mano)* y son
extra: la historia automática de ese día sale igual.

## Lo que Lupa revisa sola (cada vez que se arma la planilla)

- Que el archivo exista y no venga de una carpeta que no se publica.
- Medidas: feed de 4:5 a 1,91:1; historias 9:16; reels de 3 s a 15 min.
- Peso: fotos de menos de 8 MB; videos dentro del límite.
- Carruseles de 2 a 10 hojas, todas del mismo tamaño.
- Pie de menos de 2.200 caracteres, como mucho 30 hashtags (ideal 3 a 5) y
  que lleve a WhatsApp.
- Los montajes dicen que son montajes.
- Nada de antes/después ni "sin editar".
- **La misma foto no sale dos veces en menos de 3 días**, en feed o en
  historia, aunque esté recortada, más chica o con texto encima. El calendario
  ya se arma esquivando esas repeticiones.

Y con los ojos, la semana entera de una (`06-NOTAS/lupa/semana-AAAA-MM-DD.jpg`):
si son de tus mejores fotos, si se lee en el celular, si la grilla se ve pareja,
si parece APARDIAN y no una plantilla.

## Desde la app Centro

En la pestaña **Agentes** de la app hablás con cada uno: le pedís un pie a
Luz, le mandás una foto a Lupa para que la critique, le pegás una consulta a
Trato para que te arme la respuesta. Ya conocen tus reglas, la semana y tus
clientes. Responden borradores; no publican ni mandan nada.

Lo que necesita tocar archivos (armar piezas nuevas, cambiar el calendario)
lo dejás como **orden**. En la próxima sesión de Claude Code decís "hacé las
órdenes del Centro" y se ejecutan; en la app quedan tachadas.

En **Semana** ves cada pieza con su pie y lo que dijo Lupa, y desde ahí le
pedís un cambio a Luz o una segunda opinión a Lupa.

## La escalera de confianza

Confiar no es un salto: se gana con semanas que salen bien. Cuatro escalones.

1. **Ahora: aprobás todo.** Cada pieza te llega a Telegram un día antes. Lupa
   ya filtró lo técnico y lo que rompe la marca, así que lo que ves debería
   estar bien; si no, lo rechazás y queda anotado.
2. **Después de 4 semanas seguidas sin rechazar nada por diseño:** aprobás la
   semana de una vez, el domingo, mirando la hoja de contacto de Lupa.
3. **Después de 8 semanas así:** las historias orgánicas salen sin tu
   aprobación (siguen pasando por Lupa). Vos aprobás solo el feed. Es un
   cambio chico en el flujo 07 que se hace cuando llegues a este escalón, no
   antes.
4. **Nunca automático:** lo que habla de precios, lo que nombra a un cliente,
   lo que es nuevo (un formato o un servicio que no salió antes) y cualquier
   mensaje a un cliente real. Eso siempre pasa por vos.

Cada rechazo tuyo es información: Luz anota en `APRENDIZAJES.md` por qué lo
rechazaste, y Lupa suma esa regla a lo que revisa. Si en una semana rechazás
dos piezas por lo mismo, se vuelve un escalón para atrás.

## Archivos

| Archivo | Qué es |
|---|---|
| `.claude/agents/luz-community-manager.md` | Luz |
| `.claude/agents/lupa-critica-diseno.md` | Lupa |
| `.claude/agents/trato-ventas.md` | Trato (playbook en `CM_VENTAS.md`) |
| `10-MOTOR/calendario.py` | El calendario: un posteo y una historia por día, sin fotos repetidas |
| `10-MOTOR/calendario_sheet.py` | La planilla de aprobación (con la revisión de Lupa) |
| `10-MOTOR/lupa.py` | La revisión automática y la hoja de contacto de la semana |
| `06-NOTAS/lupa/REVISION.md` | Lo último que frenó o marcó Lupa |
| `11-AUTOMATIZACION/INSTAGRAM_APROBACION.md` | Cómo se conecta Instagram (una sola vez) |
