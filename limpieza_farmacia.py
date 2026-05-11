import os
import xml.etree.ElementTree as ET


def limpiar_farmacia(ruta_entrada: str, ruta_salida: str) -> None:
    """Limpieza simple para farmacia.xml.

    - Normaliza espacios en textos (strip).
    - Asegura codificación UTF-8 al guardar.

    Si el archivo está vacío, crea el destino vacío.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe el archivo de entrada: {ruta_entrada}")

    if os.path.getsize(ruta_entrada) == 0:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        open(ruta_salida, "w", encoding="utf-8").close()
        return

    tree = ET.parse(ruta_entrada)
    root = tree.getroot()


    def normalizar_texto(x):
        if x is None:
            return None
        # Normaliza espacios múltiples y bordes
        return " ".join(x.split())

    for elem in root.iter():
        if elem.text is not None:
            elem.text = normalizar_texto(elem.text)
        if elem.tail is not None:
            elem.tail = normalizar_texto(elem.tail)

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    tree.write(ruta_salida, encoding="utf-8", xml_declaration=True)

