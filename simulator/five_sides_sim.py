"""
FIVE SIDES · desktop simulator
==============================
Trials the ESP32-S3 firmware on the PC: the same face, the same state machine,
the same Serial lines, and - if you want - the real Groq / Ollama / Google calls
with your own keys.

    python five_sides_sim.py            normal window
    python five_sides_sim.py --selftest runs headless checks, writes PNGs

MOCK mode (default, free)    : canned answers, simulated voice, nothing leaves the PC
LIVE mode (checkbox)          : real STT / LLM / TTS using firmware/.../secrets.h

Deliberately mirrors firmware/five_sides_cloud/five_sides_cloud.ino:
  - face()      same coordinates, same 7 moods, same blink
  - the flow     button -> listen -> STT -> LLM -> face -> TTS
  - the log      online: / heard: / say: with per-stage milliseconds
"""

import base64
import io
import json
import os
import queue
import random
import re
import sys
import threading
import time
import wave

from PIL import Image, ImageDraw, ImageTk

# ---------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SKETCH = os.path.join(PROJ, 'firmware', 'five_sides_cloud')
SECRETS = os.path.join(SKETCH, 'secrets.h')
INO = os.path.join(SKETCH, 'five_sides_cloud.ino')

DEFAULTS = {
    'WIFI_SSID': '(not set)', 'WIFI_PASS': '', 'OLLAMA_KEY': '', 'OLLAMA_MODEL': '',
    'GROQ_KEY': '', 'GTTS_KEY': '', 'ROBOT_OWNER': 'Faith', 'ROBOT_AGE': '11',
    'GTTS_VOICE': 'en-US-Neural2-F', 'GTTS_LANG': 'en-US',
    'OLLAMA_HOST': 'ollama.com', 'GROQ_HOST': 'api.groq.com',
    'GTTS_HOST': 'texttospeech.googleapis.com', 'GROQ_STT': 'whisper-large-v3-turbo',
}


def load_config():
    cfg = dict(DEFAULTS)
    for path in (SECRETS, INO):
        if not os.path.exists(path):
            continue
        for line in open(path, encoding='utf-8'):
            m = re.match(r'\s*#define\s+([A-Z_0-9]+)\s+"([^"]*)"', line)
            if m:
                cfg[m.group(1)] = m.group(2)
    return cfg


CFG = load_config()
MISSING = [k for k in ('OLLAMA_KEY', 'GROQ_KEY', 'GTTS_KEY')
           if not CFG[k] or 'YOUR' in CFG[k] or len(CFG[k]) < 8]

# ---------------------------------------------------------------- face
# Straight port of face() in the .ino. 128 x 64, 1-bit, same coordinates.
W, H = 128, 64
EX1, EX2, EY, ER = 38, 90, 26, 13

MOODS = ['idle', 'happy', 'think', 'talk', 'love', 'sleep', 'sad']


def draw_face(mood='idle', open_amt=1.0, look=0, mouth_open=0.0, talking=False,
              hands=0.0, cry=0.0, side=0):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)

    def rbox(x0, y0, x1, y1, r, fill=1):
        d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)

    def box(x, y, w, h, fill=0):
        d.rectangle([x, y, x + w, y + h], fill=fill)

    def disc(cx, cy, r, fill=1):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

    # ---- eyes
    if open_amt < 0.1 or mood == 'sleep':
        rbox(EX1 - ER, EY - 2, EX1 + ER, EY + 2, 2)
        rbox(EX2 - ER, EY - 2, EX2 + ER, EY + 2, 2)
    elif mood in ('happy', 'love'):
        for cx in (EX1, EX2):
            disc(cx, EY + 4, ER)
            box(cx - ER - 2, EY + 4, ER * 2 + 4, ER + 6)
    elif mood == 'sad':
        for cx in (EX1, EX2):
            disc(cx, EY, ER)
            box(cx - ER - 2, EY - ER - 2, ER * 2 + 4, ER + 2)
    else:
        half = int(ER * open_amt)
        for cx in (EX1, EX2):
            disc(cx, EY, ER)
            disc(cx + look, EY, 5, 0)
            box(cx - ER, EY - ER, ER * 2, ER - half)
            box(cx - ER, EY + half, ER * 2, ER - half)
            if open_amt > 0.5:                 # no stray highlight on a blink
                disc(cx + look - 2, EY - 3, 1)

    # ---- mouth
    if talking:
        # talking: only the mouth moves, the eyes keep the mood
        h = 4 + int(6 * mouth_open)
        rbox(56, int(46 - h / 2), 72, int(46 - h / 2) + h, 3)
    elif mood == 'happy':
        d.arc([64 - 11, 42 - 11, 64 + 11, 42 + 11], 0, 180, fill=1, width=2)
    elif mood == 'love':
        disc(64, 47, 4)
    elif mood == 'talk':
        h = 10 if mouth_open > 0.5 else 5
        rbox(56, 44, 72, 44 + h, 3)
    elif mood == 'sad':
        d.arc([64 - 11, 50 - 11, 64 + 11, 50 + 11], 180, 360, fill=1, width=2)
    elif mood == 'sleep':
        pass
    else:
        rbox(56, 47, 72, 51, 2)
    # ---- gesture: crying, drops running down from both eyes
    if cry > 0.01:
        t = time.time()
        for cx in (EX1, EX2):
            for k in range(3):
                ph = (t * 0.85 + k * 0.33) % 1.0
                if ph < 0.88:
                    disc(cx, 40 + int(ph * 18), 2)

    # ---- gesture: hands up
    if hands > 0.01:
        hy = int(60 - 32 * hands)                  # hand centre, rises to 28
        for x, tw in ((9, 1), (119, -1)):
            if side < 0 and x != 9:      # left hand only
                continue
            if side > 0 and x != 119:    # right hand only
                continue
            box(x - 2, hy + 4, 4, 64 - (hy + 4), 1)          # arm
            disc(x, hy + 3, 7)                                # palm
            for f in (-1, 0, 1):
                disc(x + f * 5, hy - 3, 3)                    # fingers
            disc(x + tw * 6, hy + 5, 3)                       # thumb
    return img


# ---------------------------------------------------------------- audio helpers
def wav_from_pcm(pcm, rate=24000):
    b = io.BytesIO()
    w = wave.open(b, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes(pcm)
    w.close()
    return b.getvalue()


def record_speech(max_s=6.0, silence_s=0.7, rate=16000, threshold=None):
    """Record until the speaker stops. 16 kHz mono, like the firmware.

    The first 300 ms is measured as the room's noise floor, and the trigger is
    set above it - a fan or a talking sibling would otherwise hold the mic open
    for the full 6 seconds.
    """
    import sounddevice as sd
    import numpy as np
    block = int(rate * 0.05)
    frames, spoken, quiet, total = [], False, 0.0, 0.0
    with sd.InputStream(samplerate=rate, channels=1, dtype='int16',
                        blocksize=block) as st:
        ambient = 0
        for _ in range(6):                       # 300 ms of quiet to calibrate
            data, _ = st.read(block)
            ambient = max(ambient, int(np.abs(data).max()))
        if threshold is None:
            threshold = max(900, ambient * 3)
        while total < max_s:
            data, _ = st.read(block)
            total += block / rate
            frames.append(data.copy())
            if int(np.abs(data).max()) > threshold:
                spoken, quiet = True, 0.0
            elif spoken:
                quiet += block / rate
            if spoken and quiet >= silence_s and total > 0.4:
                break
    pcm = b''.join(f.tobytes() for f in frames)
    return wav_from_pcm(pcm, rate)


def sine_wav(seconds=0.35, rate=24000, freq=520):
    n = int(seconds * rate)
    frames = bytearray()
    for i in range(n):
        v = int(9000 * (0.5 - 0.5 * (i % 2) * 1.0))  # crude square
        frames += int(12000 * (1 if (i * freq // rate) % 2 else -1)).to_bytes(
            2, 'little', signed=True)
    return wav_from_pcm(bytes(frames[:n * 2]), rate)


# ---------------------------------------------------------------- pipeline
class Pipeline:
    """The firmware's loop(), minus the hardware."""

    def __init__(self, cfg, log, face_cb, live=False, speak=True, base_url=None):
        self.cfg = cfg
        self.log = log                  # callable(line)
        self.face = face_cb             # callable(mood, **kw)
        self.live = live
        self.speak = speak
        self.base_url = base_url        # for --selftest against a stub
        self.history = []
        self.turns = 0
        self.last = {}

    # ---- url helper
    def _url(self, host, path):
        if self.base_url:
            return self.base_url.rstrip('/') + path
        return 'https://' + self.cfg[host] + path

    # ---- STEP 1 + 2
    def listen(self, typed=None, wav_path=None, audio=None):
        t0 = time.time()
        self.face('think', open_amt=1.0, look=-3)
        self.log('state: LISTENING')
        if audio is None and wav_path and os.path.exists(wav_path):
            audio = open(wav_path, 'rb').read()

        if audio and self.live:
            import requests
            files = {'file': ('a.wav', audio, 'audio/wav')}
            data = {'model': self.cfg['GROQ_STT'], 'language': 'en',
                    'response_format': 'json'}
            r = requests.post(self._url('GROQ_HOST', '/openai/v1/audio/transcriptions'),
                              headers={'Authorization': 'Bearer ' + self.cfg['GROQ_KEY']},
                              files=files, data=data, timeout=40)
            if r.status_code != 200:
                raise RuntimeError(f'STT HTTP {r.status_code}: {r.text[:160]}')
            text = r.json().get('text', '').strip()
        elif audio:
            text = (typed or '').strip() or 'hello five sides'
        else:
            text = (typed or '').strip()          # typed: the ears are skipped
            if self.live:
                self.log('(typed, so Groq is skipped this turn)', 'info')

        self.last['stt_ms'] = int((time.time() - t0) * 1000) if audio else None
        if not text:
            raise RuntimeError('nothing was heard')
        self.log(f'heard: {text}', kind='serial')
        return text

    # ---- STEP 3
    def think(self, heard):
        t0 = time.time()
        self.face('think')
        self.log('state: THINKING')
        name, age = self.cfg['ROBOT_OWNER'], self.cfg['ROBOT_AGE']
        system = (f'You are Five Sides, a small friendly desk robot that belongs to '
                  f'{name}, who is {age} years old. You have one screen for a face and '
                  f'a speaker. You are curious, warm and playful. Reply in at most 12 '
                  f'words, plain simple English, no lists, no emoji. You may ask one '
                  f'short question back. '
                  f'Your body is ONLY this screen. You have two hands and can raise '
                  f'either one alone, or both together, and you can cry real tears. '
                  f'Sides are named from the VIEWER point of view: hand_right is '
                  f'the hand on their right. You cannot wave, walk, point, nod or '
                  f'touch. If you say a hand is up you MUST set that exact gesture - '
                  f'never say right when you raised both. If asked for something you '
                  f'cannot do, say so kindly. Always answer with JSON: '
                  f'{{"say":"...","face":"idle|happy|think|love|sleep|sad",'
                  f'"gesture":"none|hands_up|hand_right|hand_left|cry"}}')

        if self.live:
            import requests
            msgs = [{'role': 'system', 'content': system}]
            for h in self.history[-8:]:
                role, txt = h.split(': ', 1) if ': ' in h else ('user', h)
                msgs.append({'role': 'assistant' if role == 'bot' else 'user',
                             'content': txt})
            msgs.append({'role': 'user', 'content': heard})
            payload = {'model': self.cfg['OLLAMA_MODEL'], 'stream': False,
                       'format': 'json', 'think': False, 'messages': msgs}
            r = requests.post(self._url('OLLAMA_HOST', '/api/chat'),
                              headers={'Authorization': 'Bearer ' + self.cfg['OLLAMA_KEY'],
                                       'Content-Type': 'application/json'},
                              json=payload, timeout=90)
            if r.status_code != 200:
                raise RuntimeError(f'LLM HTTP {r.status_code}: {r.text[:200]}')
            content = r.json().get('message', {}).get('content', '')
            try:
                inner = json.loads(content)
            except Exception:
                inner = {'say': content.strip()[:120], 'face': 'idle'}
            say, face = inner.get('say', ''), inner.get('face', 'idle')
            gest = inner.get('gesture', 'none')
        else:
            time.sleep(0.25 + random.random() * 0.35)
            say, face = self._mock_reply(heard)
            low = heard.lower()
            if any(k in low for k in ('arrest', 'hands up', 'police')):
                gest = 'hands_up'
            elif any(k in low for k in ('cry', 'tears', 'sad with me')):
                gest, face = 'cry', 'sad'
            else:
                gest = 'none'

        self.last['llm_ms'] = int((time.time() - t0) * 1000)
        self.history.append('you: ' + heard)
        self.history.append('bot: ' + say)
        chosen = face if face in MOODS else 'idle'
        if gest not in ('hands_up', 'cry', 'hand_right', 'hand_left', 'none'):
            gest = 'none'
        self.log(f'say: {say}', kind='serial')
        self.log(f'face: {chosen} · gesture: {gest}   <- from the model', kind='info')
        self.last['gesture'] = gest
        return say, chosen

    def _mock_reply(self, heard):
        low = heard.lower()
        name = self.cfg['ROBOT_OWNER']
        rules = [
            (('hello', 'hi ', 'hey'), f'Hello {name}! I am Five Sides.', 'happy'),
            (('how are you', 'kamusta'), 'I feel bright and a little bit silly.', 'happy'),
            (('your name', 'who are you'), 'I am Five Sides, your desk robot.', 'love'),
            (('joke', 'funny'), 'Why did the robot nap? It was low on batteries!', 'happy'),
            (('school', 'class'), 'School is a big adventure. What did you learn?', 'idle'),
            (('love', 'like you'), 'I like you too. You are my favourite human.', 'love'),
            (('tired', 'sleep'), 'Then rest. I will keep watch.', 'sleep'),
            (('sad', 'cry'), 'That sounds heavy. Tell me about it.', 'sad'),
            (('math', 'plus', '2+2'), 'Math is fun. Four, if you were wondering.', 'think'),
            (('robot', 'build'), 'You built me with your own hands. That is magic.', 'love'),
            (('bye', 'goodbye'), 'Bye! Press my button when you come back.', 'happy'),
        ]
        for keys, reply, face in rules:
            if any(k in low for k in keys):
                return reply, face
        return random.choice([
            ('That is interesting. Tell me more.', 'think'),
            ('I am still learning. Say it another way?', 'idle'),
            ('I like the way you think.', 'happy'),
        ])

    # ---- STEP 4
    def speak_text(self, text, mood='talk', gesture='none'):
        t0 = time.time()
        self.log('state: SPEAKING')
        if self.live:
            import requests
            payload = {'input': {'text': text},
                       'voice': {'languageCode': self.cfg['GTTS_LANG'],
                                 'name': self.cfg['GTTS_VOICE']},
                       'audioConfig': {'audioEncoding': 'LINEAR16',
                                       'sampleRateHertz': 24000,
                                       'speakingRate': 1.0}}
            r = requests.post(self._url('GTTS_HOST', '/v1/text:synthesize'),
                              headers={'x-goog-api-key': self.cfg['GTTS_KEY'],
                                       'Content-Type': 'application/json'},
                              json=payload, timeout=40)
            if r.status_code != 200:
                raise RuntimeError(f'TTS HTTP {r.status_code}: {r.text[:200]}')
            pcm = base64.b64decode(r.json().get('audioContent', ''))
            if pcm[:4] == b'RIFF':
                wav = pcm
            else:
                wav = wav_from_pcm(pcm, 24000)
            self.last['tts_bytes'] = len(pcm)
        else:
            time.sleep(0.18 + len(text) / 140.0)
            wav = sine_wav(min(0.5, 0.1 + len(text) / 200.0))
            self.last['tts_bytes'] = len(wav)

        self.last['tts_ms'] = int((time.time() - t0) * 1000)

        side = -1 if gesture == 'hand_left' else (1 if gesture == 'hand_right' else 0)
        wants_hands = gesture in ('hands_up', 'hand_left', 'hand_right')
        dur = len(wav) / 48000.0
        stop = threading.Event()

        def animate():                   # mouth flaps, eyes hold mood, hands rise
            t0 = time.time()
            while not stop.is_set():
                el = time.time() - t0
                h = min(1.0, el / 0.25) if wants_hands else 0.0
                c = 1.0 if gesture == 'cry' else 0.0
                self.face(mood, talking=True, mouth=1.0, hands=h, cry=c, side=side)
                time.sleep(0.11)
                self.face(mood, talking=True, mouth=0.1, hands=h, cry=c, side=side)
                time.sleep(0.11)

        anim = threading.Thread(target=animate, daemon=True)
        anim.start()
        if self.speak:
            import winsound
            try:
                self.last['play_ms'] = int(dur * 1000)
                winsound.PlaySound(wav, winsound.SND_MEMORY)
            except Exception as e:
                self.log(f'(audio: {e})')
                time.sleep(dur)
        else:
            time.sleep(dur)
        stop.set()
        anim.join(timeout=1)
        # hold the pose for a beat after the voice stops
        self.face(mood, mouth=0.0,
                  hands=1.0 if wants_hands else 0.0,
                  cry=1.0 if gesture == 'cry' else 0.0, side=side)
        time.sleep(2.0)          # hold the pose long enough to be seen
        return wav

    # ---- full turn
    def turn(self, typed=None, wav_path=None, audio=None):
        t0 = time.time()
        self.face('idle')
        heard = self.listen(typed=typed, wav_path=wav_path, audio=audio)
        say, mood = self.think(heard)
        self.face(mood)                       # face reacts before the voice
        time.sleep(0.15)
        self.speak_text(say, mood, self.last.get('gesture', 'none'))
        self.face('idle')
        self.turns += 1
        self.last['total_ms'] = int((time.time() - t0) * 1000)
        stt = 'n/a' if self.last['stt_ms'] is None else f"{self.last['stt_ms']} ms"
        self.log(f"turn complete: {self.last['total_ms']} ms "
                 f"(stt {stt} · llm {self.last['llm_ms']} ms · "
                 f"tts {self.last['tts_ms']} ms)", kind='ok')
        return self.last


# ---------------------------------------------------------------- self test
def selftest():
    print('FIVE SIDES simulator self-test')
    out = os.path.join(HERE, 'selftest')
    os.makedirs(out, exist_ok=True)
    for m in MOODS:
        draw_face(m, mouth_open=1.0 if m == 'talk' else 0.0).resize(
            (256, 128), Image.NEAREST).save(os.path.join(out, f'face_{m}.png'))
    draw_face('idle', open_amt=0.15).resize((256, 128), Image.NEAREST).save(
        os.path.join(out, 'face_blink.png'))
    print(f'  faces written to {out}')

    cfg = dict(CFG)
    cfg.update({'OLLAMA_KEY': 'test', 'GROQ_KEY': 'test', 'GTTS_KEY': 'test',
                'OLLAMA_MODEL': 'deepseek-v4.1-flash'})
    lines = []
    logs = []

    def log(line, kind='info'):
        logs.append(line)
        print('   |', line)

    # local stub that mimics the three endpoints
    import http.server
    import socketserver
    captured = {}

    class Stub(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            n = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(n)
            if 'transcriptions' in self.path:
                captured['stt'] = body
                resp = {'text': 'hello five sides'}
            elif self.path.endswith('/api/chat'):
                captured['llm'] = json.loads(body)
                resp = {'message': {'content': json.dumps(
                    {'say': 'Hello Faith! I am Five Sides.', 'face': 'happy'})}}
            elif 'synthesize' in self.path:
                captured['tts'] = json.loads(body)
                resp = {'audioContent': base64.b64encode(
                    sine_wav(0.25)[44:]).decode()}
            else:
                self.send_response(404); self.end_headers(); return
            out_b = json.dumps(resp).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(out_b)))
            self.end_headers()
            self.wfile.write(out_b)

    srv = socketserver.TCPServer(('127.0.0.1', 0), Stub)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{port}'

    # 16 kHz mono WAV to feed the STT path
    wavp = os.path.join(out, 'spoken.wav')
    with wave.open(wavp, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b'\x00\x01' * 8000)

    p = Pipeline(cfg, log, lambda *a, **k: None, live=True, speak=False, base_url=base)
    res = p.turn(wav_path=wavp)
    srv.shutdown()

    ok = True
    checks = [
        ('STT carried a RIFF wav', b'RIFF' in captured.get('stt', b'')),
        ('STT multipart body', b'boundary' in captured.get('stt', b'').lower()
         or b'Content-Disposition' in captured.get('stt', b'')),
        ('LLM model sent', captured.get('llm', {}).get('model') == 'deepseek-v4.1-flash'),
        ('LLM think=false', captured.get('llm', {}).get('think') is False),
        ('LLM format=json', captured.get('llm', {}).get('format') == 'json'),
        ('system prompt names owner', 'Faith' in captured.get('llm', {}).get(
            'messages', [{}])[0].get('content', '')),
        ('TTS asks LINEAR16 24k', captured.get('tts', {}).get('audioConfig', {}).get(
            'audioEncoding') == 'LINEAR16'
            and captured.get('tts', {}).get('audioConfig', {}).get('sampleRateHertz') == 24000),
        ('reply parsed', any('Hello Faith' in l for l in logs)),
        ('timings recorded', 'total_ms' in res),
    ]
    print()
    for name, good in checks:
        print(f'  [{"PASS" if good else "FAIL"}] {name}')
        ok &= good
    print('\nSELF TEST', 'PASSED' if ok else 'FAILED')
    return 0 if ok else 1


# ---------------------------------------------------------------- GUI
def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    SCALE = 5
    root = tk.Tk()
    root.title('Five Sides · robot simulator')
    root.configure(bg='#14161a')
    root.geometry('1080x680')
    root.minsize(940, 620)

    q = queue.Queue()
    state = {'mood': 'idle', 'open': 1.0, 'look': 0, 'mouth': 0.0,
             'talking': False, 'hands': 0.0, 'cry': 0.0, 'side': 0}

    # ---------- left: the robot
    left = tk.Frame(root, bg='#14161a')
    left.pack(side='left', fill='y', padx=16, pady=16)

    tk.Label(left, text='OLED · 128 × 64', bg='#14161a', fg='#6b7280',
             font=('Segoe UI', 9)).pack(anchor='w')

    bezel = tk.Frame(left, bg='#05070a', bd=0, highlightthickness=2,
                     highlightbackground='#2b3038')
    bezel.pack(pady=(4, 12))
    canvas = tk.Canvas(bezel, width=W * SCALE, height=H * SCALE,
                       bg='#05070a', highlightthickness=0)
    canvas.pack(padx=10, pady=10)
    photo_ref = {'img': None}

    def paint():
        img = draw_face(state['mood'], state['open'], state['look'],
                        state['mouth'], state['talking'],
                        state['hands'], state['cry'],
                        state['side']).convert('RGB')
        img = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
        photo_ref['img'] = ImageTk.PhotoImage(img)
        canvas.delete('all')
        canvas.create_image(0, 0, anchor='nw', image=photo_ref['img'])

    def set_face(mood, open_amt=1.0, look=0, mouth=0.0, talking=False,
                 hands=0.0, cry=0.0, side=0):
        state.update(mood=mood, open=open_amt, look=look, mouth=mouth,
                     talking=talking, hands=hands, cry=cry, side=side)
        q.put(('face', None))

    # blink + idle drift timers
    def blink_loop():
        if state['mood'] not in ('sleep', 'happy', 'love'):
            a = state['open']
            state['open'] = 0.0
            q.put(('face', None))
            root.after(110, lambda: (state.update(open=a), q.put(('face', None))))
        root.after(random.randint(2800, 6200), blink_loop)

    def drift_loop():
        if state['mood'] == 'idle':
            state['look'] = random.choice([-2, -1, 0, 1, 2])
            q.put(('face', None))
        root.after(1600, drift_loop)

    # ---------- controls
    ctl = tk.Frame(left, bg='#14161a')
    ctl.pack(fill='x')

    talk_btn = tk.Button(ctl, text='◉  PRESS BUTTON', font=('Segoe UI', 12, 'bold'),
                         bg='#d6483c', fg='white', activebackground='#b93a2f',
                         relief='flat', bd=0, pady=10, cursor='hand2')
    talk_btn.pack(fill='x')

    mic_btn = tk.Button(ctl, text='🎤  SPEAK TO IT', font=('Segoe UI', 11),
                        bg='#2563a8', fg='white', activebackground='#1d4ed8',
                        relief='flat', bd=0, pady=8, cursor='hand2',
                        command=lambda: do_turn(record=True))
    mic_btn.pack(fill='x', pady=(8, 0))

    row = tk.Frame(ctl, bg='#14161a')
    row.pack(fill='x', pady=(10, 0))
    tk.Label(row, text='Say:', bg='#14161a', fg='#9aa3af',
             font=('Segoe UI', 10)).pack(side='left')
    entry = tk.Entry(row, bg='#1c2027', fg='#e5e7eb', insertbackground='#e5e7eb',
                     relief='flat', font=('Segoe UI', 11))
    entry.pack(side='left', fill='x', expand=True, padx=8, ipady=5)
    entry.insert(0, 'hello five sides')

    opts = tk.Frame(ctl, bg='#14161a')
    opts.pack(fill='x', pady=(10, 0))
    live_var = tk.BooleanVar(value=not MISSING)   # real AI unless keys are missing
    voice_var = tk.BooleanVar(value=True)
    tk.Checkbutton(opts, text='LIVE APIs (uses your keys)', variable=live_var,
                   bg='#14161a', fg='#9aa3af', selectcolor='#1c2027',
                   activebackground='#14161a', activeforeground='white',
                   font=('Segoe UI', 9)).pack(side='left')
    tk.Checkbutton(opts, text='sound', variable=voice_var, bg='#14161a',
                   fg='#9aa3af', selectcolor='#1c2027', activebackground='#14161a',
                   activeforeground='white', font=('Segoe UI', 9)).pack(side='left', padx=12)

    moods_row = tk.Frame(ctl, bg='#14161a')
    moods_row.pack(fill='x', pady=(10, 0))
    tk.Label(moods_row, text='Face:', bg='#14161a', fg='#6b7280',
             font=('Segoe UI', 9)).pack(side='left')
    for m in MOODS:
        tk.Button(moods_row, text=m, font=('Segoe UI', 8), bg='#1c2027', fg='#9aa3af',
                  relief='flat', bd=0, padx=7, pady=3, cursor='hand2',
                  command=lambda mm=m: set_face(mm)).pack(side='left', padx=2)

    # ---------- right: log + timings
    right = tk.Frame(root, bg='#14161a')
    right.pack(side='left', fill='both', expand=True, padx=(0, 16), pady=16)

    head = tk.Frame(right, bg='#14161a')
    head.pack(fill='x')
    title = tk.Label(head, text=f"Five Sides · {CFG['ROBOT_OWNER']}",
                     bg='#14161a', fg='white', font=('Segoe UI', 14, 'bold'))
    title.pack(side='left')
    badge = tk.Label(head, text='MOCK', bg='#2b3038', fg='#9aa3af',
                     font=('Segoe UI', 9, 'bold'), padx=8, pady=2)
    badge.pack(side='left', padx=10)
    if MISSING:
        tk.Label(head, text='missing: ' + ', '.join(MISSING), bg='#14161a',
                 fg='#d6483c', font=('Segoe UI', 9)).pack(side='right')

    stats = tk.Frame(right, bg='#14161a')
    stats.pack(fill='x', pady=(10, 6))
    stat_vars = {}
    for key in ('STT', 'LLM', 'TTS', 'TOTAL'):
        f = tk.Frame(stats, bg='#1c2027')
        f.pack(side='left', padx=(0, 8), ipadx=6, ipady=2)
        tk.Label(f, text=key, bg='#1c2027', fg='#6b7280',
                 font=('Segoe UI', 8)).pack(padx=8, pady=(4, 0))
        v = tk.Label(f, text='—', bg='#1c2027', fg='#e5e7eb',
                     font=('Segoe UI', 13, 'bold'))
        v.pack(padx=8, pady=(0, 4))
        stat_vars[key] = v

    logbox = tk.Text(right, bg='#0d1014', fg='#c9d1d9', insertbackground='white',
                     relief='flat', font=('Consolas', 10), wrap='word', padx=12, pady=10)
    logbox.pack(fill='both', expand=True)
    logbox.tag_config('serial', foreground='#7ee787')
    logbox.tag_config('ok', foreground='#79c0ff')
    logbox.tag_config('err', foreground='#ff7b72')
    logbox.tag_config('info', foreground='#8b949e')

    footer = tk.Frame(right, bg='#14161a')
    footer.pack(fill='x', pady=(8, 0))

    def log(line, kind='info'):
        q.put(('log', (line, kind)))

    def gui_log(line, kind='info'):
        logbox.insert('end', f'{time.strftime("%H:%M:%S")}  {line}\n', kind)
        logbox.see('end')

    def pump():
        while True:
            try:
                kind, payload = q.get_nowait()
            except queue.Empty:
                break
            if kind == 'face':
                paint()
            elif kind == 'log':
                gui_log(*payload)
            elif kind == 'stats':
                for k, v in payload.items():
                    stat_vars[k].config(text=f'{v} ms')
            elif kind == 'busy':
                talk_btn.config(state='disabled' if payload else 'normal',
                                text='… working' if payload else '◉  PRESS BUTTON')
                mic_btn.config(state='disabled' if payload else 'normal')
        root.after(40, pump)

    # ---------- actions
    busy = {'on': False}
    # ONE pipeline for the whole session, so it remembers the last 8 turns
    pipe = Pipeline(CFG, log, set_face, live=not MISSING, speak=True)

    def do_turn(record=False):
        if busy['on']:
            return
        busy['on'] = True
        talk_btn.config(state='disabled')
        mic_btn.config(state='disabled')
        text = entry.get().strip()
        pipe.live = live_var.get()
        pipe.speak = voice_var.get()

        def work():
            try:
                audio = None
                if record:
                    log('recording… speak now', 'info')
                    audio = record_speech()
                    log(f'recorded {len(audio)//1024} kB', 'info')
                log(f"online: · {CFG['ROBOT_OWNER']} · "
                    f"{'LIVE APIs' if live_var.get() else 'MOCK'}", 'serial')
                res = pipe.turn(typed=None if audio else text, audio=audio)
                q.put(('stats', {'STT': res['stt_ms'] or '—', 'LLM': res['llm_ms'],
                                 'TTS': res['tts_ms'], 'TOTAL': res['total_ms']}))
            except Exception as e:
                log(f'error: {e}', 'err')
                set_face('sad')
            finally:
                busy['on'] = False
                q.put(('busy', False))

        threading.Thread(target=work, daemon=True).start()

    def on_talk():
        talk_btn.config(text='◉  PRESS BUTTON')
        do_turn()

    talk_btn.config(command=on_talk)
    entry.bind('<Return>', lambda e: do_turn())

    def wiring():
        messagebox.showinfo('Wiring (matches the firmware)', (
            f"OLED   SDA GPIO8 · SCL GPIO9 · addr 0x3C\n"
            f"MIC    BCLK GPIO15 · WS GPIO16 · SD GPIO17\n"
            f"AMP    BCLK GPIO4 · LRC GPIO5 · DIN GPIO6\n"
            f"BUTTON GPIO18 → GND\n"
            f"LED    GPIO38 (on-board)\n\n"
            f"Owner: {CFG['ROBOT_OWNER']} ({CFG['ROBOT_AGE']})\n"
            f"Voice: {CFG['GTTS_VOICE']}\n"
            f"Model: {CFG['OLLAMA_MODEL']}"))

    tk.Button(footer, text='Wiring / config', font=('Segoe UI', 9), bg='#1c2027',
              fg='#9aa3af', relief='flat', bd=0, padx=12, pady=6, cursor='hand2',
              command=wiring).pack(side='left')
    tk.Label(footer, text='Space = press · the mic button talks', bg='#14161a', fg='#4b5563',
             font=('Segoe UI', 9)).pack(side='right')
    root.bind('<space>', lambda e: (entry.focus_set() or True) and do_turn())

    def live_changed():
        badge.config(text='LIVE' if live_var.get() else 'MOCK',
                     bg='#1f6f43' if live_var.get() else '#2b3038',
                     fg='white' if live_var.get() else '#9aa3af')
        if live_var.get() and MISSING:
            messagebox.showwarning(
                'Keys missing',
                'secrets.h is missing: ' + ', '.join(MISSING) +
                '\n\nLIVE mode will fail on those calls. MOCK still works.')

    live_var.trace_add('write', lambda *a: live_changed())
    live_changed()                       # reflect the starting state, not just changes

    paint()
    gui_log('simulator ready', 'ok')
    if live_var.get():
        gui_log('LIVE: real Groq + Ollama + Google, keys from secrets.h', 'ok')
        gui_log(f"model {CFG['OLLAMA_MODEL']} · voice {CFG['GTTS_VOICE']}", 'info')
        gui_log('Type, or press SPEAK TO IT and talk to it.', 'info')
    else:
        gui_log('MOCK mode: canned answers, no network, no cost.', 'info')
        gui_log('Tick LIVE APIs to use Groq + Ollama + Google for real.', 'info')
    root.after(150, pump)
    if '--demo-hands' in sys.argv:
        entry.delete(0, 'end')
        entry.insert(0, 'Hands up! You are under arrest!')
        root.after(1200, do_turn)
    elif '--demo' in sys.argv:
        gui_log('demo: firing one turn automatically', 'info')
        root.after(1200, do_turn)
    root.after(3000, blink_loop)
    root.after(2000, drift_loop)
    root.mainloop()


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    if '--live-test' in sys.argv:
        i = sys.argv.index('--live-test')
        say = sys.argv[i + 1] if len(sys.argv) > i + 1 else 'hello five sides'
        print('LIVE turn:', say)
        p = Pipeline(CFG, lambda l, kind='info': print('   |', l),
                     lambda *a, **k: None, live=True, speak=False)
        r = p.turn(typed=say)
        print()
        print('  stt', r['stt_ms'], 'llm', r['llm_ms'], 'tts', r['tts_ms'],
              'total', r['total_ms'], 'ms ·', r.get('tts_bytes'), 'audio bytes')
        sys.exit(0)
    run_gui()
