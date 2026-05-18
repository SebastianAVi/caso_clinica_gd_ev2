"""
Módulo de INGESTA - Etapa 1
Lee archivos de origen y los copia a data/raw/
"""

import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from clinica_etl.config import (
    ARCHIVOS_ESPERADOS,
    CARPETA_RAW,
    CARPETA_LOGS,
    crear_carpetas_proyecto,
)
from clinica_etl.utils import escribir_log


def resolver_carpeta_origen() -> str:
    """Retorna la carpeta de origen de los archivos."""
    origen_alternativo = os.path.join(os.path.dirname(CARPETA_RAW), "raw_origen")
    if os.path.isdir(origen_alternativo):
        return origen_alternativo
    return CARPETA_RAW


def contar_registros(ruta_archivo: str) -> int:
    """Cuenta registros según la extensión del archivo."""
    extension = ruta_archivo.rsplit(".", 1)[-1].lower()
    try:
        if extension == "csv":
            with open(ruta_archivo, encoding="utf-8") as f:
                filas = list(csv.reader(f))
            return max(0, len(filas) - 1)

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
        print(f"  ⚠️  Error al contar: {e}")
    return -1


def copiar_archivo(ruta_origen: str, ruta_destino: str) -> None:
    """Copia archivo en bloques de 1 MB."""
    with open(ruta_origen, "rb") as fsrc, open(ruta_destino, "wb") as fdst:
        while True:
            chunk = fsrc.read(1024 * 1024)
            if not chunk:
                break
            fdst.write(chunk)


def ejecutar_ingesta() -> None:
    """Ejecuta la etapa 1 de ingesta de datos."""
    crear_carpetas_proyecto()

    log = []
    inicio = datetime.now()
    sep = "=" * 55

    log += [sep, "  INGESTA DE DATOS - Clínica MediSalud S.A.", sep,
            f"  Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", sep]

    print(f"\n{sep}\n  ETAPA 1: INGESTA DE DATOS\n  Clínica MediSalud S.A.\n{sep}")
    print(f"  ▶ Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total_registros = archivos_ok = archivos_error = 0
    origen = resolver_carpeta_origen()

    for area, nombre_archivo in ARCHIVOS_ESPERADOS.items():
        print(f"\n📂 Procesando área: {area.upper()}")
        log.append(f"\nÁrea: {area.upper()}")

        ruta_or = os.path.join(origen, nombre_archivo)
        ruta_ds = os.path.join(CARPETA_RAW, nombre_archivo)

        if not os.path.exists(ruta_or):
            print(f"  ❌ Archivo no encontrado: {ruta_or}")
            log.append(f"  ERROR: No encontrado en {ruta_or}")
            archivos_error += 1
            continue

        try:
            if os.path.abspath(ruta_or) != os.path.abspath(ruta_ds):
                copiar_archivo(ruta_or, ruta_ds)
                print(f"  ✅ Archivo copiado: {nombre_archivo}")
                log.append(f"  {nombre_archivo} → copiado correctamente")
            else:
                print(f"  ℹ️  Origen y destino iguales (sin copia): {nombre_archivo}")
                log.append(f"  {nombre_archivo} → sin copia (origen==destino)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            log.append(f"  ERROR: {e}")
            archivos_error += 1
            continue

        n = contar_registros(ruta_ds)
        if n >= 0:
            print(f"  📊 Registros encontrados: {n}")
            log.append(f"  Registros: {n}")
            total_registros += n
        else:
            log.append("  Registros: no contados")

        archivos_ok += 1

    fin = datetime.now()
    duracion = (fin - inicio).total_seconds()

    resumen = [
        f"\n{sep}", "  RESUMEN DE INGESTA", sep,
        f"  ✅ Archivos procesados : {archivos_ok}",
        f"  ❌ Archivos con error  : {archivos_error}",
        f"  📊 Total registros     : {total_registros}",
        f"  ⏱  Duración            : {duracion:.2f} s",
        f"  🏁 Fin                 : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)

    nombre_log = f"ingesta_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
    ruta_log = escribir_log(log, nombre_log, CARPETA_LOGS)
    print(f"📋 Log guardado en: {ruta_log}")
