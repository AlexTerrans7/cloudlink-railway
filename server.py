import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from cloudlink import server
from cloudlink.server.protocols import clpv4

# --- HTTP health check handler ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs so they don't clutter output

def run_health_server():
    http_port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(("0.0.0.0", http_port), HealthCheck)
    httpd.serve_forever()

# --- CloudLink WebSocket server ---
def run_cloudlink():
    cl_server = server()
    cl_server.logging.basicConfig(level=cl_server.logging.INFO)
    clpv4(cl_server)
    cl_server.run(ip="0.0.0.0", port=3000)

# --- Run both ---
if __name__ == "__main__":
    # Health check on Render's PORT, CloudLink on 3000
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    run_cloudlink()
