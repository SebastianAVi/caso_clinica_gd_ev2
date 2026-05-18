"""
================================================================
  LIMPIEZA.PY - Clínica MediSalud S.A.
================================================================
Orquestador de la Etapa 2: llama a los tres módulos de
limpieza y genera un log consolidado con estadísticas.

IMPORTANTE: Esta versión NO borra los logs de ingesta.
Los logs de cada etapa son evidencia y deben conservarse.
================================================================
"""

import os
from datetime import datetime

import limpieza_farmacia
import limpieza_laboratorio
import limpieza_urgencia
from config import (
    CARPETA_CLEAN,
    CARPETA_LOGS,
    CARPETA_RAW,
)


def crear_carpetas() -> None:
    for carpeta in [CARPETA_CLEAN, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def escribir_log(log_entries: list, nombre_log: str) -> None:
    ruta_log = os.path.join(CARPETA_LOGS, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries) + "\n")
    print(f"\n📋 Log guardado en: {ruta_log}")


def ejecutar_limpieza() -> None:
    crear_carpetas()

    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log += [sep, "  LIMPIEZA Y TRANSFORMACIÓN - Clínica MediSalud S.A.", sep,
            f"  Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", sep]

    print(f"\n{sep}\n  ETAPA 2: LIMPIEZA Y TRANSFORMACIÓN\n  Clínica MediSalud S.A.\n{sep}")
    print(f"  ▶ Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total_originales = total_limpios = total_duplicados = 0

    # ---- LABORATORIO ----
    print("\n🔬 Limpiando: LABORATORIO")
    log.append("\n--- LABORATORIO ---")
    try:
        stats = limpieza_laboratorio.limpiar_laboratorio(
            ruta_entrada=os.path.join(CARPETA_RAW, "laboratorio.csv"),
            ruta_salida =os.path.join(CARPETA_CLEAN, "laboratorio.csv"),
        )
        print(f"  📥 Originales         : {stats['originales']}")
        print(f"  🗑️  Duplicados elim.   : {stats['duplicados']}")
        print(f"  📅 Fechas corregidas  : {stats['fechas_corregidas']}")
        print(f"  ✅ Limpios            : {stats['limpios']}")
        log += [f"  Originales         : {stats['originales']}",
                f"  Duplicados elim.   : {stats['duplicados']}",
                f"  Fechas corregidas  : {stats['fechas_corregidas']}",
                f"  Limpios            : {stats['limpios']}"]
        total_originales += stats["originales"]
        total_limpios    += stats["limpios"]
        total_duplicados += stats["duplicados"]
    except Exception as e:
        msg = f"  ❌ Error en laboratorio: {e}"
        print(msg); log.append(msg)

    # ---- URGENCIAS ----
    print("\n🚑 Limpiando: URGENCIAS")
    log.append("\n--- URGENCIAS ---")
    try:
        stats = limpieza_urgencia.limpiar_urgencias(
            ruta_entrada=os.path.join(CARPETA_RAW, "urgencias.json"),
            ruta_salida =os.path.join(CARPETA_CLEAN, "urgencias.json"),
        )
        print(f"  📥 Originales         : {stats['originales']}")
        print(f"  🗑️  Duplicados elim.   : {stats['duplicados']}")
        print(f"  📅 Fechas corregidas  : {stats['fechas_corregidas']}")
        print(f"  ✅ Limpios            : {stats['limpios']}")
        for c in stats.get("correcciones", []):
            print(f"  ⚠️  {c}")
            log.append(f"  ⚠️  {c}")
        log += [f"  Originales         : {stats['originales']}",
                f"  Duplicados elim.   : {stats['duplicados']}",
                f"  Fechas corregidas  : {stats['fechas_corregidas']}",
                f"  Limpios            : {stats['limpios']}"]
        total_originales += stats["originales"]
        total_limpios    += stats["limpios"]
        total_duplicados += stats["duplicados"]
    except Exception as e:
        msg = f"  ❌ Error en urgencias: {e}"
        print(msg); log.append(msg)

    # ---- FARMACIA ----
    print("\n💊 Limpiando: FARMACIA")
    log.append("\n--- FARMACIA ---")
    try:
        stats = limpieza_farmacia.limpiar_farmacia(
            ruta_entrada=os.path.join(CARPETA_RAW, "farmacia.xml"),
            ruta_salida =os.path.join(CARPETA_CLEAN, "farmacia.xml"),
        )
        print(f"  📥 Originales         : {stats['originales']}")
        print(f"  🗑️  Duplicados elim.   : {stats['duplicados']}")
        print(f"  📅 Fechas corregidas  : {stats['fechas_corregidas']}")
        print(f"  ✅ Limpios            : {stats['limpios']}")
        for c in stats.get("correcciones", []):
            print(f"  ⚠️  {c}")
            log.append(f"  ⚠️  {c}")
        log += [f"  Originales         : {stats['originales']}",
                f"  Duplicados elim.   : {stats['duplicados']}",
                f"  Fechas corregidas  : {stats['fechas_corregidas']}",
                f"  Limpios            : {stats['limpios']}"]
        total_originales += stats["originales"]
        total_limpios    += stats["limpios"]
        total_duplicados += stats["duplicados"]
    except Exception as e:
        msg = f"  ❌ Error en farmacia: {e}"
        print(msg); log.append(msg)

    # ---- RESUMEN ----
    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()

    resumen = [
        f"\n{sep}", "  RESUMEN DE LIMPIEZA", sep,
        f"  📥 Total originales        : {total_originales}",
        f"  🗑️  Total duplicados elim.  : {total_duplicados}",
        f"  ✅ Total limpios           : {total_limpios}",
        f"  ⏱  Duración                : {duracion:.2f} segundos",
        f"  🏁 Fin                     : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)

    escribir_log(log, f"limpieza_{inicio.strftime('%Y%m%d_%H%M%S')}.log")


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    ejecutar_limpieza()
