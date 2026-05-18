"""
================================================================
  ETAPA 4: CARGA A BASE DE DATOS - Clínica MediSalud S.A.
================================================================
Lee los archivos validados desde data/validados/, los inserta
en la base de datos (SQLite por defecto, PostgreSQL opcional),
evita duplicados y genera un log con resumen y consulta de ejemplo.

Variables de entorno opcionales:
  DB_ENGINE   → "sqlite" (default) o "postgresql"
  DB_PATH     → ruta del archivo SQLite (default: data/clinica.db)
  DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT  → para PostgreSQL
================================================================
"""

import csv
import json
import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from config import ESTADOS_URGENCIA_VALIDOS, CARPETA_LOGS

# -------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------
CLEAN_DIR  = "data/validados"          # Lee desde validados (ya pasaron etapa 3)
DB_PATH    = os.environ.get("DB_PATH",    "data/clinica.db")
DB_ENGINE  = os.environ.get("DB_ENGINE",  "sqlite").lower()


# -------------------------------------------------------
# FUNCIONES DE BASE DE DATOS
# -------------------------------------------------------

def crear_carpetas() -> None:
    os.makedirs(CARPETA_LOGS, exist_ok=True)
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def conectar_base_datos():
    """
    Conecta a la BD configurada y retorna (conexion, placeholder).
    placeholder es "?" para SQLite y "%s" para PostgreSQL.
    """
    if DB_ENGINE == "postgresql":
        try:
            import psycopg2
        except ImportError as e:
            raise RuntimeError(
                "PostgreSQL no disponible: instale psycopg2-binary o use DB_ENGINE=sqlite"
            ) from e
        conexion = psycopg2.connect(
            dbname  =os.environ.get("DB_NAME",     "clinica"),
            user    =os.environ.get("DB_USER",     "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
            host    =os.environ.get("DB_HOST",     "localhost"),
            port    =os.environ.get("DB_PORT",     "5432"),
        )
        return conexion, "%s"
    else:
        return sqlite3.connect(DB_PATH), "?"


def crear_tablas(cursor, ph: str) -> None:
    """Crea las tablas si no existen. ph = placeholder del motor."""
    tipo_fecha = "TEXT"    if DB_ENGINE == "sqlite" else "DATE"
    tipo_real  = "REAL"    if DB_ENGINE == "sqlite" else "NUMERIC"

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS laboratorio (
            id_examen   TEXT PRIMARY KEY,
            id_paciente TEXT NOT NULL,
            fecha_examen {tipo_fecha} NOT NULL,
            resultado    {tipo_real}  NOT NULL
        )
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS urgencias (
            id_atencion  TEXT PRIMARY KEY,
            id_paciente  TEXT NOT NULL,
            fecha_ingreso {tipo_fecha} NOT NULL,
            estado        TEXT NOT NULL
        )
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS farmacia (
            id_despacho    TEXT PRIMARY KEY,
            id_paciente    TEXT NOT NULL,
            fecha_despacho {tipo_fecha} NOT NULL,
            cantidad       INTEGER NOT NULL,
            medicamento    TEXT NOT NULL
        )
    """)


def ya_existe(cursor, tabla: str, campo_pk: str, valor_pk: str, ph: str) -> bool:
    cursor.execute(f"SELECT 1 FROM {tabla} WHERE {campo_pk} = {ph}", [valor_pk])
    return cursor.fetchone() is not None


# -------------------------------------------------------
# FUNCIONES DE VALIDACIÓN INLINE (antes de insertar)
# -------------------------------------------------------

def _fecha_ok(v: str) -> bool:
    try:
        datetime.strptime((v or "").strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _num_positivo(v) -> bool:
    try:
        return float(str(v).strip()) > 0
    except (ValueError, TypeError):
        return False


def _texto_ok(v) -> bool:
    return bool(v and str(v).strip())


# -------------------------------------------------------
# CARGA POR ÁREA
# -------------------------------------------------------

def cargar_laboratorio(cursor, ph: str, log: list) -> tuple:
    archivo = os.path.join(CLEAN_DIR, "laboratorio_valido.csv")

    # Fallback: si no existe el archivo validado, intenta con el limpio
    if not os.path.exists(archivo):
        archivo = os.path.join("data/clean", "laboratorio.csv")

    if not os.path.exists(archivo):
        log.append(f"  ❌ Laboratorio: archivo no encontrado ({archivo})")
        return 0, 0

    insertados = rechazados = 0
    with open(archivo, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            id_ex  = (fila.get("id_examen",   "") or "").strip()
            id_pac = (fila.get("id_paciente", "") or "").strip()
            fecha  = (fila.get("fecha_examen","") or "").strip()
            res    = (fila.get("resultado",   "") or "").strip()

            if not all([_texto_ok(id_ex), _texto_ok(id_pac), _fecha_ok(fecha), _num_positivo(res)]):
                rechazados += 1
                log.append(f"  ❌ Lab rechazado en carga: {id_ex}")
                continue

            if ya_existe(cursor, "laboratorio", "id_examen", id_ex, ph):
                log.append(f"  ⚠️  Lab duplicado ignorado: {id_ex}")
                continue

            cursor.execute(
                f"INSERT INTO laboratorio (id_examen, id_paciente, fecha_examen, resultado) VALUES ({ph},{ph},{ph},{ph})",
                [id_ex, id_pac, fecha, float(res)],
            )
            insertados += 1

    log.append(f"  Laboratorio → insertados: {insertados}, rechazados: {rechazados}")
    return insertados, rechazados


def cargar_urgencias(cursor, ph: str, log: list) -> tuple:
    archivo = os.path.join(CLEAN_DIR, "urgencias_valido.json")

    if not os.path.exists(archivo):
        archivo = os.path.join("data/clean", "urgencias.json")

    if not os.path.exists(archivo):
        log.append(f"  ❌ Urgencias: archivo no encontrado ({archivo})")
        return 0, 0

    with open(archivo, encoding="utf-8") as f:
        datos = json.load(f)

    insertados = rechazados = 0
    for reg in datos:
        id_at  = str(reg.get("id_atencion",  "") or "").strip()
        id_pac = str(reg.get("id_paciente",  "") or "").strip()
        fecha  = str(reg.get("fecha_ingreso","") or "").strip()
        estado = str(reg.get("estado",       "") or "").strip().lower()

        if not all([_texto_ok(id_at), _texto_ok(id_pac), _fecha_ok(fecha)]) \
                or estado not in ESTADOS_URGENCIA_VALIDOS:
            rechazados += 1
            log.append(f"  ❌ Urgencias rechazado en carga: {id_at}")
            continue

        if ya_existe(cursor, "urgencias", "id_atencion", id_at, ph):
            log.append(f"  ⚠️  Urgencias duplicado ignorado: {id_at}")
            continue

        cursor.execute(
            f"INSERT INTO urgencias (id_atencion, id_paciente, fecha_ingreso, estado) VALUES ({ph},{ph},{ph},{ph})",
            [id_at, id_pac, fecha, estado],
        )
        insertados += 1

    log.append(f"  Urgencias → insertados: {insertados}, rechazados: {rechazados}")
    return insertados, rechazados


def cargar_farmacia(cursor, ph: str, log: list) -> tuple:
    archivo = os.path.join(CLEAN_DIR, "farmacia_valido.xml")

    if not os.path.exists(archivo):
        archivo = os.path.join("data/clean", "farmacia.xml")

    if not os.path.exists(archivo):
        log.append(f"  ❌ Farmacia: archivo no encontrado ({archivo})")
        return 0, 0

    try:
        raiz = ET.parse(archivo).getroot()
    except ET.ParseError as e:
        log.append(f"  ❌ XML inválido en farmacia: {e}")
        return 0, 0

    insertados = rechazados = 0
    for d in raiz:
        id_d   = (d.findtext("id_despacho")    or "").strip()
        id_pac = (d.findtext("id_paciente")     or "").strip()
        fecha  = (d.findtext("fecha_despacho")  or "").strip()
        cant   = (d.findtext("cantidad")        or "").strip()
        med    = (d.findtext("medicamento")     or "").strip()

        if not all([_texto_ok(id_d), _texto_ok(id_pac), _fecha_ok(fecha),
                    _num_positivo(cant), _texto_ok(med)]):
            rechazados += 1
            log.append(f"  ❌ Farmacia rechazado en carga: {id_d}")
            continue

        if ya_existe(cursor, "farmacia", "id_despacho", id_d, ph):
            log.append(f"  ⚠️  Farmacia duplicado ignorado: {id_d}")
            continue

        cursor.execute(
            f"INSERT INTO farmacia (id_despacho, id_paciente, fecha_despacho, cantidad, medicamento) VALUES ({ph},{ph},{ph},{ph},{ph})",
            [id_d, id_pac, fecha, int(float(cant)), med],
        )
        insertados += 1

    log.append(f"  Farmacia → insertados: {insertados}, rechazados: {rechazados}")
    return insertados, rechazados


# -------------------------------------------------------
# CONSULTAS DE EJEMPLO
# -------------------------------------------------------

def consultas_ejemplo(cursor) -> dict:
    """Ejecuta una consulta de muestra en cada tabla y retorna los resultados."""
    resultados = {}
    for tabla in ["laboratorio", "urgencias", "farmacia"]:
        cursor.execute(f"SELECT * FROM {tabla} ORDER BY 1 LIMIT 5")
        resultados[tabla] = cursor.fetchall()
    return resultados


def escribir_log(entries: list, nombre_log: str) -> str:
    ruta_log = os.path.join(CARPETA_LOGS, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        f.write("\n".join(entries) + "\n")
    return ruta_log


# -------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------

def main() -> None:
    crear_carpetas()

    inicio = datetime.now()
    sep    = "=" * 55
    log    = [sep, "  ETAPA 4: CARGA A BASE DE DATOS - Clínica MediSalud S.A.", sep,
              f"  Inicio   : {inicio.strftime('%Y-%m-%d %H:%M:%S')}",
              f"  Motor BD : {DB_ENGINE}",
              f"  Ruta BD  : {DB_PATH}", sep]

    print(f"\n{sep}\n  ETAPA 4: CARGA A BASE DE DATOS\n  Clínica MediSalud S.A.\n{sep}")
    print(f"  ▶ Motor : {DB_ENGINE.upper()}")
    print(f"  ▶ BD    : {DB_PATH}\n{sep}")

    # Conectar
    try:
        conexion, ph = conectar_base_datos()
    except RuntimeError as ex:
        log.append(f"ERROR: {ex}")
        ruta = escribir_log(log, f"carga_bd_error_{inicio.strftime('%Y%m%d_%H%M%S')}.log")
        print(f"❌ ERROR al conectar. Ver log: {ruta}")
        return

    cursor = conexion.cursor()
    crear_tablas(cursor, ph)
    conexion.commit()

    # Cargar
    ins_lab,  rech_lab  = cargar_laboratorio(cursor, ph, log)
    ins_urg,  rech_urg  = cargar_urgencias  (cursor, ph, log)
    ins_farm, rech_farm = cargar_farmacia   (cursor, ph, log)
    conexion.commit()

    total_ins  = ins_lab  + ins_urg  + ins_farm
    total_rech = rech_lab + rech_urg + rech_farm

    # Consultas de ejemplo
    resultados = consultas_ejemplo(cursor)

    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()

    # Resumen en consola y log
    resumen = [
        f"\n{sep}", "  RESUMEN DE CARGA", sep,
        f"  🔬 Laboratorio → insertados: {ins_lab:3d}  rechazados: {rech_lab}",
        f"  🚑 Urgencias   → insertados: {ins_urg:3d}  rechazados: {rech_urg}",
        f"  💊 Farmacia    → insertados: {ins_farm:3d}  rechazados: {rech_farm}",
        sep,
        f"  ✅ Total insertados : {total_ins}",
        f"  ❌ Total rechazados : {total_rech}",
        f"  ⏱  Duración         : {duracion:.2f} segundos",
        f"  🏁 Fin              : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)

    if total_ins == 0:
        print("  ⚠️  ADVERTENCIA: no se insertó ningún registro.")
        log.append("  ADVERTENCIA: no se insertó ningún registro.")

    # Mostrar consultas de ejemplo
    print("\n  📋 CONSULTA DE EJEMPLO (primeras 5 filas por tabla):")
    log.append("\n--- CONSULTA DE EJEMPLO ---")
    for tabla, filas in resultados.items():
        print(f"\n  {tabla.upper()} ({len(filas)} fila/s):")
        log.append(f"{tabla} ({len(filas)} filas):")
        for fila in filas:
            print(f"    {fila}")
            log.append(f"  {fila}")

    nombre_log = f"carga_bd_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
    ruta_log   = escribir_log(log, nombre_log)
    print(f"\n📋 Log guardado en: {ruta_log}")
    conexion.close()


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    main()
