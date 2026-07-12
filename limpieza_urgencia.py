import json
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


def limpiar_urgencias(ruta_entrada, ruta_salida):
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe: {ruta_entrada}")

    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)

    if os.path.getsize(ruta_entrada) == 0:
        open(ruta_salida, "w", encoding="utf-8").close()
        return {"originales": 0, "limpios": 0, "duplicados": 0, "fechas_corregidas": 0, "correcciones": []}

    with open(ruta_entrada, encoding="utf-8") as f:
        datos = json.load(f)

    vistos = set()
    limpios = []
    duplicados = 0
    fechas_corregidas = 0
    correcciones = []

    for reg in datos:
        for campo in ["nombre", "apellido"]:
            if campo in reg:
                reg[campo] = capitalizar(str(reg[campo]))

        original = str(reg.get("fecha_ingreso", ""))
        nueva = normalizar_fecha(original)
        reg["fecha_ingreso"] = nueva
        if nueva and nueva != original.strip():
            fechas_corregidas += 1

        cama = reg.get("cama_asignada")
        if isinstance(cama, (int, float)) and cama < 0:
            correcciones.append(f"Cama negativa {cama} corregida a None en atencion {reg.get('id_atencion', '?')}")
            reg["cama_asignada"] = None

        if not str(reg.get("medico", "")).strip():
            correcciones.append(f"Medico vacio asignado como Sin asignar en atencion {reg.get('id_atencion', '?')}")
            reg["medico"] = "Sin asignar"

        clave = (reg.get("id_atencion", ""), reg.get("id_paciente", ""))
        if clave in vistos:
            duplicados += 1
            continue
        vistos.add(clave)
        limpios.append(reg)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(limpios, f, ensure_ascii=False, indent=2)

    return {
        "originales": len(datos),
        "limpios": len(limpios),
        "duplicados": duplicados,
        "fechas_corregidas": fechas_corregidas,
        "correcciones": correcciones,
    }
