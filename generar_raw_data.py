import json
import random
from pathlib import Path
from datetime import datetime, timedelta

Path("data/raw").mkdir(parents=True, exist_ok=True)

# Génera laboratorio.csv con 1000 registros con fallas
def generar_laboratorio():
    lineas = ["id_examen,id_paciente,nombre,apellido,fecha_examen,resultado"]
    for i in range(1, 1001):
        id_examen = f"E{i:03d}"
        id_paciente = f"P{random.randint(1, 500):03d}"
        nombre = random.choice(["juan", "MARIA", "carlos", "ANA", "pedro", "", None, "invalido"])
        apellido = random.choice(["perez", "LOPEZ", "mendoza", "torres", "", None, "RAMIREZ"])
        
        # Fechas con errores
        fecha_type = random.randint(0, 4)
        if fecha_type == 0:
            fecha = (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 120))).strftime('%Y-%m-%d')
        elif fecha_type == 1:
            fecha = '2026-15-35'
        elif fecha_type == 2:
            fecha = '2026/01/03'
        elif fecha_type == 3:
            fecha = ''
        else:
            fecha = 'invalid'
        
        # Resultados con errores
        res_type = random.randint(0, 5)
        if res_type == 0:
            resultado = round(random.uniform(2.0, 12.0), 1)
        elif res_type == 1:
            resultado = 'N/A'
        elif res_type == 2:
            resultado = -15.5
        elif res_type == 3:
            resultado = ''
        elif res_type == 4:
            resultado = 999.9
        else:
            resultado = round(random.uniform(2.0, 12.0), 1)
        
        lineas.append(f"{id_examen},{id_paciente},{nombre or ''},{apellido or ''},{fecha},{resultado}")
    
    return "\n".join(lineas)

laboratorio_csv = generar_laboratorio()


# Genera urgencias.json con 1000 registros con fallas
def generar_urgencias():
    registros = []
    estados = ['alta', 'hospitalizado', 'ALTA', 'observacion ', ' uci', None, '', 'desconocido']
    doctores = ['Dr. Torres', 'Dra. Vega', 'Dr. Rojas', 'Dra. Munoz', '', None, 'Dr. Invalido']
    
    for i in range(1, 1001):
        registro = {
            "id_atencion": f"A{i:03d}",
            "id_paciente": f"P{random.randint(1, 500):03d}",
            "nombre": random.choice(["juan", "MARIA", "carlos", "ANA", "", None]),
            "apellido": random.choice(["perez", "LOPEZ", "torres", "", None]),
            "fecha_ingreso": (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 120))).strftime('%Y-%m-%d') if random.random() > 0.15 else '',
            "estado": random.choice(estados),
            "cama_asignada": random.randint(-5, 20) if random.random() > 0.1 else '',
            "medico": random.choice(doctores)
        }
        
        # Algunos registros sin campos
        if random.random() > 0.85:
            if 'estado' in registro:
                del registro['estado']
        
        registros.append(registro)
    
    return registros

urgencias = generar_urgencias()


# Genera farmacia.xml con 1000 registros con fallas
def generar_farmacia():
    medicamentos = ["Paracetamol", "Ibuprofeno", "Amoxicilina", None, "", "###", "Omeprazol", "Aspirina", "Insulina"]
    farmaceuticos = ["Carmen Soto", "Luis Vera", "", None, "Dr. Lopez"]
    
    xml_lines = ["<farmacia>"]
    
    for i in range(1, 1001):
        id_despacho = f"D{i:03d}"
        id_paciente = f"P{random.randint(1, 500):03d}"
        nombre = random.choice(["juan", "MARIA", "carlos", "", None])
        apellido = random.choice(["perez", "LOPEZ", "torres", "", None])
        
        # Fechas con errores
        fecha_type = random.randint(0, 4)
        if fecha_type == 0:
            fecha = (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 120))).strftime('%Y-%m-%d')
        elif fecha_type == 1:
            fecha = '2026-15-35'
        elif fecha_type == 2:
            fecha = '2026/01/03'
        elif fecha_type == 3:
            fecha = ''
        else:
            fecha = 'invalid'
        
        # Cantidades con errores
        cant_type = random.randint(0, 5)
        if cant_type == 0:
            cantidad = 0
        elif cant_type == 1:
            cantidad = -5
        elif cant_type == 2:
            cantidad = 99999
        elif cant_type == 3:
            cantidad = ''
        else:
            cantidad = random.randint(1, 5)
        
        medicamento = random.choice(medicamentos) or ""
        farmaceutico = random.choice(farmaceuticos) or ""
        
        xml_lines.append(f"  <despacho><id_despacho>{id_despacho}</id_despacho><id_paciente>{id_paciente}</id_paciente><nombre>{nombre or ''}</nombre><apellido>{apellido or ''}</apellido><fecha_despacho>{fecha}</fecha_despacho><cantidad>{cantidad}</cantidad><medicamento>{medicamento}</medicamento><farmaceutico>{farmaceutico}</farmaceutico></despacho>")
    
    xml_lines.append("</farmacia>")
    return "\n".join(xml_lines)

farmacia_xml = generar_farmacia()

Path("data/raw/laboratorio.csv").write_text(laboratorio_csv, encoding="utf-8")
Path("data/raw/urgencias.json").write_text(json.dumps(urgencias, indent=2, ensure_ascii=False), encoding="utf-8")
Path("data/raw/farmacia.xml").write_text(farmacia_xml, encoding="utf-8")

print("Datos generados en data/raw/")
print("  laboratorio.csv : 1000 registros (fechas distintos formatos, resultados invalidos/vacios)")
print("  urgencias.json  : 1000 registros (camas negativas, medicos vacios, estados inconsistentes, campos faltantes)")
print("  farmacia.xml    : 1000 registros (cantidades invalidas/vacias, farmaceuticos vacios, fechas distintos formatos)")
