# Pipeline de Datos - Clinica MediSalud S.A.

Evaluacion 2 - Gestion de Datos para la Inteligencia Artificial  
Seccion 901D | Docente: Cristian Gandolfi  
Integrantes: Sebastian Aviles, Santiago Vega, Vicente Vergara

## Descripcion

Pipeline ETL automatizado que ingesta, limpia, valida y carga datos clinicos provenientes de tres fuentes heterogeneas hacia una base de datos centralizada, permitiendo analisis operacional de atenciones, examenes y despachos de farmacia.

## Estructura del proyecto

```
caso_clinica_gd_ev2/
├── config.py                  # Constantes y configuracion centralizada
├── etapa1_ingesta.py          # Etapa 1: copia archivos a data/raw/ y genera log
├── limpieza.py                # Etapa 2: orquestador de limpieza
├── limpieza_laboratorio.py    # Limpieza especifica de laboratorio.csv
├── limpieza_urgencia.py       # Limpieza especifica de urgencias.json
├── limpieza_farmacia.py       # Limpieza especifica de farmacia.xml
├── etapa3_validacion.py       # Etapa 3: validacion y separacion validos/rechazados
├── etapa4_carga_bd.py         # Etapa 4: carga a SQLite (o PostgreSQL)
├── analisis_operacional.py    # Consultas y metricas operacionales desde la BD
├── requirements.txt
├── scripts/
│   └── generar_raw_data.py    # Genera datos de ejemplo con errores intencionales
└── data/
    └── raw/                   # Archivos fuente (CSV, JSON, XML)
```

## Fuentes de datos

| Area        | Formato | Archivo              |
|-------------|---------|----------------------|
| Laboratorio | CSV     | data/raw/laboratorio.csv |
| Urgencias   | JSON    | data/raw/urgencias.json  |
| Farmacia    | XML     | data/raw/farmacia.xml    |

## Etapas del pipeline

| Etapa | Script               | Descripcion                                      | Estado      |
|-------|----------------------|--------------------------------------------------|-------------|
| 1     | etapa1_ingesta.py    | Copia archivos a data/raw/ y registra log        | Completa    |
| 2     | limpieza.py          | Limpia y transforma datos hacia data/clean/      | Completa    |
| 3     | etapa3_validacion.py | Valida reglas de negocio, separa validos/rechazados | Completa |
| 4     | etapa4_carga_bd.py   | Carga registros validos a la base de datos       | Completa    |
| +     | analisis_operacional.py | Metricas de uso de camas, examenes y farmacia | Completa    |

## Como ejecutar

### 1. Generar datos de ejemplo (con errores intencionales para demostrar el pipeline)

```bash
python scripts/generar_raw_data.py
```

### 2. Ejecutar el pipeline completo en orden

```bash
python etapa1_ingesta.py
python limpieza.py
python etapa3_validacion.py
python etapa4_carga_bd.py
python analisis_operacional.py
```

## Que hace cada etapa

**Etapa 1 - Ingesta:** Lee los archivos desde `data/raw/` (o `data/raw_origen/` si existe), los copia al destino y genera un log con cantidad de registros por fuente.

**Etapa 2 - Limpieza:** Capitaliza nombres, estandariza fechas a formato YYYY-MM-DD, elimina duplicados, corrige camas negativas y campos vacios. Guarda resultados en `data/clean/`.

**Etapa 3 - Validacion:** Aplica reglas de negocio: campos obligatorios, fechas no futuras, resultado numerico positivo, estado de urgencia valido, cantidad mayor a 0. Separa registros en `data/validados/` y `data/rechazados/` con motivo de rechazo.

**Etapa 4 - Carga:** Inserta los registros validados en SQLite (por defecto) o PostgreSQL. Evita duplicados y genera log con resumen y consulta de ejemplo.

**Analisis operacional:** Consultas sobre uso de camas por estado, examenes de laboratorio (promedio, min, max), medicamentos mas despachados y actividad por mes.

## Configuracion de base de datos

Por defecto usa SQLite (`data/clinica.db`). Para usar PostgreSQL:

```bash
DB_ENGINE=postgresql DB_NAME=clinica DB_USER=postgres DB_PASSWORD=postgres python etapa4_carga_bd.py
```

## Tecnologias

- Python 3
- SQLite / PostgreSQL
- Modulos estandar: csv, json, xml, sqlite3, datetime, os
