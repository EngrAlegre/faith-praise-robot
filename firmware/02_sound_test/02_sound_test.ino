/* ============================================================
   FIVE SIDES  ·  test 2:  THE SOUND
   ------------------------------------------------------------
   Tests the speaker and the microphone separately, so when
   the robot is silent later you know which half is broken.

   1. It plays three rising beeps  -> that is the SPEAKER.
   2. Then it listens for 1 second -> that is the MICROPHONE,
      and it prints how loud it heard you.

   Open Tools > Serial Monitor at 115200 to watch it.

   Wiring
     speaker amp:  BCLK GPIO4  LRC GPIO5  DIN GPIO6   VIN 5V
     microphone:   SCK GPIO15  WS  GPIO16 SD  GPIO17   L/R -> GND
   ============================================================ */

#include <driver/i2s_std.h>

#define OUT_BCLK 4
#define OUT_LRC  5
#define OUT_DIN  6
#define IN_SCK   15
#define IN_WS    16
#define IN_SD    17

#define RATE 16000

i2s_chan_handle_t tx, rx;
static int16_t beepBuf[400];   // 'tone' is already an Arduino function
static int32_t raw[256];


void audioStart() {
  // ---- speaker out
  i2s_chan_config_t c0 = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  i2s_new_channel(&c0, &tx, nullptr);
  i2s_std_config_t s0 = {
    .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(RATE),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)OUT_BCLK,
                  .ws = (gpio_num_t)OUT_LRC, .dout = (gpio_num_t)OUT_DIN,
                  .din = I2S_GPIO_UNUSED, .invert_flags = { false, false, false } },
  };
  i2s_channel_init_std_mode(tx, &s0);
  i2s_channel_enable(tx);

  // ---- microphone in
  i2s_chan_config_t c1 = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
  i2s_new_channel(&c1, nullptr, &rx);
  i2s_std_config_t s1 = {
    .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(RATE),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)IN_SCK,
                  .ws = (gpio_num_t)IN_WS, .dout = I2S_GPIO_UNUSED,
                  .din = (gpio_num_t)IN_SD, .invert_flags = { false, false, false } },
  };
  i2s_channel_init_std_mode(rx, &s1);
  i2s_channel_enable(rx);
}


void beep(float hz) {
  float step = 2 * PI * hz / RATE;
  for (int i = 0; i < 400; i++)
    beepBuf[i] = (int16_t)(sinf(step * i) * 6000 * (1.0f - (float)i / 400));
  size_t wrote = 0, off = 0;
  while (off < 400) {
    i2s_channel_write(tx, beepBuf + off, (400 - off) * sizeof(int16_t), &wrote, 1000);
    if (!wrote) break;
    off += wrote / sizeof(int16_t);
  }
}


// listen for a moment and return the loudest sample
int loudest() {
  int peak = 0;
  for (int i = 0; i < 8; i++) {                 // 8 x 256 samples
    size_t got = 0;
    if (i2s_channel_read(rx, raw, sizeof(raw), &got, 500) != ESP_OK) continue;
    for (size_t k = 0; k < got / sizeof(int32_t); k++) {
      int v = abs(raw[k] >> 14);
      if (v > peak) peak = v;
    }
  }
  return peak;
}


void setup() {
  Serial.begin(115200);
  delay(300);
  audioStart();
  Serial.println("sound test starting");
}

void loop() {
  Serial.println("--- speaker: three beeps");
  beep(523);  delay(120);
  beep(659);  delay(120);
  beep(784);  delay(300);

  Serial.println("--- microphone: say something!");
  int level = loudest();
  Serial.print("heard level = ");
  Serial.println(level);

  if (level < 300)      Serial.println("  very quiet  -> mic not wired, or L/R pin not to GND");
  else if (level < 3000) Serial.println("  quiet       -> normal for a room");
  else                   Serial.println("  loud        -> mic is working");

  delay(1500);
}

/* TRY THIS
   - Change 523, 659, 784 to other numbers for a different tune.
     (440 is A, 523 is C, 587 is D, 659 is E, 784 is G.)
   - Clap near the robot and watch the level jump.
*/
