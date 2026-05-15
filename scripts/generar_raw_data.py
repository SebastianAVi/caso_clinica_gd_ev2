from pathlib import Path
import json

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

urgencias = [
    {"id_atencion": "A001", "id_paciente": "P001", "fecha_ingreso": "2026-01-03", "estado": "alta"},
    {"id_atencion": "A002", "id_paciente": "P002", "fecha_ingreso": "2026-01-05", "estado": "hospitalizado"},
    {"id_atencion": "A003", "id_paciente": "P003", "fecha_ingreso": "2026-01-08", "estado": "observacion"},
    {"id_atencion": "A004", "id_paciente": "P004", "fecha_ingreso": "2026-01-10", "estado": "uci"},
    {"id_atencion": "A005", "id_paciente": "P005", "fecha_ingreso": "2026-01-12", "estado": "fallecido"},
    {"id_atencion": "A006", "id_paciente": "P006", "fecha_ingreso": "2026-01-15", "estado": "alta"},
    {"id_atencion": "A007", "id_paciente": "P007", "fecha_ingreso": "2026-01-18", "estado": "hospitalizado"},
    {"id_atencion": "A008", "id_paciente": "P008", "fecha_ingreso": "2026-02-01", "estado": "observacion"},
    {"id_atencion": "A009", "id_paciente": "P009", "fecha_ingreso": "2026-02-03", "estado": "uci"},
    {"id_atencion": "A010", "id_paciente": "P010", "fecha_ingreso": "2026-02-05", "estado": "alta"},
    {"id_atencion": "A011", "id_paciente": "P011", "fecha_ingreso": "2026-02-08", "estado": "hospitalizado"},
    {"id_atencion": "A012", "id_paciente": "P012", "fecha_ingreso": "2026-02-10", "estado": "observacion"},
    {"id_atencion": "A013", "id_paciente": "P013", "fecha_ingreso": "2026-02-12", "estado": "fallecido"},
    {"id_atencion": "A014", "id_paciente": "P014", "fecha_ingreso": "2026-02-14", "estado": "uci"},
    {"id_atencion": "A015", "id_paciente": "P015", "fecha_ingreso": "2026-02-16", "estado": "alta"},
    {"id_atencion": "A016", "id_paciente": "P016", "fecha_ingreso": "2026-02-18", "estado": "hospitalizado"},
    {"id_atencion": "A017", "id_paciente": "P017", "fecha_ingreso": "2026-02-20", "estado": "observacion"},
    {"id_atencion": "A018", "id_paciente": "P018", "fecha_ingreso": "2026-02-22", "estado": "uci"},
    {"id_atencion": "A019", "id_paciente": "P019", "fecha_ingreso": "2026-02-24", "estado": "alta"},
    {"id_atencion": "A020", "id_paciente": "P020", "fecha_ingreso": "2026-02-26", "estado": "hospitalizado"},
]

farmacia = """<farmacia>
  <despacho>
    <id_despacho>D001</id_despacho>
    <id_paciente>P001</id_paciente>
    <fecha_despacho>2026-01-03</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Paracetamol</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D002</id_despacho>
    <id_paciente>P002</id_paciente>
    <fecha_despacho>2026-01-04</fecha_despacho>
    <cantidad>2</cantidad>
    <medicamento>Ibuprofeno</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D003</id_despacho>
    <id_paciente>P003</id_paciente>
    <fecha_despacho>2026-01-05</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Amoxicilina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D004</id_despacho>
    <id_paciente>P004</id_paciente>
    <fecha_despacho>2026-01-06</fecha_despacho>
    <cantidad>3</cantidad>
    <medicamento>Omeprazol</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D005</id_despacho>
    <id_paciente>P005</id_paciente>
    <fecha_despacho>2026-01-07</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Salbutamol</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D006</id_despacho>
    <id_paciente>P006</id_paciente>
    <fecha_despacho>2026-01-08</fecha_despacho>
    <cantidad>2</cantidad>
    <medicamento>Enalapril</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D007</id_despacho>
    <id_paciente>P007</id_paciente>
    <fecha_despacho>2026-01-09</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Losartan</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D008</id_despacho>
    <id_paciente>P008</id_paciente>
    <fecha_despacho>2026-01-10</fecha_despacho>
    <cantidad>2</cantidad>
    <medicamento>Metformina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D009</id_despacho>
    <id_paciente>P009</id_paciente>
    <fecha_despacho>2026-01-11</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Aspirina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D010</id_despacho>
    <id_paciente>P010</id_paciente>
    <fecha_despacho>2026-01-12</fecha_despacho>
    <cantidad>4</cantidad>
    <medicamento>Clorfenamina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D011</id_despacho>
    <id_paciente>P011</id_paciente>
    <fecha_despacho>2026-01-13</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Furosemida</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D012</id_despacho>
    <id_paciente>P012</id_paciente>
    <fecha_despacho>2026-01-14</fecha_despacho>
    <cantidad>2</cantidad>
    <medicamento>Atorvastatina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D013</id_despacho>
    <id_paciente>P013</id_paciente>
    <fecha_despacho>2026-01-15</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Salbutamol</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D014</id_despacho>
    <id_paciente>P014</id_paciente>
    <fecha_despacho>2026-01-16</fecha_despacho>
    <cantidad>3</cantidad>
    <medicamento>Dimenhidrinato</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D015</id_despacho>
    <id_paciente>P015</id_paciente>
    <fecha_despacho>2026-01-17</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Clopidogrel</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D016</id_despacho>
    <id_paciente>P016</id_paciente>
    <fecha_despacho>2026-01-18</fecha_despacho>
    <cantidad>2</cantidad>
    <medicamento>Prednisona</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D017</id_despacho>
    <id_paciente>P017</id_paciente>
    <fecha_despacho>2026-01-19</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Diclofenaco</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D018</id_despacho>
    <id_paciente>P018</id_paciente>
    <fecha_despacho>2026-01-20</fecha_despacho>
    <cantidad>2</cantidad>
    <medicamento>Insulina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D019</id_despacho>
    <id_paciente>P019</id_paciente>
    <fecha_despacho>2026-01-21</fecha_despacho>
    <cantidad>1</cantidad>
    <medicamento>Ranitidina</medicamento>
  </despacho>
  <despacho>
    <id_despacho>D020</id_despacho>
    <id_paciente>P020</id_paciente>
    <fecha_despacho>2026-01-22</fecha_despacho>
    <cantidad>3</cantidad>
    <medicamento>Metoclopramida</medicamento>
  </despacho>
</farmacia>"""

lab_data = """id_examen,id_paciente,fecha_examen,resultado
E001,P001,2026-01-02,5.4
E002,P002,2026-01-04,7.1
E003,P003,2026-01-06,11.2
E004,P004,2026-01-08,3.5
E005,P005,2026-01-10,9.8
E006,P006,2026-01-12,2.4
E007,P007,2026-01-14,6.0
E008,P008,2026-01-16,4.7
E009,P009,2026-01-18,8.9
E010,P010,2026-01-20,12.5
E011,P011,2026-01-22,5.1
E012,P012,2026-01-24,7.3
E013,P013,2026-01-26,10.0
E014,P014,2026-01-28,3.9
E015,P015,2026-01-30,6.2
E016,P016,2026-02-01,4.4
E017,P017,2026-02-03,9.0
E018,P018,2026-02-05,5.7
E019,P019,2026-02-07,8.1
E020,P020,2026-02-09,11.6
"""

Path("data/raw/urgencias.json").write_text(json.dumps(urgencias, indent=2, ensure_ascii=False), encoding="utf-8")
Path("data/raw/farmacia.xml").write_text(farmacia, encoding="utf-8")
Path("data/raw/laboratorio.csv").write_text(lab_data, encoding="utf-8")
print("raw files written")
