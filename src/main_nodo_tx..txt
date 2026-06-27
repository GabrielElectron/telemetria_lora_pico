#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

// Pines del modulo SX1262 para Raspberry Pi Pico 2W
#define LORA_BUSY   2
#define LORA_CS     3
#define LORA_SCK    10
#define LORA_MOSI   11
#define LORA_MISO   12
#define LORA_RST    15
#define LORA_DIO1   20

// Pin de medicion de bateria del modulo
#define BAT_AD      26

// Usamos SPI1 porque el modulo esta cableado en GP10, GP11 y GP12
SX1262 radio = new Module(LORA_CS, LORA_DIO1, LORA_RST, LORA_BUSY, SPI1);

int contador = 0;

void setup() {
  Serial.begin(115200);
  delay(3000);

  Serial.println();
  Serial.println("======================================");
  Serial.println("PPS - Nodo 1 Pico 2W + LoRa SX1262");
  Serial.println("Modo: TRANSMISOR");
  Serial.println("======================================");

  SPI1.setSCK(LORA_SCK);
  SPI1.setTX(LORA_MOSI);
  SPI1.setRX(LORA_MISO);
  SPI1.begin();

  Serial.println("SPI1 configurado:");
  Serial.println("SCK  = GP10");
  Serial.println("MOSI = GP11");
  Serial.println("MISO = GP12");
  Serial.println("CS   = GP3");
  Serial.println("DIO1 = GP20");
  Serial.println("RST  = GP15");
  Serial.println("BUSY = GP2");

  Serial.println();
  Serial.println("Iniciando SX1262...");

  int state = radio.begin(
    915.0,   // frecuencia MHz
    125.0,   // bandwidth kHz
    7,       // spreading factor
    5,       // coding rate 4/5
    0x12,    // sync word
    17,      // potencia dBm
    8        // preamble length
  );

  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("LoRa inicializado OK");
  } else {
    Serial.print("Error inicializando LoRa. Codigo: ");
    Serial.println(state);
    Serial.println("Revisar alimentacion, antena, SPI, CS, RESET, BUSY y DIO1.");

    while (true) {
      delay(1000);
    }
  }
}

void loop() {
  String mensaje = "Nodo=1; contador=" + String(contador) + "; Irms=3.25; Vrms=220.5; Estado=OK";

  Serial.print("Transmitiendo: ");
  Serial.println(mensaje);

  int state = radio.transmit(mensaje);

  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("Envio OK");
  } else {
    Serial.print("Error enviando. Codigo: ");
    Serial.println(state);
  }

  contador++;
  delay(2000);
}