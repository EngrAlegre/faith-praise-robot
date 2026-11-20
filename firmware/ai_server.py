#!/usr/bin/env python3
"""
Five Sides robot brain  ·  Faith & Praise build
------------------------------------------------
Tiny HTTP server the robot talks to.  Runs on any laptop on the same WiFi.

    python ai_server.py                 # offline demo mode (no API key needed)
    set AI_KEY=sk-...  (Windows)        # real speech + real answers
    ./ai_server.py                      # macOS / Linux

Endpoints
    POST /chat   body = 16 kHz mono WAV  ->  {"say": "...", "move": "...", "face": "..."}
    GET  /       status page (open in a browser to check the robot can reach it)

Only the Python standard library is used, so it runs on a clean install.
Environment variables
    AI_BASE   default https://api.openai.com/v1   (any OpenAI-compatible server)
    AI_KEY    API key. Without it the server stays in offline demo mode.
    AI_MODEL  default gpt-4o-mini
    STT_MODEL default whisper-1
    PORT      default 8080
"""
import json
import os
import random
import re
import sys
import time
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AI_BASE = os.environ.get("AI_BASE", "https://api.openai.com/v1").rstrip("/")
AI_KEY = os.environ.get("AI_KEY", "").strip()
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")
STT_MODEL = os.environ.get("STT_MODEL", "whisper-1")
PORT = int(os.environ.get("PORT", "8080"))

MOVES = {"stop", "forward", "back", "left", "right", "spin", "wiggle"}
FACES = {"idle", "happy", "think", "talk", "love", "sleep"}

SYSTEM_PROMPT = """You are FIVE SIDES, a small friendly robot built by two children,
Faith and Praise. You sit on a desk, you have two wheels, one eye-screen and one
speaker. You are curious, kind, playful and you never use long words.

Rules:
- Answer in at most 25 words. Short sentences. Warm and simple.
- You may ask the child one short question back.
- If you do not know something, say so and suggest trying it together.

Pick exactly one action from these lists.
move: stop, forward, back, left, right, spin, wiggle
face: idle, happy, think, talk, love, sleep

Reply with ONLY this JSON and nothing else:
{"say": "...", "move": "...", "face": "..."}"""


# --------------------------------------------------------------------------- #
#  helpers
# --------------------------------------------------------------------------- #
def http_json(url, payload, headers, timeout=30):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def transcribe(wav_bytes):
    """Send a WAV file to an OpenAI-compatible /audio/transcriptions endpoint."""
    boundary = "----fivesides" + uuid.uuid4().hex
    parts = []

    def field(name, value):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())

    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"speech.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode())
    parts.append(wav_bytes)
    parts.append(b"\r\n")
    field("model", STT_MODEL)
    field("language", "en")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        f"{AI_BASE}/audio/transcriptions", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                 "Authorization": f"Bearer {AI_KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode()).get("text", "").strip()


def ask_llm(text):
    out = http_json(f"{AI_BASE}/chat/completions", {
        "model": AI_MODEL,
        "temperature": 0.7,
        "max_tokens": 120,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": text}],
    }, {"Authorization": f"Bearer {AI_KEY}"})
    raw = out["choices"][0]["message"]["content"]
    return clean_reply(raw)


def clean_reply(raw):
    """Never trust the model: parse, clamp, and fall back rather than crash."""
    try:
        obj = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except Exception:
        return {"say": raw.strip()[:200] or "I am thinking.", "move": "stop", "face": "think"}
    say = str(obj.get("say", "")).strip()[:200] or "I am thinking."
    move = str(obj.get("move", "stop")).lower().strip()
    face = str(obj.get("face", "idle")).lower().strip()
    return {"say": say,
            "move": move if move in MOVES else "stop",
            "face": face if face in FACES else "idle"}


# --------------------------------------------------------------------------- #
#  offline demo brain — works with no key, no internet
# --------------------------------------------------------------------------- #
def offline_reply(text):
    t = (text or "").lower()
    rules = [
        (("hello", "hi ", "hey"), "Hello! I am Five Sides. Do you want to see me roll?", "forward", "happy"),
        (("your name", "who are you"), "I am Five Sides. Faith and Praise built me.", "spin", "love"),
        (("how are you",), "I am happy! My wheels are warm and my screen is bright.", "wiggle", "happy"),
        (("dance", "sing"), "I cannot sing well, but I can dance!", "spin", "love"),
        (("move", "go", "roll", "drive"), "Watch me roll!", "forward", "happy"),
        (("turn", "left"), "Turning left!", "left", "happy"),
        (("right",), "Turning right!", "right", "happy"),
        (("robot", "arduino", "esp32", "code"), "You can code me with blocks and Arduino. Want to change my face?", "wiggle", "think"),
        (("face", "smile", "happy"), "Look, my happy face!", "stop", "happy"),
        (("tired", "sleep", "goodnight"), "Goodnight. I will keep the desk warm.", "stop", "sleep"),
        (("thank",), "You are welcome!", "wiggle", "love"),
        (("love", "friend"), "You are my favourite human.", "spin", "love"),
        (("math", "plus", "add"), "I love numbers. One wheel plus one wheel is two!", "wiggle", "think"),
    ]
    for keys, say, move, face in rules:
        if any(k in t for k in keys):
            return {"say": say, "move": move, "face": face}
    if not t:
        return {"say": "I heard something but I am not sure. Say hello again?",
                "move": "stop", "face": "think"}
    openers = ["I heard you say: ", "You said: ", "So you said: "]
    return {"say": (random.choice(openers) + text.strip())[:180] + ". Tell me more!",
            "move": random.choice(["wiggle", "stop", "spin"]),
            "face": random.choice(["happy", "think"])}


# --------------------------------------------------------------------------- #
#  HTTP
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    server_version = "FiveSides/1.0"

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        mode = "AI (speech + language model)" if AI_KEY else "offline demo (no API key)"
        self._send(200, f"""<!doctype html><meta charset=utf-8>
<title>Five Sides</title>
<style>body{{font:16px/1.6 system-ui;margin:40px;max-width:640px}}
b{{color:#c2185b}}code{{background:#f3f3f3;padding:2px 6px;border-radius:4px}}</style>
<h2>Five Sides robot brain</h2>
<p>Status: <b>running</b><br>Mode: <b>{mode}</b><br>Model: <code>{AI_MODEL}</code></p>
<p>The robot POSTs a WAV recording to <code>/chat</code> and gets back
<code>{{"say","move","face"}}</code>.</p>""", "text/html; charset=utf-8")

    def do_POST(self):
        if self.path.rstrip("/") != "/chat":
            self._send(404, '{"error":"not found"}')
            return
        length = int(self.headers.get("Content-Length", "0"))
        wav = self.rfile.read(length) if length else b""
        hint = self.headers.get("X-Hint", "")

        t0 = time.time()
        try:
            if AI_KEY and len(wav) > 1000:
                heard = transcribe(wav)
                reply = ask_llm(heard) if heard else offline_reply(hint)
            else:
                heard = hint or "(demo mode: no microphone audio sent to a model)"
                reply = offline_reply(heard)
        except Exception as exc:                      # never leave the robot hanging
            print(f"  ! {type(exc).__name__}: {exc}")
            reply = {"say": "My brain hiccupped. Try once more.",
                     "move": "stop", "face": "think"}
            heard = "(error)"

        print(f'  heard : {heard[:90]!r}')
        print(f'  say   : {reply["say"]!r}  [{reply["move"]}/{reply["face"]}]  '
              f'{time.time()-t0:.2f}s')
        self._send(200, json.dumps(reply))

    def log_message(self, fmt, *args):
        pass


def local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    print("=" * 62)
    print(" Five Sides robot brain")
    print(f" mode      : {'AI' if AI_KEY else 'OFFLINE DEMO (set AI_KEY for real AI)'}")
    print(f" listening : http://{local_ip()}:{PORT}")
    print(" put that address in AI_HOST inside five_sides_bot.ino")
    print("=" * 62)
    try:
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
