#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

// ======================================================
// Pines del modulo SX1262 para Raspberry Pi Pico 2W
// ======================================================
#define LORA_BUSY   2
#define LORA_CS     3
#define LORA_SCK    10
#define LORA_MOSI   11
#define LORA_MISO   12
#define LORA_RST    15
#define LORA_DIO1   20

// Pin de medicion de bateria del modulo
#define BAT_AD      26

// ======================================================
// Configuracion LoRa
// ======================================================
#define LORA_FREQ_MHZ      915.0
#define LORA_BW_KHZ        125.0
#define LORA_SF            7
#define LORA_CR            5
#define LORA_SYNC_WORD     0x12
#define LORA_TX_POWER_DBM  17
#define LORA_PREAMBLE_LEN  8

// Usamos SPI1 porque el modulo esta cableado en GP10, GP11 y GP12
SX1262 radio = new Module(LORA_CS, LORA_DIO1, LORA_RST, LORA_BUSY, SPI1);

#ifndef NODE_ID
#define NODE_ID 0
#endif

int contador = 0;

unsigned long ultimo_envio_ms = 0;
const unsigned long PERIODO_ENVIO_MS = 2000;

// ======================================================
// Inicializacion comun del SX1262
// ======================================================
void iniciar_lora() {
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
    LORA_FREQ_MHZ,
    LORA_BW_KHZ,
    LORA_SF,
    LORA_CR,
    LORA_SYNC_WORD,
    LORA_TX_POWER_DBM,
    LORA_PREAMBLE_LEN
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

// ======================================================
// Setup
// ======================================================
void setup() {
  Serial.begin(115200);
  delay(3000);

  Serial.println();
  Serial.println("======================================");
  Serial.println("PPS - Telemetria LoRa SX1262");
  Serial.println("Raspberry Pi Pico 2W");
  Serial.println("======================================");

#ifdef DEVICE_MODE_TX
  Serial.print("Modo: NODO TRANSMISOR ");
  Serial.println(NODE_ID);
#endif

#ifdef DEVICE_MODE_GATEWAY
  Serial.println("Modo: GATEWAY RECEPTOR");
#endif

  iniciar_lora();

#ifdef DEVICE_MODE_TX
  // Desfase inicial entre nodos:
  // Nodo 1 transmite casi inmediatamente.
  // Nodo 2 espera aproximadamente 1 segundo.
  if (NODE_ID == 1) {
    ultimo_envio_ms = millis() - PERIODO_ENVIO_MS;
  } else if (NODE_ID == 2) {
    ultimo_envio_ms = millis() - PERIODO_ENVIO_MS + 1000;
  } else {
    ultimo_envio_ms = millis();
  }
#endif

#ifdef DEVICE_MODE_GATEWAY
  Serial.println();
  Serial.println("Esperando paquetes LoRa...");
#endif
}

// ======================================================
// Loop
// ======================================================
void loop() {

#ifdef DEVICE_MODE_TX

  unsigned long ahora_ms = millis();

  if (ahora_ms - ultimo_envio_ms >= PERIODO_ENVIO_MS) {
    ultimo_envio_ms = ahora_ms;

    float vrms;
    float irms;

    if (NODE_ID == 1) {
      vrms = 220.5;
      irms = 3.25;
    } else if (NODE_ID == 2) {
      vrms = 219.8;
      irms = 1.80;
    } else {
      vrms = 0.0;
      irms = 0.0;
    }

    float potencia = vrms * irms;

    String mensaje = "";
    mensaje += "NODE=" + String(NODE_ID);
    mensaje += ";SEQ=" + String(contador);
    mensaje += ";VRMS=" + String(vrms, 2);
    mensaje += ";IRMS=" + String(irms, 2);
    mensaje += ";P=" + String(potencia, 2);
    mensaje += ";STATUS=OK";

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
  }

#endif


#ifdef DEVICE_MODE_GATEWAY

  String mensaje;

  int state = radio.receive(mensaje);

  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("--------------------------------------");
    Serial.print("Paquete recibido: ");
    Serial.println(mensaje);

    Serial.print("RSSI: ");
    Serial.print(radio.getRSSI());
    Serial.println(" dBm");

    Serial.print("SNR: ");
    Serial.print(radio.getSNR());
    Serial.println(" dB");

    Serial.print("Frequency error: ");
    Serial.print(radio.getFrequencyError());
    Serial.println(" Hz");
  }
  else if (state == RADIOLIB_ERR_RX_TIMEOUT) {
    // Es normal, no llego ningun paquete.
  }
  else {
    Serial.print("Error recibiendo. Codigo: ");
    Serial.println(state);
    delay(500);
  }

#endif
}