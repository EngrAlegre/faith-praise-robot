# Cloud-direct setup (no laptop)

The robot talks to three services by itself. No server, no PC in the loop.

```
button → record → Groq Whisper → Ollama Cloud → Google TTS → speaker
                     (ears)          (brain)        (voice)
```

Sketch: `firmware/five_sides_cloud/five_sides_cloud.ino`
Compiles to 34 % of a 16 MB board, verified with
`PSRAM=opi, FlashSize=16M, PartitionScheme=huge_app, CDCOnBoot=cdc`.

---

## 1. Get the three keys

### Groq — ears (free, no card)
1. console.groq.com → sign up
2. **API Keys** → Create
3. Model used: `whisper-large-v3-turbo` (already in the sketch)

Free tier has a daily audio allowance. Two kids will not come close, but if the
robot ever answers "I could not reach my brain", check the Groq console first.

### Ollama Cloud — brain (your key)
1. ollama.com → sign in → **API keys** → create
2. Pick the model in the library and **copy its exact id** — it usually carries a
   suffix, e.g. `something:latest-cloud`. Paste it into `OLLAMA_MODEL`.
3. Endpoint used: `https://ollama.com/api/chat` (the native API, not `/v1`)

### Google Cloud TTS — voice (free tier, billing must be enabled)
1. console.cloud.google.com → new project (or reuse one)
2. **APIs & Services → Library → Cloud Text-to-Speech API → Enable**
3. **Billing** must be switched on — Google requires a card even inside the free
   allowance
4. **APIs & Services → Credentials → Create credentials → API key**
5. Restrict the key to the Text-to-Speech API, so a stolen key can't do anything else

Free allowance per month: **Standard 4 M characters, WaveNet 4 M, Neural2 1 M**.
The sketch asks for a Neural2 voice (`en-US-Neural2-F`), so budget 1 M characters —
roughly 150,000 words. A chatty week is a few thousand characters.

---

## 2. Fill in the config block

At the top of the sketch:

```cpp
#define ROBOT_OWNER   "Faith"          // second board: "Praise"
#define ROBOT_AGE     "11"             // second board: "9"

#define WIFI_SSID     "..."
#define WIFI_PASS     "..."

#define OLLAMA_KEY    "..."
#define OLLAMA_MODEL  "paste-the-exact-id-here"

#define GROQ_KEY      "..."

#define GTTS_KEY      "..."
#define GTTS_VOICE    "en-US-Neural2-F"   // other options below
```

Voices worth trying:

| Voice | Sound |
|---|---|
| `en-US-Neural2-F` | warm female (default) |
| `en-US-Neural2-C` | female, brighter |
| `en-US-Neural2-D` | male, calm |
| `en-US-Wavenet-F` | warm female, slightly softer |

The persona ("belongs to Faith, who is 11, answers in 12 words") is built from
`ROBOT_OWNER` and `ROBOT_AGE` — change those two lines and the same firmware
becomes Praise's robot, with his own greetings and his own sense of who he is.

---

## 3. Flash the two robots

Same sketch twice, different config block:

| | Robot 1 | Robot 2 |
|---|---|---|
| `ROBOT_OWNER` | `"Faith"` | `"Praise"` |
| `ROBOT_AGE` | `"11"` | `"9"` |
| `GTTS_VOICE` | pick one | pick the **other** — they should not sound identical |

---

## 4. Test in this order

| Step | What to check | Why in this order |
|---|---|---|
| 1 | Serial prints `online: 192.168.x.x` | WiFi before anything else |
| 2 | press button, Serial prints `heard: ...` | Groq + the mic |
| 3 | Serial prints `say: ...` | Ollama + the persona |
| 4 | it speaks out loud | Google TTS + I2S |
| 5 | the face matches the mood | the last, easiest piece |

The face changes **before** the audio starts — that's deliberate. The eyes move
about 0.4 s earlier, so waiting for speech feels like attention, not lag.

---

## 5. Things that will bite

1. **Two keys in one robot's flash.** Anyone with a USB cable can read them.
   Use a Groq account you don't mind losing and a **spend-capped** Ollama key.
2. **Google needs billing enabled.** The free tier is real, but a card must be on
   the project. Set a budget alert at ₱1 so a bug can't run up a bill.
3. **`en-US` vs Filipino-accented English.** The robot speaks US English. If the
   kids want it to sound local, change `GTTS_LANG`/`GTTS_VOICE` to a `fil-PH` or
   `en-PH` voice if one is available on the account — the API will reject a voice
   name that doesn't exist, and the Serial monitor will say so.
4. **Base64 audio is big.** A 5-second answer is ~240 KB of PCM, ~320 KB encoded.
   The sketch allocates 700 KB of PSRAM for it — that is why the N16R8 (8 MB)
   board is mandatory and the N8R2 is not enough.
5. **First question of the session is slowest** — three TLS handshakes. After
   that the connections are reused and it settles at 1.5–2.5 s.
6. **The microphone hears the speaker.** The sketch is half-duplex: recording
   only happens while the button is held-ish, and playback happens after. Don't
   add always-listening without echo cancellation.

---

## 6. What this robot cannot do

- No internet → no answers. It shows a sad face and says "I cannot find the wifi."
- No wake word yet. It's a button. "Hi ESP" is a separate firmware job, and a
  custom "Hey Five" needs a model trained by Espressif.
- It will not remember yesterday. It keeps the last 8 turns in RAM only; a power
  cycle wipes them. Saving to NVS is a 20-line addition if they want it.
