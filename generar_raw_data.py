import json
from pathlib import Path

Path("data/raw").mkdir(parents=True, exist_ok=True)

laboratorio_csv = """id_examen,id_paciente,nombre,apellido,fecha_examen,resultado
E001,P001,juan,perez,2026-01-02,5.4
E002,P002,MARIA,LOPEZ,2026/01/04,7.1
E003,P003,carlos,mendoza,03-01-2026,11.2
E004,P004,ANA,SILVA,2026-01-08,3.5
E005,P005,pedro,gonzalez,2026-01-10,9.8
E006,P006,lucia,RAMIREZ,2026-01-12,2.4
E007,P007,jorge,castillo,2026-01-14,6.0
E008,P008,carmen,flores,2026-01-16,4.7
E009,P009,roberto,vargas,2026-01-18,8.9
E010,P010,elena,morales,2026-01-20,12.5
E001,P001,juan,perez,2026-01-02,5.4
E011,P011,,torres,2026-01-22,5.1
E012,P012,sandra,nunez,2026-01-24,7.3
E013,P013,miguel,herrera,2026-01-26,10.0
E014,P014,patricia,rojas,2026-01-28,3.9
E015,P015,andres,diaz,2026-01-30,6.2
E016,P016,VERÓNICA,MENDEZ,01/02/2026,4.4
E017,P017,hugo,reyes,2026-02-03,9.0
E018,P018,beatriz,soto,2026-02-05,5.7
E019,P019,francisco,pinto,2026-02-07,8.1
E020,P020,valentina,araya,2026-02-09,11.6
"""

urgencias = [
    {"id_atencion": "A001", "id_paciente": "P001", "nombre": "juan",      "apellido": "perez",    "fecha_ingreso": "2026-01-03",  "estado": "alta",          "cama_asignada": 5,  "medico": "Dr. Torres"},
    {"id_atencion": "A002", "id_paciente": "P002", "nombre": "MARIA",     "apellido": "LOPEZ",    "fecha_ingreso": "03-01-2026",  "estado": "hospitalizado", "cama_asignada": 12, "medico": "Dra. Vega"},
    {"id_atencion": "A003", "id_paciente": "P003", "nombre": "carlos",    "apellido": "mendoza",  "fecha_ingreso": "2026/01/08",  "estado": "observacion",   "cama_asignada": 3,  "medico": ""},
    {"id_atencion": "A004", "id_paciente": "P004", "nombre": "ANA",       "apellido": "SILVA",    "fecha_ingreso": "2026-01-10",  "estado": "uci",           "cama_asignada": -1, "medico": "Dr. Rojas"},
    {"id_atencion": "A005", "id_paciente": "P005", "nombre": "pedro",     "apellido": "gonzalez", "fecha_ingreso": "2026-01-12",  "estado": "fallecido",     "cama_asignada": 7,  "medico": "Dra. Munoz"},
    {"id_atencion": "A006", "id_paciente": "P006", "nombre": "lucia",     "apellido": "ramirez",  "fecha_ingreso": "2026-01-15",  "estado": "alta",          "cama_asignada": 2,  "medico": "Dr. Torres"},
    {"id_atencion": "A007", "id_paciente": "P007", "nombre": "jorge",     "apellido": "castillo", "fecha_ingreso": "2026-01-18",  "estado": "hospitalizado", "cama_asignada": 9,  "medico": ""},
    {"id_atencion": "A008", "id_paciente": "P008", "nombre": "carmen",    "apellido": "flores",   "fecha_ingreso": "2026-02-01",  "estado": "observacion",   "cama_asignada": 6,  "medico": "Dra. Vega"},
    {"id_atencion": "A009", "id_paciente": "P009", "nombre": "roberto",   "apellido": "vargas",   "fecha_ingreso": "2026-02-03",  "estado": "uci",           "cama_asignada": 14, "medico": "Dr. Rojas"},
    {"id_atencion": "A010", "id_paciente": "P010", "nombre": "elena",     "apellido": "morales",  "fecha_ingreso": "02-02-2026",  "estado": "alta",          "cama_asignada": 1,  "medico": "Dr. Torres"},
    {"id_atencion": "A001", "id_paciente": "P001", "nombre": "juan",      "apellido": "perez",    "fecha_ingreso": "2026-01-03",  "estado": "alta",          "cama_asignada": 5,  "medico": "Dr. Torres"},
    {"id_atencion": "A011", "id_paciente": "P011", "nombre": "beatriz",   "apellido": "soto",     "fecha_ingreso": "2026-02-08",  "estado": "hospitalizado", "cama_asignada": 11, "medico": "Dra. Munoz"},
    {"id_atencion": "A012", "id_paciente": "P012", "nombre": "SANDRA",    "apellido": "NUNEZ",    "fecha_ingreso": "2026-02-10",  "estado": "observacion",   "cama_asignada": 4,  "medico": "Dra. Vega"},
    {"id_atencion": "A013", "id_paciente": "P013", "nombre": "miguel",    "apellido": "herrera",  "fecha_ingreso": "2026-02-12",  "estado": "fallecido",     "cama_asignada": 8,  "medico": "Dr. Rojas"},
    {"id_atencion": "A014", "id_paciente": "P014", "nombre": "patricia",  "apellido": "rojas",    "fecha_ingreso": "2026-02-14",  "estado": "uci",           "cama_asignada": 15, "medico": ""},
    {"id_atencion": "A015", "id_paciente": "P015", "nombre": "andres",    "apellido": "diaz",     "fecha_ingreso": "2026-02-16",  "estado": "alta",          "cama_asignada": 2,  "medico": "Dr. Torres"},
    {"id_atencion": "A016", "id_paciente": "P016", "nombre": "veronica",  "apellido": "mendez",   "fecha_ingreso": "2026-02-18",  "estado": "hospitalizado", "cama_asignada": 10, "medico": "Dra. Vega"},
    {"id_atencion": "A017", "id_paciente": "P017", "nombre": "HUGO",      "apellido": "REYES",    "fecha_ingreso": "2026/02/20",  "estado": "observacion",   "cama_asignada": -3, "medico": "Dr. Rojas"},
    {"id_atencion": "A018", "id_paciente": "P018", "nombre": "francisco", "apellido": "pinto",    "fecha_ingreso": "2026-02-22",  "estado": "uci",           "cama_asignada": 13, "medico": "Dra. Munoz"},
    {"id_atencion": "A019", "id_paciente": "P019", "nombre": "valentina", "apellido": "araya",    "fecha_ingreso": "2026-02-24",  "estado": "alta",          "cama_asignada": 3,  "medico": "Dr. Torres"},
    {"id_atencion": "A020", "id_paciente": "P020", "nombre": "rodrigo",   "apellido": "fuentes",  "fecha_ingreso": "2026-02-26",  "estado": "hospitalizado", "cama_asignada": 7,  "medico": "Dra. Vega"},
]

farmacia_xml = """<farmacia>
  <despacho><id_despacho>D001</id_despacho><id_paciente>P001</id_paciente><nombre>juan</nombre><apellido>perez</apellido><fecha_despacho>2026-01-03</fecha_despacho><cantidad>1</cantidad><medicamento>Paracetamol</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D002</id_despacho><id_paciente>P002</id_paciente><nombre>MARIA</nombre><apellido>LOPEZ</apellido><fecha_despacho>03-01-2026</fecha_despacho><cantidad>2</cantidad><medicamento>Ibuprofeno</medicamento><farmaceutico></farmaceutico></despacho>
  <despacho><id_despacho>D003</id_despacho><id_paciente>P003</id_paciente><nombre>carlos</nombre><apellido>mendoza</apellido><fecha_despacho>2026/01/05</fecha_despacho><cantidad></cantidad><medicamento>Amoxicilina</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D004</id_despacho><id_paciente>P004</id_paciente><nombre>ANA</nombre><apellido>SILVA</apellido><fecha_despacho>2026-01-06</fecha_despacho><cantidad>3</cantidad><medicamento>Omeprazol</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D005</id_despacho><id_paciente>P005</id_paciente><nombre>pedro</nombre><apellido>gonzalez</apellido><fecha_despacho>2026-01-07</fecha_despacho><cantidad>1</cantidad><medicamento>Salbutamol</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D006</id_despacho><id_paciente>P006</id_paciente><nombre>lucia</nombre><apellido>ramirez</apellido><fecha_despacho>2026-01-08</fecha_despacho><cantidad>2</cantidad><medicamento>Enalapril</medicamento><farmaceutico></farmaceutico></despacho>
  <despacho><id_despacho>D007</id_despacho><id_paciente>P007</id_paciente><nombre>jorge</nombre><apellido>castillo</apellido><fecha_despacho>2026-01-09</fecha_despacho><cantidad>1</cantidad><medicamento>Losartan</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D008</id_despacho><id_paciente>P008</id_paciente><nombre>carmen</nombre><apellido>flores</apellido><fecha_despacho>2026-01-10</fecha_despacho><cantidad>2</cantidad><medicamento>Metformina</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D009</id_despacho><id_paciente>P009</id_paciente><nombre>roberto</nombre><apellido>vargas</apellido><fecha_despacho>2026-01-11</fecha_despacho><cantidad>1</cantidad><medicamento>Aspirina</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D010</id_despacho><id_paciente>P010</id_paciente><nombre>elena</nombre><apellido>morales</apellido><fecha_despacho>2026-01-12</fecha_despacho><cantidad>4</cantidad><medicamento>Clorfenamina</medicamento><farmaceutico></farmaceutico></despacho>
  <despacho><id_despacho>D001</id_despacho><id_paciente>P001</id_paciente><nombre>juan</nombre><apellido>perez</apellido><fecha_despacho>2026-01-03</fecha_despacho><cantidad>1</cantidad><medicamento>Paracetamol</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D011</id_despacho><id_paciente>P011</id_paciente><nombre>beatriz</nombre><apellido>soto</apellido><fecha_despacho>2026-01-13</fecha_despacho><cantidad>1</cantidad><medicamento>Furosemida</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D012</id_despacho><id_paciente>P012</id_paciente><nombre>SANDRA</nombre><apellido>NUNEZ</apellido><fecha_despacho>2026-01-14</fecha_despacho><cantidad>2</cantidad><medicamento>Atorvastatina</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D013</id_despacho><id_paciente>P013</id_paciente><nombre>miguel</nombre><apellido>herrera</apellido><fecha_despacho>15-01-2026</fecha_despacho><cantidad>1</cantidad><medicamento>Salbutamol</medicamento><farmaceutico></farmaceutico></despacho>
  <despacho><id_despacho>D014</id_despacho><id_paciente>P014</id_paciente><nombre>patricia</nombre><apellido>rojas</apellido><fecha_despacho>2026-01-16</fecha_despacho><cantidad>3</cantidad><medicamento>Dimenhidrinato</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D015</id_despacho><id_paciente>P015</id_paciente><nombre>andres</nombre><apellido>diaz</apellido><fecha_despacho>2026-01-17</fecha_despacho><cantidad>1</cantidad><medicamento>Clopidogrel</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D016</id_despacho><id_paciente>P016</id_paciente><nombre>veronica</nombre><apellido>mendez</apellido><fecha_despacho>2026/01/18</fecha_despacho><cantidad>2</cantidad><medicamento>Prednisona</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D017</id_despacho><id_paciente>P017</id_paciente><nombre>HUGO</nombre><apellido>REYES</apellido><fecha_despacho>2026-01-19</fecha_despacho><cantidad>1</cantidad><medicamento>Diclofenaco</medicamento><farmaceutico></farmaceutico></despacho>
  <despacho><id_despacho>D018</id_despacho><id_paciente>P018</id_paciente><nombre>francisco</nombre><apellido>pinto</apellido><fecha_despacho>2026-01-20</fecha_despacho><cantidad>2</cantidad><medicamento>Insulina</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
  <despacho><id_despacho>D019</id_despacho><id_paciente>P019</id_paciente><nombre>valentina</nombre><apellido>araya</apellido><fecha_despacho>2026-01-21</fecha_despacho><cantidad>1</cantidad><medicamento>Ranitidina</medicamento><farmaceutico>Luis Vera</farmaceutico></despacho>
  <despacho><id_despacho>D020</id_despacho><id_paciente>P020</id_paciente><nombre>rodrigo</nombre><apellido>fuentes</apellido><fecha_despacho>2026-01-22</fecha_despacho><cantidad>3</cantidad><medicamento>Metoclopramida</medicamento><farmaceutico>Carmen Soto</farmaceutico></despacho>
</farmacia>"""

Path("data/raw/laboratorio.csv").write_text(laboratorio_csv, encoding="utf-8")
Path("data/raw/urgencias.json").write_text(json.dumps(urgencias, indent=2, ensure_ascii=False), encoding="utf-8")
Path("data/raw/farmacia.xml").write_text(farmacia_xml, encoding="utf-8")

print("Datos de ejemplo generados en data/raw/")
print("  laboratorio.csv : 20 registros (1 duplicado, nombres en mayusculas, fechas distintos formatos)")
print("  urgencias.json  : 20 registros (1 duplicado, camas negativas, medicos vacios, fechas distintos formatos)")
print("  farmacia.xml    : 20 registros (1 duplicado, cantidades vacias, farmaceuticos vacios, fechas distintos formatos)")
