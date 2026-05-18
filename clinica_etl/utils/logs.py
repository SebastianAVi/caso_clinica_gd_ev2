"""Utilidades para manejo de logs y carpetas del proyecto"""

import os
from pathlib import Path


def crear_carpetas(rutas: dict = None) -> None:
    """
    Crea las carpetas necesarias del proyecto.
    
    Args:
        rutas: diccionario con nombres de carpetas como claves.
               Si es None, crea las carpetas estándar.
    """
    if rutas is None:
        rutas = {
            "data": "data",
            "data_raw": "data/raw",
            "data_clean": "data/clean",
            "data_validados": "data/validados",
            "logs": "logs",
        }
    
    for ruta in rutas.values():
        Path(ruta).mkdir(parents=True, exist_ok=True)


def escribir_log(entries: list, nombre_log: str, carpeta_logs: str = "logs") -> str:
    """
    Escribe un log en archivo.
    
    Args:
        entries: lista de strings a escribir
        nombre_log: nombre del archivo de log
        carpeta_logs: carpeta donde guardar el log
        
    Returns:
        Ruta completa del archivo de log creado
    """
    Path(carpeta_logs).mkdir(parents=True, exist_ok=True)
    ruta_log = os.path.join(carpeta_logs, nombre_log)
    with open(ruta_log, "w", encoding="utf-8") as f:
        f.write("\n".join(entries) + "\n")
    return ruta_log
