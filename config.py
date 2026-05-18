"""
================================================================
  CONFIG.PY - Configuración centralizada del proyecto
  Clínica MediSalud S.A.
================================================================
Todas las constantes compartidas entre etapas van aquí.
"""

# -------------------------------------------------------
# RUTAS DEL PROYECTO
# -------------------------------------------------------
CARPETA_RAW        = "data/raw"
CARPETA_RAW_ORIGEN = "data/raw_origen"
CARPETA_CLEAN      = "data/clean"
CARPETA_VALIDADOS  = "data/validados"
CARPETA_RECHAZADOS = "data/rechazados"
CARPETA_LOGS       = "logs"
DB_PATH            = "data/clinica.db"

# -------------------------------------------------------
# ARCHIVOS ESPERADOS POR ÁREA
# -------------------------------------------------------
ARCHIVOS_ESPERADOS = {
    "laboratorio": "laboratorio.csv",
    "urgencias":   "urgencias.json",
    "farmacia":    "farmacia.xml",
}

# -------------------------------------------------------
# REGLAS DE NEGOCIO
# -------------------------------------------------------
# Estados válidos para urgencias (usados en validación y carga)
ESTADOS_URGENCIA_VALIDOS = {
    "alta",
    "hospitalizado",
    "uci",
    "observacion",
    "fallecido",
}

# Formatos de fecha aceptados en limpieza
FORMATOS_FECHA = [
    "%d-%m-%Y",   # 12-03-2024
    "%Y/%m/%d",   # 2024/03/15
    "%Y-%m-%d",   # 2024-03-15
    "%d/%m/%Y",   # 12/03/2024
]
