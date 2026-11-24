"""
POST /api/run  ->  compile and run one program on an online C++ compiler.

Used when the app is hosted (Vercel) instead of run locally with server.py.
The compile happens on wandbox.org; this function only relays it, so the
browser never needs CORS permission and the response shape matches the local
runner exactly.

The pure function `compile_via_wandbox()` is importable, so it can be tested
without a web server.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

WANDBOX = "https://wandbox.org/api/compile.json"
COMPILER = "gcc-13.2.0"          # C++20 capable; verified with <ranges>
UA = "Mozilla/5.0 (compatible; cpp-lab/1.0)"
MAX_SOURCE = 64 * 1024
MAX_OUTPUT = 20_000


def compile_via_wandbox(code: str, stdin_text: str = "") -> dict:
    result = {
        "ok": False, "phase": "setup", "stdout": "", "stderr": "",
        "exit": None, "compile_ms": 0, "run_ms": 0,
        "compiler": f"{COMPILER} (wandbox.org)", "message": "",
    }
    if not isinstance(code, str) or not code.strip():
        result["message"] = "No code was sent."
        return result
    if len(code) > MAX_SOURCE:
        result["message"] = f"Program is too long ({len(code)} characters)."
        return result

    payload = json.dumps({
        "compiler": COMPILER,
        "code": code,
        "stdin": stdin_text or "",
        "compiler-option-raw": "-std=c++20\n-O1\n-Wall",
    }).encode()

    started = time.perf_counter()
    try:
        req = urllib.request.Request(
            WANDBOX, data=payload,
            headers={"Content-Type": "application/json", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=50) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        result["message"] = f"The online compiler answered {exc.code}. Try again in a moment."
        return result
    except Exception as exc:
        result["message"] = f"Could not reach the online compiler ({type(exc).__name__})."
        return result

    elapsed = int((time.perf_counter() - started) * 1000)
    compile_err = (data.get("compiler_error") or "").strip()
    compile_out = (data.get("compiler_message") or "").strip()
    program_out = data.get("program_output") or ""
    program_err = (data.get("program_error") or "").strip()
    status = str(data.get("status", ""))

    if status == "0" and not compile_err:
        result.update({
            "ok": True, "phase": "run", "stdout": program_out[:MAX_OUTPUT],
            "stderr": program_err[:MAX_OUTPUT], "exit": 0,
            "run_ms": elapsed, "compile_ms": 0,
        })
        if compile_out:
            result["warnings"] = compile_out[:MAX_OUTPUT]
        return result

    # non-zero: either it did not compile, or it crashed / timed out
    if compile_err:
        result.update({
            "phase": "compile", "stderr": compile_err[:MAX_OUTPUT],
            "message": "The compiler found a problem. Read the first error line.",
        })
    else:
        result.update({
            "phase": "run", "stdout": program_out[:MAX_OUTPUT],
            "stderr": program_err[:MAX_OUTPUT],
            "message": "The program did not finish cleanly.",
        })
    return result


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        self._send(200, {"ok": True, "compiler": f"{COMPILER} (wandbox.org)",
                         "mode": "hosted"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._send(400, {"ok": False, "message": "Body is not valid JSON."})
            return
        self._send(200, compile_via_wandbox(payload.get("code", ""), payload.get("stdin", "")))

    def log_message(self, *args):
        pass
