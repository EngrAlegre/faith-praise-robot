"""
Tiny server for the C++ lab: serves the app and exposes one endpoint that
compiles and runs a learner's program.

    python server.py                # http://127.0.0.1:8765
    python server.py --port 9000
    python server.py --host 0.0.0.0 # only on a network you trust

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import runner

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
DATA = ROOT / "data"
MAX_BODY = 128 * 1024

_run_lock = threading.Semaphore(2)   # at most two compiles at once


class Handler(BaseHTTPRequestHandler):
    server_version = "CppLab/1.0"

    # ---------------- helpers
    def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, status: int, payload: dict):
        self._send(status, json.dumps(payload).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _file(self, path: Path):
        if not path.is_file():
            self._json(404, {"error": "not found", "path": str(path.name)})
            return
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".js":
            ctype = "text/javascript; charset=utf-8"
        elif path.suffix in {".json"}:
            ctype = "application/json; charset=utf-8"
        elif path.suffix in {".css"}:
            ctype = "text/css; charset=utf-8"
        elif path.suffix in {".html"}:
            ctype = "text/html; charset=utf-8"
        self._send(200, path.read_bytes(), ctype)

    def _safe(self, base: Path, rel: str) -> Path | None:
        """Resolve a URL path inside base, refusing traversal."""
        rel = rel.split("?", 1)[0].lstrip("/")
        target = (base / rel).resolve()
        try:
            target.relative_to(base.resolve())
        except ValueError:
            return None
        return target

    # ---------------- routes
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            gxx = runner.find_compiler()
            self._json(200, {
                "ok": True,
                "compiler": runner.compiler_version(gxx),
                "path": gxx,
                "limits": {"compile_s": runner.COMPILE_TIMEOUT,
                           "run_s": runner.RUN_TIMEOUT,
                           "output_chars": runner.MAX_OUTPUT},
            })
            return
        if path in ("/", "/index.html"):
            self._file(WEB / "index.html")
            return
        if path.startswith("/data/"):
            target = self._safe(DATA, path[len("/data/"):])
            if target is None:
                self._json(403, {"error": "forbidden"})
                return
            self._file(target)
            return
        target = self._safe(WEB, path)
        if target is None:
            self._json(403, {"error": "forbidden"})
            return
        self._file(target)

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/run":
            self._json(404, {"error": "unknown endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            self._json(400, {"error": "empty request"})
            return
        if length > MAX_BODY:
            self._json(413, {"error": "program too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._json(400, {"error": "body is not valid JSON"})
            return

        code = payload.get("code", "")
        stdin_text = payload.get("stdin", "") or ""
        if not _run_lock.acquire(timeout=30):
            self._json(503, {"error": "the runner is busy, try again in a moment"})
            return
        try:
            result = runner.run_cpp(code, stdin_text)
        except Exception as exc:                      # never leak a stack trace
            result = {"ok": False, "phase": "error", "stdout": "", "stderr": "",
                      "message": f"Runner error: {type(exc).__name__}: {exc}"}
        finally:
            _run_lock.release()
        self._json(200, result)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    gxx = runner.find_compiler()
    print("C++ Lab")
    print(f"  compiler : {runner.compiler_version(gxx) or 'NOT FOUND'}")
    if gxx:
        print(f"             {gxx}")
    print(f"  serving  : http://{args.host}:{args.port}")
    if not gxx:
        print("  warning  : the Run button will explain the missing compiler "
              "and link to an online one.")
    try:
        ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
