# Pipeline de Datos - Clinica MediSalud S.A.

Evaluacion Final Transversal - Gestion de Datos para la Inteligencia Artificial
Seccion 901D | Docente: Cristian Gandolfi
Integrantes: Sebastian Aviles, Santiago Vega, Vicente Vergara

## Descripcion

Pipeline ETL automatizado que ingesta, limpia, valida y carga datos clinicos provenientes de tres fuentes heterogeneas hacia una base de datos centralizada, permitiendo analisis operacional de atenciones, examenes y despachos de farmacia.

Este repositorio contiene **solo codigo**. Los datos (crudos, limpios y la base de datos) no se versionan: se generan en el momento al ejecutar los scripts, lo que permite demostrar el pipeline completo en vivo durante la presentacion.

## Estructura del proyecto

```
caso_clinica_gd_ev2/
├── config.py                  # Constantes y configuracion centralizada
├── 01_ingesta.py              # Etapa 1: copia archivos a data/raw/ y genera log
├── 02_limpieza.py             # Etapa 2: orquestador de limpieza
├── limpieza_laboratorio.py    # Limpieza especifica de laboratorio.csv
├── limpieza_urgencia.py       # Limpieza especifica de urgencias.json
├── limpieza_farmacia.py       # Limpieza especifica de farmacia.xml
├── 03_validacion.py           # Etapa 3: validacion y separacion validos/rechazados
├── 04_carga_bd.py             # Etapa 4: carga a SQLite (o PostgreSQL)
├── analisis_operacional.py    # Consultas y metricas operacionales desde la BD
├── requirements.txt
├── .gitignore                 # Excluye toda la carpeta data/ y logs/ generados
└── scripts/
    └── generar_raw_data.py    # Genera los datos de origen (CSV, JSON, XML)
```

> Nota: la carpeta `data/` no existe en el repositorio. Se crea automaticamente la primera vez que se ejecuta un script.
> Nota: los scripts principales de ETL se renombraron con prefijos numéricos para que el flujo sea más claro: `01_ingesta.py`, `02_limpieza.py`, `03_validacion.py`, `04_carga_bd.py`.
> Repositorio remoto: https://github.com/SebastianAVi/caso_clinica_gd_ev2.git

## Fuentes de datos

| Area        | Formato | Archivo generado          | Registros base |
|-------------|---------|----------------------------|-----------------|
| Laboratorio | CSV     | data/raw/laboratorio.csv  | 1000            |
| Urgencias   | JSON    | data/raw/urgencias.json   | 1000            |
| Farmacia    | XML     | data/raw/farmacia.xml     | 1000            |

Cada archivo se genera con una proporcion realista de errores intencionales (~2% duplicados, fechas en formatos mixtos, campos vacios, valores invalidos) para poder demostrar la limpieza y validacion trabajando sobre datos reales.

## Etapas del pipeline

| Etapa | Script                       | Descripcion                                         | Estado      |
|-------|-----------------------------|-----------------------------------------------------|-------------|
| 0     | scripts/generar_raw_data.py | Genera los archivos fuente en data/raw/             | Completa    |
| 1     | 01_ingesta.py              | Copia archivos a data/raw/ y registra log           | Completa    |
| 2     | 02_limpieza.py             | Limpia y transforma datos hacia data/clean/         | Completa    |
| 3     | 03_validacion.py           | Valida reglas de negocio, separa validos/rechazados | Completa    |
| 4     | 04_carga_bd.py             | Carga registros validos a la base de datos          | Completa    |
| +     | analisis_operacional.py    | Metricas de uso de camas, examenes y farmacia       | Completa    |

## Como ejecutar (demo en vivo)

Ejecutar en este orden exacto. Cada comando puede mostrarse y explicarse en la presentacion.

```bash
# 0. Generar los datos de origen (1000 registros por area, con errores intencionales)
python scripts/generar_raw_data.py

# 1. Ingesta: copia los archivos a data/raw/ y genera log
python 01_ingesta.py

# 2. Limpieza: corrige duplicados, fechas, nombres y campos vacios
python 02_limpieza.py

# 3. Validacion: separa registros validos de rechazados con motivo
python 03_validacion.py

# 4. Carga: inserta los registros validos en la base de datos SQLite
python 04_carga_bd.py

# 5. Analisis: metricas operacionales desde la base de datos ya cargada
python analisis_operacional.py
```

Al finalizar, revisar la carpeta `logs/` para ver la trazabilidad completa de cada etapa (fecha, duracion, registros procesados y errores).

## Que hace cada etapa

**Etapa 0 - Generacion de datos:** Crea `data/raw/laboratorio.csv`, `data/raw/urgencias.json` y `data/raw/farmacia.xml` con 1000 registros base por area, inyectando duplicados, fechas en formatos distintos y campos vacios de forma controlada.

**Etapa 1 - Ingesta:** Lee los archivos desde `data/raw/` (o `data/raw_origen/` si existe), los copia al destino y genera un log con cantidad de registros por fuente.

**Etapa 2 - Limpieza:** Capitaliza nombres, estandariza fechas a formato YYYY-MM-DD, elimina duplicados, corrige camas negativas y campos vacios. Guarda resultados en `data/clean/`.

**Etapa 3 - Validacion:** Aplica reglas de negocio: campos obligatorios, fechas no futuras, resultado numerico positivo, estado de urgencia valido, cantidad mayor a 0. Separa registros en `data/validados/` y `data/rechazados/` con motivo de rechazo.

**Etapa 4 - Carga:** Inserta los registros validados en SQLite (por defecto) o PostgreSQL. Evita duplicados y genera log con resumen y consulta de ejemplo.

**Analisis operacional:** Consultas sobre uso de camas por estado, examenes de laboratorio (promedio, min, max), medicamentos mas despachados y actividad por mes.

## Configuracion de base de datos

Por defecto usa SQLite (`data/clinica.db`). Para usar PostgreSQL:

```bash
DB_ENGINE=postgresql DB_NAME=clinica DB_USER=postgres DB_PASSWORD=postgres python 04_carga_bd.py
```

## Datos y archivos no versionados

El `.gitignore` excluye toda la carpeta `data/` (incluyendo `raw/`, `clean/`, `validados/`, `rechazados/` y `clinica.db`) y `logs/`, ya que son artefactos generados por la ejecucion del pipeline y no codigo fuente. Esto permite que cualquier persona que clone el repositorio genere sus propios datos desde cero siguiendo los pasos de la seccion anterior.

## Tecnologias

- Python 3
- SQLite / PostgreSQL
- Modulos estandar: csv, json, xml, sqlite3, datetime, os
README.md
7 KB
