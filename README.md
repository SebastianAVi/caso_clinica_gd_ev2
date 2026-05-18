# 🏥 Caso Clínico: Pipeline de Gestión de Datos - Clínica MediSalud S.A.

**Evaluación 2 - Gestión de Datos para la Inteligencia Artificial**

Proyecto que implementa un **pipeline completo de datos** (ETL) para una clínica, siguiendo las 4 etapas solicitadas: **Ingesta → Limpieza → Validación → Carga**.

---

## 🎯 Objetivo del Proyecto

Desarrollar un flujo de procesamiento de datos desde fuentes heterogéneas (CSV, JSON, XML) hasta una base de datos, aplicando buenas prácticas de **Data Engineering**: ingesta controlada, limpieza, validación de reglas de negocio y carga confiable.

---

## 📋 Etapas del Pipeline

| Semana | Etapa                    | Estado     | Archivo Principal              |
|--------|--------------------------|------------|--------------------------------|
| 1      | Ingesta de Datos         | ✅ Completa | `etapa1_ingesta.py`            |
| 2      | Limpieza y Transformación| ✅ Completa | `etapa2_limpieza.py`       |
| 3      | Validación               | 🔄 En progreso | `etapa3_validacion.py`     |
| 4      | Carga a Base de Datos    | 🔄 En progreso | `etapa4_carga_bd.py`       |

---

## 🛠 Tecnologías Utilizadas

- **Python 3**
- **pandas** (próximamente)
- **PostgreSQL** (planeado)
- **XML**, **JSON**, **CSV**
- **Git + GitHub**

---

## 📁 Estructura del Proyecto
caso_clinica_gd_ev2/
├── data/
│   ├── raw/              # Datos tal como llegan
│   └── processed/        # Datos limpios (próximamente)
├── logs/                 # Logs de cada ejecución
├── etapa1_ingesta.py
├── etapa2_limpieza.py
├── etapa3_validacion.py
├── etapa4_carga_bd.py
├── requirements.txt
├── TODO.md
└── README.md
text---

## 🚀 Cómo Ejecutar la Etapa 1 (Ingesta)

```bash
# 1. Clonar el repositorio
git clone https://github.com/SebastianAVi/caso_clinica_gd_ev2.git
cd caso_clinica_gd_ev2

# 2. Ejecutar la ingesta
python etapa1_ingesta.py
Lo que hace el script:

Crea las carpetas necesarias (data/raw, logs)
Copia los archivos desde data/raw_origen/ a data/raw/
Cuenta registros de cada fuente
Genera un log detallado con fecha, duración y cantidad de registros

## 🧪 Etapa 4: Carga a Base de Datos

Después de limpiar y validar los datos, ejecute:

```bash
python etapa4_carga_bd.py
```

El script crea tablas en la base de datos SQLite (`data/clinica.db`), carga los registros válidos de `data/clean`, evita duplicados y genera un log en `logs/`.


📊 Datos de Ejemplo Incluidos

laboratorio.csv → Resultados de exámenes
urgencias.json → Atenciones de urgencia
farmacia.xml → Despachos de medicamentos
