import sqlite3
import os

# Buscamos la carpeta donde está este archivo (database)
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
# Unimos la ruta para que siempre apunte a database/infracciones.db
DB_PATH = os.path.join(DIRECTORIO_ACTUAL, "infracciones.db")

def obtener_conexion():
    """Crea y retorna una conexión absoluta a la base de datos."""
    # Verificamos si la ruta es correcta en consola para estar seguros
    # print(f"Conectando a: {DB_PATH}")
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row 
    conexion.execute("PRAGMA foreign_keys = 1")
    return conexion