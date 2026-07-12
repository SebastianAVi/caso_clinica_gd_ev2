import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from config import ARCHIVOS_ESPERADOS, CARPETA_LOGS, CARPETA_RAW, CARPETA_RAW_ORIGEN


def resolver_carpeta_origen():
    if os.path.isdir(CARPETA_RAW_ORIGEN):
        return CARPETA_RAW_ORIGEN
    return CARPETA_RAW


def crear_carpetas():
    for carpeta in [CARPETA_RAW, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def contar_registros(ruta):
    ext = ruta.rsplit(".", 1)[-1].lower()
    try:
        if ext == "csv":
            with open(ruta, encoding="utf-8") as f:
                return max(0, len(list(csv.reader(f))) - 1)
        elif ext == "json":
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list):
                return len(datos)
            if isinstance(datos, dict):
                for v in datos.values():
                    if isinstance(v, list):
                        return len(v)
            return 0
        elif ext == "xml":
            return len(list(ET.parse(ruta).getroot()))
    except Exception as e:
        print(f"  Error al contar registros en {ruta}: {e}")
    return -1


def copiar_archivo(origen, destino):
    with open(origen, "rb") as src, open(destino, "wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            dst.write(chunk)


def escribir_log(entradas, nombre):
    ruta = os.path.join(CARPETA_LOGS, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(entradas) + "\n")
    print(f"Log guardado en: {ruta}")


def ejecutar_ingesta():
    crear_carpetas()
    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log += [sep, "INGESTA DE DATOS - Clinica MediSalud S.A.", sep,
            f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", sep]
    print(f"\n{sep}\nETAPA 1: INGESTA DE DATOS\nClinica MediSalud S.A.\n{sep}")
    print(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total = ok = errores = 0

    for area, archivo in ARCHIVOS_ESPERADOS.items():
        print(f"\nProcesando area: {area.upper()}")
        log.append(f"\nArea: {area.upper()}")

        origen  = resolver_carpeta_origen()
        ruta_or = os.path.join(origen, archivo)
        ruta_ds = os.path.join(CARPETA_RAW, archivo)

        if not os.path.exists(ruta_or):
            print(f"  ERROR: Archivo no encontrado: {ruta_or}")
            log.append(f"  ERROR: No encontrado: {ruta_or}")
            errores += 1
            continue

        try:
            if os.path.abspath(ruta_or) == os.path.abspath(ruta_ds):
                print(f"  Origen y destino iguales, sin copia: {archivo}")
                log.append(f"  {archivo} -> sin copia (origen==destino)")
            else:
                copiar_archivo(ruta_or, ruta_ds)
                print(f"  Archivo copiado: {archivo}")
                log.append(f"  {archivo} -> copiado correctamente")
        except Exception as e:
            print(f"  ERROR al copiar {archivo}: {e}")
            log.append(f"  ERROR al copiar: {e}")
            errores += 1
            continue

        n = contar_registros(ruta_ds)
        if n >= 0:
            print(f"  Registros encontrados: {n}")
            log.append(f"  Registros: {n}")
            total += n
        else:
            log.append("  Registros: no se pudo contar")
        ok += 1

    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()
    resumen  = [
        f"\n{sep}", "RESUMEN DE INGESTA", sep,
        f"  Archivos procesados : {ok}",
        f"  Archivos con error  : {errores}",
        f"  Total de registros  : {total}",
        f"  Duracion            : {duracion:.2f} segundos",
        f"  Fin                 : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)
    escribir_log(log, f"ingesta_{inicio.strftime('%Y%m%d_%H%M%S')}.log")


if __name__ == "__main__":
    ejecutar_ingesta()
