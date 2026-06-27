import csv
import os
import serial
import time
from datetime import datetime


PUERTO = "/dev/ttyACM0"
BAUDRATE = 115200

ARCHIVO_CSV = "software/raspberry_pi/datos_lora_app.csv"

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

estado_nodos = {}
ultimo_seq = {}
paquetes_perdidos = {}


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def parsear_linea(linea: str):
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


def actualizar_estado(datos):
    node = datos.get("NODE")
    seq = datos.get("SEQ")

    if node is None or seq is None:
        return

    if node not in paquetes_perdidos:
        paquetes_perdidos[node] = 0

    if node in ultimo_seq:
        esperado = ultimo_seq[node] + 1

        if seq > esperado:
            paquetes_perdidos[node] += seq - esperado

    ultimo_seq[node] = seq

    datos["ULTIMA_RECEPCION"] = datetime.now().strftime("%H:%M:%S")
    datos["PERDIDOS"] = paquetes_perdidos[node]

    estado_nodos[node] = datos


def mostrar_estado():
    limpiar_pantalla()

    print("==============================================================")
    print("PPS - Gateway LoRa App")
    print("==============================================================")
    print(f"Puerto: {PUERTO} | Baudrate: {BAUDRATE}")
    print(f"CSV: {ARCHIVO_CSV}")
    print()

    print(
        f"{'Nodo':<6}"
        f"{'Nombre':<10}"
        f"{'SEQ':<8}"
        f"{'Vrms':<10}"
        f"{'Irms':<10}"
        f"{'P':<10}"
        f"{'RSSI':<10}"
        f"{'SNR':<8}"
        f"{'Perdidos':<10}"
        f"{'Hora':<10}"
    )

    print("-" * 100)

    for node in sorted(estado_nodos.keys()):
        d = estado_nodos[node]

        print(
            f"{d.get('NODE', ''):<6}"
            f"{d.get('NAME', ''):<10}"
            f"{d.get('SEQ', ''):<8}"
            f"{d.get('VRMS', 0):<10.2f}"
            f"{d.get('IRMS', 0):<10.2f}"
            f"{d.get('P', 0):<10.2f}"
            f"{d.get('RSSI', 0):<10.2f}"
            f"{d.get('SNR', 0):<8.2f}"
            f"{d.get('PERDIDOS', 0):<10}"
            f"{d.get('ULTIMA_RECEPCION', ''):<10}"
        )

    print()
    print("Ctrl+C para salir.")


def main():
    print("==============================================================")
    print("PPS - Gateway LoRa App")
    print("==============================================================")
    print(f"Abriendo puerto {PUERTO} a {BAUDRATE} baudios...")
    print(f"Guardando en: {ARCHIVO_CSV}")
    print()

    crear_csv_si_no_existe()

    ser = serial.Serial(PUERTO, BAUDRATE, timeout=1)
    time.sleep(2)

    ultima_actualizacion_pantalla = 0

    while True:
        try:
            linea = ser.readline().decode("utf-8", errors="ignore").strip()

            if linea:
                datos = parsear_linea(linea)

                if datos is not None:
                    guardar_datos_csv(datos)
                    actualizar_estado(datos)

            ahora = time.time()

            if ahora - ultima_actualizacion_pantalla >= 1.0:
                mostrar_estado()
                ultima_actualizacion_pantalla = ahora

        except KeyboardInterrupt:
            print()
            print("Programa detenido por el usuario.")
            break

        except serial.SerialException as e:
            print("Error de puerto serial:", e)
            break

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()