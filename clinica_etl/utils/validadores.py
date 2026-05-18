"""Funciones de validación comunes reutilizables en todas las etapas"""

from datetime import datetime


def validar_fecha(fecha_str: str) -> bool:
    """Verifica que la fecha tenga formato YYYY-MM-DD."""
    if not fecha_str or str(fecha_str).strip() == "":
        return False
    try:
        datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validar_numero_positivo(valor) -> bool:
    """Verifica que el valor sea numérico y mayor que 0."""
    try:
        num = float(str(valor).strip())
        return num > 0
    except (ValueError, TypeError):
        return False


def validar_texto(valor) -> bool:
    """Verifica que un texto no esté vacío."""
    return bool(valor and str(valor).strip())


def validar_campo_requerido(valor: str, nombre_campo: str) -> tuple:
    """
    Verifica que un campo obligatorio no esté vacío.
    Retorna (es_válido, mensaje_error)
    """
    if not validar_texto(valor):
        return False, f"Campo obligatorio vacío: {nombre_campo}"
    return True, ""
