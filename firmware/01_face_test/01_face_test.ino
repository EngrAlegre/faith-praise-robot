/* ============================================================
   FIVE SIDES  ·  test 1:  THE FACE
   ------------------------------------------------------------
   The very first thing to upload. No WiFi, no sound, no AI.
   Just the screen. If this works, your wiring is right.

   You need:  Arduino IDE + the U8g2 library
   Board:     ESP32S3 Dev Module
   Wiring:    screen SDA -> GPIO8
              screen SCL -> GPIO9
              screen VCC -> 3V3
              screen GND -> GND
   ============================================================ */

#include <Wire.h>
#include <U8g2lib.h>

#define SDA_PIN 8
#define SCL_PIN 9

// our screen: 2.42 inch, 128x64, driver SSD1309
U8G2_SSD1309_128X64_NONAME0_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);


// ---- one eye -------------------------------------------------
// cx, cy = middle of the eye.  open = 1.0 wide open, 0.0 shut.
void eye(int cx, int cy, int r, float open, int look) {
  u8g2.setDrawColor(1);
  u8g2.drawDisc(cx, cy, r);              // the white part
  u8g2.setDrawColor(0);
  u8g2.drawDisc(cx + look, cy, 5);       // the pupil
  int half = (int)(r * open);
  u8g2.drawBox(cx - r, cy - r, r * 2, r - half);   // top eyelid
  u8g2.drawBox(cx - r, cy + half, r * 2, r - half); // bottom eyelid
  u8g2.setDrawColor(1);
  u8g2.drawDisc(cx + look - 2, cy - 3, 1);         // a little sparkle
}


// ---- the whole face ------------------------------------------
void face(float open, int look) {
  u8g2.clearBuffer();
  eye(38, 26, 13, open, look);           // left eye
  eye(90, 26, 13, open, look);           // right eye
  u8g2.drawRBox(56, 47, 16, 4, 2);       // mouth
  u8g2.sendBuffer();
}


void setup() {
  Wire.begin(SDA_PIN, SCL_PIN);
  u8g2.begin();
  u8g2.setBusClock(400000);
}

void loop() {
  // look left, centre, right, centre...
  face(1.0, -3);  delay(900);
  face(1.0, 0);   delay(900);
  face(1.0, 3);   delay(900);
  face(1.0, 0);   delay(1200);

  // blink!
  face(0.0, 0);   delay(90);
  face(1.0, 0);   delay(600);
}

/* TRY THIS
   1. Make the eyes bigger:  eye(38, 26, 16)  and  eye(90, 26, 16).
   2. Make it blink twice:   copy the blink line once more.
   3. Make a happy mouth:    replace the mouth line with
                             u8g2.drawCircle(64, 42, 11,
                               U8G2_DRAW_LOWER_LEFT | U8G2_DRAW_LOWER_RIGHT);
   Change ONE thing, then press Upload. That is how you learn.
*/
