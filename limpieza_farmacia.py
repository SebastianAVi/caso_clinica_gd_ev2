"""
================================================================
  LIMPIEZA_FARMACIA.PY - Clínica MediSalud S.A.
================================================================
Limpieza real del archivo farmacia.xml:
  - Capitaliza nombres y apellidos
  - Estandariza fechas a formato YYYY-MM-DD
  - Rellena cantidad vacía → "0"
  - Rellena farmacéutico vacío → "Sin asignar"
  - Elimina registros duplicados
================================================================
"""

import os
import xml.etree.ElementTree as ET
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


def get_text(elemento, tag: str) -> str:
    """Obtiene el texto de un subelemento XML o retorna cadena vacía."""
    nodo = elemento.find(tag)
    return (nodo.text or "").strip() if nodo is not None else ""


def set_text(elemento, tag: str, valor: str) -> None:
    """Asigna texto a un subelemento XML si existe."""
    nodo = elemento.find(tag)
    if nodo is not None:
        nodo.text = valor


def limpiar_farmacia(ruta_entrada: str, ruta_salida: str) -> dict:
    """
    Limpia el archivo farmacia.xml y guarda el resultado en ruta_salida.
    Retorna un dict con estadísticas del proceso.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe el archivo: {ruta_entrada}")

    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)

    # Archivo vacío → crear destino vacío
    if os.path.getsize(ruta_entrada) == 0:
        open(ruta_salida, "w", encoding="utf-8").close()
        return {"originales": 0, "limpios": 0, "duplicados": 0, "fechas_corregidas": 0, "correcciones": []}

    arbol = ET.parse(ruta_entrada)
    raiz  = arbol.getroot()
    todos = list(raiz)

    vistos            = set()
    a_eliminar        = []
    duplicados        = 0
    fechas_corregidas = 0
    correcciones      = []

    for despacho in todos:
        id_d = get_text(despacho, "id_despacho")
        id_p = get_text(despacho, "id_paciente")

        # --- Capitalizar nombres y apellidos ---
        for campo in ["nombre", "apellido"]:
            nodo = despacho.find(campo)
            if nodo is not None:
                nodo.text = capitalizar(nodo.text or "")

        # --- Normalizar fecha ---
        original = get_text(despacho, "fecha_despacho")
        nueva    = normalizar_fecha(original)
        set_text(despacho, "fecha_despacho", nueva)
        if nueva and nueva != original:
            fechas_corregidas += 1

        # --- Rellenar cantidad vacía ---
        cantidad = get_text(despacho, "cantidad")
        if not cantidad:
            correcciones.append(f"Cantidad vacía → '0' en despacho {id_d}")
            set_text(despacho, "cantidad", "0")

        # --- Rellenar farmacéutico vacío ---
        farmaceutico = get_text(despacho, "farmaceutico")
        if not farmaceutico:
            correcciones.append(f"Farmacéutico vacío → 'Sin asignar' en despacho {id_d}")
            set_text(despacho, "farmaceutico", "Sin asignar")

        # --- Eliminar duplicados ---
        clave = (id_d, id_p)
        if clave in vistos:
            duplicados += 1
            a_eliminar.append(despacho)
            continue
        vistos.add(clave)

    for dup in a_eliminar:
        raiz.remove(dup)

    arbol.write(ruta_salida, encoding="unicode", xml_declaration=True)

    return {
        "originales"       : len(todos),
        "limpios"          : len(todos) - duplicados,
        "duplicados"       : duplicados,
        "fechas_corregidas": fechas_corregidas,
        "correcciones"     : correcciones,
    }
