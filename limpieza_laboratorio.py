"""
================================================================
  LIMPIEZA_LABORATORIO.PY - Clínica MediSalud S.A.
================================================================
Limpieza real del archivo laboratorio.csv:
  - Capitaliza nombres y apellidos
  - Estandariza fechas a formato YYYY-MM-DD
  - Elimina registros duplicados
  - Marca campos vacíos obligatorios
================================================================
"""

import csv
import os
from datetime import datetime

from config import FORMATOS_FECHA


def normalizar_fecha(fecha_str: str) -> str:
    """
    Convierte una fecha al formato estándar YYYY-MM-DD.
    Retorna la fecha convertida o cadena vacía si no se pudo.
    """
    fecha_str = (fecha_str or "").strip()
    for fmt in FORMATOS_FECHA:
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def capitalizar(texto: str) -> str:
    """Capitaliza un texto (primera letra mayúscula, resto minúscula)."""
    return texto.strip().capitalize() if texto and texto.strip() else ""


def limpiar_laboratorio(ruta_entrada: str, ruta_salida: str) -> dict:
    """
    Limpia el archivo laboratorio.csv y guarda el resultado en ruta_salida.
    Retorna un dict con estadísticas del proceso.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe el archivo: {ruta_entrada}")

    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)

    # Archivo vacío → crear destino vacío
    if os.path.getsize(ruta_entrada) == 0:
        open(ruta_salida, "w", encoding="utf-8").close()
        return {"originales": 0, "limpios": 0, "duplicados": 0, "fechas_corregidas": 0}

    with open(ruta_entrada, encoding="utf-8") as f:
        reader     = csv.DictReader(f)
        campos     = reader.fieldnames or []
        registros  = list(reader)

    vistos            = set()
    limpios           = []
    duplicados        = 0
    fechas_corregidas = 0

    for fila in registros:
        # --- Capitalizar nombres y apellidos ---
        for campo in ["nombre", "apellido"]:
            if campo in fila:
                fila[campo] = capitalizar(fila[campo])

        # --- Normalizar fecha ---
        if "fecha_examen" in fila:
            original     = fila["fecha_examen"]
            fila["fecha_examen"] = normalizar_fecha(original)
            if fila["fecha_examen"] and fila["fecha_examen"] != original.strip():
                fechas_corregidas += 1

        # --- Marcar campos obligatorios vacíos ---
        for campo in ["id_examen", "id_paciente"]:
            if campo in fila and not (fila[campo] or "").strip():
                fila[campo] = "SIN_DATO"

        # --- Eliminar duplicados ---
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
        "originales"       : len(registros),
        "limpios"          : len(limpios),
        "duplicados"       : duplicados,
        "fechas_corregidas": fechas_corregidas,
    }
