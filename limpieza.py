import glob
import os
from datetime import datetime

import limpieza_farmacia
import limpieza_laboratorio
import limpieza_urgencia


def limpiar_logs_ingesta(logs_dir: str = "logs") -> int:
    """Elimina los logs generados por la etapa de ingesta.

    Borra archivos que cumplan: logs/ingesta_*.log
    """
    patron = os.path.join(logs_dir, "ingesta_*.log")
    rutas = sorted(glob.glob(patron))
    for ruta in rutas:
        try:
            os.remove(ruta)
        except FileNotFoundError:
            pass
    return len(rutas)


def ejecutar_limpieza() -> None:
    inicio = datetime.now()

    # 1) Limpiar logs de ingesta
    logs_borrados = limpiar_logs_ingesta("logs")

    # 2) Normalización/limpieza por dominio -> data/clean
    os.makedirs("data/clean", exist_ok=True)

    # Si el input viene vacío, el/los limpiadores crearán igualmente el output.
    limpieza_farmacia.limpiar_farmacia(
        ruta_entrada="data/raw/farmacia.xml",
        ruta_salida="data/clean/farmacia.xml",
    )

    limpieza_laboratorio.limpiar_laboratorio(
        ruta_entrada="data/raw/laboratorio.csv",
        ruta_salida="data/clean/laboratorio.csv",
    )

    limpieza_urgencia.limpiar_urgencias(
        ruta_entrada="data/raw/urgencias.json",
        ruta_salida="data/clean/urgencias.json",
    )

    fin = datetime.now()
    dur = (fin - inicio).total_seconds()

    print("=" * 60)
    print("LIMPIEZA FINALIZADA")
    print("Inicio:", inicio.strftime("%Y-%m-%d %H:%M:%S"))
    print("Fin:", fin.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Logs de ingesta borrados: {logs_borrados}")
    print(f"Duración: {dur:.2f} s")
    print("=" * 60)


if __name__ == "__main__":
    ejecutar_limpieza()

