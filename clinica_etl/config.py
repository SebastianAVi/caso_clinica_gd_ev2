"""
================================================================
  CONFIGURACIÓN CENTRALIZADA - Clínica MediSalud S.A.
================================================================
Constantes compartidas entre todos los módulos del pipeline ETL.
"""

import os
from pathlib import Path

# -------------------------------------------------------
# RUTAS DEL PROYECTO (relativas a la raíz)
# -------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
VALIDADOS_DIR = DATA_DIR / "validados"
RECHAZADOS_DIR = DATA_DIR / "rechazados"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "clinica.db"

# Convertir a strings para compatibilidad
CARPETA_RAW = str(RAW_DATA_DIR)
CARPETA_CLEAN = str(CLEAN_DATA_DIR)
CARPETA_VALIDADOS = str(VALIDADOS_DIR)
CARPETA_RECHAZADOS = str(RECHAZADOS_DIR)
CARPETA_LOGS = str(LOGS_DIR)
DB_PATH_STR = str(DB_PATH)

# -------------------------------------------------------
# ARCHIVOS ESPERADOS POR ÁREA
# -------------------------------------------------------
ARCHIVOS_ESPERADOS = {
    "laboratorio": "laboratorio.csv",
    "urgencias": "urgencias.json",
    "farmacia": "farmacia.xml",
}

# -------------------------------------------------------
# REGLAS DE NEGOCIO - VALIDACIÓN
# -------------------------------------------------------
ESTADOS_URGENCIA_VALIDOS = {
    "alta",
    "hospitalizado",
    "uci",
    "observacion",
    "fallecido",
}

# -------------------------------------------------------
# CONFIGURACIÓN DE BASE DE DATOS
# -------------------------------------------------------
DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite").lower()
DB_NAME = os.environ.get("DB_NAME", "clinica")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# -------------------------------------------------------
# FUNCIONES HELPER
# -------------------------------------------------------
def crear_carpetas_proyecto() -> None:
    """Crea todas las carpetas necesarias del proyecto."""
    for carpeta in [RAW_DATA_DIR, CLEAN_DATA_DIR, VALIDADOS_DIR, 
                    RECHAZADOS_DIR, LOGS_DIR]:
        carpeta.mkdir(parents=True, exist_ok=True)
