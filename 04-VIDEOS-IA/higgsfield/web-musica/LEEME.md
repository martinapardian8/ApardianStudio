# Fondo de la sección Música (web)

Ambiente, no portfolio: el portfolio musical es el EP de Spotify embebido.

| Archivo | Qué es | Modelo | Créditos |
|---|---|---|---|
| `piano_rojo.jpg` | Macro del interior de un piano con luz roja, tercio izquierdo negro para el texto | nano_banana_pro 2k 16:9 | 2 |
| `05-WEB/img/produccion/fondo_musica.mp4` / `.webm` | La misma imagen animada: polvo en la luz, la luz respira, un martillo avanza apenas | kling3_0 std, 5 s, sin sonido, primer y último cuadro iguales | 7,5 |

**Prompt de la imagen:** Extreme macro photograph inside a black grand piano: a row of felt hammers and taut steel strings receding diagonally into darkness, shallow depth of field, a single thin red rim light (#FF0033) grazing the strings from the right, the rest deep black and charcoal, faint dust particles floating in the light beam. Cinematic, minimal, high contrast, lots of negative black space on the left third. No people, no text, no logos.

**Prompt del video:** Locked-off macro shot inside a piano, almost still. Fine dust particles drift slowly through the thin red light beam, the red light gently pulses brighter and dimmer like a slow breath, the strings shimmer faintly as if a note just faded. No hammer movement, no camera shake, no people. Slow, hypnotic, seamless loop, ends exactly where it starts.

**Cómo se armó el loop:** la red de la sesión no llega al CDN de Higgsfield, así que
los cuadros pasaron como hojas de 2×2 desde el sandbox. Se usaron los primeros 64
cuadros (2,7 s) en ida y vuelta: 126 cuadros a 24 fps, 5,25 s, sin corte al repetir.
960×536, H.264 (~410 KB) y VP9 (~410 KB). Con `prefers-reduced-motion` se ve solo la foto.
