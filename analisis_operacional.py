import sqlite3
import os
from datetime import datetime
from config import DB_PATH, CARPETA_LOGS


def conectar():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Base de datos no encontrada: {DB_PATH}. Ejecute primero 04_carga_bd.py")
    return sqlite3.connect(DB_PATH)


def escribir_log(entradas, nombre):
    os.makedirs(CARPETA_LOGS, exist_ok=True)
    ruta = os.path.join(CARPETA_LOGS, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(entradas) + "\n")
    return ruta


def analisis_uso_camas(cursor, log):
    print("\nANALISIS DE USO DE CAMAS")
    log.append("\n--- USO DE CAMAS ---")

    cursor.execute("""
        SELECT estado, COUNT(*) as total
        FROM urgencias
        GROUP BY estado
        ORDER BY total DESC
    """)
    filas = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM urgencias")
    total = cursor.fetchone()[0]

    print(f"  Total atenciones registradas: {total}")
    log.append(f"  Total atenciones: {total}")

    print(f"  {'Estado':<20} {'Cantidad':>10} {'Porcentaje':>12}")
    print(f"  {'-'*44}")
    log.append(f"  {'Estado':<20} {'Cantidad':>10} {'Porcentaje':>12}")

    for estado, cantidad in filas:
        porcentaje = (cantidad / total * 100) if total > 0 else 0
        linea = f"  {estado:<20} {cantidad:>10} {porcentaje:>11.1f}%"
        print(linea)
        log.append(linea)

    cursor.execute("""
        SELECT COUNT(*) as total
        FROM urgencias
        WHERE estado IN ('hospitalizado', 'uci')
    """)
    ocupadas = cursor.fetchone()[0] or 0
    linea = f"\n  Camas en uso (hospitalizado + uci): {ocupadas}"
    print(linea)
    log.append(linea)


def analisis_examenes_laboratorio(cursor, log):
    print("\nANALISIS DE EXAMENES DE LABORATORIO")
    log.append("\n--- EXAMENES DE LABORATORIO ---")

    cursor.execute("SELECT COUNT(*) FROM laboratorio")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(resultado), MIN(resultado), MAX(resultado) FROM laboratorio")
    promedio, minimo, maximo = cursor.fetchone()

    print(f"  Total examenes registrados : {total}")
    print(f"  Resultado promedio         : {promedio:.2f}" if promedio else "  Resultado promedio: sin datos")
    print(f"  Resultado minimo           : {minimo}")
    print(f"  Resultado maximo           : {maximo}")

    log += [
        f"  Total examenes: {total}",
        f"  Promedio resultado: {promedio:.2f}" if promedio else "  Promedio: sin datos",
        f"  Minimo: {minimo}",
        f"  Maximo: {maximo}",
    ]

    cursor.execute("""
        SELECT id_paciente, COUNT(*) as examenes
        FROM laboratorio
        GROUP BY id_paciente
        ORDER BY examenes DESC
        LIMIT 5
    """)
    filas = cursor.fetchall()
    print(f"\n  Top 5 pacientes con mas examenes:")
    log.append("  Top 5 pacientes con mas examenes:")
    for paciente, examenes in filas:
        linea = f"    {paciente}: {examenes} examen/es"
        print(linea)
        log.append(linea)


def analisis_farmacia(cursor, log):
    print("\nANALISIS DE DESPACHOS DE FARMACIA")
    log.append("\n--- DESPACHOS DE FARMACIA ---")

    cursor.execute("SELECT COUNT(*) FROM farmacia")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT medicamento, COUNT(*) as despachos, SUM(cantidad) as unidades
        FROM farmacia
        GROUP BY medicamento
        ORDER BY despachos DESC
        LIMIT 5
    """)
    filas = cursor.fetchall()

    print(f"  Total despachos registrados: {total}")
    log.append(f"  Total despachos: {total}")
    print(f"\n  Top 5 medicamentos mas despachados:")
    log.append("  Top 5 medicamentos mas despachados:")
    print(f"  {'Medicamento':<25} {'Despachos':>10} {'Unidades':>10}")
    print(f"  {'-'*47}")

    for med, despachos, unidades in filas:
        linea = f"  {med:<25} {despachos:>10} {unidades:>10}"
        print(linea)
        log.append(linea)


def analisis_actividad_por_mes(cursor, log):
    print("\nACTIVIDAD POR MES")
    log.append("\n--- ACTIVIDAD POR MES ---")

    cursor.execute("""
        SELECT substr(fecha_ingreso, 1, 7) as mes, COUNT(*) as atenciones
        FROM urgencias
        GROUP BY mes
        ORDER BY mes
    """)
    filas = cursor.fetchall()

    print(f"  {'Mes':<12} {'Atenciones Urgencias':>22}")
    print(f"  {'-'*35}")
    log.append(f"  {'Mes':<12} {'Atenciones':>22}")

    for mes, atenciones in filas:
        linea = f"  {mes:<12} {atenciones:>22}"
        print(linea)
        log.append(linea)


def main():
    inicio = datetime.now()
    sep    = "=" * 55
    log    = [sep, "ANALISIS OPERACIONAL - Clinica MediSalud S.A.", sep,
              f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}", sep]

    print(f"\n{sep}\nANALISIS OPERACIONAL\nClinica MediSalud S.A.\n{sep}")
    print(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    try:
        conexion = conectar()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    cursor = conexion.cursor()

    analisis_uso_camas(cursor, log)
    analisis_examenes_laboratorio(cursor, log)
    analisis_farmacia(cursor, log)
    analisis_actividad_por_mes(cursor, log)

    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()
    cierre   = [f"\n{sep}", f"Fin: {fin.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Duracion: {duracion:.2f} segundos", sep]
    for linea in cierre:
        print(linea)
    log.extend(cierre)

    nombre_log = f"analisis_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
    ruta_log   = escribir_log(log, nombre_log)
    print(f"Log guardado en: {ruta_log}")
    conexion.close()


if __name__ == "__main__":
    main()
