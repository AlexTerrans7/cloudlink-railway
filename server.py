import os
import asyncio
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from cloudlink import server
from cloudlink.server.protocols import clpv4

# ── Silence the HEAD-request spam (cosmetic, belt-and-suspenders) ──
logging.getLogger("websockets.server").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO)

WS_PORT   = 3000                                      # CloudLink always uses 3000
HTTP_PORT = int(os.environ.get("PORT", 8080))         # Render health-check port

# ── Tiny HTTP server just for Render's health checks ──────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):
        pass  # keep logs clean

def start_health_server():
    httpd = HTTPServer(("0.0.0.0", HTTP_PORT), HealthHandler)
    httpd.serve_forever()

# ── Start health check in background thread ────────────────────────
t = threading.Thread(target=start_health_server, daemon=True)
t.start()
logging.info(f"Health check HTTP server running on port {HTTP_PORT}")

# ── Start CloudLink (blocking) ─────────────────────────────────────
cl = server()
clpv4(cl)
cl.run(ip="0.0.0.0", port=WS_PORT)
