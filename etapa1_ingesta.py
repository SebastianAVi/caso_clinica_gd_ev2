

import os

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime


CARPETA_ORIGEN = "data/raw_origen"
CARPETA_DESTINO = "data/raw"


def resolver_carpeta_origen():
    """Devuelve la carpeta origen existente para copiar. 

    Preferimos `data/raw_origen`; si no existe, hacemos fallback a `data/raw`.
    """
    if os.path.isdir(CARPETA_ORIGEN):
        return CARPETA_ORIGEN
    return CARPETA_DESTINO
CARPETA_LOGS = "logs"
ARCHIVOS_ESPERADOS = {
    "laboratorio": "laboratorio.csv",
    "urgencias":   "urgencias.json",
    "farmacia":    "farmacia.xml",
}






def crear_carpetas():

    for carpeta in [CARPETA_DESTINO, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def contar_registros(ruta_archivo):

    extension = ruta_archivo.split(".")[-1].lower()

    try:
        if extension == "csv":
            with open(ruta_archivo, encoding="utf-8") as f:
                lector = csv.reader(f)
                filas = list(lector)
                # Asumimos primera fila cabecera
                return max(0, len(filas) - 1)

        elif extension == "json":
            with open(ruta_archivo, encoding="utf-8") as f:
                datos = json.load(f)

            # Soporta lista o dict con lista en algún campo
            if isinstance(datos, list):
                return len(datos)
            if isinstance(datos, dict):
                for v in datos.values():
                    if isinstance(v, list):
                        return len(v)

            return 0

        elif extension == "xml":
            arbol = ET.parse(ruta_archivo)
            raiz = arbol.getroot()

            hijos = list(raiz)
            return len(hijos)

    except Exception as e:
        print(f"  ⚠️  Error al contar registros: {e}")
        return -1


def escribir_log(log_entries, nombre_log):

    ruta_log = os.path.join(CARPETA_LOGS, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        for linea in log_entries:
            f.write(linea + "\n")
    print(f"\n📋 Log guardado en: {ruta_log}")





def ejecutar_ingesta():


    crear_carpetas()

    log = []
    inicio = datetime.now()

    separador = "=" * 55
    log.append(separador)
    log.append("  INGESTA DE DATOS - Clínica MediSalud S.A.")
    log.append(separador)
    log.append(f"  Inicio : {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(separador)

    print("\n" + separador)
    print("  ETAPA 1: INGESTA DE DATOS")
    print("  Clínica MediSalud S.A.")
    print(separador)
    print(f"  ▶ Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print(separador)

    total_registros = 0
    archivos_ok = 0
    archivos_error = 0

    for area, nombre_archivo in ARCHIVOS_ESPERADOS.items():

        print(f"\n📂 Procesando área: {area.upper()}")
        log.append(f"\nÁrea: {area.upper()}")

        ruta_origen = os.path.join(resolver_carpeta_origen(), nombre_archivo)
        ruta_destino = os.path.join(CARPETA_DESTINO, nombre_archivo)

        # Verificar si el archivo existe
        if not os.path.exists(ruta_origen):
            mensaje = f"  ❌ Archivo no encontrado: {ruta_origen}"
            print(mensaje)
            log.append(f"  ERROR: Archivo no encontrado en {ruta_origen}")
            archivos_error += 1
            continue

        try:
            # Si origen==destino (por fallback), evitamos truncar el archivo destino.
            if os.path.abspath(ruta_origen) == os.path.abspath(ruta_destino):
                print(f"  ⚪ Origen y destino iguales; se omite copia: {nombre_archivo}")
                log.append(f"  Archivo: {nombre_archivo} → (sin copia, origen==destino)")
            else:
                with open(ruta_origen, "rb") as fsrc, open(ruta_destino, "wb") as fdst:
                    while True:
                        chunk = fsrc.read(1024 * 1024)
                        if not chunk:
                            break
                        fdst.write(chunk)
                print(f"  ✅ Archivo copiado: {nombre_archivo}")
                log.append(f"  Archivo: {nombre_archivo} → copiado correctamente")
        except Exception as e:
            print(f"  ❌ Error al copiar: {e}")
            log.append(f"  ERROR al copiar: {e}")
            archivos_error += 1
            continue


        # Contar registros del archivo
        n_registros = contar_registros(ruta_destino)
        if n_registros >= 0:
            print(f"  📊 Registros encontrados: {n_registros}")
            log.append(f"  Registros encontrados: {n_registros}")
            total_registros += n_registros
        else:
            log.append("  Registros: no se pudo contar")

        archivos_ok += 1

    # Resumen final
    fin = datetime.now()
    duracion = (fin - inicio).seconds

    print("\n" + separador)
    print("  RESUMEN DE INGESTA")
    print(separador)
    print(f"  ✅ Archivos procesados : {archivos_ok}")
    print(f"  ❌ Archivos con error  : {archivos_error}")
    print(f"  📊 Total de registros  : {total_registros}")
    print(f"  ⏱  Duración            : {duracion} segundos")
    print(f"  🏁 Fin                 : {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    print(separador + "\n")

    log.append("\n" + separador)
    log.append("  RESUMEN")
    log.append(separador)
    log.append(f"  Archivos procesados : {archivos_ok}")
    log.append(f"  Archivos con error  : {archivos_error}")
    log.append(f"  Total de registros  : {total_registros}")
    log.append(f"  Duración            : {duracion} segundos")
    log.append(f"  Fin                 : {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(separador)

    # Guardar log
    nombre_log = f"ingesta_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
    escribir_log(log, nombre_log)


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    ejecutar_ingesta()
