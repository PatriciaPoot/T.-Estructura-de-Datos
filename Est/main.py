import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
import views.estilos as estilos
# 1. Asegurar que Python encuentre todos tus módulos
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ruta_raiz)

# 2. Importaciones de tu proyecto
from database.inicializar_db import crear_tablas
from views.login import VentanaLogin

def verificar_entorno():
    """Verifica que la base de datos exista. Si no, la crea."""
    try:
        # Esto asegura que el archivo .db se cree con todas las tablas
        crear_tablas()
        return True
    except Exception as e:
        print(f"Error crítico al inicializar la base de datos: {e}")
        return False

def main():
    # Creamos la instancia de la aplicación
    app = QApplication(sys.argv)
    
    # Aplicamos un estilo visual
    app.setStyleSheet(estilos.TEMA_OSCURO)

    # Verificamos si la base de datos está lista
    if not verificar_entorno():
        QMessageBox.critical(None, "Error de Sistema", 
                            "No se pudo inicializar la base de datos. Verifique los permisos de carpeta.")
        sys.exit(1)

    # 3. Lanzamos el punto de entrada: El Login [cite: 603, 606]
    login = VentanaLogin()
    login.show()

    # Ejecutamos el bucle de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()