# 🏥 Clínica MediSalud S.A. - Pipeline ETL de Datos

**Evaluación 2 - Gestión de Datos para Inteligencia Artificial**

Pipeline completo de datos (ETL) que implementa ingesta, limpieza, validación y carga de datos desde fuentes heterogéneas (CSV, JSON, XML) a una base de datos, aplicando buenas prácticas de **Data Engineering** con arquitectura modular y escalable.

---

## 📚 Estructura del Proyecto

```
caso_clinica_gd_ev2/
│
├── clinica_etl/                 # 📦 Paquete modular
│   ├── __init__.py
│   ├── config.py                # Configuración centralizada
│   ├── ingesta/                 # Etapa 1: Ingesta
│   ├── limpieza/                # Etapa 2: Limpieza
│   ├── validacion/              # Etapa 3: Validación
│   ├── carga/                   # Etapa 4: Carga
│   └── utils/                   # Utilidades compartidas
│
├── scripts/                     # Scripts adicionales
│   └── generar_raw_data.py
│
├── data/                        # 📁 Datos
│   ├── raw/                     # Datos sin procesar
│   ├── clean/                   # Datos limpios
│   ├── validados/               # Datos validados
│   ├── rechazados/              # Registros rechazados
│   └── clinica.db               # Base de datos
│
├── logs/                        # 📋 Logs de ejecución
│
├── etapa1_ingesta.py            # 🚀 Etapa 1
├── limpieza.py                  # 🚀 Etapa 2
├── etapa3_validacion.py         # 🚀 Etapa 3
├── etapa4_carga_bd.py           # 🚀 Etapa 4
│
├── config.py                    # Configuración compartida
├── requirements.txt             # Dependencias
├── .env.example                 # Variables de entorno
├── .gitignore                   # Git ignore
└── README.md                    # Este archivo
```

---

## 🎯 Etapas del Pipeline

| # | Etapa | Descripción | Estado |
|---|-------|-----------|--------|
| 1 | 📥 **Ingesta** | Lee archivos de origen (CSV, JSON, XML) y copia a `data/raw/` | ✅ |
| 2 | 🧹 **Limpieza** | Transforma y normaliza datos | ✅ |
| 3 | ✔️ **Validación** | Valida contra reglas de negocio | ✅ |
| 4 | 💾 **Carga** | Inserta datos en BD (SQLite/PostgreSQL) | ✅ |

---

## 🚀 Inicio Rápido

### 1. Instalación

```bash
git clone https://github.com/SebastianAVi/caso_clinica_gd_ev2.git
cd caso_clinica_gd_ev2

# Entorno virtual (recomendado)
python -m venv venv
source venv/Scripts/activate  # Windows

# Instalar
pip install -r requirements.txt
```

### 2. Ejecutar

**Opción A: Scripts principales (recomendado)**
```bash
# Etapa 1: Ingesta
python etapa1_ingesta.py

# Etapa 2: Limpieza
python limpieza.py

# Etapa 3: Validación
python etapa3_validacion.py

# Etapa 4: Carga
python etapa4_carga_bd.py
```

**Opción B: Importar módulos del paquete**
```python
from clinica_etl.ingesta import ejecutar_ingesta
from clinica_etl.limpieza import ejecutar_limpieza

ejecutar_ingesta()
ejecutar_limpieza()
```

---

## 🛠 Tecnologías

- Python 3.8+
- pandas, numpy
- SQLite / PostgreSQL
- XML, JSON, CSV

---

## 📊 Datos de Entrada

Tres archivos en `data/raw/`:

1. **laboratorio.csv** - Exámenes
2. **urgencias.json** - Urgencias
3. **farmacia.xml** - Medicamentos

---

## 📝 Logs

Guardados en `logs/` con timestamp (ej: `ingesta_20260518_131557.log`)

---

## 💡 Ejemplo de Uso

```python
from clinica_etl.ingesta import ejecutar_ingesta
from clinica_etl.limpieza import ejecutar_limpieza

ejecutar_ingesta()
ejecutar_limpieza()
```

Ver [ESTRUCTURA_OPTIMIZADA.md](ESTRUCTURA_OPTIMIZADA.md) para más detalles.
