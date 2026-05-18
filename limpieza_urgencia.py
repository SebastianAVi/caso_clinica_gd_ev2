"""
================================================================
  LIMPIEZA_URGENCIA.PY - Clínica MediSalud S.A.
================================================================
Limpieza real del archivo urgencias.json:
  - Capitaliza nombres y apellidos
  - Estandariza fechas a formato YYYY-MM-DD
  - Corrige camas con valor negativo → None
  - Rellena médico vacío → "Sin asignar"
  - Elimina registros duplicados
================================================================
"""

import json
import os
from datetime import datetime

from config import FORMATOS_FECHA


def normalizar_fecha(fecha_str: str) -> str:
    """Convierte una fecha al formato YYYY-MM-DD o retorna cadena vacía."""
    fecha_str = (fecha_str or "").strip()
    for fmt in FORMATOS_FECHA:
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def capitalizar(texto: str) -> str:
    """Capitaliza un texto."""
    return texto.strip().capitalize() if texto and texto.strip() else ""


def limpiar_urgencias(ruta_entrada: str, ruta_salida: str) -> dict:
    """
    Limpia el archivo urgencias.json y guarda el resultado en ruta_salida.
    Retorna un dict con estadísticas del proceso.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe el archivo: {ruta_entrada}")

    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)

    # Archivo vacío → crear destino vacío
    if os.path.getsize(ruta_entrada) == 0:
        open(ruta_salida, "w", encoding="utf-8").close()
        return {"originales": 0, "limpios": 0, "duplicados": 0, "fechas_corregidas": 0, "correcciones": []}

    with open(ruta_entrada, encoding="utf-8") as f:
        datos = json.load(f)

    vistos            = set()
    limpios           = []
    duplicados        = 0
    fechas_corregidas = 0
    correcciones      = []

    for reg in datos:
        # --- Capitalizar nombres y apellidos ---
        for campo in ["nombre", "apellido"]:
            if campo in reg:
                reg[campo] = capitalizar(str(reg[campo]))

        # --- Normalizar fecha ---
        original = str(reg.get("fecha_ingreso", ""))
        nueva    = normalizar_fecha(original)
        reg["fecha_ingreso"] = nueva
        if nueva and nueva != original.strip():
            fechas_corregidas += 1

        # --- Corregir cama negativa ---
        cama = reg.get("cama_asignada")
        if isinstance(cama, (int, float)) and cama < 0:
            correcciones.append(f"Cama negativa {cama} → None en atención {reg.get('id_atencion','?')}")
            reg["cama_asignada"] = None

        # --- Rellenar médico vacío ---
        if not str(reg.get("medico", "")).strip():
            correcciones.append(f"Médico vacío → 'Sin asignar' en atención {reg.get('id_atencion','?')}")
            reg["medico"] = "Sin asignar"

        # --- Eliminar duplicados ---
        clave = (reg.get("id_atencion", ""), reg.get("id_paciente", ""))
        if clave in vistos:
            duplicados += 1
            continue
        vistos.add(clave)
        limpios.append(reg)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(limpios, f, ensure_ascii=False, indent=2)

    return {
        "originales"       : len(datos),
        "limpios"          : len(limpios),
        "duplicados"       : duplicados,
        "fechas_corregidas": fechas_corregidas,
        "correcciones"     : correcciones,
    }
