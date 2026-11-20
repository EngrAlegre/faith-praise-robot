/* ==========================================================================
   FIVE SIDES  ·  desk companion  ·  Faith & Praise build
   --------------------------------------------------------------------------
   Static desk robot: one 0.96" 128x64 I2C OLED face, I2S mic, I2S speaker, one
   button. It listens, asks the laptop brain, answers out loud, and acts with
   its eyes.  No motors.

   HARDWARE
     ESP32-S3-DevKitC-1 (N16R8)
     1x 2.42" 128x64 OLED, I2C, SSD1309  (4-pin, address 0x3C)
     1x INMP441 I2S mic
     1x MAX98357A + 40 mm speaker
     1x push button to GND
     on-board WS2812 (GPIO48) = mood glow

   WIRING (change the pin block if you wire differently)
     OLED  SDA GPIO8   SCL GPIO9   VCC 3V3   GND
     MAX98357A  BCLK GPIO4  LRC GPIO5  DIN GPIO6   VIN 5V
     INMP441    SCK GPIO15  WS GPIO16  SD GPIO17   L/R -> GND
     button     GPIO18 -> GND

   Requires the U8g2 library (Library Manager: "U8g2").
   ========================================================================== */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <driver/i2s_std.h>

// ---------------------------------------------------------------- settings
const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASS = "YOUR_PASSWORD";
const char* AI_HOST   = "http://192.168.1.50:8080";

// ---------------------------------------------------------------- pins
const int PIN_SDA = 8, PIN_SCL = 9;          // OLED I2C
const int PIN_I2S_OUT_BCLK = 4, PIN_I2S_OUT_LRC = 5, PIN_I2S_OUT_DIN = 6;
const int PIN_I2S_IN_BCLK = 15, PIN_I2S_IN_WS = 16, PIN_I2S_IN_SD = 17;
const int PIN_BUTTON = 18;
const int PIN_LED = 48;

// ---------------------------------------------------------------- types
enum Mood { M_IDLE, M_HAPPY, M_THINK, M_TALK, M_LOVE, M_SLEEP, M_ANGRY };

struct Reply {
  char say[220];
  char face[12];
};

// ---------------------------------------------------------------- face
// One 128x64 I2C OLED is the whole face: two eyes + a mouth.
// Pick the panel you actually bought — all three use the same 128x64 layout:
//   PANEL_242  2.42" SSD1309   (default, 55 x 27 mm active - best face)
//   PANEL_13   1.3"  SH1106    (29 x 15 mm)
//   PANEL_096  0.96" SSD1306   (22 x 11 mm)
#define PANEL_242
// #define PANEL_13
// #define PANEL_096

#if defined(PANEL_096)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
#elif defined(PANEL_13)
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
#else
U8G2_SSD1309_128X64_NONAME0_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
#endif

void drawFace(Mood m, float open = 1.0f, int lookX = 0) {
  const int ex1 = 38, ex2 = 90, ey = 26, er = 13;
  u8g2.clearBuffer();
  u8g2.setDrawColor(1);

  if (open < 0.1f) {                                   // blink
    u8g2.drawRBox(ex1 - er, ey - 2, er * 2, 4, 2);
    u8g2.drawRBox(ex2 - er, ey - 2, er * 2, 4, 2);
  } else if (m == M_SLEEP) {                           // shut
    u8g2.drawRBox(ex1 - er, ey - 2, er * 2, 4, 2);
    u8g2.drawRBox(ex2 - er, ey - 2, er * 2, 4, 2);
  } else if (m == M_HAPPY) {                           // ^ ^
    for (int e = 0; e < 2; e++) {
      int cx = e ? ex2 : ex1;
      u8g2.drawDisc(cx, ey + 4, er);
      u8g2.setDrawColor(0);
      u8g2.drawBox(cx - er - 2, ey + 4, er * 2 + 4, er + 6);
      u8g2.setDrawColor(1);
    }
  } else {                                              // round eyes + pupils
    int half = (int)(er * open);
    for (int e = 0; e < 2; e++) {
      int cx = e ? ex2 : ex1;
      u8g2.drawDisc(cx, ey, er);
      u8g2.setDrawColor(0);
      u8g2.drawDisc(cx + lookX, ey, 5);
      u8g2.drawBox(cx - er, ey - er, er * 2, er - half);   // upper lid
      u8g2.drawBox(cx - er, ey + half, er * 2, er - half); // lower lid
      u8g2.setDrawColor(1);
      u8g2.drawDisc(cx + lookX - 2, ey - 3, 1);            // catch light
    }
  }

  // mouth
  switch (m) {
    case M_HAPPY:
      u8g2.drawCircle(64, 42, 11, U8G2_DRAW_LOWER_LEFT | U8G2_DRAW_LOWER_RIGHT);
      break;
    case M_LOVE:
      u8g2.drawDisc(64, 47, 4);
      break;
    case M_TALK:
      u8g2.drawRBox(56, 44, 16, 10, 4);
      break;
    case M_ANGRY:
      u8g2.drawLine(52, 50, 76, 45);
      break;
    case M_SLEEP:
      break;
    default:
      u8g2.drawRBox(56, 47, 16, 4, 2);
      break;
  }
  u8g2.sendBuffer();
}

// ==========================================================================
//  AUDIO
// ==========================================================================
static const int AUDIO_HZ = 16000;
static const int REC_SECONDS = 3;
static const size_t REC_SAMPLES = AUDIO_HZ * REC_SECONDS;
int16_t* recBuf = nullptr;
i2s_chan_handle_t txChan = nullptr, rxChan = nullptr;

void audioBegin() {
  i2s_chan_config_t txCfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  i2s_new_channel(&txCfg, &txChan, nullptr);
  i2s_std_config_t txStd = {
    .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(AUDIO_HZ),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)PIN_I2S_OUT_BCLK,
                  .ws = (gpio_num_t)PIN_I2S_OUT_LRC, .dout = (gpio_num_t)PIN_I2S_OUT_DIN,
                  .din = I2S_GPIO_UNUSED, .invert_flags = { false, false, false } },
  };
  i2s_channel_init_std_mode(txChan, &txStd);
  i2s_channel_enable(txChan);

  i2s_chan_config_t rxCfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
  i2s_new_channel(&rxCfg, nullptr, &rxChan);
  i2s_std_config_t rxStd = {
    .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(AUDIO_HZ),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)PIN_I2S_IN_BCLK,
                  .ws = (gpio_num_t)PIN_I2S_IN_WS, .dout = I2S_GPIO_UNUSED,
                  .din = (gpio_num_t)PIN_I2S_IN_SD, .invert_flags = { false, false, false } },
  };
  i2s_channel_init_std_mode(rxChan, &rxStd);
  i2s_channel_enable(rxChan);

  recBuf = (int16_t*)ps_malloc(REC_SAMPLES * sizeof(int16_t));
  if (!recBuf) recBuf = (int16_t*)malloc(REC_SAMPLES * sizeof(int16_t));
}

void playSamples(const int16_t* buf, size_t n) {
  size_t off = 0, wrote = 0;
  while (off < n) {
    i2s_channel_write(txChan, buf + off, (n - off) * sizeof(int16_t), &wrote, 1000);
    if (!wrote) break;
    off += wrote / sizeof(int16_t);
  }
}

void sayBeeps(const char* text) {
  static int16_t chunk[512];
  float phase = 0;
  for (const char* p = text; *p; ++p) {
    float f = 420 + ((*p) % 32) * 22;
    int len = (*p == ' ') ? 40 : 90;
    float step = 2 * PI * f / AUDIO_HZ;
    for (int i = 0; i < len; i++) {
      phase += step;
      chunk[i] = (int16_t)(sinf(phase) * 5000 * (1.0f - (float)i / len));
    }
    playSamples(chunk, len);
  }
}

void playMelody(int which) {
  static int16_t tone[420];
  const float notes[2][5] = { {523, 659, 784, 1046, 0}, {523, 392, 330, 0, 0} };
  for (int n = 0; n < 5; n++) {
    if (!notes[which][n]) break;
    float step = 2 * PI * notes[which][n] / AUDIO_HZ;
    for (int i = 0; i < 420; i++)
      tone[i] = (int16_t)(sinf(step * i) * 6000 * (1.0f - (float)i / 420));
    playSamples(tone, 420);
  }
}

void recordAudio() {
  const size_t CHUNK = 512;
  int32_t raw[CHUNK];
  size_t got = 0, idx = 0;
  while (idx < REC_SAMPLES) {
    if (i2s_channel_read(rxChan, raw, sizeof(raw), &got, 1000) != ESP_OK || !got) break;
    size_t n = got / sizeof(int32_t);
    for (size_t i = 0; i < n && idx < REC_SAMPLES; i++)
      recBuf[idx++] = (int16_t)(raw[i] >> 14);
  }
}

size_t wavHeader(uint8_t* h, size_t pcmBytes) {
  uint32_t chunk = 36 + pcmBytes, sub = pcmBytes, rate = AUDIO_HZ, byteRate = rate * 2;
  uint16_t ch = 1, align = 2, bits = 16, pcm = 1;
  uint32_t sixteen = 16;
  memcpy(h, "RIFF", 4); memcpy(h + 4, &chunk, 4); memcpy(h + 8, "WAVE", 4);
  memcpy(h + 12, "fmt ", 4); memcpy(h + 16, &sixteen, 4); memcpy(h + 20, &pcm, 2);
  memcpy(h + 22, &ch, 2); memcpy(h + 24, &rate, 4); memcpy(h + 28, &byteRate, 4);
  memcpy(h + 32, &align, 2); memcpy(h + 34, &bits, 2); memcpy(h + 36, "data", 4);
  memcpy(h + 40, &sub, 4);
  return 44;
}

// ==========================================================================
//  AI
// ==========================================================================
const char* field(const char* json, const char* key, char* out, size_t outLen) {
  char pat[24]; snprintf(pat, sizeof(pat), "\"%s\"", key);
  const char* p = strstr(json, pat);
  if (!p) return nullptr;
  p = strchr(p + strlen(pat), ':');
  if (!p) return nullptr;
  p = strchr(p, '"');
  if (!p) return nullptr;
  p++;
  size_t i = 0;
  while (*p && *p != '"' && i + 1 < outLen) out[i++] = *p++;
  out[i] = 0;
  return out;
}

bool askAI(Reply& r) {
  r.say[0] = 0; strcpy(r.face, "idle");
  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, String(AI_HOST) + "/chat")) return false;
  http.setTimeout(15000);

  size_t pcm = REC_SAMPLES * sizeof(int16_t), total = 44 + pcm;
  uint8_t* body = (uint8_t*)ps_malloc(total);
  if (!body) body = (uint8_t*)malloc(total);
  if (!body) return false;
  wavHeader(body, pcm);
  memcpy(body + 44, recBuf, pcm);

  http.addHeader("Content-Type", "audio/wav");
  int code = http.POST(body, total);
  free(body);
  if (code != 200) { http.end(); return false; }
  String payload = http.getString();
  http.end();
  const char* js = payload.c_str();
  if (!field(js, "say", r.say, sizeof(r.say))) return false;
  field(js, "face", r.face, sizeof(r.face));
  return true;
}

Mood moodFromName(const char* n) {
  if (!strcmp(n, "happy")) return M_HAPPY;
  if (!strcmp(n, "think")) return M_THINK;
  if (!strcmp(n, "talk"))  return M_TALK;
  if (!strcmp(n, "love"))  return M_LOVE;
  if (!strcmp(n, "sleep")) return M_SLEEP;
  if (!strcmp(n, "angry")) return M_ANGRY;
  return M_IDLE;
}

// ==========================================================================
//  SETUP / LOOP
// ==========================================================================
void setup() {
  Serial.begin(115200);
  delay(200);

  neopixelWrite(PIN_LED, 20, 0, 40);

  Wire.begin(PIN_SDA, PIN_SCL);
  u8g2.begin();
  u8g2.setBusClock(400000);          // I2C fast mode: smoother animation
  drawFace(M_IDLE);

  audioBegin();
  pinMode(PIN_BUTTON, INPUT_PULLUP);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 80 && WiFi.status() != WL_CONNECTED; i++) delay(250);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("IP: "); Serial.println(WiFi.localIP());
    neopixelWrite(PIN_LED, 0, 40, 10);
    drawFace(M_HAPPY); playMelody(0);
  } else {
    Serial.println("no wifi");
    neopixelWrite(PIN_LED, 60, 0, 0);
    drawFace(M_SLEEP);
  }
  delay(600);
}

void loop() {
  static unsigned long lastBlink = 0;
  static int lookDir = 0;

  lookDir = (lookDir + 1) % 3;            // idle: eyes drift around
  drawFace(M_IDLE, 1.0f, (lookDir - 1) * 3);
  delay(140);

  unsigned long t0 = millis();
  while (digitalRead(PIN_BUTTON) == HIGH) {
    if (millis() - t0 > 4200) {
      t0 = millis();
      drawFace(M_IDLE, 0.0f);  delay(90);    // blink
      drawFace(M_IDLE, 1.0f);
    }
    delay(30);
  }
  delay(250);

  // ---- listen
  drawFace(M_THINK);
  neopixelWrite(PIN_LED, 10, 10, 50);
  recordAudio();

  // ---- think and answer
  Reply r;
  if (!askAI(r)) {
    strcpy(r.say, "I cannot reach my brain. Is the laptop running the server?");
    strcpy(r.face, "think");
  }
  Serial.println(r.say);

  Mood m = moodFromName(r.face);
  neopixelWrite(PIN_LED, 40, 10, 30);
  drawFace(m);
  sayBeeps(r.say);
  drawFace(M_HAPPY);
  delay(500);
}
