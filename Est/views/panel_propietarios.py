from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PySide6.QtCore import Qt

# Importaremos las pestañas (que por ahora estarán vacías o en construcción)
from views.tabs.registrar_propietario import TabRegistrarPropietario
from views.tabs.modificar_propietario import TabModificarPropietario

import logic.catalogos as cat

class PanelPropietarios(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual # Recibimos el gafete
        self.configurar_ui()

    def configurar_ui(self):
        layout_principal = QVBoxLayout(self)
        
        #Título del módulo
        lbl_titulo = QLabel("Módulo de Gestión de Propietarios")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #cdd6f4;") # Usando colores de tu nuevo tema oscuro
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        # ==========================================
        # CREACIÓN DE PESTAÑAS (QTabWidget)
        # ==========================================
        
        self.pestanas = QTabWidget()
        
        # Instanciamos nuestras futuras pestañas pasándoles el gafete
        self.tab_registrar = TabRegistrarPropietario(self.usuario_actual)
        self.tab_modificar = TabModificarPropietario(self.usuario_actual)

        # --- APLICACIÓN DE ROLES ---
        rol = self.usuario_actual.rol
        
        if rol in [cat.ROLES_USUARIO[0], cat.ROLES_USUARIO[1]]: # Admin u Operador
            self.pestanas.addTab(self.tab_registrar, "Registrar Nuevo Propietario")
            self.pestanas.addTab(self.tab_modificar, "Modificar Propietario")
            
        elif rol in [cat.ROLES_USUARIO[2], cat.ROLES_USUARIO[3]]: # Agente o Supervisor
            # Solo lectura
            self.pestanas.addTab(self.tab_modificar, "Consultar Propietario")

        layout_principal.addWidget(self.pestanas)