import json
import os


def limpiar_urgencias(ruta_entrada: str, ruta_salida: str) -> None:
    """Limpieza simple para urgencias.json.

    - Si la estructura es lista: normaliza textos en cada dict (strip + colapsar espacios)
    - Si la estructura es dict: aplica lo mismo a cada lista/elemento dentro de sus valores.

    Si el archivo está vacío, crea el destino vacío.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No existe el archivo de entrada: {ruta_entrada}")

    if os.path.getsize(ruta_entrada) == 0:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        open(ruta_salida, "w", encoding="utf-8").close()
        return

    with open(ruta_entrada, encoding="utf-8") as f:
        datos = json.load(f)


    def normalizar_texto(s):
        return " ".join(str(s).split())

    def normalizar_obj(obj):
        if isinstance(obj, dict):
            nuevo = {}
            for k, v in obj.items():
                if isinstance(v, str):
                    nuevo[k] = normalizar_texto(v)
                elif isinstance(v, (dict, list)):
                    nuevo[k] = normalizar_obj(v)
                else:
                    nuevo[k] = v
            return nuevo
        if isinstance(obj, list):
            return [normalizar_obj(x) for x in obj]
        if isinstance(obj, str):
            return normalizar_texto(obj)
        return obj

    datos_limpios = normalizar_obj(datos)

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos_limpios, f, ensure_ascii=False, indent=2)

