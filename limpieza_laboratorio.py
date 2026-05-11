import csv
import os


def limpiar_laboratorio(ruta_entrada: str, ruta_salida: str) -> None:
    """Limpieza simple para laboratorio.csv.

    - Normaliza espacios en cada celda (strip + colapsar espacios)
    - Mantiene encabezado y el resto como CSV.

    Si el archivo está vacío, crea el destino vacío.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe el archivo de entrada: {ruta_entrada}")

    if os.path.getsize(ruta_entrada) == 0:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        open(ruta_salida, "w", encoding="utf-8").close()
        return

    def normalizar_cell(v):

        if v is None:
            return ""
        return " ".join(str(v).split())

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    with open(ruta_entrada, encoding="utf-8") as f_in:
        reader = csv.reader(f_in)
        rows = list(reader)

    if not rows:
        # Si viene vacío, igual creamos el destino
        open(ruta_salida, "w", encoding="utf-8").close()
        return

    with open(ruta_salida, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        for row in rows:
            writer.writerow([normalizar_cell(c) for c in row])

