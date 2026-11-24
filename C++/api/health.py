"""GET /api/health for the hosted build: reports the online compiler."""
import json
from http.server import BaseHTTPRequestHandler

COMPILER = "gcc-13.2.0 (wandbox.org)"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "ok": True,
            "compiler": COMPILER,
            "path": "wandbox.org",
            "mode": "hosted",
            "limits": {"compile_s": 50, "run_s": 10, "output_chars": 20000},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass
