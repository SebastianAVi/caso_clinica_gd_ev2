"""
================================================================
  ETAPA 1: INGESTA DE DATOS - Clínica MediSalud S.A.
================================================================
Lee los archivos de origen (CSV, JSON, XML) y los copia a
data/raw/, registrando un log detallado de cada operación.
================================================================
"""

import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from config import (
    ARCHIVOS_ESPERADOS,
    CARPETA_CLEAN,
    CARPETA_LOGS,
    CARPETA_RAW,
    CARPETA_RAW_ORIGEN,
)

# -------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------

def resolver_carpeta_origen() -> str:
    """
    Devuelve la carpeta de origen de los archivos.
    Prefiere data/raw_origen; si no existe, usa data/raw como fallback.
    """
    if os.path.isdir(CARPETA_RAW_ORIGEN):
        return CARPETA_RAW_ORIGEN
    return CARPETA_RAW


def crear_carpetas() -> None:
    """Crea las carpetas necesarias si no existen."""
    for carpeta in [CARPETA_RAW, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def contar_registros(ruta_archivo: str) -> int:
    """
    Cuenta los registros de un archivo según su extensión.
    Retorna el número de registros o -1 si hubo error.
    """
    extension = ruta_archivo.rsplit(".", 1)[-1].lower()
    try:
        if extension == "csv":
            with open(ruta_archivo, encoding="utf-8") as f:
                filas = list(csv.reader(f))
            return max(0, len(filas) - 1)  # descuenta encabezado

        elif extension == "json":
            with open(ruta_archivo, encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list):
                return len(datos)
            if isinstance(datos, dict):
                for v in datos.values():
                    if isinstance(v, list):
                        return len(v)
            return 0

        elif extension == "xml":
            arbol = ET.parse(ruta_archivo)
            return len(list(arbol.getroot()))

    except Exception as e:
        print(f"  ⚠️  Error al contar registros en '{ruta_archivo}': {e}")
    return -1


def escribir_log(log_entries: list, nombre_log: str) -> None:
    """Guarda las entradas del log en un archivo de texto."""
    ruta_log = os.path.join(CARPETA_LOGS, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries) + "\n")
    print(f"\n📋 Log guardado en: {ruta_log}")


def copiar_archivo(ruta_origen: str, ruta_destino: str) -> None:
    """Copia un archivo en bloques de 1 MB."""
    with open(ruta_origen, "rb") as fsrc, open(ruta_destino, "wb") as fdst:
        while True:
            chunk = fsrc.read(1024 * 1024)
            if not chunk:
                break
            fdst.write(chunk)


# -------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------

def ejecutar_ingesta() -> None:
    crear_carpetas()

    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log += [sep, "  INGESTA DE DATOS - Clínica MediSalud S.A.", sep,
            f"  Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", sep]

    print(f"\n{sep}\n  ETAPA 1: INGESTA DE DATOS\n  Clínica MediSalud S.A.\n{sep}")
    print(f"  ▶ Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total_registros = archivos_ok = archivos_error = 0

    for area, nombre_archivo in ARCHIVOS_ESPERADOS.items():
        print(f"\n📂 Procesando área: {area.upper()}")
        log.append(f"\nÁrea: {area.upper()}")

        origen  = resolver_carpeta_origen()
        ruta_or = os.path.join(origen, nombre_archivo)
        ruta_ds = os.path.join(CARPETA_RAW, nombre_archivo)

        # Verificar existencia
        if not os.path.exists(ruta_or):
            print(f"  ❌ Archivo no encontrado: {ruta_or}")
            log.append(f"  ERROR: Archivo no encontrado en {ruta_or}")
            archivos_error += 1
            continue

        # Copiar archivo
        try:
            if os.path.abspath(ruta_or) == os.path.abspath(ruta_ds):
                print(f"  ℹ️  Origen y destino iguales; se omite copia: {nombre_archivo}")
                log.append(f"  Archivo: {nombre_archivo} → (sin copia, origen==destino)")
            else:
                copiar_archivo(ruta_or, ruta_ds)
                print(f"  ✅ Archivo copiado: {nombre_archivo}")
                log.append(f"  Archivo: {nombre_archivo} → copiado correctamente")
        except Exception as e:
            print(f"  ❌ Error al copiar '{nombre_archivo}': {e}")
            log.append(f"  ERROR al copiar: {e}")
            archivos_error += 1
            continue

        # Contar registros
        n = contar_registros(ruta_ds)
        if n >= 0:
            print(f"  📊 Registros encontrados: {n}")
            log.append(f"  Registros encontrados: {n}")
            total_registros += n
        else:
            log.append("  Registros: no se pudo contar")

        archivos_ok += 1

    # Resumen
    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()

    resumen = [
        f"\n{sep}", "  RESUMEN DE INGESTA", sep,
        f"  ✅ Archivos procesados : {archivos_ok}",
        f"  ❌ Archivos con error  : {archivos_error}",
        f"  📊 Total de registros  : {total_registros}",
        f"  ⏱  Duración            : {duracion:.2f} segundos",
        f"  🏁 Fin                 : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)

    escribir_log(log, f"ingesta_{inicio.strftime('%Y%m%d_%H%M%S')}.log")


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    ejecutar_ingesta()
