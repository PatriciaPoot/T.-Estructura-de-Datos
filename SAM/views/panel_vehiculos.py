from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PySide6.QtCore import Qt
import logic.catalogos as cat

# Importamos nuestros nuevos componentes limpios y modulares
from views.tabs.tab_registrar_vehiculo import TabRegistrarVehiculo
from views.tabs.tab_modificar_vehiculo import TabModificarVehiculo

class PanelVehiculos(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()

    def configurar_ui(self):
        # Layout principal del panel
        layout_principal = QVBoxLayout(self)
        
        # Título del módulo
        lbl_titulo = QLabel("Módulo de Gestión de Vehículos")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        # ==========================================
        # CREACIÓN DE PESTAÑAS (QTabWidget)
        # ==========================================
        self.pestanas = QTabWidget()
        
        # Instanciamos nuestras clases independientes
        self.tab_registrar = TabRegistrarVehiculo(self.usuario_actual)
        self.tab_modificar = TabModificarVehiculo(self.usuario_actual)

        # --- APLICACIÓN DE ROLES ---
        rol = self.usuario_actual.rol
        
        # cat.ROLES_USUARIO[0] -> "Administrador"
        # cat.ROLES_USUARIO[1] -> "Operador Administrativo"
        if rol in [cat.ROLES_USUARIO[0], cat.ROLES_USUARIO[1]]:
            # Tienen poder de escritura, ven todo
            self.pestanas.addTab(self.tab_registrar, "Registrar Nuevo Vehículo")
            self.pestanas.addTab(self.tab_modificar, "Modificar Vehículo")
        
        # cat.ROLES_USUARIO[2] -> "Agente de Tránsito"
        # cat.ROLES_USUARIO[3] -> "Supervisor"
        elif rol in [cat.ROLES_USUARIO[2], cat.ROLES_USUARIO[3]]:
            self.pestanas.addTab(self.tab_modificar, "Consultar Vehículo")
            
        layout_principal.addWidget(self.pestanas)