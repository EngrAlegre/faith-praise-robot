# Five Sides · desktop simulator

Trials the ESP32-S3 robot **on the PC**, before the hardware is finished.

It runs the same face, the same conversation flow and the same log lines as
`firmware/five_sides_cloud/five_sides_cloud.ino`, so a mistake shows up here in
seconds instead of on a printed robot.

```
simulator/
├─ Run Simulator.bat        double-click this
├─ five_sides_sim.py        the app
├─ selftest/                face PNGs + the self-test
└─ README.md
```

## Run it

Double-click **Run Simulator.bat**. Nothing to install — it uses the Python 3.12
already on the machine (tkinter, PIL, requests).

Or from a terminal, which is better if something misbehaves because errors show:

```
C:\Users\isaac\AppData\Local\Programs\Python\Python312\python.exe five_sides_sim.py
```

## Two modes

| | MOCK | LIVE (default when keys are present) |
|---|---|---|
| Ears | your typed text | **your microphone**, via Groq Whisper |
| Brain | canned rules | Ollama Cloud, your model |
| Voice | silence + simulated timing | Google TTS, real speech from the speakers |
| Cost | nothing | fractions of a centavo per turn |

Tick **LIVE APIs** to use the real services. The keys are read from
`firmware/five_sides_cloud/secrets.h` — you do not enter them again here, and
nothing is duplicated.

Untick **sound** to run turns silently while checking timings or faces.

## What it actually tests

- the **face**: all seven moods, blink, idle drift — pixel-for-pixel the same
  coordinates as the firmware's `face()`
- the **flow**: press → listen → think → face reacts → speak
- the **log**: `online:` / `heard:` / `say:` in the same order as the Serial
  monitor, so a failure points at the same stage it would on the robot
- **latency per stage**, which is the number that decides whether the robot feels
  alive or broken
- the **API calls themselves**: multipart upload, JSON parsing, base64 PCM, WAV
  wrapping — verified by `--selftest` against a local stub server

## What it cannot test

- **nothing about the microphone is left untested** — `sounddevice` is installed,
  capture is verified at 16 kHz mono, and the voice detection calibrates itself
  against the room for the first 300 ms before it starts listening.
- **the real speaker.** Mock mode plays a placeholder tone so you know when the
  robot would be talking. Voice quality can only be judged on the Google TTS path
  or on the robot itself.
- **wiring.** It proves the code, never the soldering.


## Gestures

The model can do two things with its body, and it must declare them in the reply:

| gesture | what the screen does |
|---|---|
| `none` | just the face |
| `hands_up` | two mittens rise beside the head, hold while speaking, then lower |
| `cry` | tear drops run down beneath both eyes |

The system prompt tells it that the screen **is** its whole body: no waving, no
pointing, no nodding — and that it must never claim a gesture it did not set. Ask
"raise your right hand" and it answers *"I can't raise one hand, only both
together. Want me to?"* instead of pretending.

Both gestures exist in the firmware too, driven by the same JSON field.

## Self-test

```
python five_sides_sim.py --selftest
```

Writes every face to `selftest/`, spins up a local stub that pretends to be
Groq + Ollama + Google, runs a full turn through the real HTTP code, and checks
nine things — the WAV is in the multipart body, `think:false` and `format:json`
are sent, the system prompt names the owner, TTS asks for LINEAR16 at 24 kHz, and
the reply parses. All nine pass.

Run this after any firmware change: it is much faster than reflashing.

## Keyboard

- **Space** — press the robot's button
- **Enter** in the Say box — same thing

## Notes

- The face renderer and `face()` in the .ino are deliberately kept identical.
  A bug found in one applies to the other — the blink highlight bug was found
  exactly this way and fixed in both.
- GPIO map is under **Wiring / config**, taken from the firmware, not retyped
  from memory.
