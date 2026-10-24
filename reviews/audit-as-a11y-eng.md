# Auditoría de accesibilidad: Almanac Azimuth

**Perspectiva**: Ingeniería de accesibilidad
**Fecha**: 2026-10-17
**Plan**: `almanac-azimuth/page.html` (y su versión completa, `almanac-azimuth/index.html`)

## Resumen
Landing de un rooftop. El fondo (cielo, sol, luna y techos) se dibuja en un canvas fijo que cambia con el scroll. El texto de cada sección tiene un color fijo, claro u oscuro. El riesgo principal es que el fondo es continuo y el color del texto no lo es: en las transiciones el texto queda sobre un fondo que no le corresponde. También revisé la carta interactiva y el formulario de reserva.

**Método.** Leí el código y medí el contraste con Playwright. Recorrí la página entera en pasos de 20% del alto de pantalla, a 1440px y a 390px, con `prefers-reduced-motion` activado para que el cielo quede quieto en cada paso. Para cada texto visible tomé el color real de fondo: el gradiente del cielo más el píxel del canvas debajo (techos, ventanas, sol). Con eso calculé la relación de contraste WCAG, teniendo en cuenta la opacidad del texto.

## Archivos revisados
| Archivo | Rol de accesibilidad | Riesgo |
|------|----------|------|
| `almanac-azimuth/page.html` | Página completa: navegación, carta (botones de selección), formulario de reserva, escena decorativa | Alto (contraste dinámico) |
| `almanac-azimuth/index.html` | Misma página con `<html lang="es-UY">` | Igual, salvo el idioma |

## Veredicto: APROBAR CON CAMBIOS

La estructura es sólida: landmarks, encabezados, `fieldset`/`legend`, radios nativos, `<label for>`, `autocomplete`, la escena con `aria-hidden` y `prefers-reduced-motion` respetado. Lo que falla son problemas concretos y acotados. Se arreglan con CSS y unas pocas líneas de script, sin rehacer nada.

## Problemas críticos (hay que corregir)
| # | Problema | Criterio WCAG | Archivo(s) | Impacto | Corrección |
|---|-------|---------------|---------|--------|-----|
| 1 | **El texto pierde contraste en las transiciones entre capítulos.** El cielo depende del centro de la pantalla, pero el color del texto es fijo por sección. En los cambios, el texto oscuro queda sobre cielo oscuro y el claro sobre cielo claro. Medido: «Una carta para la hora azul.» en marfil sobre cielo rosado da **1.65:1**. «Seis tragos pensados…» da **2.32:1**. Los precios de la carta dan **2.14:1**. «Cerramos / A la 1:00…» da **3.29:1**. 35 textos fallan en escritorio y 27 en celular. | 1.4.3 Contraste (mínimo) | `page.html`: `target()`, `SKY_*`, `.tone-light` / `.tone-dark` | Cualquier lector con baja visión, o con el sol de frente en el celular, pierde el texto mientras scrollea. | (a) Que el cielo cambie solo **entre** secciones: reemplazar el tramo lineal de `target()` por `i + smooth(clamp((t - .3) / .4))`, así queda quieto mientras el texto está en pantalla. (b) Agregar un halo del color del tono: en `.tone-light`, un `text-shadow` crema; en `.tone-dark`, uno con `--noche` en dos capas (2px y 18px). |
| 2 | **Texto sobre los techos y sobre las ventanas encendidas.** Mientras la ciudad baja en el primer scroll, el texto oscuro de «La terraza» pasa sobre techos marrones: **1.58–1.76:1**. En celular, el h2 «Siete pisos…» da **1.26:1**. De noche, el texto claro del formulario pasa sobre ventanas ámbar: «sol 19:05» da **1.51:1** y la leyenda «Día», **1.72:1**. | 1.4.3 | `page.html`: `SINK`, dibujo de `windows` | En celular la sección de la terraza es ilegible durante el primer gesto de scroll. | Bajar la ciudad del hero en función del scroll directo, sin la inercia: `sink = max(num(SINK,f), smooth(clamp(scrollY / (cityH * .7))))` mientras `f < 2.5`. Así se va antes de que llegue el texto. Bajar las ventanas a `rgb(255 190 110 / .45)`; con eso el texto marfil queda en ≥ 4.5:1 encima de ellas. |
| 3 | **El indicador de foco no se ve en las secciones claras.** El `outline` usa `--bronce-claro` (#D2B07A) sobre el cielo dorado (#F7E4C6): **1.67:1**. | 1.4.11 Contraste de elementos no textuales y 2.4.7 Foco visible | `page.html`: `:focus-visible` | Quien navega con teclado no ve dónde está en el hero ni en la terraza. | Usar color de foco según el tono: `.tone-light :focus-visible, .nav[data-tone=light] :focus-visible { outline-color: var(--tinta) }` y bronce claro solo en los tonos oscuros. |
| 4 | **La confirmación de la reserva no se anuncia.** `#confirm` tiene `role="status"`, pero empieza con `hidden` y se muestra y se llena en el mismo paso. Varios lectores de pantalla ignoran una región en vivo que recién aparece. | 4.1.3 Mensajes de estado | `page.html`: `#confirm` y el handler `submit` | Quien usa lector de pantalla manda la reserva y no escucha nada. | Dejar la región siempre en el DOM (vacía, sin `hidden`) y solo cambiarle el contenido. O, además, mover el foco a la confirmación con `tabindex="-1"` y `focus()`. |
| 5 | **La página publicada no declara el idioma.** `page.html` no tiene `lang`, porque el esqueleto del Artifact lo pone el host. `index.html` sí lo tiene. | 3.1.1 Idioma de la página (nivel A) | `page.html` | El lector puede leer el texto en español con voz en inglés. | Al principio del script: `document.documentElement.lang = "es-UY";` |

## Recomendaciones
| # | Problema | Criterio WCAG | Corrección |
|---|-------|---------------|-----|
| 6 | El nav fijo (~80px) tapa lo que recibe foco cuando se tabula hacia arriba, y los anclas (`#carta`, `#reservar`) dejan el título debajo del nav. | 2.4.11 Foco no oculto (AA, WCAG 2.2) | `html { scroll-padding-top: 6rem }` |
| 7 | Los placeholders («Como figura en la reserva», «099 123 456») dan **2.96–3.45:1**. | 1.4.3 | `::placeholder { color: var(--marmol); opacity: .7 }` (≈ 7:1 sobre la noche) |
| 8 | Errores del formulario: el mensaje sale por `role="alert"` (bien), pero el campo no queda marcado. | 3.3.1 Identificación de errores y 1.3.1 | En el campo con error: `aria-invalid="true"` y `aria-describedby="form-error"`; sacarlos cuando se corrige. |
| 9 | Nombre y WhatsApp son obligatorios, pero no se indica hasta que falla el envío. | 3.3.2 Etiquetas o instrucciones | `required` + `aria-required="true"`, y en la etiqueta: «Nombre (obligatorio)». |
| 10 | Los botones de la carta usan `aria-pressed`, que se lee como interruptor («botón de alternancia, presionado»). En realidad es una selección única. | 4.1.2 Nombre, función, valor | Opción 1: `role="radiogroup"` con `role="radio"` y `aria-checked`, flechas para moverse y tabindex rotativo. Opción 2, mínima: dejar `aria-pressed` y darle a la lista `aria-label="Elegí un cocktail para verlo servido"`. |
| 11 | El nombre accesible de cada trago lee el precio sin moneda: «Azimut 590 Gin…». | 1.3.1 | Envolver el precio: `<span class="d-price"><span class="sr-only">Precio: </span>590<span class="sr-only"> pesos</span></span>` |
| 12 | Los `h3` del footer («Dónde», «Cuándo», «Hoy») quedan, para el lector, como subtítulos de «Pedí tu mesa.». | 1.3.1 | Pasarlos a `h2` con el mismo estilo, o agregar un `<h2 class="sr-only">Información</h2>` al principio del footer. |
| 13 | El SVG de la copa se nombra solo con el trago; el tipo de copa queda afuera. | 1.1.1 Contenido no textual | `aria-labelledby="glass-name glass-cap"` |
| 14 | Al cambiar de día, el horario «Al atardecer» cambia sin aviso. | 4.1.3 | Agregar una línea `aria-live="polite"`: «El sábado 24 el sol se pone a las 19:06». |

## Mejoras opcionales
| # | Sugerencia | Por qué |
|---|------------|-----------|
| 15 | Link «Saltar al contenido» al principio | El nav tiene solo cinco paradas, así que no es obligatorio, pero es una cortesía barata. |
| 16 | Con `prefers-contrast: more`, poner un velo sólido detrás de cada sección | Garantiza el contraste para quien lo pide, sin cambiar la escena para el resto. |
| 17 | Con `prefers-reduced-motion`, pausar también el grano (`.grain`) | Hoy ya se apaga; anotarlo como regla para cambios futuros. No titila: cambia unas 4,5 veces por segundo con opacidad .10, muy lejos del umbral de destellos de 2.3.1. |

## Recorrido con teclado
| Paso | Acción | Foco esperado | Anuncio esperado | ¿Lo resuelve? |
|------|--------|---------------|----------------------|---------------|
| 1 | Tab | «Almanac Azimuth» (logo) | «Almanac Azimuth, enlace» | Sí. El foco no se ve sobre el cielo claro (#3) |
| 2 | Tab ×3 | La terraza → La carta → Las noches | «La terraza, enlace, navegación Secciones» | Sí. Mismo problema de foco (#3) |
| 3 | Tab | Reservar (nav) | «Reservar, enlace» | Sí |
| 4 | Enter | Salta a `#reservar` | Título «Pedí tu mesa.» | Parcial: el título queda debajo del nav (#6) |
| 5 | Tab (desde el principio, en el hero) | Reservar mesa → Ver la carta | «Reservar mesa, enlace» | Sí. Foco poco visible (#3) |
| 6 | Tab | Primer trago | «Azimut 590 Gin…, botón de alternancia, presionado» | Parcial: la función y el precio se entienden mal (#10, #11) |
| 7 | Tab ×5 | Cada trago; la copa se sirve al recibir foco | «Hora azul…, botón de alternancia, presionado» | Sí, el cambio se entiende por el estado |
| 8 | Tab | Grupo «Día», radio seleccionado | «Día, grupo. Hoy sol 19:00, radio, seleccionado, 1 de 6» | Sí (radios nativos) |
| 9 | Flechas | Otro día; los horarios se regeneran | «Mañana sol 19:01, radio, seleccionado» | Sí. El cambio de horario no se anuncia (#14) |
| 10 | Tab | Grupo «Hora» | «Hora, grupo. Al atardecer 18:30, radio…» | Sí |
| 11 | Tab ×2 | Personas, Dónde (`select`) | «Personas, cuadro combinado, 2» | Sí |
| 12 | Tab ×2 | Nombre, WhatsApp | «Nombre, editar texto» | Parcial: no se dice que son obligatorios (#9) |
| 13 | Tab, Enter con Nombre vacío | Vuelve a Nombre | «Escribí el nombre para la reserva.» (alerta) | Sí. El campo no queda marcado como inválido (#8) |
| 14 | Enter con todo completo | Se queda en el botón | «Mesa pedida…» | **No.** La región en vivo recién mostrada puede no anunciarse (#4) |

Ningún elemento atrapa el foco. No hay modales. El canvas y el reloj del nav están fuera del árbol de accesibilidad (`aria-hidden`).

## Checklist ARIA
| Elemento | Función | Nombre | Estados | Teclado | Notas |
|---------|------|-------|--------|----------|-------|
| `header.nav` | banner | n/a | n/a | n/a | Bien |
| `nav.links` | navigation | «Secciones» | n/a | Tab | Bien |
| `.dial` | (oculto) | n/a | n/a | n/a | Decorativo, `aria-hidden` |
| `.scene` | (oculto) | n/a | n/a | n/a | Decorativo, `aria-hidden` |
| `h1` / `h2` | heading | texto | n/a | n/a | Orden correcto; los `h3` del footer quedan mal anidados (#12) |
| `.drink` | button | nombre + precio + ingredientes | `aria-pressed` | Tab, Enter, Espacio | Debería ser radiogroup (#10); falta la moneda (#11) |
| `svg.glass` | img | `#glass-name` | n/a | n/a | Sumar `#glass-cap` (#13) |
| `.facts` | `dl` | n/a | n/a | n/a | Bien |
| `.program` | list | n/a | n/a | n/a | Bien |
| `fieldset` Día / Hora | group | legend | radios nativos | Flechas | Bien |
| `select` Personas / Dónde | combobox | `<label for>` | n/a | Nativo | Bien |
| `input` Nombre / WhatsApp | textbox | `<label for>` | falta `aria-invalid` y `aria-required` | Nativo | #8, #9 |
| `#form-error` | alert | n/a | n/a | n/a | Bien, ya está en el DOM antes de usarse |
| `#confirm` | status | n/a | empieza `hidden` | n/a | No se anuncia de forma confiable (#4) |

## Detalle del veredicto
- Compatibilidad con lector de pantalla: **CON OBSERVACIONES** (idioma #5, confirmación #4)
- Navegación con teclado: **APROBADA**
- Manejo del foco: **CON OBSERVACIONES** (foco invisible #3, tapado por el nav #6)
- Contraste de color: **CON OBSERVACIONES** (#1, #2, #7; es el problema principal)
- Sensibilidad al movimiento: **APROBADA**

## Estado después de los arreglos (2026-10-24)
| # | Estado | Qué se hizo |
|---|--------|-------------|
| 1 | Corregido | Todo el texto toma el tono del cielo de ese momento (`data-tone` en la raíz), y el cielo queda quieto mientras se lee cada capítulo: cambia en el 16% del tramo entre uno y otro. Además, halo del color del fondo detrás del texto. |
| 2 | Corregido | En el primer scroll la ciudad baja siguiendo directamente el scroll y se redibuja aunque el cielo no cambie. Ventanas al 45% de opacidad. Las opciones del formulario tienen fondo propio. |
| 3 | Corregido | Color de foco según el tono: tinta sobre fondo claro, bronce sobre fondo oscuro, también en el nav. |
| 4 | Corregido | `#confirm` queda siempre en el DOM; solo cambia el contenido. |
| 5 | Corregido | `document.documentElement.lang = "es-UY"`. |
| 6–9, 11–14 | Corregido | `scroll-padding-top`, placeholder a 70% de marfil, `aria-invalid` y `aria-describedby` en los errores, `required` con «(obligatorio)» visible, precio con «Precio: … pesos» para lectores de pantalla, `h2` en el footer, copa nombrada con trago y tipo, aviso en vivo del atardecer al cambiar de día. |
| 10 | Parcial | La lista se nombra «Elegí un cocktail para verlo servido»; los botones siguen con `aria-pressed`. |

**Contraste medido de nuevo** (mismo método; los halos no se cuentan, así que el resultado real es algo mejor):
- **Escritorio:** de 35 textos por debajo de AA a 0.
- **Celular:** de 27 a 8. Lo que queda:
  - Cinco textos (nav y datos de la terraza) dan 3.35–3.55:1, solo durante el cambio rápido de luz entre la terraza y la carta.
  - Los horarios del programa pasan por encima de la luna (1.14:1) por un momento.
  - Dos medidas sobre ventanas iluminadas (3.82 y 4.2:1). La de la opción del formulario no cuenta su fondo propio, que el script de medición no considera.
