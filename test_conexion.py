import sqlite3

db_path = "data/clinica.db"

# Verificar conexión y mostrar tablas con cantidad de registros
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()

    if tablas:
        print(f"Conexión exitosa")
        print(f"Tablas encontradas:")
        for tabla in tablas:
            nombre = tabla[0]
            cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
            cantidad = cursor.fetchone()[0]
            print(f"   → {nombre}: {cantidad} registros")
    else:
        print("Base de Datos vacía — ejecuta etapa4_carga_bd.py primero")

    conn.close()

except Exception as e:
    print(f"Error: {e}")