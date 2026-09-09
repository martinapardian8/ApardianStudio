# -*- coding: utf-8 -*-
# Catalogo de piezas de marca para APARDIAN STUDIO.
# (carpeta, nombre, modelo, aspect, prompt-especifico)

ADN = (
 "Brand identity for APARDIAN STUDIO, a photography, video and web-design studio from Uruguay. "
 "Strict palette, nothing else: off-white #F8F7F6, near-black #171717, one signal red #FF0033 used sparingly. "
 "The wordmark is the single word APARDIAN set in a heavy condensed uppercase display sans, "
 "immediately followed by a full stop rendered in the signal red. Spell it exactly A-P-A-R-D-I-A-N. "
 "Any small supporting text is a clean neutral grotesque, uppercase, widely letter-spaced. "
 "Swiss editorial art direction, large areas of empty space, precise alignment. "
 "No gradients, no drop shadows, no other logos, no watermark, no fake or garbled lettering. "
 "Photorealistic, soft directional daylight, crisp detail, shot on a 50mm lens."
)

PRO, NB = "nano_banana_pro", "nano_banana"

C = []
def add(carp, nom, modelo, ar, p): C.append((carp, nom, modelo, ar, p + " " + ADN))

# ---------- 01 LOGO / IDENTIDAD ----------
add("01-logo","logo_negro_sobre_hueso",PRO,"1:1","The wordmark APARDIAN. centred on a clean off-white field, black letters, red full stop, nothing else in the frame. Flat graphic, vector-crisp.")
add("01-logo","logo_blanco_sobre_negro",PRO,"1:1","The wordmark APARDIAN. centred on a deep near-black field, off-white letters, red full stop. Flat graphic, vector-crisp.")
add("01-logo","logo_relieve_papel",PRO,"1:1","The wordmark APARDIAN. blind-embossed into thick cotton paper, raking side light revealing the deboss, off-white on off-white, the full stop foil-stamped in red.")
add("01-logo","logo_hormigon",PRO,"1:1","The wordmark APARDIAN. painted directly on a smooth grey concrete wall, slightly weathered black paint, red full stop, hard afternoon shadow crossing the wall.")
add("01-logo","monograma_A",PRO,"1:1","A single letter A in the heavy condensed display sans, reversed out in off-white from a solid signal-red square, centred on a near-black field. Extremely simple mark.")
add("01-logo","sello_caucho",PRO,"1:1","A wooden-handled rubber stamp and its fresh black ink impression of the wordmark APARDIAN. on off-white paper, ink slightly uneven, red full stop hand-stamped separately.")
add("01-logo","tarjeta_frente",PRO,"4:5","Two thick business cards on a near-black surface: one face up showing only the wordmark APARDIAN. in black on off-white, one face down showing a solid red back. Overhead, tight crop.")
add("01-logo","tarjeta_marmol",PRO,"4:5","A stack of off-white business cards fanned on a pale marble slab, top card showing the wordmark APARDIAN., a black fountain pen resting alongside. Overhead.")
add("01-logo","hoja_membrete",PRO,"4:5","An A4 letterhead sheet on a near-black desk, the wordmark APARDIAN. small in the top-left corner, a thin red rule beneath it, the rest of the page empty. Overhead.")
add("01-logo","sobre_lacre",PRO,"4:5","A closed off-white envelope sealed with a red wax seal bearing a single letter A, the wordmark APARDIAN. printed small on the flap. Overhead on dark linen.")
add("01-logo","firma_marca_agua",PRO,"16:9","The wordmark APARDIAN. as a small, semi-transparent white signature in the lower-right corner of a dark moody photograph of an empty studio. Elegant and restrained.")
add("01-logo","favicon_azulejo",PRO,"1:1","A grid of nine small square tiles on off-white, each tile a different scale of the letter A in black, one single tile in signal red. Design-system sheet look.")

# ---------- 02 PAPELERIA ----------
add("02-papeleria","carpeta_entrega",PRO,"4:5","A rigid near-black presentation folder with the wordmark APARDIAN. foil-stamped small in off-white on its cover, sitting on a pale wooden table with a stack of photographic prints beside it.")
add("02-papeleria","caja_prints",PRO,"4:5","An off-white archival print box, lid slightly ajar showing photographic prints inside, the wordmark APARDIAN. letterpressed on the lid, a red ribbon tie. Overhead on dark wood.")
add("02-papeleria","cinta_marca",PRO,"4:5","A roll of off-white packing tape printed with a repeating black APARDIAN. wordmark, unspooled slightly, on a near-black surface.")
add("02-papeleria","sticker_troquelado",PRO,"4:5","A sheet of die-cut vinyl stickers on off-white backing: the wordmark APARDIAN., a red dot, a small camera outline, a letter A in a red square. Overhead, flat, evenly lit.")
add("02-papeleria","cuaderno",PRO,"4:5","A near-black hardcover notebook with the wordmark APARDIAN. debossed on the cover, closed, an elastic band and a red pencil across it. Overhead on off-white paper.")
add("02-papeleria","credencial",PRO,"4:5","A press credential on a woven off-white lanyard, the card showing the wordmark APARDIAN. and a thin red stripe, hanging against a near-black wall.")
add("02-papeleria","factura",PRO,"4:5","A minimal invoice document on off-white paper, the wordmark APARDIAN. at the top, a thin red rule, ruled empty rows below, a pen laid diagonally. Overhead.")
add("02-papeleria","bolsa_papel",PRO,"4:5","A small off-white paper shopping bag with flat black handles, the wordmark APARDIAN. printed once, low and small, on the front. Studio floor, single soft shadow.")
add("02-papeleria","tarjeta_gracias",PRO,"4:5","A small off-white card standing on a dark surface reading only GRACIAS in widely letter-spaced black uppercase, with the wordmark APARDIAN. tiny at the bottom and a red dot above it.")
add("02-papeleria","pack_completo",PRO,"4:5","An overhead flatlay of a complete stationery set on near-black linen: business cards, letterhead, envelope, sticker sheet and notebook, all off-white with black APARDIAN. wordmarks and small red accents. Perfectly aligned grid.")

# ---------- 03 FLYERS / AFICHES ----------
add("03-flyers","afiche_bodas",PRO,"4:5","A poster: a large black-and-white photograph of a bride and groom on a windy seaside promenade fills the upper two thirds; below on off-white, the single word BODAS in huge black condensed uppercase, and the wordmark APARDIAN. small underneath.")
add("03-flyers","afiche_gastronomia",PRO,"4:5","A poster: an overhead colour photograph of a rustic wooden table of grilled food fills the frame, a near-black band across the bottom holds the single word GASTRONOMIA in off-white condensed uppercase with the wordmark APARDIAN. beside it in red.")
add("03-flyers","afiche_retratos",PRO,"4:5","A poster: a tightly cropped black-and-white studio portrait of a man looking straight at the lens, off-white margin at the bottom carrying the single word RETRATOS in black condensed uppercase and a small red dot.")
add("03-flyers","afiche_lightroom",PRO,"4:5","A poster split diagonally: the same landscape photograph flat and grey on one half, richly graded on the other, with the single word EDICION in huge black condensed uppercase on an off-white band below and the wordmark APARDIAN. small in red.")
add("03-flyers","afiche_webs",PRO,"4:5","A poster: a laptop seen straight on displaying a stark black-and-white photography website, standing on an off-white plinth against a near-black wall, the single word WEB in enormous condensed uppercase running across the bottom.")
add("03-flyers","afiche_eventos",PRO,"4:5","A poster: a long-exposure colour photograph of a crowded party with light trails, a solid red band across the lower third carrying the single word EVENTOS in off-white condensed uppercase.")
add("03-flyers","afiche_marcas",PRO,"4:5","A poster: a clean product photograph of an olive-oil bottle on a lit sweep, off-white background, the single word MARCAS set small and widely letter-spaced in black at the very bottom with a red dot.")
add("03-flyers","afiche_reserva",PRO,"4:5","A stark typographic poster on off-white: the phrase RESERVA TU FECHA in huge black condensed uppercase stacked over three lines, one line rendered entirely in signal red, the wordmark APARDIAN. tiny at the foot.")
add("03-flyers","afiche_antes_despues",PRO,"4:5","A poster showing one photograph split down the middle, the left half deliberately flat and lifeless, the right half deeply graded and cinematic, a thin red hairline dividing them, small black uppercase captions ANTES and DESPUES underneath.")
add("03-flyers","afiche_80_proyectos",PRO,"4:5","A stark typographic poster on near-black: the numeral 80 set enormous in off-white condensed type filling most of the frame, the words PROYECTOS ENTREGADOS small and letter-spaced beneath it in red.")
add("03-flyers","afiche_musica",PRO,"4:5","A poster: a high-contrast black-and-white photograph of a singer at a microphone under a hard spotlight, off-white band at the bottom with the single word MUSICA in black condensed uppercase.")
add("03-flyers","afiche_naturaleza",PRO,"4:5","A poster: a wide colour photograph of a cliff meeting the ocean under heavy cloud, a narrow off-white band at the foot carrying the single word NATURALEZA in black letter-spaced uppercase and a red dot.")
add("03-flyers","volante_promo",PRO,"4:5","A double-sided flyer photographed on a near-black surface, front showing a full-bleed photograph, back showing only the wordmark APARDIAN. and a red dot on off-white. Slight overlap, overhead.")
add("03-flyers","afiche_calle",NB,"4:5","A large printed poster wheat-pasted onto a weathered concrete city wall in Montevideo, showing a black-and-white photograph and a bold condensed wordmark, slightly torn at one corner, hard sunlight.")
add("03-flyers","valla_ciudad",NB,"16:9","A minimal billboard on a Montevideo rooftop against an overcast sky, carrying one enormous black-and-white photograph and a small wordmark in the corner, no other advertising.")

# ---------- 04 ROPA ----------
add("04-ropa","remera_negra",PRO,"4:5","A near-black heavyweight cotton t-shirt laid flat on off-white paper, the wordmark APARDIAN. screen-printed small and centred on the chest in off-white with a red full stop. Overhead, soft even light.")
add("04-ropa","remera_hueso",PRO,"4:5","An off-white heavyweight t-shirt laid flat on a near-black surface, the wordmark APARDIAN. printed small on the chest in black. Overhead.")
add("04-ropa","remera_espalda",PRO,"4:5","A near-black t-shirt hung on a plain wooden hanger against a concrete wall, seen from the back, a large off-white condensed wordmark APARDIAN. printed across the shoulder blades.")
add("04-ropa","buzo_capucha",PRO,"4:5","A near-black heavyweight hoodie laid flat on off-white paper, a small red embroidered dot on the chest and the wordmark APARDIAN. embroidered in off-white across the hood. Overhead.")
add("04-ropa","buzo_hueso",PRO,"4:5","An off-white boxy hoodie on a near-black surface, black wordmark APARDIAN. printed small on the left chest. Overhead.")
add("04-ropa","buzo_cuello_redondo",PRO,"4:5","A charcoal crewneck sweatshirt worn by a cropped torso against an off-white studio wall, the wordmark APARDIAN. embroidered small on the chest, hands in pockets, no face visible.")
add("04-ropa","gorra_negra",PRO,"4:5","A near-black five-panel cap on an off-white plinth, the wordmark APARDIAN. embroidered small and flat across the front panel in off-white with a red full stop. Three-quarter view, single soft shadow.")
add("04-ropa","gorra_hueso",PRO,"4:5","An off-white unstructured dad cap on a near-black surface, black embroidered wordmark APARDIAN. on the front panel, curved brim. Three-quarter view.")
add("04-ropa","gorra_roja",PRO,"4:5","A signal-red cap on an off-white background, the wordmark APARDIAN. embroidered small in off-white on the front. Clean product shot, three-quarter view.")
add("04-ropa","bucket",PRO,"4:5","An off-white cotton bucket hat on a near-black surface, black wordmark APARDIAN. embroidered on the brim. Overhead product shot.")
add("04-ropa","gorro_lana",PRO,"4:5","A ribbed near-black beanie on off-white paper, a small woven label at the fold carrying the wordmark APARDIAN. and a red dot. Overhead.")
add("04-ropa","campera_trabajo",PRO,"4:5","A charcoal cotton-canvas work jacket hung on a hook against a concrete wall, the wordmark APARDIAN. embroidered small on the left chest, a red dot on the right. Natural side light.")
add("04-ropa","rompevientos",PRO,"4:5","An off-white lightweight windbreaker laid flat on near-black, the wordmark APARDIAN. printed large and condensed across the back, seen from behind. Overhead.")
add("04-ropa","chaleco_fotografo",PRO,"4:5","A near-black photographer's utility vest on a plain hanger against an off-white wall, many pockets, the wordmark APARDIAN. embroidered small on the chest and a red dot on the collar.")
add("04-ropa","delantal",PRO,"4:5","A charcoal canvas apron with leather straps hanging against a tiled kitchen wall, the wordmark APARDIAN. screen-printed small and low on the front, a red dot beside it.")
add("04-ropa","remera_oversize_calle",NB,"4:5","A person from the shoulders down wearing an oversized near-black t-shirt with a small off-white condensed wordmark on the chest, standing on a Montevideo street in overcast daylight, shallow depth of field.")
add("04-ropa","gorra_en_uso",NB,"4:5","A photographer seen from behind wearing a near-black cap with a small embroidered wordmark, camera strap across the shoulder, walking on a seaside promenade at golden hour.")
add("04-ropa","medias",PRO,"4:5","A folded pair of near-black ribbed socks on off-white paper, a repeating small off-white wordmark APARDIAN. woven along the cuff. Overhead, tight crop.")
add("04-ropa","correa_camara",PRO,"4:5","A woven camera strap in near-black with a single signal-red stripe, coiled on off-white paper, a small leather tab stamped APARDIAN. Overhead.")
add("04-ropa","etiqueta_tejida",PRO,"4:5","A macro shot of a woven clothing label sewn into a near-black garment seam, the label off-white with the wordmark APARDIAN. woven in black and a red full stop. Extreme close-up.")

# ---------- 05 OBJETOS / MERCH ----------
add("05-objetos","imanes_heladera",PRO,"4:5","A set of six square fridge magnets arranged in a grid on a brushed steel surface: four carry small black-and-white photographs, one is solid signal red, one carries the wordmark APARDIAN. on off-white. Overhead.")
add("05-objetos","iman_unico",PRO,"4:5","A single square fridge magnet on a stainless-steel door, off-white with the wordmark APARDIAN. in black and a red full stop, slightly angled, soft kitchen daylight.")
add("05-objetos","pines_esmalte",PRO,"4:5","Three hard-enamel lapel pins on off-white card: a red dot, a black letter A, and a tiny camera outline. Overhead macro, precise metal edges.")
add("05-objetos","taza",PRO,"4:5","A matte near-black ceramic mug on an off-white surface, the wordmark APARDIAN. printed small in off-white on one side, steam rising, morning window light.")
add("05-objetos","botella",PRO,"4:5","An off-white matte stainless steel water bottle standing on a near-black surface, the wordmark APARDIAN. printed vertically in black along the body, a red dot at the base.")
add("05-objetos","llavero",PRO,"4:5","A near-black leather keychain tag stamped with the wordmark APARDIAN. in blind deboss, a single red stitch, lying on off-white paper with a brass key ring. Overhead macro.")
add("05-objetos","pendrive_caja",PRO,"4:5","A small wooden box lined in off-white, open, holding a black USB drive engraved with the wordmark APARDIAN. and a stack of small photographic prints. Overhead, warm side light.")
add("05-objetos","pano_lentes",PRO,"4:5","A microfibre lens cloth in off-white printed with a repeating small black APARDIAN. wordmark, draped loosely beside a camera lens on a near-black surface.")
add("05-objetos","mousepad",PRO,"4:5","A near-black desk mat on a pale wooden desk, the wordmark APARDIAN. printed small and low in the bottom-right corner in off-white, a keyboard and a red pencil resting on it. Overhead.")
add("05-objetos","funda_notebook",PRO,"4:5","An off-white felt laptop sleeve on a near-black surface, the wordmark APARDIAN. embroidered small in black at the bottom-left, a red zipper pull. Overhead.")
add("05-objetos","tubo_afiches",PRO,"4:5","A near-black cardboard poster tube standing upright on off-white paper, a printed label wrapped around it carrying the wordmark APARDIAN. and a red band. Single soft shadow.")
add("05-objetos","album_boda",PRO,"4:5","A linen-bound wedding album in off-white on a dark wooden table, the wordmark APARDIAN. blind-debossed small on the cover, a red ribbon marker peeking from the pages.")
add("05-objetos","porta_prints",PRO,"4:5","A slim off-white folio open on a dark table, revealing three black-and-white photographic prints in slipsheets, the wordmark APARDIAN. printed small on the inside cover.")
add("05-objetos","vinilo_auto",NB,"16:9","A plain white cargo van parked on a Montevideo street, a small black condensed wordmark and a red dot applied low on the side panel, no other graphics, overcast daylight.")
add("05-objetos","cartel_local",NB,"16:9","A minimal blade sign projecting from a concrete building facade, near-black metal with an off-white condensed wordmark and a red dot, seen against a pale sky.")
add("05-objetos","kit_completo",PRO,"4:5","An overhead flatlay of a complete merchandise kit on near-black linen: cap, folded t-shirt, mug, sticker sheet, notebook, tote bag and magnets, all in off-white and black with small red accents, arranged in a precise grid.")

# ---------- 06 POSTEOS IG (4:5) ----------
add("06-posteos","post_frase_instante",PRO,"4:5","An Instagram post: near-black field, the phrase EL INSTANTE QUE NO SE REPITE set in off-white condensed uppercase stacked over three lines, one word in signal red, the wordmark APARDIAN. tiny at the foot.")
add("06-posteos","post_servicios",PRO,"4:5","An Instagram post on off-white: four stacked rows, each a thin black rule with one word in condensed black uppercase, reading FOTO, VIDEO, WEB, EDICION, with a red dot beside the last one.")
add("06-posteos","post_agenda",PRO,"4:5","An Instagram post: a solid signal-red field with the phrase AGENDA TU SESION in off-white condensed uppercase centred, and the wordmark APARDIAN. small at the bottom in off-white.")
add("06-posteos","post_grilla_portfolio",PRO,"4:5","An Instagram post showing a precise three-by-three grid of small square photographs, all black-and-white except one in colour, on an off-white field, the wordmark APARDIAN. tiny below the grid.")
add("06-posteos","post_antes_despues",PRO,"4:5","An Instagram post: one photograph split vertically, flat and dull on the left, richly graded on the right, a signal-red hairline between them, the words ANTES and DESPUES tiny in black uppercase at the base.")
add("06-posteos","post_testimonio",PRO,"4:5","An Instagram post on off-white: a large black quotation mark in the top-left, three lines of small black uppercase text below it, a red rule, and the wordmark APARDIAN. at the foot.")
add("06-posteos","post_detras_escena",PRO,"4:5","An Instagram post: a grainy black-and-white photograph of a photographer crouching to frame a shot at a wedding, a narrow off-white band at the bottom with the words DETRAS DE ESCENA in small black uppercase.")
add("06-posteos","post_precio",PRO,"4:5","An Instagram post on near-black: a large off-white numeral set condensed and centred, the words DESDE above it and POR SESION below, both small and letter-spaced, a red dot as punctuation.")
add("06-posteos","post_tip_fotografo",PRO,"4:5","An Instagram post on off-white: the numeral 01 in signal red at the top-left, a short line of black condensed uppercase headline beneath, and a small black-and-white photograph occupying the lower half.")
add("06-posteos","post_lightroom",PRO,"4:5","An Instagram post: a laptop screen seen straight on showing a photo-editing interface with a landscape image and colour sliders, on a near-black desk, the wordmark APARDIAN. small in the corner of the frame.")
add("06-posteos","post_carrusel_portada",PRO,"4:5","An Instagram carousel cover on near-black: a single enormous off-white numeral 1 in condensed type, a small red arrow at the right edge suggesting a swipe, the wordmark APARDIAN. tiny at the foot.")
add("06-posteos","post_web_nueva",PRO,"4:5","An Instagram post: a laptop and a phone side by side on an off-white surface, both screens showing the same stark black-and-white photography website, the single word WEB in black condensed uppercase across the bottom.")
add("06-posteos","post_boda_gancho",PRO,"4:5","An Instagram post: a full-bleed black-and-white photograph of a bride's veil catching the wind, a small signal-red dot in the lower-right corner as the only graphic element.")
add("06-posteos","post_gastro_gancho",PRO,"4:5","An Instagram post: a tight overhead colour photograph of grilled meat on a wooden board, a narrow near-black band at the foot with the wordmark APARDIAN. in off-white.")
add("06-posteos","post_retrato_gancho",PRO,"4:5","An Instagram post: a tightly cropped black-and-white portrait, half the face in deep shadow, a thin signal-red rule running along the bottom edge of the frame.")
add("06-posteos","post_disponibilidad",PRO,"4:5","An Instagram post on off-white: a simple month calendar grid drawn in thin black rules, three squares filled solid signal red, the word DISPONIBLE small and letter-spaced in black beneath it.")
add("06-posteos","post_bienvenida",PRO,"4:5","An Instagram post: a near-black field with the single word HOLA in enormous off-white condensed uppercase, a red full stop after it, and a small line of letter-spaced text underneath.")
add("06-posteos","post_proceso",PRO,"4:5","An Instagram post on off-white: three numbered steps 01 02 03 stacked as thin black rules with short uppercase labels, the numerals in signal red, plenty of empty space.")
add("06-posteos","post_equipo",NB,"4:5","An Instagram post: an overhead flatlay of camera bodies, lenses and a laptop on a near-black desk, arranged in a precise grid, cool daylight, no branding visible.")
add("06-posteos","post_uruguay",NB,"4:5","An Instagram post: a moody wide photograph of the Montevideo rambla at dusk with the river on one side and streetlights coming on, muted colour, cinematic.")

# ---------- 07 HISTORIAS IG (9:16) ----------
add("07-historias","story_agenda",PRO,"9:16","A vertical Instagram story: solid near-black, the phrase AGENDA TU SESION in off-white condensed uppercase centred over two lines, a signal-red dot beneath, the wordmark APARDIAN. small at the very bottom. Wide empty margins top and bottom.")
add("07-historias","story_nuevo_post",PRO,"9:16","A vertical Instagram story: a black-and-white photograph occupying the middle third of the frame, off-white above and below, the words NUEVO POST in small black letter-spaced uppercase under the image.")
add("07-historias","story_link_bio",PRO,"9:16","A vertical Instagram story: solid signal red, the words LINK EN BIO in off-white condensed uppercase centred, a small off-white arrow pointing up above the text.")
add("07-historias","story_antes_despues",PRO,"9:16","A vertical Instagram story: one photograph split horizontally across the middle, the top half flat and grey, the bottom half richly graded, a thin off-white line dividing them, tiny uppercase labels at each edge.")
add("07-historias","story_testimonio",PRO,"9:16","A vertical Instagram story on off-white: a large black quotation mark, three short lines of small black uppercase text, a red rule beneath, generous empty space.")
add("07-historias","story_detras",PRO,"9:16","A vertical Instagram story: a grainy vertical black-and-white photograph of a photographer working at a wedding reception, a small off-white caption bar at the foot with letter-spaced uppercase text.")
add("07-historias","story_encuesta",PRO,"9:16","A vertical Instagram story: near-black field with two stacked off-white rectangles like poll options, one outlined in signal red, a short black uppercase word inside each.")
add("07-historias","story_cuenta_regresiva",PRO,"9:16","A vertical Instagram story: a huge off-white numeral centred on near-black, the word FALTAN in small letter-spaced uppercase above it and a red dot below.")
add("07-historias","story_servicios",PRO,"9:16","A vertical Instagram story on off-white: four thin black rules stacked down the frame, each with one condensed black uppercase word, FOTO VIDEO WEB EDICION, the last one accented in signal red.")
add("07-historias","story_portfolio",PRO,"9:16","A vertical Instagram story: a full-bleed vertical black-and-white photograph of a couple on a windswept promenade, a small off-white wordmark APARDIAN. in the lower-left corner.")
add("07-historias","story_gastro",PRO,"9:16","A vertical Instagram story: a full-bleed vertical colour photograph of hands plating food in a dark kitchen, a signal-red rule running along the very bottom edge.")
add("07-historias","story_retrato",PRO,"9:16","A vertical Instagram story: a full-bleed vertical black-and-white portrait lit from one side, deep shadows, a tiny off-white wordmark APARDIAN. bottom-centre.")
add("07-historias","story_precio",PRO,"9:16","A vertical Instagram story on near-black: a large off-white condensed numeral centred, the word DESDE small above and POR SESION small below, both letter-spaced, a red full stop as the only accent.")
add("07-historias","story_web",PRO,"9:16","A vertical Instagram story: a phone held upright in one hand against an off-white wall, its screen showing a stark black-and-white photography website, the single word WEB in black uppercase at the foot.")
add("07-historias","story_lightroom",PRO,"9:16","A vertical Instagram story: a vertical crop of a photo-editing interface with colour sliders over a landscape image, a near-black band at the bottom carrying the word EDICION in off-white uppercase.")
add("07-historias","story_bodas",PRO,"9:16","A vertical Instagram story: a full-bleed vertical black-and-white photograph of a bride's dress catching wind, an off-white band across the lower quarter with the word BODAS in black condensed uppercase.")
add("07-historias","story_80",PRO,"9:16","A vertical Instagram story: the numeral 80 set enormous in off-white condensed type on near-black, filling most of the frame, the words PROYECTOS ENTREGADOS small and letter-spaced in signal red beneath it.")
add("07-historias","story_bienvenida",PRO,"9:16","A vertical Instagram story: solid off-white, the single word HOLA in enormous black condensed uppercase centred with a signal-red full stop, one small line of letter-spaced text far below.")
add("07-historias","story_musica",NB,"9:16","A vertical high-contrast black-and-white photograph of a singer at a microphone under a hard spotlight, deep black background, dramatic and grainy.")
add("07-historias","story_naturaleza",NB,"9:16","A vertical photograph of a rocky Uruguayan coastline under heavy grey cloud, long exposure smoothing the sea, muted cold colour, cinematic.")

# ---------- 08 AMBIENTE ----------
add("08-ambiente","escritorio",NB,"16:9","An overhead shot of a tidy editing desk: a laptop showing a photo-editing interface, a camera body, a graphics tablet, a notebook and a red pencil, all on pale wood, cool north light.")
add("08-ambiente","pared_prints",NB,"16:9","A gallery wall in a bright studio: nine black-and-white photographic prints hung in a precise grid on an off-white wall, a concrete floor, a single wooden bench.")
add("08-ambiente","estudio_vacio",NB,"16:9","An empty photography studio: a seamless off-white backdrop, one softbox on a stand, a stool, concrete floor, large industrial window light from the left.")
add("08-ambiente","equipo_negro",NB,"16:9","A precise overhead grid of camera gear on a near-black surface: two camera bodies, four lenses, a light meter and batteries, hard directional light, deep shadows.")
add("08-ambiente","recepcion",NB,"16:9","A minimal studio reception: a concrete wall with a small off-white blade sign, a low wooden bench, one potted plant, soft daylight from a skylight.")
add("08-ambiente","escritorio_web",NB,"16:9","A designer's desk seen from above: a large monitor showing a stark black-and-white website layout, a keyboard, a coffee cup and a stack of printed cards on pale wood.")
add("08-ambiente","fotografo_boda",NB,"16:9","A documentary photograph of a photographer crouching low to frame a shot during a wedding reception, warm string lights bokeh behind, motion in the crowd, grainy.")
add("08-ambiente","backdrop_rojo",NB,"16:9","An empty studio corner with a signal-red seamless paper backdrop rolling onto a concrete floor, a single light stand casting a hard shadow, nothing else.")
add("08-ambiente","rambla_montevideo",NB,"16:9","A wide cinematic photograph of the Montevideo rambla at blue hour, wet pavement reflecting streetlights, the river flat and grey, one distant figure walking.")
add("08-ambiente","mesa_reunion",NB,"16:9","A meeting table seen from above: an open laptop, printed photographs spread out, two coffee cups and a notebook, hands of two people gesturing over the prints, warm daylight.")

if __name__ == "__main__":
    import json, collections
    c = collections.Counter(x[0] for x in C)
    m = collections.Counter(x[2] for x in C)
    print(json.dumps({"total": len(C), "por_carpeta": dict(c), "por_modelo": dict(m),
                      "costo_creditos": m["nano_banana_pro"]*2 + m["nano_banana"]*1}, ensure_ascii=False, indent=1))
