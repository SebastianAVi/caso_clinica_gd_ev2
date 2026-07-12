import os

CARPETA_RAW        = "data/raw"
CARPETA_RAW_ORIGEN = "data/raw_origen"
CARPETA_CLEAN      = "data/clean"
CARPETA_VALIDADOS  = "data/validados"
CARPETA_RECHAZADOS = "data/rechazados"
CARPETA_LOGS       = "logs"
DB_PATH            = os.environ.get("DB_PATH", "data/clinica.db")
DB_ENGINE          = os.environ.get("DB_ENGINE", "sqlite").lower()

ARCHIVOS_ESPERADOS = {
    "laboratorio": "laboratorio.csv",
    "urgencias":   "urgencias.json",
    "farmacia":    "farmacia.xml",
}

ESTADOS_URGENCIA_VALIDOS = {"alta", "hospitalizado", "uci", "observacion", "fallecido"}

FORMATOS_FECHA = ["%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y"]
