import csv
import os
import serial
import time
from datetime import datetime


PUERTO = "COM3"
BAUDRATE = 115200

ARCHIVO_CSV = "software/raspberry_pi/datos_lora.csv"

COLUMNAS = [
    "timestamp",
    "node",
    "name",
    "seq",
    "vrms",
    "irms",
    "p",
    "rssi",
    "snr",
    "ferr",
    "status",
]


def parsear_linea(linea: str):
    """
    Convierte una linea tipo:
    RX;NODE=1;NAME=NODO_1;SEQ=7;VRMS=220.50;IRMS=3.25;P=716.63;STATUS=OK;RSSI=-30.00;SNR=12.00;FERR=-209.25

    en un diccionario de Python.
    """

    linea = linea.strip()

    if not linea.startswith("RX;"):
        return None

    partes = linea.split(";")
    datos = {"TYPE": partes[0]}

    for parte in partes[1:]:
        if "=" not in parte:
            continue

        clave, valor = parte.split("=", 1)
        datos[clave] = valor

    try:
        for clave in ["NODE", "SEQ"]:
            if clave in datos:
                datos[clave] = int(datos[clave])

        for clave in ["VRMS", "IRMS", "P", "RSSI", "SNR", "FERR"]:
            if clave in datos:
                datos[clave] = float(datos[clave])

    except ValueError:
        return None

    return datos


def crear_csv_si_no_existe():
    carpeta = os.path.dirname(ARCHIVO_CSV)

    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta)

    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNAS)
            writer.writeheader()


def guardar_datos_csv(datos):
    fila = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "node": datos.get("NODE"),
        "name": datos.get("NAME"),
        "seq": datos.get("SEQ"),
        "vrms": datos.get("VRMS"),
        "irms": datos.get("IRMS"),
        "p": datos.get("P"),
        "rssi": datos.get("RSSI"),
        "snr": datos.get("SNR"),
        "ferr": datos.get("FERR"),
        "status": datos.get("STATUS"),
    }

    with open(ARCHIVO_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS)
        writer.writerow(fila)


def main():
    print("======================================")
    print("PPS - Lector Gateway LoRa con CSV")
    print("======================================")
    print(f"Puerto: {PUERTO}")
    print(f"Baudrate: {BAUDRATE}")
    print(f"Archivo CSV: {ARCHIVO_CSV}")
    print()

    crear_csv_si_no_existe()

    ser = serial.Serial(PUERTO, BAUDRATE, timeout=1)
    time.sleep(2)

    print("Leyendo datos del gateway y guardando en CSV...")
    print("Presionar Ctrl+C para detener.")
    print()

    while True:
        try:
            linea = ser.readline().decode("utf-8", errors="ignore").strip()

            if not linea:
                continue

            datos = parsear_linea(linea)

            if datos is None:
                print("Linea ignorada:", linea)
                continue

            guardar_datos_csv(datos)

            print(
                f"Guardado | "
                f"Nodo {datos.get('NODE')} | "
                f"{datos.get('NAME')} | "
                f"SEQ={datos.get('SEQ')} | "
                f"Vrms={datos.get('VRMS')} V | "
                f"Irms={datos.get('IRMS')} A | "
                f"P={datos.get('P')} W | "
                f"RSSI={datos.get('RSSI')} dBm | "
                f"SNR={datos.get('SNR')} dB"
            )

        except KeyboardInterrupt:
            print()
            print("Lectura detenida por el usuario.")
            break

        except serial.SerialException as e:
            print("Error de puerto serial:", e)
            break

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()