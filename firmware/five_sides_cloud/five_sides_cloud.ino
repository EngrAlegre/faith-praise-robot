/* ============================================================================
   FIVE SIDES · cloud-direct firmware  (no laptop, no server)
   ----------------------------------------------------------------------------
   Faith's robot and Praise's robot run THIS SAME SKETCH. The only difference
   is the config block below - change ROBOT_OWNER and the voice, flash the
   second board.

   WHAT HAPPENS WHEN THEY PRESS THE BUTTON
     1. records until they stop talking (or 6 s)
     2. Groq Whisper        audio -> text        (free tier)
     3. Ollama Cloud        text  -> answer+face (your key, DeepSeek)
     4. Google TTS          answer -> PCM audio  (free tier)
     5. the OLED shows the face, the speaker talks

   LIBRARIES:  ArduinoJson, U8g2
   BOARD:      ESP32S3 Dev Module, PSRAM: OPI, Flash 16MB, Partition Huge APP
   ========================================================================== */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <driver/i2s_std.h>

// ============================ WHO IS THIS ROBOT ============================
#define ROBOT_OWNER   "Faith"                   // second board: "Praise"
#define ROBOT_AGE     "11"                      // second board: "9"

// All keys, passwords and the model id live in secrets.h - nothing secret here.
#include "secrets.h"

// ---- endpoints (not secret) -----------------------------------------------
#define OLLAMA_HOST   "ollama.com"
#define GROQ_HOST     "api.groq.com"
#define GROQ_STT      "whisper-large-v3-turbo"

// ---- voice (not secret) ---------------------------------------------------
#define GTTS_HOST     "texttospeech.googleapis.com"
#define GTTS_VOICE    "en-US-Neural2-F"         // warm female; or -Neural2-D (male)
#define GTTS_LANG     "en-US"
// ===========================================================================

// ------------------------------- pins --------------------------------------
// ---- display: 4-pin I2C module, or 7-pin SPI module ---------------------
#ifndef DISPLAY_I2C
#define DISPLAY_I2C   1        // 1 = I2C (4 pins, address 0x3C)  |  0 = SPI (7 pins)
#endif
#define OLED_RESET_PIN 12      // wire the module's RES here; a 4-pin module ignores it
const int PIN_SDA = 8, PIN_SCL = 9;                       // I2C: SDA / SCL
const int PIN_I2S_OUT_BCLK = 4, PIN_I2S_OUT_LRC = 5, PIN_I2S_OUT_DIN = 6;
const int PIN_I2S_IN_BCLK  = 15, PIN_I2S_IN_WS  = 16, PIN_I2S_IN_SD  = 17;
const int PIN_BUTTON = 18;
const int PIN_LED = 38;

// ------------------------------- audio -------------------------------------
static const int MIC_HZ  = 16000;
static const int PLAY_HZ = 24000;                          // Google LINEAR16 output
static const int MAX_REC_SECONDS = 6;
static const size_t MAX_REC_SAMPLES = MIC_HZ * MAX_REC_SECONDS;
static const int PLAY_VOLUME_PCT = 62;     // 1 W speaker on a 1.8 W amp - keep headroom
static const size_t MAX_TTS_BYTES = 700 * 1024;            // ~7 s of 24 kHz PCM, base64 already decoded

int16_t* recBuf = nullptr;                                  // PSRAM
uint8_t* ttsBuf = nullptr;                                  // PSRAM
size_t   recLen = 0;

i2s_chan_handle_t txChan = nullptr, rxChan = nullptr;

// keep one TLS connection per host alive - a fresh handshake is 300-800 ms
WiFiClientSecure sttCli, llmCli, ttsCli;

// ------------------------------- face --------------------------------------
#if DISPLAY_I2C
U8G2_SSD1309_128X64_NONAME0_F_HW_I2C oled(U8G2_R0, OLED_RESET_PIN);
#else
const int PIN_OLED_CS = 10, PIN_OLED_DC = 11;
U8G2_SSD1309_128X64_NONAME0_F_4W_HW_SPI oled(U8G2_R0, PIN_OLED_CS, PIN_OLED_DC, OLED_RESET_PIN);
#endif

enum Mood { M_IDLE, M_HAPPY, M_THINK, M_TALK, M_LOVE, M_SLEEP, M_SAD };

void face(Mood m, float open = 1.0f, int look = 0, float talk = -1.0f,
          float hands = 0.0f, float cry = 0.0f, int side = 0) {
  const int ex1 = 38, ex2 = 90, ey = 26, er = 13;
  oled.clearBuffer();
  oled.setDrawColor(1);
  if (open < 0.1f || m == M_SLEEP) {
    oled.drawRBox(ex1 - er, ey - 2, er * 2, 4, 2);
    oled.drawRBox(ex2 - er, ey - 2, er * 2, 4, 2);
  } else if (m == M_HAPPY || m == M_LOVE) {
    for (int e = 0; e < 2; e++) {
      int cx = e ? ex2 : ex1;
      oled.drawDisc(cx, ey + 4, er);
      oled.setDrawColor(0);
      oled.drawBox(cx - er - 2, ey + 4, er * 2 + 4, er + 6);
      oled.setDrawColor(1);
    }
  } else if (m == M_SAD) {
    for (int e = 0; e < 2; e++) {
      int cx = e ? ex2 : ex1;
      oled.drawDisc(cx, ey, er);
      oled.setDrawColor(0);
      oled.drawBox(cx - er - 2, ey - er - 2, er * 2 + 4, er + 2);
      oled.setDrawColor(1);
    }
  } else {
    int half = (int)(er * open);
    for (int e = 0; e < 2; e++) {
      int cx = e ? ex2 : ex1;
      oled.drawDisc(cx, ey, er);
      oled.setDrawColor(0);
      oled.drawDisc(cx + look, ey, 5);
      oled.drawBox(cx - er, ey - er, er * 2, er - half);
      oled.drawBox(cx - er, ey + half, er * 2, er - half);
      oled.setDrawColor(1);
      if (open > 0.5f) oled.drawDisc(cx + look - 2, ey - 3, 1);
    }
  }
  if (talk >= 0.0f) {
    // talking: only the mouth moves, the eyes keep whatever mood was chosen
    int mh = 4 + (int)(6.0f * talk);
    oled.drawRBox(56, 46 - mh / 2, 16, mh, 3);
  } else switch (m) {
    case M_HAPPY: oled.drawCircle(64, 42, 11, U8G2_DRAW_LOWER_LEFT | U8G2_DRAW_LOWER_RIGHT); break;
    case M_LOVE:  oled.drawDisc(64, 47, 4); break;
    case M_TALK:  oled.drawRBox(56, 44, 16, 10, 4); break;
    case M_SAD:   oled.drawCircle(64, 50, 11, U8G2_DRAW_UPPER_LEFT | U8G2_DRAW_UPPER_RIGHT); break;
    case M_SLEEP: break;
    default:      oled.drawRBox(56, 47, 16, 4, 2); break;
  }
  // ---- gesture: crying, drops running down from both eyes
  if (cry > 0.01f) {
    for (int e = 0; e < 2; e++) {
      int cx = e ? 90 : 38;
      for (int k = 0; k < 3; k++) {
        float ph = fmod(millis() / 1100.0f + k * 0.33f, 1.0f);
        if (ph < 0.88f) oled.drawDisc(cx, 40 + (int)(ph * 18.0f), 2);
      }
    }
  }

  // ---- gesture: both hands raised beside the head
  if (hands > 0.01f) {
    int hy = 60 - (int)(32.0f * hands);
    for (int s = 0; s < 2; s++) {
      if (side < 0 && s == 1) continue;      // left hand only
      if (side > 0 && s == 0) continue;      // right hand only
      int x  = s ? 119 : 9;
      int tw = s ? -1 : 1;
      oled.drawBox(x - 2, hy + 4, 4, 64 - (hy + 4));      // arm
      oled.drawDisc(x, hy + 3, 7);                        // palm
      for (int f = -1; f <= 1; f++) oled.drawDisc(x + f * 5, hy - 3, 3);
      oled.drawDisc(x + tw * 6, hy + 5, 3);               // thumb
    }
  }
  oled.sendBuffer();
}

// ------------------------------- i2s ---------------------------------------
void audioBegin() {
  i2s_chan_config_t c0 = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  i2s_new_channel(&c0, &txChan, nullptr);
  i2s_std_config_t s0 = {
    .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(PLAY_HZ),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)PIN_I2S_OUT_BCLK,
                  .ws = (gpio_num_t)PIN_I2S_OUT_LRC, .dout = (gpio_num_t)PIN_I2S_OUT_DIN,
                  .din = I2S_GPIO_UNUSED, .invert_flags = { false, false, false } },
  };
  i2s_channel_init_std_mode(txChan, &s0);
  i2s_channel_enable(txChan);

  i2s_chan_config_t c1 = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
  i2s_new_channel(&c1, nullptr, &rxChan);
  i2s_std_config_t s1 = {
    .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(MIC_HZ),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)PIN_I2S_IN_BCLK,
                  .ws = (gpio_num_t)PIN_I2S_IN_WS, .dout = I2S_GPIO_UNUSED,
                  .din = (gpio_num_t)PIN_I2S_IN_SD, .invert_flags = { false, false, false } },
  };
  i2s_channel_init_std_mode(rxChan, &s1);
  i2s_channel_enable(rxChan);
}

Mood  gSpeakMood = M_TALK;      // eyes used while the voice plays
bool  gMouthOpen = false;
bool  gHandsUp   = false;       // gestures requested by the model
bool  gCry       = false;
int   gHandSide  = 0;           // 0 both, -1 left, +1 right
unsigned long gMouthT = 0;
unsigned long gSpeakStart = 0;

void playPcm(const uint8_t* data, size_t bytes) {
  // The amp can push ~1.8 W into 8 ohm; a 1 W speaker must not see full scale.
  // Scaling in software is cleaner than fighting the GAIN pin.
  const size_t CHUNK = 256;
  static int16_t chunk[CHUNK];
  const int16_t* src = (const int16_t*)data;
  size_t total = bytes / 2, i = 0;
  while (i < total) {
    size_t n = (total - i < CHUNK) ? (total - i) : CHUNK;
    for (size_t k = 0; k < n; k++)
      chunk[k] = (int16_t)((int32_t)src[i + k] * PLAY_VOLUME_PCT / 100);
    size_t wrote = 0;
    if (i2s_channel_write(txChan, chunk, n * 2, &wrote, 1000) != ESP_OK) break;
    if (millis() - gMouthT > 110) {
      gMouthT = millis(); gMouthOpen = !gMouthOpen;
      unsigned long el = millis() - gSpeakStart;
      float h = gHandsUp ? (el < 250 ? el / 250.0f : 1.0f) : 0.0f;
      face(gSpeakMood, 1.0f, 0, gMouthOpen ? 1.0f : 0.15f, h,
           gCry ? 1.0f : 0.0f, gHandSide);
    }
    if (!wrote) break;
    i += wrote / 2;
  }
}

// -------------------------- record with voice activity ----------------------
// Records until the room goes quiet for QUIET_MS, or MAX_REC_SECONDS.
// Returns the number of samples captured.
size_t recordSpeech() {
  const int   BLOCK = 256;
  const float THRESHOLD_MIN = 700.0f;
  const int   QUIET_MS = 700;
  const int   MIN_MS   = 300;

  int32_t raw[BLOCK];

  // Measure the room for ~300 ms first and put the trigger above its noise
  // floor. A fan, a TV or a sibling would otherwise hold the mic open for the
  // full 6 seconds and send six seconds of nothing to Whisper.
  float ambient = 0;
  for (int b = 0; b < 6; b++) {
    size_t g = 0;
    if (i2s_channel_read(rxChan, raw, sizeof(raw), &g, 300) != ESP_OK) continue;
    for (size_t i = 0; i < g / sizeof(int32_t); i++) {
      float a = fabsf((float)(int16_t)(raw[i] >> 16));
      if (a > ambient) ambient = a;
    }
  }
  const float THRESHOLD = ambient * 3.0f > THRESHOLD_MIN ? ambient * 3.0f : THRESHOLD_MIN;
  Serial.printf("mic floor %.0f, trigger %.0f\n", ambient, THRESHOLD);
  size_t total = 0;
  bool  spoken = false;
  uint32_t lastLoud = millis();
  uint32_t start = millis();

  while (total < MAX_REC_SAMPLES && (millis() - start) < (MAX_REC_SECONDS + 3) * 1000UL) {
    size_t got = 0;
    if (i2s_channel_read(rxChan, raw, sizeof(raw), &got, 300) != ESP_OK) continue;
    size_t n = got / sizeof(int32_t);
    if (!n) continue;

    float peak = 0;
    for (size_t i = 0; i < n && total < MAX_REC_SAMPLES; i++) {
      int16_t s = (int16_t)(raw[i] >> 16);          // INMP441: 24-bit left-justified in 32
      recBuf[total++] = s;
      float a = fabsf(s);
      if (a > peak) peak = a;
    }
    if (peak > THRESHOLD) { spoken = true; lastLoud = millis(); }
    bool longEnough = (millis() - start) > MIN_MS;
    if (spoken && longEnough && (millis() - lastLoud) > QUIET_MS) break;
  }
  recLen = total;
  return total;
}

size_t wavHeader(uint8_t* h, size_t pcm, int rate) {
  uint32_t chunk = 36 + pcm, sub = pcm, byteRate = rate * 2;
  uint16_t ch = 1, align = 2, bits = 16, pcmFmt = 1;
  uint32_t sixteen = 16;
  memcpy(h, "RIFF", 4); memcpy(h + 4, &chunk, 4); memcpy(h + 8, "WAVE", 4);
  memcpy(h + 12, "fmt ", 4); memcpy(h + 16, &sixteen, 4); memcpy(h + 20, &pcmFmt, 2);
  memcpy(h + 22, &ch, 2); memcpy(h + 24, &rate, 4); memcpy(h + 28, &byteRate, 4);
  memcpy(h + 32, &align, 2); memcpy(h + 34, &bits, 2); memcpy(h + 36, "data", 4);
  memcpy(h + 40, &sub, 4);
  return 44;
}

// ------------------------------- STEP 2: Groq whisper ------------------------
bool transcribe(String& outText) {
  if (!recLen) return false;

  size_t pcmBytes = recLen * 2;
  size_t total = 44 + pcmBytes;
  uint8_t* body = (uint8_t*)ps_malloc(total);
  if (!body) return false;
  wavHeader(body, pcmBytes, MIC_HZ);
  memcpy(body + 44, recBuf, pcmBytes);

  // multipart envelope
  String head = "--BOUND\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\n"
                "Content-Type: audio/wav\r\n\r\n";
  String tail = "\r\n--BOUND\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n" +
                String(GROQ_STT) +
                "\r\n--BOUND\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nen"
                "\r\n--BOUND\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\njson"
                "\r\n--BOUND--\r\n";

  HTTPClient http;
  if (!http.begin(sttCli, "https://" GROQ_HOST "/openai/v1/audio/transcriptions")) { free(body); return false; }
  http.setReuse(true);
  http.setTimeout(20000);
  http.addHeader("Authorization", "Bearer " GROQ_KEY);
  http.addHeader("Content-Type", "multipart/form-data; boundary=BOUND");

  size_t len = head.length() + total + tail.length();
  uint8_t* mp = (uint8_t*)ps_malloc(len);
  if (!mp) { free(body); http.end(); return false; }
  size_t p = 0;
  memcpy(mp + p, head.c_str(), head.length()); p += head.length();
  memcpy(mp + p, body, total); p += total;
  memcpy(mp + p, tail.c_str(), tail.length());
  free(body);

  int code = http.POST(mp, len);
  free(mp);
  bool ok = false;
  if (code == 200) {
    JsonDocument doc;
    if (!deserializeJson(doc, http.getString())) {
      const char* t = doc["text"] | "";
      outText = t;
      outText.trim();
      ok = outText.length() > 0;
    }
  } else {
    Serial.printf("STT http %d %s\n", code, http.getString().c_str());
  }
  http.end();
  return ok;
}

// --------------------------- STEP 3: Ollama Cloud ---------------------------
// Keeps the last few turns so it feels like a conversation, and remembers
// who it belongs to.
String history[8];          // ring of "user: ..." / "bot: ..."
int    histCount = 0;

void pushHistory(const String& who, const String& what) {
  if (histCount < 8) history[histCount] = who + ": " + what;
  else {
    for (int i = 1; i < 8; i++) history[i - 1] = history[i];
    history[7] = who + ": " + what;
  }
  if (histCount < 8) histCount++;
}

bool think(const String& heard, String& say, String& faceName, String& gesture) {
  JsonDocument doc;
  doc["model"]  = OLLAMA_MODEL;
  doc["stream"] = false;
  doc["format"] = "json";
  doc["think"]  = false;          // DeepSeek is a reasoning model - skip the
                                  // thinking pass, it would add 1-3 s per reply
  JsonArray msgs = doc["messages"].to<JsonArray>();

  String sys = String("You are Five Sides, a small friendly desk robot that belongs to ") +
               ROBOT_OWNER + ", who is " + ROBOT_AGE + " years old. "
               "You have one screen for a face and a speaker. You are curious, warm and playful. "
               "Reply in at most 12 words, plain simple English, no lists, no emoji. "
               "You may ask one short question back. "
               "Your body is ONLY this screen. You have two hands and can raise "
               "either one alone or both together, and you can cry real tear drops. "
               "Sides are named from the viewer's point of view: hand_right is the "
               "hand on their right. You cannot wave, walk, point, nod or touch. "
               "If you say a hand is up, you MUST set that exact gesture - never say "
               "right when you raised both. If asked for something you cannot do, "
               "say so kindly. "
               "Always answer with JSON: {\"say\":\"...\","
               "\"face\":\"idle|happy|think|love|sleep|sad\","
               "\"gesture\":\"none|hands_up|hand_right|hand_left|cry\"}";
  JsonObject s0 = msgs.add<JsonObject>();
  s0["role"] = "system"; s0["content"] = sys;
  for (int i = 0; i < histCount; i++) {
    JsonObject m = msgs.add<JsonObject>();
    bool isBot = history[i].startsWith("bot:");
    m["role"]    = isBot ? "assistant" : "user";
    m["content"] = history[i].substring(5);
  }
  JsonObject u = msgs.add<JsonObject>();
  u["role"] = "user"; u["content"] = heard;

  String payload; serializeJson(doc, payload);

  HTTPClient http;
  if (!http.begin(llmCli, "https://" OLLAMA_HOST "/api/chat")) return false;
  http.setReuse(true);
  http.setTimeout(30000);
  http.addHeader("Authorization", "Bearer " OLLAMA_KEY);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(payload);
  bool ok = false;
  if (code == 200) {
    JsonDocument r;
    if (!deserializeJson(r, http.getString())) {
      const char* content = r["message"]["content"] | "";
      JsonDocument inner;
      if (!deserializeJson(inner, content)) {
        say      = String((const char*)(inner["say"] | ""));
        faceName = String((const char*)(inner["face"] | "idle"));
        gesture  = String((const char*)(inner["gesture"] | "none"));
        ok = say.length() > 0;
      }
    }
  } else {
    Serial.printf("LLM http %d %s\n", code, http.getString().c_str());
  }
  http.end();
  return ok;
}

// ----------------------------- STEP 4: Google TTS ---------------------------
int b64val(char c) {
  if (c >= 'A' && c <= 'Z') return c - 'A';
  if (c >= 'a' && c <= 'z') return c - 'a' + 26;
  if (c >= '0' && c <= '9') return c - '0' + 52;
  if (c == '+') return 62;
  if (c == '/') return 63;
  return -1;
}

size_t b64decode(const char* in, size_t inLen, uint8_t* out, size_t outMax) {
  size_t o = 0; int buf = 0, bits = 0;
  for (size_t i = 0; i < inLen && o < outMax; i++) {
    int v = b64val(in[i]);
    if (v < 0) continue;
    buf = (buf << 6) | v; bits += 6;
    if (bits >= 8) { bits -= 8; out[o++] = (uint8_t)((buf >> bits) & 0xFF); }
  }
  return o;
}

bool speak(const String& text, Mood mood = M_TALK, String gesture = "none") {
  gSpeakMood  = mood;
  gCry        = (gesture == "cry");
  gHandsUp    = (gesture == "hands_up") || gesture.startsWith("hand_");
  gHandSide   = (gesture == "hand_left") ? -1 : (gesture == "hand_right") ? 1 : 0;
  gSpeakStart = millis();
  JsonDocument doc;
  doc["input"]["text"] = text;
  doc["voice"]["languageCode"] = GTTS_LANG;
  doc["voice"]["name"]         = GTTS_VOICE;
  doc["audioConfig"]["audioEncoding"]    = "LINEAR16";
  doc["audioConfig"]["sampleRateHertz"]  = PLAY_HZ;
  doc["audioConfig"]["speakingRate"]     = 1.0;
  String payload; serializeJson(doc, payload);

  HTTPClient http;
  if (!http.begin(ttsCli, "https://" GTTS_HOST "/v1/text:synthesize")) return false;
  http.setReuse(true);
  http.setTimeout(20000);
  http.addHeader("x-goog-api-key", GTTS_KEY);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(payload);
  bool ok = false;
  if (code == 200) {
    JsonDocument r;
    if (!deserializeJson(r, http.getString())) {
      const char* b64 = r["audioContent"] | "";
      size_t n = b64decode(b64, strlen(b64), ttsBuf, MAX_TTS_BYTES);
      if (n > 44) {
        const uint8_t* pcm = ttsBuf;
        if (!memcmp(ttsBuf, "RIFF", 4)) { pcm += 44; n -= 44; }   // header included
        playPcm(pcm, n);
        ok = true;
      }
    }
  } else {
    Serial.printf("TTS http %d %s\n", code, http.getString().c_str());
  }
  http.end();
  return ok;
}

// ------------------------------- helpers ------------------------------------
Mood moodFrom(const String& s) {
  if (s == "happy") return M_HAPPY;
  if (s == "think") return M_THINK;
  if (s == "talk")  return M_TALK;
  if (s == "love")  return M_LOVE;
  if (s == "sleep") return M_SLEEP;
  if (s == "sad")   return M_SAD;
  return M_IDLE;
}

void chirp(bool good) {
  face(good ? M_HAPPY : M_SAD);
  delay(400);
}

// ------------------------------- config guard -------------------------------
// A missing key still compiles. This prints exactly which one is empty at boot,
// instead of leaving the robot silently failing with HTTP 401 later.
bool unset(const char* v) {
  return strlen(v) < 8 || strstr(v, "YOUR_") || strstr(v, "COPY-THE");
}

int configCheck() {
  const char* names[] = { "WIFI_SSID", "OLLAMA_KEY", "OLLAMA_MODEL", "GROQ_KEY", "GTTS_KEY" };
  const char* vals[]  = { WIFI_SSID,   OLLAMA_KEY,   OLLAMA_MODEL,   GROQ_KEY,   GTTS_KEY };
  int bad = 0;
  for (int i = 0; i < 5; i++) {
    if (unset(vals[i])) { Serial.printf("!! secrets.h: %s is not filled in\n", names[i]); bad++; }
  }
  if (bad) Serial.printf("!! %d key(s) missing - the robot cannot talk yet\n", bad);
  return bad;
}

// ------------------------------- setup / loop -------------------------------
void setup() {
  Serial.begin(115200);
  delay(200);
  int missing = configCheck();

#if DISPLAY_I2C
  Wire.begin(PIN_SDA, PIN_SCL);          // SPI mode lets U8g2 start SPI itself
#endif
  oled.begin();
  oled.setBusClock(400000);
  face(missing ? M_SAD : M_IDLE);

  audioBegin();
  recBuf = (int16_t*)ps_malloc(MAX_REC_SAMPLES * sizeof(int16_t));
  ttsBuf = (uint8_t*)ps_malloc(MAX_TTS_BYTES);
  if (!recBuf || !ttsBuf) { Serial.println("PSRAM alloc failed"); face(M_SAD); }

  sttCli.setInsecure();      // prototype only: no certificate pinning
  llmCli.setInsecure();
  ttsCli.setInsecure();

  pinMode(PIN_BUTTON, INPUT_PULLUP);
  neopixelWrite(PIN_LED, 12, 12, 30);

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);                      // latency matters
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 80 && WiFi.status() != WL_CONNECTED; i++) delay(250);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("online: "); Serial.println(WiFi.localIP());
    neopixelWrite(PIN_LED, 0, 30, 12);
    face(M_HAPPY); delay(500);
  } else {
    Serial.println("no wifi");
    neopixelWrite(PIN_LED, 60, 0, 0);
    face(M_SAD);
  }
}

void loop() {
  face(M_IDLE);

  // ---- wait for the button
  while (digitalRead(PIN_BUTTON) == HIGH) {
    delay(20);
  }
  delay(200);

  if (WiFi.status() != WL_CONNECTED) {
    face(M_SAD); speak("I cannot find the wifi.", M_SAD); delay(500);
    return;
  }

  // ---- listen
  face(M_THINK, 1.0f, -3);
  recordSpeech();
  if (recLen < MIC_HZ / 4) {                 // less than 250 ms of audio
    face(M_SAD); delay(600);
    return;
  }

  // ---- ears
  face(M_THINK);
  String heard;
  if (!transcribe(heard)) { face(M_SAD); delay(800); return; }
  Serial.print("heard: "); Serial.println(heard);
  pushHistory("you", heard);

  // ---- brain
  String answer, faceName, gesture;
  if (!think(heard, answer, faceName, gesture)) {
    face(M_SAD);
    speak("I could not reach my brain.", M_SAD);
    delay(400);
    return;
  }
  Serial.print("say: "); Serial.println(answer);
  Serial.printf("face: %s · gesture: %s\n", faceName.c_str(), gesture.c_str());
  pushHistory("bot", answer);

  // ---- face reacts BEFORE the audio, so it feels fast
  face(moodFrom(faceName));
  neopixelWrite(PIN_LED, 30, 12, 30);

  // ---- voice
  // the face stays on the mood from the LLM; only the mouth animates
  if (!speak(answer, moodFrom(faceName), gesture)) chirp(false);

  delay(2000);              // hold the pose - 0.4 s was too fast to see
  neopixelWrite(PIN_LED, 12, 12, 30);
  face(M_IDLE);
}
