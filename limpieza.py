import os
from datetime import datetime

import limpieza_farmacia
import limpieza_laboratorio
import limpieza_urgencia
from config import CARPETA_CLEAN, CARPETA_LOGS, CARPETA_RAW


def crear_carpetas():
    for carpeta in [CARPETA_CLEAN, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def escribir_log(entradas, nombre):
    ruta = os.path.join(CARPETA_LOGS, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(entradas) + "\n")
    print(f"Log guardado en: {ruta}")


def imprimir_stats(area, stats, log):
    print(f"  Originales        : {stats['originales']}")
    print(f"  Duplicados elim.  : {stats['duplicados']}")
    print(f"  Fechas corregidas : {stats['fechas_corregidas']}")
    print(f"  Limpios           : {stats['limpios']}")
    for c in stats.get("correcciones", []):
        print(f"  Correccion: {c}")
        log.append(f"  Correccion: {c}")
    log += [
        f"  Originales        : {stats['originales']}",
        f"  Duplicados elim.  : {stats['duplicados']}",
        f"  Fechas corregidas : {stats['fechas_corregidas']}",
        f"  Limpios           : {stats['limpios']}",
    ]


def ejecutar_limpieza():
    crear_carpetas()
    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log += [sep, "LIMPIEZA Y TRANSFORMACION - Clinica MediSalud S.A.", sep,
            f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", sep]
    print(f"\n{sep}\nETAPA 2: LIMPIEZA Y TRANSFORMACION\nClinica MediSalud S.A.\n{sep}")
    print(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total_orig = total_limp = total_dups = 0

    areas = [
        ("LABORATORIO", limpieza_laboratorio.limpiar_laboratorio,
         os.path.join(CARPETA_RAW, "laboratorio.csv"),
         os.path.join(CARPETA_CLEAN, "laboratorio.csv")),
        ("URGENCIAS", limpieza_urgencia.limpiar_urgencias,
         os.path.join(CARPETA_RAW, "urgencias.json"),
         os.path.join(CARPETA_CLEAN, "urgencias.json")),
        ("FARMACIA", limpieza_farmacia.limpiar_farmacia,
         os.path.join(CARPETA_RAW, "farmacia.xml"),
         os.path.join(CARPETA_CLEAN, "farmacia.xml")),
    ]

    for nombre, fn, entrada, salida in areas:
        print(f"\nLimpiando: {nombre}")
        log.append(f"\n--- {nombre} ---")
        try:
            stats = fn(ruta_entrada=entrada, ruta_salida=salida)
            imprimir_stats(nombre, stats, log)
            total_orig += stats["originales"]
            total_limp += stats["limpios"]
            total_dups += stats["duplicados"]
        except Exception as e:
            msg = f"  ERROR en {nombre}: {e}"
            print(msg)
            log.append(msg)

    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()
    resumen  = [
        f"\n{sep}", "RESUMEN DE LIMPIEZA", sep,
        f"  Total originales       : {total_orig}",
        f"  Total duplicados elim. : {total_dups}",
        f"  Total limpios          : {total_limp}",
        f"  Duracion               : {duracion:.2f} segundos",
        f"  Fin                    : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)
    escribir_log(log, f"limpieza_{inicio.strftime('%Y%m%d_%H%M%S')}.log")


if __name__ == "__main__":
    ejecutar_limpieza()
