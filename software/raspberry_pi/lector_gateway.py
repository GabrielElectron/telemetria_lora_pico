import serial
import time


PUERTO = "COM3"
BAUDRATE = 115200


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

    for clave in ["NODE", "SEQ"]:
        if clave in datos:
            datos[clave] = int(datos[clave])

    for clave in ["VRMS", "IRMS", "P", "RSSI", "SNR", "FERR"]:
        if clave in datos:
            datos[clave] = float(datos[clave])

    return datos


def main():
    print("======================================")
    print("PPS - Lector Gateway LoRa")
    print("======================================")
    print(f"Puerto: {PUERTO}")
    print(f"Baudrate: {BAUDRATE}")
    print()

    ser = serial.Serial(PUERTO, BAUDRATE, timeout=1)
    time.sleep(2)

    print("Leyendo datos del gateway...")
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

            print(
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

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()