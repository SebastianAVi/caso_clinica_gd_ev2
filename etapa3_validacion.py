import os
import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime, date

# -------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# -------------------------------------------------------
CARPETA_PROCESSED  = "data/clean"
CARPETA_LIMPIEZA   = "limpieza"
CARPETA_LOGS       = "logs"

# Valores permitidos para el estado en urgencias
ESTADOS_URGENCIA_VALIDOS = {"alta", "hospitalizado", "uci", "observacion", "fallecido"}

# Fecha de hoy para validar que no haya fechas futuras
HOY = date.today()


# -------------------------------------------------------
# FUNCIONES DE APOYO
# -------------------------------------------------------

def crear_carpetas():
    os.makedirs(CARPETA_LOGS, exist_ok=True)


def es_fecha_valida(fecha_str):
    """
    Verifica que la fecha tenga formato YYYY-MM-DD y no sea futura.
    Retorna (True/False, mensaje_error)
    """
    if not fecha_str or fecha_str.strip() == "":
        return False, "Fecha vacía"
    try:
        fecha = datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
        if fecha > HOY:
            return False, f"Fecha futura: {fecha_str}"
        return True, ""
    except ValueError:
        return False, f"Formato de fecha inválido: {fecha_str}"


def es_numero_positivo(valor_str):
    """
    Verifica que el valor sea numérico y mayor que 0.
    Retorna (True/False, mensaje_error)
    """
    try:
        num = float(str(valor_str).strip())
        if num <= 0:
            return False, f"Valor debe ser mayor a 0, se recibió: {valor_str}"
        return True, ""
    except (ValueError, TypeError):
        return False, f"Valor no numérico: {valor_str}"


def campo_requerido(valor, nombre_campo):
    """
    Verifica que un campo obligatorio no esté vacío.
    Retorna (True/False, mensaje_error)
    """
    if not valor or str(valor).strip() == "":
        return False, f"Campo obligatorio vacío: {nombre_campo}"
    return True, ""


def buscar_ruta_entrada(nombre_archivo, log):
    """
    Busca el archivo de entrada en los lugares esperados.
    Primero revisa data/clean y luego intenta usar la carpeta limpieza.
    """
    candidatos = [
        os.path.join(CARPETA_PROCESSED, nombre_archivo),
        os.path.join(CARPETA_LIMPIEZA, nombre_archivo),
        os.path.join("data", "processed", nombre_archivo),
        os.path.join("data", "raw", nombre_archivo),
    ]

    for ruta in candidatos:
        if os.path.exists(ruta):
            if ruta.startswith(CARPETA_LIMPIEZA):
                msg = f"  ℹ️  Archivo encontrado en carpeta limpieza: {ruta}"
                print(msg); log.append(msg)
            return ruta

    for root, _, files in os.walk(CARPETA_LIMPIEZA):
        if nombre_archivo in files:
            ruta = os.path.join(root, nombre_archivo)
            msg = f"  ℹ️  Archivo encontrado en limpieza (recursivo): {ruta}"
            print(msg); log.append(msg)
            return ruta

    return None


def escribir_log(log_entries, nombre_log):
    ruta_log = os.path.join(CARPETA_LOGS, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        for linea in log_entries:
            f.write(linea + "\n")
    print(f"\n📋 Log guardado en: {ruta_log}")


# -------------------------------------------------------
# VALIDACIÓN POR ÁREA
# -------------------------------------------------------

def validar_laboratorio(log):
    """
    Valida cada registro del archivo laboratorio.csv.
    Separa en válidos y rechazados.
    """
    entrada   = buscar_ruta_entrada("laboratorio.csv", log)

    print("\n🔬 Validando: LABORATORIO")
    log.append("\n--- LABORATORIO ---")

    if not entrada:
        msg = f"  ❌ Archivo no encontrado ni en data/clean ni en limpieza: laboratorio.csv"
        print(msg); log.append(msg)
        return 0, 0, 0

    validos    = 0
    rechazados = 0

    with open(entrada, encoding="utf-8") as f:
        lector = csv.DictReader(f)

        for fila in lector:
            errores = []

            # Regla 1: Campos obligatorios
            for campo in ["id_examen", "id_paciente"]:
                ok, msg = campo_requerido(fila.get(campo), campo)
                if not ok:
                    errores.append(msg)

            # Regla 2: Fecha válida y no futura
            ok, msg = es_fecha_valida(fila.get("fecha_examen", ""))
            if not ok:
                errores.append(msg)

            # Regla 3: Resultado debe ser número positivo
            ok, msg = es_numero_positivo(fila.get("resultado", ""))
            if not ok:
                errores.append(msg)

            if errores:
                rechazados += 1
                motivo = " | ".join(errores)
                log.append(f"  ❌ Rechazado {fila.get('id_examen','?')}: {motivo}")
            else:
                validos += 1

    total = validos + rechazados
    print(f"  📥 Total revisados : {total}")
    print(f"  ✅ Válidos         : {validos}")
    print(f"  ❌ Rechazados      : {rechazados}")

    log.append(f"  Total revisados : {total}")
    log.append(f"  Válidos         : {validos}")
    log.append(f"  Rechazados      : {rechazados}")

    return total, validos, rechazados


def validar_urgencias(log):
    """
    Valida cada registro del archivo urgencias.json.
    """
    entrada  = buscar_ruta_entrada("urgencias.json", log)

    print("\n🚑 Validando: URGENCIAS")
    log.append("\n--- URGENCIAS ---")

    if not entrada:
        msg = f"  ❌ Archivo no encontrado ni en data/clean ni en limpieza: urgencias.json"
        print(msg); log.append(msg)
        return 0, 0, 0

    if os.path.getsize(entrada) == 0:
        msg = f"  ⚠️  JSON vacío en {entrada}: no hay registros para validar"
        print(msg); log.append(msg)
        return 0, 0, 0

    try:
        with open(entrada, encoding="utf-8") as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"  ❌ JSON inválido en {entrada}: {e.msg}"
        print(msg); log.append(msg)
        return 0, 0, 0

    validos    = 0
    rechazados = 0

    for reg in datos:
        errores = []

        # Regla 1: Campos obligatorios
        for campo in ["id_atencion", "id_paciente"]:
            ok, msg = campo_requerido(reg.get(campo), campo)
            if not ok:
                errores.append(msg)

        # Regla 2: Fecha válida y no futura
        ok, msg = es_fecha_valida(reg.get("fecha_ingreso", ""))
        if not ok:
            errores.append(msg)

        # Regla 3: Estado debe ser un valor permitido
        estado = str(reg.get("estado", "")).strip().lower()
        if estado not in ESTADOS_URGENCIA_VALIDOS:
            errores.append(f"Estado inválido: '{estado}' (permitidos: {', '.join(ESTADOS_URGENCIA_VALIDOS)})")

        if errores:
            rechazados += 1
            motivo = " | ".join(errores)
            log.append(f"  ❌ Rechazado {reg.get('id_atencion','?')}: {motivo}")
        else:
            validos += 1

    total = validos + rechazados
    print(f"  📥 Total revisados : {total}")
    print(f"  ✅ Válidos         : {validos}")
    print(f"  ❌ Rechazados      : {rechazados}")

    log.append(f"  Total revisados : {total}")
    log.append(f"  Válidos         : {validos}")
    log.append(f"  Rechazados      : {rechazados}")

    return total, validos, rechazados


def validar_farmacia(log):
    """
    Valida cada registro del archivo farmacia.xml.
    """
    entrada  = buscar_ruta_entrada("farmacia.xml", log)

    print("\n💊 Validando: FARMACIA")
    log.append("\n--- FARMACIA ---")

    if not entrada:
        msg = f"  ❌ Archivo no encontrado ni en data/clean ni en limpieza: farmacia.xml"
        print(msg); log.append(msg)
        return 0, 0, 0

    if os.path.getsize(entrada) == 0:
        msg = f"  ⚠️  XML vacío en {entrada}: no hay registros para validar"
        print(msg); log.append(msg)
        return 0, 0, 0

    try:
        arbol = ET.parse(entrada)
    except ET.ParseError as e:
        msg = f"  ❌ XML inválido en {entrada}: {e}"
        print(msg); log.append(msg)
        return 0, 0, 0

    raiz       = arbol.getroot()
    todos      = list(raiz)
    validos    = 0
    rechazados = 0

    for despacho in todos:
        errores    = []
        id_d = despacho.findtext("id_despacho", "").strip()
        id_p = despacho.findtext("id_paciente", "").strip()

        # Regla 1: Campos obligatorios
        ok, msg = campo_requerido(id_d, "id_despacho")
        if not ok: errores.append(msg)
        ok, msg = campo_requerido(id_p, "id_paciente")
        if not ok: errores.append(msg)

        # Regla 2: Fecha válida y no futura
        ok, msg = es_fecha_valida(despacho.findtext("fecha_despacho", ""))
        if not ok: errores.append(msg)

        # Regla 3: Cantidad mayor a 0
        ok, msg = es_numero_positivo(despacho.findtext("cantidad", "0"))
        if not ok: errores.append(msg)

        # Regla 4: Medicamento no vacío
        ok, msg = campo_requerido(despacho.findtext("medicamento", ""), "medicamento")
        if not ok: errores.append(msg)

        if errores:
            rechazados += 1
            motivo = " | ".join(errores)
            log.append(f"  ❌ Rechazado despacho {id_d}: {motivo}")
        else:
            validos += 1

    total = validos + rechazados
    print(f"  📥 Total revisados : {total}")
    print(f"  ✅ Válidos         : {validos}")
    print(f"  ❌ Rechazados      : {rechazados}")

    log.append(f"  Total revisados : {total}")
    log.append(f"  Válidos         : {validos}")
    log.append(f"  Rechazados      : {rechazados}")

    return total, validos, rechazados


# -------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------

def ejecutar_validacion():
    crear_carpetas()

    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log.append(sep)
    log.append("  VALIDACIÓN DE DATOS - Clínica MediSalud S.A.")
    log.append(sep)
    log.append(f"  Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(f"  Fecha de referencia (hoy): {HOY}")
    log.append(sep)

    print("\n" + sep)
    print("  ETAPA 3: VALIDACIÓN DE DATOS")
    print("  Clínica MediSalud S.A.")
    print(sep)
    print(f"  ▶ Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep)

    total_rev  = 0
    total_val  = 0
    total_rech = 0

    for fn in [validar_laboratorio, validar_urgencias, validar_farmacia]:
        rev, val, rech = fn(log)
        total_rev  += rev
        total_val  += val
        total_rech += rech

    fin      = datetime.now()
    duracion = (fin - inicio).seconds

    print("\n" + sep)
    print("  RESUMEN DE VALIDACIÓN")
    print(sep)
    print(f"  📥 Total revisados  : {total_rev}")
    print(f"  ✅ Total válidos    : {total_val}")
    print(f"  ❌ Total rechazados : {total_rech}")
    print(f"  ⏱  Duración         : {duracion} segundos")
    print(f"  🏁 Fin              : {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep + "\n")

    log.append("\n" + sep)
    log.append("  RESUMEN")
    log.append(sep)
    log.append(f"  Total revisados  : {total_rev}")
    log.append(f"  Total válidos    : {total_val}")
    log.append(f"  Total rechazados : {total_rech}")
    log.append(f"  Duración         : {duracion} segundos")
    log.append(f"  Fin              : {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    log.append(sep)

    nombre_log = f"validacion_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
    escribir_log(log, nombre_log)


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    ejecutar_validacion()