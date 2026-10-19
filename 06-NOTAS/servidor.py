#!/usr/bin/env python3
"""Servidor local para la web, sin caché.
   Uso:  python3 "06-NOTAS/servidor.py"      ->  http://localhost:8788
   Sin caché para que cada F5 traiga los últimos cambios."""
import http.server, os
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "05-WEB")
PUERTO = 8788

# Las mismas cabeceras que manda Hostinger (05-WEB/.htaccess), asi un error de
# CSP aparece aca antes de publicar. Sin frame-ancestors ni X-Frame-Options:
# _qa_puente.html necesita meter el sitio en un iframe para las capturas.
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; "
       "img-src 'self' data: blob:; media-src 'self' blob:; "
       "frame-src https://open.spotify.com https://www.youtube-nocookie.com; connect-src 'self'; "
       "object-src 'none'; base-uri 'self'; form-action 'self' https://wa.me https://api.whatsapp.com")

# archivos de trabajo que nunca se sirven, ni siquiera en la red de casa
PRIVADO = (".md", ".py", ".sh", ".json", ".log", ".bak")

class SinCache(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.abspath(RAIZ), **kw)
    def send_head(self):
        ruta = self.path.split("?")[0].lower()
        if ruta.endswith(PRIVADO) or "/." in ruta.replace("/.well-known/", "/"):
            self.send_error(404)
            return None
        return super().send_head()
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        if self.path.split("?")[0].lower().endswith((".jpg", ".jpeg", ".png", ".mp4", ".webp")):
            self.send_header("Cache-Control", "max-age=300")   # fotos: 5 minutos, para que la otra PC no las vuelva a bajar en cada F5
        else:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
    def log_message(self, *a): pass

# multihilo: una conexión colgada no traba al resto
http.server.ThreadingHTTPServer.allow_reuse_address = True
http.server.ThreadingHTTPServer.daemon_threads = True
http.server.ThreadingHTTPServer.request_queue_size = 256   # muchas fotos en paralelo desde otra PC
with http.server.ThreadingHTTPServer(("", PUERTO), SinCache) as s:
    print(f"Apardian Studio -> http://localhost:{PUERTO}")
    print(f"Editor          -> http://localhost:{PUERTO}/index.html?edit=1")
    s.serve_forever()
