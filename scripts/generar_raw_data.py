"""Generador de datos de ejemplo a gran escala para el pipeline ETL.
Genera 1000 registros por area (laboratorio, urgencias, farmacia),
con una proporcion realista de errores intencionales para poder
demostrar limpieza y validacion en volumen.
"""

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

N = 1000  # registros por area

Path("data/raw").mkdir(parents=True, exist_ok=True)

NOMBRES = [
    "juan", "maria", "carlos", "ana", "pedro", "lucia", "jorge", "carmen",
    "roberto", "elena", "sandra", "miguel", "patricia", "andres", "veronica",
    "hugo", "francisco", "valentina", "rodrigo", "beatriz", "camila", "diego",
    "fernanda", "ignacio", "javiera", "matias", "paula", "sebastian", "tamara", "vicente"
]
APELLIDOS = [
    "perez", "lopez", "mendoza", "silva", "gonzalez", "ramirez", "castillo",
    "flores", "vargas", "morales", "nunez", "herrera", "rojas", "diaz",
    "mendez", "reyes", "pinto", "araya", "fuentes", "soto", "torres", "vera",
    "munoz", "contreras", "espinoza", "carrasco", "sepulveda", "riquelme"
]
ESTADOS_URGENCIA = ["alta", "hospitalizado", "observacion", "uci", "fallecido"]
MEDICAMENTOS = [
    "Paracetamol", "Ibuprofeno", "Amoxicilina", "Omeprazol", "Salbutamol",
    "Enalapril", "Losartan", "Metformina", "Aspirina", "Clorfenamina",
    "Furosemida", "Atorvastatina", "Dimenhidrinato", "Clopidogrel",
    "Prednisona", "Diclofenaco", "Insulina", "Ranitidina", "Metoclopramida",
    "Naproxeno", "Cetirizina", "Levotiroxina", "Captopril", "Amlodipino"
]

FECHA_INICIO = datetime(2026, 1, 1)
FECHA_FIN = datetime(2026, 4, 30)
FORMATOS_RUIDO = ["%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"]


def fecha_aleatoria():
    delta = (FECHA_FIN - FECHA_INICIO).days
    return FECHA_INICIO + timedelta(days=random.randint(0, delta))


def fecha_con_formato_variable(fecha, prob_raro=0.25):
    if random.random() < prob_raro:
        return fecha.strftime(random.choice(FORMATOS_RUIDO))
    return fecha.strftime("%Y-%m-%d")


def nombre_ruidoso(valor, prob_mayuscula=0.35):
    if not valor:
        return ""
    if random.random() < prob_mayuscula:
        return valor.upper()
    return valor


def con_probabilidad(p):
    return random.random() < p


# LABORATORIO (CSV)
# -----------------

def generar_laboratorio():
    filas = []
    for i in range(1, N + 1):
        id_examen = f"E{i:04d}"
        id_paciente = f"P{random.randint(1, N // 2):04d}"
        nombre = nombre_ruidoso(random.choice(NOMBRES))
        apellido = nombre_ruidoso(random.choice(APELLIDOS))
        fecha = fecha_con_formato_variable(fecha_aleatoria())
        resultado = round(random.uniform(1.5, 14.0), 1)

        if con_probabilidad(0.02):
            nombre = ""
        if con_probabilidad(0.02):
            apellido = ""
        if con_probabilidad(0.01):
            fecha = fecha_con_formato_variable(fecha_aleatoria(), prob_raro=1.0)
        if con_probabilidad(0.01):
            resultado = ""
        elif con_probabilidad(0.02):
            resultado = round(random.uniform(-2.0, 0.0), 1)
        if con_probabilidad(0.01):
            id_examen = ""
        if con_probabilidad(0.01):
            id_paciente = ""

        filas.append({
            "id_examen": id_examen,
            "id_paciente": id_paciente,
            "nombre": nombre,
            "apellido": apellido,
            "fecha_examen": fecha,
            "resultado": resultado,
        })

    n_dup = int(N * 0.02)
    for _ in range(n_dup):
        filas.append(dict(random.choice(filas)))

    random.shuffle(filas)
    with open("data/raw/laboratorio.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id_examen", "id_paciente", "nombre", "apellido", "fecha_examen", "resultado"],
        )
        writer.writeheader()
        writer.writerows(filas)

    print(f"laboratorio.csv generado: {len(filas)} filas ({n_dup} duplicados inyectados)")


# URGENCIAS (JSON)
# ----------------

def generar_urgencias():
    registros = []
    for i in range(1, N + 1):
        id_atencion = f"A{i:04d}"
        id_paciente = f"P{random.randint(1, N // 2):04d}"
        fecha = fecha_aleatoria()
        estado = random.choice(ESTADOS_URGENCIA)
        medico = random.choice(["Dr. Perez", "Dra. Ramirez", "Dra. Soto", "Dr. Morales", ""])
        nombre = nombre_ruidoso(random.choice(NOMBRES))
        apellido = nombre_ruidoso(random.choice(APELLIDOS))
        cama_asignada = random.choice([None, random.randint(1, 120)])

        if con_probabilidad(0.05):
            estado = "desconocido"
        if con_probabilidad(0.04):
            fecha = fecha_con_formato_variable(fecha, prob_raro=1.0)
        if con_probabilidad(0.03):
            cama_asignada = random.randint(-5, -1)
        if con_probabilidad(0.05):
            id_atencion = ""
        if con_probabilidad(0.05):
            id_paciente = ""
        if con_probabilidad(0.08):
            medico = ""

        registros.append({
            "id_atencion": id_atencion,
            "id_paciente": id_paciente,
            "fecha_ingreso": fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha,
            "estado": estado,
            "nombre": nombre,
            "apellido": apellido,
            "cama_asignada": cama_asignada,
            "medico": medico,
        })

    n_dup = int(N * 0.02)
    for _ in range(n_dup):
        registros.append(dict(random.choice(registros)))

    random.shuffle(registros)
    with open("data/raw/urgencias.json", "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    print(f"urgencias.json generado: {len(registros)} filas ({n_dup} duplicados inyectados)")


# FARMACIA (XML)
# --------------

def generar_farmacia():
    nodos = []
    for i in range(1, N + 1):
        id_despacho = f"D{i:04d}"
        id_paciente = f"P{random.randint(1, N // 2):04d}"
        fecha = fecha_aleatoria()
        cantidad = random.randint(1, 5)
        medicamento = random.choice(MEDICAMENTOS)
        farmaceutico = random.choice(["Carlos", "Maria", "", "Ana", "Luis"])
        nombre = nombre_ruidoso(random.choice(NOMBRES)) if con_probabilidad(0.6) else ""
        apellido = nombre_ruidoso(random.choice(APELLIDOS)) if con_probabilidad(0.6) else ""

        if con_probabilidad(0.03):
            cantidad = random.randint(-3, 0)
        if con_probabilidad(0.04):
            fecha = fecha_con_formato_variable(fecha, prob_raro=1.0)
        if con_probabilidad(0.04):
            medicamento = ""
        if con_probabilidad(0.05):
            id_despacho = ""
        if con_probabilidad(0.05):
            id_paciente = ""
        if con_probabilidad(0.08):
            farmaceutico = ""

        nodo = {
            "id_despacho": id_despacho,
            "id_paciente": id_paciente,
            "fecha_despacho": fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha,
            "cantidad": str(cantidad),
            "medicamento": medicamento,
            "farmaceutico": farmaceutico,
            "nombre": nombre,
            "apellido": apellido,
        }
        nodos.append(nodo)

    n_dup = int(N * 0.02)
    for _ in range(n_dup):
        nodos.append(dict(random.choice(nodos)))

    random.shuffle(nodos)
    with open("data/raw/farmacia.xml", "w", encoding="utf-8") as f:
        f.write("<farmacia>\n")
        for nodo in nodos:
            f.write("  <despacho>\n")
            for campo in [
                "id_despacho",
                "id_paciente",
                "fecha_despacho",
                "cantidad",
                "medicamento",
                "farmaceutico",
                "nombre",
                "apellido",
            ]:
                f.write(f"    <{campo}>{nodo[campo]}</{campo}>\n")
            f.write("  </despacho>\n")
        f.write("</farmacia>\n")

    print(f"farmacia.xml generado: {len(nodos)} filas ({n_dup} duplicados inyectados)")


if __name__ == "__main__":
    generar_laboratorio()
    generar_urgencias()
    generar_farmacia()
    print("Generacion de datos raw completada.")
