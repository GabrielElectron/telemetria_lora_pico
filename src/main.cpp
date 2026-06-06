#include <Arduino.h>

#ifndef LED_BUILTIN
#define LED_BUILTIN 25
#endif

void setup() {
  Serial.begin(115200);
  delay(2000);

  pinMode(LED_BUILTIN, OUTPUT);

  Serial.println("PPS - Nodo LoRa Pico 2W");
  Serial.println("Prueba inicial Blink");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("LED ON");
  delay(500);

  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("LED OFF");
  delay(500);
}