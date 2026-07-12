import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import date, datetime

from config import CARPETA_CLEAN, CARPETA_LOGS, ESTADOS_URGENCIA_VALIDOS

CARPETA_VALIDADOS  = "data/validados"
CARPETA_RECHAZADOS = "data/rechazados"
HOY                = date.today()


def crear_carpetas():
    for carpeta in [CARPETA_VALIDADOS, CARPETA_RECHAZADOS, CARPETA_LOGS]:
        os.makedirs(carpeta, exist_ok=True)


def escribir_log(entradas, nombre):
    ruta = os.path.join(CARPETA_LOGS, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(entradas) + "\n")
    print(f"Log guardado en: {ruta}")


def campo_requerido(valor, nombre):
    if not valor or str(valor).strip() == "":
        return False, f"Campo obligatorio vacio: {nombre}"
    return True, ""


def es_fecha_valida(fecha_str):
    if not (fecha_str or "").strip():
        return False, "Fecha vacia"
    try:
        fecha = datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
        if fecha > HOY:
            return False, f"Fecha futura: {fecha_str}"
        return True, ""
    except ValueError:
        return False, f"Formato de fecha invalido: {fecha_str}"


def es_numero_positivo(valor_str):
    try:
        if float(str(valor_str).strip()) > 0:
            return True, ""
        return False, f"Valor debe ser mayor a 0: {valor_str}"
    except (ValueError, TypeError):
        return False, f"Valor no numerico: {valor_str}"


def imprimir_stats(validos, rechazados, log):
    total = validos + rechazados
    print(f"  Total revisados : {total}")
    print(f"  Validos         : {validos}")
    print(f"  Rechazados      : {rechazados}")
    log += [f"  Total revisados : {total}",
            f"  Validos         : {validos}",
            f"  Rechazados      : {rechazados}"]


def validar_laboratorio(log):
    entrada  = os.path.join(CARPETA_CLEAN, "laboratorio.csv")
    sal_val  = os.path.join(CARPETA_VALIDADOS,  "laboratorio_valido.csv")
    sal_rech = os.path.join(CARPETA_RECHAZADOS, "laboratorio_rechazado.csv")

    print("\nValidando: LABORATORIO")
    log.append("\n--- LABORATORIO ---")

    if not os.path.exists(entrada):
        msg = f"  ERROR: Archivo no encontrado: {entrada}"
        print(msg); log.append(msg)
        return 0, 0, 0

    validos = []
    rechazados = []

    with open(entrada, encoding="utf-8") as f:
        lector = csv.DictReader(f)
        campos = lector.fieldnames or []
        for fila in lector:
            errores = []
            for campo in ["id_examen", "id_paciente"]:
                ok, msg = campo_requerido(fila.get(campo), campo)
                if not ok:
                    errores.append(msg)
            ok, msg = es_fecha_valida(fila.get("fecha_examen", ""))
            if not ok:
                errores.append(msg)
            ok, msg = es_numero_positivo(fila.get("resultado", ""))
            if not ok:
                errores.append(msg)

            if errores:
                fila["motivo_rechazo"] = " | ".join(errores)
                rechazados.append(fila)
                log.append(f"  Rechazado {fila.get('id_examen','?')}: {fila['motivo_rechazo']}")
            else:
                validos.append(fila)

    with open(sal_val, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(validos)

    if rechazados:
        with open(sal_rech, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(campos) + ["motivo_rechazo"])
            writer.writeheader()
            writer.writerows(rechazados)

    imprimir_stats(len(validos), len(rechazados), log)
    return len(validos) + len(rechazados), len(validos), len(rechazados)


def validar_urgencias(log):
    entrada  = os.path.join(CARPETA_CLEAN, "urgencias.json")
    sal_val  = os.path.join(CARPETA_VALIDADOS,  "urgencias_valido.json")
    sal_rech = os.path.join(CARPETA_RECHAZADOS, "urgencias_rechazado.json")

    print("\nValidando: URGENCIAS")
    log.append("\n--- URGENCIAS ---")

    if not os.path.exists(entrada):
        msg = f"  ERROR: Archivo no encontrado: {entrada}"
        print(msg); log.append(msg)
        return 0, 0, 0

    if os.path.getsize(entrada) == 0:
        msg = "  JSON vacio: sin registros para validar"
        print(msg); log.append(msg)
        return 0, 0, 0

    with open(entrada, encoding="utf-8") as f:
        datos = json.load(f)

    validos = []
    rechazados = []

    for reg in datos:
        errores = []
        for campo in ["id_atencion", "id_paciente"]:
            ok, msg = campo_requerido(reg.get(campo), campo)
            if not ok:
                errores.append(msg)
        ok, msg = es_fecha_valida(reg.get("fecha_ingreso", ""))
        if not ok:
            errores.append(msg)
        estado = str(reg.get("estado", "")).strip().lower()
        if estado not in ESTADOS_URGENCIA_VALIDOS:
            errores.append(f"Estado invalido: '{estado}' (permitidos: {', '.join(sorted(ESTADOS_URGENCIA_VALIDOS))})")

        if errores:
            reg["motivo_rechazo"] = " | ".join(errores)
            rechazados.append(reg)
            log.append(f"  Rechazado {reg.get('id_atencion','?')}: {reg['motivo_rechazo']}")
        else:
            validos.append(reg)

    with open(sal_val,  "w", encoding="utf-8") as f:
        json.dump(validos, f, ensure_ascii=False, indent=2)
    with open(sal_rech, "w", encoding="utf-8") as f:
        json.dump(rechazados, f, ensure_ascii=False, indent=2)

    imprimir_stats(len(validos), len(rechazados), log)
    return len(validos) + len(rechazados), len(validos), len(rechazados)


def validar_farmacia(log):
    entrada  = os.path.join(CARPETA_CLEAN, "farmacia.xml")
    sal_val  = os.path.join(CARPETA_VALIDADOS,  "farmacia_valido.xml")
    sal_rech = os.path.join(CARPETA_RECHAZADOS, "farmacia_rechazado.csv")

    print("\nValidando: FARMACIA")
    log.append("\n--- FARMACIA ---")

    if not os.path.exists(entrada):
        msg = f"  ERROR: Archivo no encontrado: {entrada}"
        print(msg); log.append(msg)
        return 0, 0, 0

    if os.path.getsize(entrada) == 0:
        msg = "  XML vacio: sin registros para validar"
        print(msg); log.append(msg)
        return 0, 0, 0

    try:
        arbol = ET.parse(entrada)
    except ET.ParseError as e:
        msg = f"  ERROR: XML invalido: {e}"
        print(msg); log.append(msg)
        return 0, 0, 0

    raiz = arbol.getroot()
    validos = []
    rechazados = []

    for despacho in raiz:
        errores = []
        id_d = (despacho.findtext("id_despacho") or "").strip()
        id_p = (despacho.findtext("id_paciente") or "").strip()

        for campo, val in [("id_despacho", id_d), ("id_paciente", id_p)]:
            ok, msg = campo_requerido(val, campo)
            if not ok:
                errores.append(msg)
        ok, msg = es_fecha_valida(despacho.findtext("fecha_despacho") or "")
        if not ok:
            errores.append(msg)
        ok, msg = es_numero_positivo(despacho.findtext("cantidad") or "0")
        if not ok:
            errores.append(msg)
        ok, msg = campo_requerido(despacho.findtext("medicamento"), "medicamento")
        if not ok:
            errores.append(msg)

        if errores:
            rechazados.append({
                "id_despacho":    id_d,
                "id_paciente":    id_p,
                "medicamento":    (despacho.findtext("medicamento") or "").strip(),
                "motivo_rechazo": " | ".join(errores),
            })
            log.append(f"  Rechazado despacho {id_d}: {' | '.join(errores)}")
        else:
            validos.append(despacho)

    raiz_val = ET.Element(raiz.tag)
    for d in validos:
        raiz_val.append(d)
    ET.ElementTree(raiz_val).write(sal_val, encoding="unicode", xml_declaration=True)

    if rechazados:
        with open(sal_rech, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rechazados[0].keys()))
            writer.writeheader()
            writer.writerows(rechazados)

    imprimir_stats(len(validos), len(rechazados), log)
    return len(validos) + len(rechazados), len(validos), len(rechazados)


def ejecutar_validacion():
    crear_carpetas()
    log    = []
    inicio = datetime.now()
    sep    = "=" * 55

    log += [sep, "VALIDACION DE DATOS - Clinica MediSalud S.A.", sep,
            f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Fecha de referencia: {HOY}", sep]
    print(f"\n{sep}\nETAPA 3: VALIDACION DE DATOS\nClinica MediSalud S.A.\n{sep}")
    print(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}\n{sep}")

    total_rev = total_val = total_rech = 0
    for fn in [validar_laboratorio, validar_urgencias, validar_farmacia]:
        rev, val, rech = fn(log)
        total_rev  += rev
        total_val  += val
        total_rech += rech

    fin      = datetime.now()
    duracion = (fin - inicio).total_seconds()
    resumen  = [
        f"\n{sep}", "RESUMEN DE VALIDACION", sep,
        f"  Total revisados  : {total_rev}",
        f"  Total validos    : {total_val}",
        f"  Total rechazados : {total_rech}",
        f"  Duracion         : {duracion:.2f} segundos",
        f"  Fin              : {fin.strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
    ]
    for linea in resumen:
        print(linea)
    log.extend(resumen)
    escribir_log(log, f"validacion_{inicio.strftime('%Y%m%d_%H%M%S')}.log")


if __name__ == "__main__":
    ejecutar_validacion()
