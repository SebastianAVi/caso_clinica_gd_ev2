import csv
import json
import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

LOGS_DIR = "logs"
CLEAN_DIR = "data/clean"
DB_PATH = os.environ.get("DB_PATH", "data/clinica.db")
DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite").lower()


def crear_carpetas():
    os.makedirs(LOGS_DIR, exist_ok=True)
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def conectar_base_datos():
    """Conecta a la base de datos SQLite por defecto."""
    if DB_ENGINE == "postgresql":
        try:
            import psycopg2
        except ImportError as e:
            raise RuntimeError(
                "PostgreSQL no disponible: instale psycopg2-binary o use DB_ENGINE=sqlite"
            ) from e

        conexion = psycopg2.connect(
            dbname=os.environ.get("DB_NAME", "clinica"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
        )
        placeholder = "%s"
    else:
        conexion = sqlite3.connect(DB_PATH)
        placeholder = "?"

    return conexion, placeholder


def ejecutar_sql(cursor, sentencia, params=None):
    if params is None:
        params = []
    cursor.execute(sentencia, params)


def crear_tablas(cursor):
    tipo_fecha = "TEXT" if DB_ENGINE == "sqlite" else "DATE"
    tipo_real = "REAL" if DB_ENGINE == "sqlite" else "NUMERIC"

    ejecutar_sql(
        cursor,
        f"""
        CREATE TABLE IF NOT EXISTS laboratorio (
            id_examen TEXT PRIMARY KEY,
            id_paciente TEXT NOT NULL,
            fecha_examen {tipo_fecha} NOT NULL,
            resultado {tipo_real} NOT NULL
        )
        """,
    )

    ejecutar_sql(
        cursor,
        f"""
        CREATE TABLE IF NOT EXISTS urgencias (
            id_atencion TEXT PRIMARY KEY,
            id_paciente TEXT NOT NULL,
            fecha_ingreso {tipo_fecha} NOT NULL,
            estado TEXT NOT NULL
        )
        """,
    )

    ejecutar_sql(
        cursor,
        f"""
        CREATE TABLE IF NOT EXISTS farmacia (
            id_despacho TEXT PRIMARY KEY,
            id_paciente TEXT NOT NULL,
            fecha_despacho {tipo_fecha} NOT NULL,
            cantidad INTEGER NOT NULL,
            medicamento TEXT NOT NULL
        )
        """,
    )


def existe_registro(cursor, tabla, campo_pk, valor_pk, placeholder):
    ejecutar_sql(
        cursor,
        f"SELECT 1 FROM {tabla} WHERE {campo_pk} = {placeholder}",
        [valor_pk],
    )
    return cursor.fetchone() is not None


def validar_fecha(fecha_str):
    if not fecha_str or str(fecha_str).strip() == "":
        return False
    try:
        datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validar_numero_positivo(valor):
    try:
        return float(str(valor).strip()) > 0
    except (ValueError, TypeError):
        return False


def validar_texto(valor):
    return bool(valor and str(valor).strip())


def cargar_laboratorio(cursor, placeholder, log):
    archivo = os.path.join(CLEAN_DIR, "laboratorio.csv")
    if not os.path.exists(archivo):
        msg = f"Archivo no encontrado: {archivo}"
        log.append(msg)
        return 0, 0

    insertados = 0
    rechazados = 0

    with open(archivo, encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            id_examen = fila.get("id_examen", "").strip()
            id_paciente = fila.get("id_paciente", "").strip()
            fecha_examen = fila.get("fecha_examen", "").strip()
            resultado = fila.get("resultado", "").strip()

            valido = True
            if not validar_texto(id_examen):
                valido = False
            if not validar_texto(id_paciente):
                valido = False
            if not validar_fecha(fecha_examen):
                valido = False
            if not validar_numero_positivo(resultado):
                valido = False

            if not valido:
                rechazados += 1
                log.append(f"  ❌ Laboratorio rechazado: {fila}")
                continue

            if existe_registro(cursor, "laboratorio", "id_examen", id_examen, placeholder):
                log.append(f"  ⚠️  Laboratorio duplicado ignorado: {id_examen}")
                continue

            ejecutar_sql(
                cursor,
                f"INSERT INTO laboratorio (id_examen, id_paciente, fecha_examen, resultado) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
                [id_examen, id_paciente, fecha_examen, float(resultado)],
            )
            insertados += 1

    return insertados, rechazados


def cargar_urgencias(cursor, placeholder, log):
    archivo = os.path.join(CLEAN_DIR, "urgencias.json")
    if not os.path.exists(archivo):
        msg = f"Archivo no encontrado: {archivo}"
        log.append(msg)
        return 0, 0

    insertados = 0
    rechazados = 0

    with open(archivo, encoding="utf-8") as f:
        datos = json.load(f)

    for reg in datos:
        id_atencion = str(reg.get("id_atencion", "")).strip()
        id_paciente = str(reg.get("id_paciente", "")).strip()
        fecha_ingreso = str(reg.get("fecha_ingreso", "")).strip()
        estado = str(reg.get("estado", "")).strip().lower()

        valido = True
        if not validar_texto(id_atencion):
            valido = False
        if not validar_texto(id_paciente):
            valido = False
        if not validar_fecha(fecha_ingreso):
            valido = False
        if estado not in {"alta", "hospitalizado", "uci", "observacion", "fallecido"}:
            valido = False

        if not valido:
            rechazados += 1
            log.append(f"  ❌ Urgencias rechazado: {reg}")
            continue

        if existe_registro(cursor, "urgencias", "id_atencion", id_atencion, placeholder):
            log.append(f"  ⚠️  Urgencias duplicado ignorado: {id_atencion}")
            continue

        ejecutar_sql(
            cursor,
            f"INSERT INTO urgencias (id_atencion, id_paciente, fecha_ingreso, estado) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
            [id_atencion, id_paciente, fecha_ingreso, estado],
        )
        insertados += 1

    return insertados, rechazados


def cargar_farmacia(cursor, placeholder, log):
    archivo = os.path.join(CLEAN_DIR, "farmacia.xml")
    if not os.path.exists(archivo):
        msg = f"Archivo no encontrado: {archivo}"
        log.append(msg)
        return 0, 0

    insertados = 0
    rechazados = 0

    try:
        arbol = ET.parse(archivo)
    except ET.ParseError as e:
        log.append(f"  ❌ XML inválido: {e}")
        return 0, 0

    raiz = arbol.getroot()
    for despacho in raiz.findall("despacho"):
        id_despacho = despacho.findtext("id_despacho", "").strip()
        id_paciente = despacho.findtext("id_paciente", "").strip()
        fecha_despacho = despacho.findtext("fecha_despacho", "").strip()
        cantidad = despacho.findtext("cantidad", "").strip()
        medicamento = despacho.findtext("medicamento", "").strip()

        valido = True
        if not validar_texto(id_despacho):
            valido = False
        if not validar_texto(id_paciente):
            valido = False
        if not validar_fecha(fecha_despacho):
            valido = False
        if not validar_numero_positivo(cantidad):
            valido = False
        if not validar_texto(medicamento):
            valido = False

        if not valido:
            rechazados += 1
            log.append(f"  ❌ Farmacia rechazado: {id_despacho}")
            continue

        if existe_registro(cursor, "farmacia", "id_despacho", id_despacho, placeholder):
            log.append(f"  ⚠️  Farmacia duplicado ignorado: {id_despacho}")
            continue

        ejecutar_sql(
            cursor,
            f"INSERT INTO farmacia (id_despacho, id_paciente, fecha_despacho, cantidad, medicamento) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})",
            [id_despacho, id_paciente, fecha_despacho, int(float(cantidad)), medicamento],
        )
        insertados += 1

    return insertados, rechazados


def escribir_log(entries, nombre_log):
    ruta_log = os.path.join(LOGS_DIR, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        for linea in entries:
            f.write(linea + "\n")
    return ruta_log


def consulta_ejemplo(cursor):
    consultas = {
        "laboratorio": "SELECT * FROM laboratorio ORDER BY id_examen LIMIT 5",
        "urgencias": "SELECT * FROM urgencias ORDER BY id_atencion LIMIT 5",
        "farmacia": "SELECT * FROM farmacia ORDER BY id_despacho LIMIT 5",
    }
    resultado = {}
    for tabla, sql in consultas.items():
        ejecutar_sql(cursor, sql)
        filas = cursor.fetchall()
        resultado[tabla] = filas
    return resultado


def main():
    crear_carpetas()
    inicio = datetime.now()
    log = ["=== ETAPA 4: CARGA A BASE DE DATOS ===", f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", f"DB Engine: {DB_ENGINE}"]

    try:
        conexion, placeholder = conectar_base_datos()
    except RuntimeError as ex:
        log.append(f"ERROR: {ex}")
        ruta_log = escribir_log(log, f"carga_bd_error_{inicio.strftime('%Y%m%d_%H%M%S')}.log")
        print("ERROR al conectar a la base de datos. Ver log:", ruta_log)
        return

    cursor = conexion.cursor()
    crear_tablas(cursor)
    conexion.commit()

    cargados_labo, rechazados_labo = cargar_laboratorio(cursor, placeholder, log)
    cargados_urg, rechazados_urg = cargar_urgencias(cursor, placeholder, log)
    cargados_farm, rechazados_farm = cargar_farmacia(cursor, placeholder, log)

    total_insertados = cargados_labo + cargados_urg + cargados_farm
    total_rechazados = rechazados_labo + rechazados_urg + rechazados_farm

    conexion.commit()

    log.append("--- RESUMEN ---")
    log.append(f"Laboratorio insertados: {cargados_labo}, rechazados: {rechazados_labo}")
    log.append(f"Urgencias insertados  : {cargados_urg}, rechazados: {rechazados_urg}")
    log.append(f"Farmacia insertados   : {cargados_farm}, rechazados: {rechazados_farm}")
    log.append(f"Total insertados      : {total_insertados}")
    log.append(f"Total rechazados      : {total_rechazados}")

    if total_insertados == 0:
        log.append("ADVERTENCIA: No se insertó ningún registro.")

    consultas = consulta_ejemplo(cursor)
    log.append("--- CONSULTA DE EJEMPLO ---")
    for tabla, filas in consultas.items():
        log.append(f"{tabla} ({len(filas)} filas mostradas):")
        for fila in filas:
            log.append(f"  {fila}")

    fin = datetime.now()
    duracion = (fin - inicio).total_seconds()
    log.append(f"Fin: {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(f"Duración: {duracion:.2f} s")

    nombre_log = f"carga_bd_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
    ruta_log = escribir_log(log, nombre_log)

    print("Carga finalizada.")
    print(f"Base de datos utilizada: {DB_PATH}")
    print(f"Registros insertados: {total_insertados}")
    print(f"Log generado en: {ruta_log}")
    print("Consulta de ejemplo: primera filas de cada tabla")
    for tabla, filas in consultas.items():
        print(f"\n{tabla}:")
        for fila in filas:
            print(f"  {fila}")

    conexion.close()


if __name__ == "__main__":
    main()
