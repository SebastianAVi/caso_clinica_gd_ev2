"""
================================================================
  ETAPA 3: VALIDACIÓN - Clínica MediSalud S.A.
================================================================
Lee los archivos limpios desde data/clean/, aplica reglas de
negocio y separa los registros en:
  - Válidos   → data/validados/
  - Rechazados → data/rechazados/  (con motivo del rechazo)

Reglas aplicadas:
  LABORATORIO : id_examen, id_paciente obligatorios | fecha válida
                y no futura | resultado número positivo
  URGENCIAS   : id_atencion, id_paciente obligatorios | fecha válida
                y no futura | estado en lista permitida
  FARMACIA    : id_despacho, id_paciente, medicamento obligatorios
                | fecha válida y no futura | cantidad > 0
================================================================
"""

import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import date, datetime

from config import (
    CARPETA_CLEAN,
    CARPETA_LOGS,
    ESTADOS_URGENCIA_VALIDOS,
)

CARPETA_VALIDADOS  = "data/validados"
CARPETA_RECHAZADOS = "data/rechazados"
HOY                = date.today()


# -------------------------------------------------------
# FUNCIONES DE VALIDACIÓN REUTILIZABLES
# -------------------------------------------------------

def campo_requerido(valor, nombre: str):
    if not valor or str(valor).strip() == "":
        return False, f"Campo obligatorio vacío: {nombre}"
    return True, ""


def es_fecha_valida(fecha_str: str):
    if not (fecha_str or "").strip():
        return False, "Fecha vacía"
    try:
        fecha = datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
        if fecha > HOY:
            return False, f"Fecha futura: {fecha_str}"
        return True, ""
    except ValueError:
        return False, f"Formato de fecha inválido: {fecha_str}"


def es_numero_positivo(valor_str):
    try:
        if float(str(valor_str).strip()) > 0:
            return True, ""
        return False, f"Valor debe ser mayor a 0, se recibió: {valor_str}"
    except (ValueError, TypeError):
        return False, f"Valor no numérico: {valor_str}"


# -------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------

def crear_carpetas() -> None:
    for carpeta in [CARPETA_VALIDADOS, CARPETA_RECHAZADOS, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def escribir_log(log_entries: list, nombre_log: str) -> None:
    ruta_log = os.path.join(CARPETA_LOGS, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries) + "\n")
    print(f"\n📋 Log guardado en: {ruta_log}")


# -------------------------------------------------------
# VALIDACIÓN POR ÁREA
# -------------------------------------------------------

def validar_laboratorio(log: list):
    entrada  = os.path.join(CARPETA_CLEAN, "laboratorio.csv")
    sal_val  = os.path.join(CARPETA_VALIDADOS,  "laboratorio_valido.csv")
    sal_rech = os.path.join(CARPETA_RECHAZADOS, "laboratorio_rechazado.csv")

    print("\n🔬 Validando: LABORATORIO")
    log.append("\n--- LABORATORIO ---")

    if not os.path.exists(entrada):
        msg = f"  ❌ Archivo no encontrado: {entrada}"
        print(msg); log.append(msg)
        return 0, 0, 0

    validos    = []
    rechazados = []

    with open(entrada, encoding="utf-8") as f:
        lector = csv.DictReader(f)
        campos = lector.fieldnames or []
        for fila in lector:
            errores = []
            for campo in ["id_examen", "id_paciente"]:
                ok, msg = campo_requerido(fila.get(campo), campo)
                if not ok: errores.append(msg)
            ok, msg = es_fecha_valida(fila.get("fecha_examen", ""))
            if not ok: errores.append(msg)
            ok, msg = es_numero_positivo(fila.get("resultado", ""))
            if not ok: errores.append(msg)

            if errores:
                fila["motivo_rechazo"] = " | ".join(errores)
                rechazados.append(fila)
                log.append(f"  ❌ Rechazado {fila.get('id_examen','?')}: {fila['motivo_rechazo']}")
            else:
                validos.append(fila)

    # Guardar válidos
    with open(sal_val, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader(); writer.writerows(validos)

    # Guardar rechazados
    if rechazados:
        with open(sal_rech, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(campos) + ["motivo_rechazo"])
            writer.writeheader(); writer.writerows(rechazados)

    _imprimir_stats("LABORATORIO", len(validos), len(rechazados), log)
    return len(validos) + len(rechazados), len(validos), len(rechazados)


def validar_urgencias(log: list):
    entrada  = os.path.join(CARPETA_CLEAN, "urgencias.json")
    sal_val  = os.path.join(CARPETA_VALIDADOS,  "urgencias_valido.json")
    sal_rech = os.path.join(CARPETA_RECHAZADOS, "urgencias_rechazado.json")

    print("\n🚑 Validando: URGENCIAS")
    log.append("\n--- URGENCIAS ---")

    if not os.path.exists(entrada):
        msg = f"  ❌ Archivo no encontrado: {entrada}"
        print(msg); log.append(msg)
        return 0, 0, 0

    if os.path.getsize(entrada) == 0:
        msg = "  ⚠️  JSON vacío: no hay registros para validar"
        print(msg); log.append(msg)
        return 0, 0, 0

    with open(entrada, encoding="utf-8") as f:
        datos = json.load(f)

    validos    = []
    rechazados = []

    for reg in datos:
        errores = []
        for campo in ["id_atencion", "id_paciente"]:
            ok, msg = campo_requerido(reg.get(campo), campo)
            if not ok: errores.append(msg)
        ok, msg = es_fecha_valida(reg.get("fecha_ingreso", ""))
        if not ok: errores.append(msg)
        estado = str(reg.get("estado", "")).strip().lower()
        if estado not in ESTADOS_URGENCIA_VALIDOS:
            errores.append(f"Estado inválido: '{estado}' (permitidos: {', '.join(sorted(ESTADOS_URGENCIA_VALIDOS))})")

        if errores:
            reg["motivo_rechazo"] = " | ".join(errores)
            rechazados.append(reg)
            log.append(f"  ❌ Rechazado {reg.get('id_atencion','?')}: {reg['motivo_rechazo']}")
        else:
            validos.append(reg)

    with open(sal_val,  "w", encoding="utf-8") as f:
        json.dump(validos, f, ensure_ascii=False, indent=2)
    with open(sal_rech, "w", encoding="utf-8") as f:
        json.dump(rechazados, f, ensure_ascii=False, indent=2)

    _imprimir_stats("URGENCIAS", len(validos), len(rechazados), log)
    return len(validos) + len(rechazados), len(validos), len(rechazados)


def validar_farmacia(log: list):
    entrada  = os.path.join(CARPETA_CLEAN, "farmacia.xml")
    sal_val  = os.path.join(CARPETA_VALIDADOS,  "farmacia_valido.xml")
    sal_rech = os.path.join(CARPETA_RECHAZADOS, "farmacia_rechazado.csv")

    print("\n💊 Validando: FARMACIA")
    log.append("\n--- FARMACIA ---")

    if not os.path.exists(entrada):
        msg = f"  ❌ Archivo no encontrado: {entrada}"
        print(msg); log.append(msg)
        return 0, 0, 0

    if os.path.getsize(entrada) == 0:
        msg = "  ⚠️  XML vacío: no hay registros para validar"
        print(msg); log.append(msg)
        return 0, 0, 0

    try:
        arbol = ET.parse(entrada)
    except ET.ParseError as e:
        msg = f"  ❌ XML inválido: {e}"
        print(msg); log.append(msg)
        return 0, 0, 0

    raiz       = arbol.getroot()
    validos    = []
    rechazados = []

    for despacho in raiz:
        errores = []
        id_d = (despacho.findtext("id_despacho") or "").strip()
        id_p = (despacho.findtext("id_paciente") or "").strip()

        ok, msg = campo_requerido(id_d, "id_despacho");  not ok and errores.append(msg)
        ok, msg = campo_requerido(id_p, "id_paciente");  not ok and errores.append(msg)
        ok, msg = es_fecha_valida(despacho.findtext("fecha_despacho") or ""); not ok and errores.append(msg)
        ok, msg = es_numero_positivo(despacho.findtext("cantidad") or "0");   not ok and errores.append(msg)
        ok, msg = campo_requerido(despacho.findtext("medicamento"), "medicamento"); not ok and errores.append(msg)

        if errores:
            rechazados.append({
                "id_despacho"   : id_d,
                "id_paciente"   : id_p,
                "medicamento"   : (despacho.findtext("medicamento") or "").strip(),
                "motivo_rechazo": " | ".join(errores),
            })
            log.append(f"  ❌ Rechazado despacho {id_d}: {' | '.join(errores)}")
        else:
            validos.append(despacho)

    # Guardar XML válidos
    raiz_val = ET.Element(raiz.tag)
    for d in validos:
        raiz_val.append(d)
    ET.ElementTree(raiz_val).write(sal_val, encoding="unicode", xml_declaration=True)

    # Guardar rechazados CSV
    if rechazados:
        with open(sal_rech, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rechazados[0].keys()))
            writer.writeheader(); writer.writerows(rechazados)

    _imprimir_stats("FARMACIA", len(validos), len(rechazados), log)
    return len(validos) + len(rechazados), len(validos), len(rechazados)


def _imprimir_stats(area: str, validos: int, rechazados: int, log: list) -> None:
    total = validos + rechazados
    print(f"  📥 Total revisados : {total}")
    print(f"  ✅ Válidos         : {validos}")
    print(f"  ❌ Rechazados      : {rechazados}")
    log += [f"  Total revisados : {total}",
            f"  Válidos         : {validos}",
            f"  Rechazados      : {rechazados}"]


# -------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------

def ejecutar_validacion() -> None:
    crear_carpetas()

    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log += [sep, "  VALIDACIÓN DE DATOS - Clínica MediSalud S.A.", sep,
            f"  Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Fecha de referencia (hoy): {HOY}", sep]

    print(f"\n{sep}\n  ETAPA 3: VALIDACIÓN DE DATOS\n  Clínica MediSalud S.A.\n{sep}")
    print(f"  ▶ Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total_rev = total_val = total_rech = 0
    for fn in [validar_laboratorio, validar_urgencias, validar_farmacia]:
        rev, val, rech = fn(log)
        total_rev  += rev
        total_val  += val
        total_rech += rech

    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()

    resumen = [
        f"\n{sep}", "  RESUMEN DE VALIDACIÓN", sep,
        f"  📥 Total revisados  : {total_rev}",
        f"  ✅ Total válidos    : {total_val}",
        f"  ❌ Total rechazados : {total_rech}",
        f"  ⏱  Duración         : {duracion:.2f} segundos",
        f"  🏁 Fin              : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)

    escribir_log(log, f"validacion_{inicio.strftime('%Y%m%d_%H%M%S')}.log")


# -------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    ejecutar_validacion()
