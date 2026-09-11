#!/usr/bin/env python3
"""Servidor local para la web, sin caché.
   Uso:  python3 "06-NOTAS/servidor.py"      ->  http://localhost:8788
   Sin caché para que cada F5 traiga los últimos cambios."""
import http.server, os
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "05-WEB")
PUERTO = 8788

class SinCache(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.abspath(RAIZ), **kw)
    def end_headers(self):
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
