import csv
import os
from datetime import datetime

from config import FORMATOS_FECHA


def normalizar_fecha(fecha_str):
    fecha_str = (fecha_str or "").strip()
    for fmt in FORMATOS_FECHA:
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def capitalizar(texto):
    return texto.strip().capitalize() if texto and texto.strip() else ""


def limpiar_laboratorio(ruta_entrada, ruta_salida):
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe: {ruta_entrada}")

    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)

    if os.path.getsize(ruta_entrada) == 0:
        open(ruta_salida, "w", encoding="utf-8").close()
        return {"originales": 0, "limpios": 0, "duplicados": 0, "fechas_corregidas": 0}

    with open(ruta_entrada, encoding="utf-8") as f:
        reader    = csv.DictReader(f)
        campos    = reader.fieldnames or []
        registros = list(reader)

    vistos = set()
    limpios = []
    duplicados = 0
    fechas_corregidas = 0

    for fila in registros:
        for campo in ["nombre", "apellido"]:
            if campo in fila:
                fila[campo] = capitalizar(fila[campo])

        if "fecha_examen" in fila:
            original = fila["fecha_examen"]
            fila["fecha_examen"] = normalizar_fecha(original)
            if fila["fecha_examen"] and fila["fecha_examen"] != original.strip():
                fechas_corregidas += 1

        for campo in ["id_examen", "id_paciente"]:
            if campo in fila and not (fila[campo] or "").strip():
                fila[campo] = "SIN_DATO"

        clave = (fila.get("id_examen", ""), fila.get("id_paciente", ""))
        if clave in vistos:
            duplicados += 1
            continue
        vistos.add(clave)
        limpios.append(fila)

    with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(limpios)

    return {
        "originales": len(registros),
        "limpios": len(limpios),
        "duplicados": duplicados,
        "fechas_corregidas": fechas_corregidas,
    }
