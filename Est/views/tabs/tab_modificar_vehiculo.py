from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
QLineEdit, QPushButton, QComboBox, QFormLayout, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt

# Importaciones del backend
import logic.catalogos as cat
from logic.gestor_vehiculos import GestorVehiculos

class TabModificarVehiculo(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()
        self.aplicar_permisos()
        
    def configurar_ui(self):
        layout = QVBoxLayout(self)
        
        # ==========================================
        # 1. ZONA DE BÚSQUEDA
        # ==========================================
        layout_busqueda = QHBoxLayout()
        self.input_buscar_vin = QLineEdit()
        self.input_buscar_vin.setPlaceholderText("Ingrese VIN o Placa a buscar...")
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.procesar_busqueda_vehiculo)

        layout_busqueda.addWidget(QLabel("VIN del Vehículo:"))
        layout_busqueda.addWidget(self.input_buscar_vin)
        layout_busqueda.addWidget(btn_buscar)
        
        layout.addLayout(layout_busqueda)

        # ==========================================
        # 2. FORMULARIO DE MODIFICACIÓN
        # ==========================================
        formulario = QFormLayout()
        
        # --- CAMPOS DE SOLO LECTURA ---
        self.mod_marca = QLineEdit()
        self.mod_marca.setReadOnly(True)

        self.mod_modelo = QLineEdit()
        self.mod_modelo.setReadOnly(True)

        self.mod_anio = QLineEdit()
        self.mod_anio.setReadOnly(True)

        self.mod_clase = QLineEdit()
        self.mod_clase.setReadOnly(True)

        # --- CAMPO PROPIETARIO (Lectura + Botón) ---
        self.mod_id_propietario = QLineEdit()
        self.mod_id_propietario.setReadOnly(True)
        
        self.btn_cambiar_propietario = QPushButton("Cambio de Propietario")
        self.btn_cambiar_propietario.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold;")
        self.btn_cambiar_propietario.clicked.connect(self.abrir_ventana_cambio_propietario)
        
        layout_propietario = QHBoxLayout()
        layout_propietario.addWidget(self.mod_id_propietario)
        layout_propietario.addWidget(self.btn_cambiar_propietario)

        # --- CAMPO PLACAS (Lectura + Botón) ---
        self.mod_placa = QLineEdit()
        self.mod_placa.setReadOnly(True)
        
        self.btn_cambiar_placa = QPushButton("Realizar Reemplacamiento")
        self.btn_cambiar_placa.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.btn_cambiar_placa.clicked.connect(self.abrir_ventana_reemplacamiento)

        layout_placa = QHBoxLayout()
        layout_placa.addWidget(self.mod_placa)
        layout_placa.addWidget(self.btn_cambiar_placa)

        # ===== CAMPOS EDITABLES =====
        self.mod_color = QComboBox()
        self.mod_color.setEditable(False)
        self.mod_color.addItems(cat.COLORES_VEHICULO)
        self.mod_color.setCurrentIndex(-1)
        
        self.mod_estado = QComboBox()
        self.mod_estado.setEditable(False)
        self.mod_estado.addItems(cat.ESTADOS_VEHICULO)
        self.mod_estado.setCurrentIndex(-1)

        # --- ENSAMBLAJE DEL FORMULARIO ---
        formulario.addRow("Marca:", self.mod_marca)
        formulario.addRow("Modelo:", self.mod_modelo)
        formulario.addRow("Clase:", self.mod_clase)
        formulario.addRow("Año:", self.mod_anio)
        formulario.addRow("ID Propietario:", layout_propietario)
        
        formulario.addRow("Placa Actual:", layout_placa)
        formulario.addRow("Color:", self.mod_color)
        formulario.addRow("Estado Legal:", self.mod_estado)
        
        layout.addLayout(formulario)

        # ==========================================
        # MARCA DE AGUA DE AUDITORÍA
        # ==========================================
        self.lbl_auditoria = QLabel("")
        self.lbl_auditoria.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        layout.addWidget(self.lbl_auditoria, alignment=Qt.AlignLeft)
        
        # ==========================================
        # 3. BOTÓN DE ACTUALIZACIÓN
        # ==========================================
        self.btn_actualizar = QPushButton("Actualizar Datos")
        self.btn_actualizar.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 10px;")
        self.btn_actualizar.clicked.connect(self.procesar_actualizacion)
        
        layout.addStretch() 
        layout.addWidget(self.btn_actualizar, alignment=Qt.AlignRight)

    # ==========================================
    # MÉTODOS DE VENTANAS EMERGENTES
    # ==========================================
    def abrir_ventana_reemplacamiento(self):
        """Ejecuta el trámite de cambio de placa"""
        vin = self.input_buscar_vin.text().strip().upper()
        
        nueva_placa, ok = QInputDialog.getText(
            self, "Trámite de Reemplacamiento", 
            f"Ingrese la nueva placa para el vehículo (VIN: {vin}):"
        )
        
        if ok and nueva_placa.strip():
            exito, msj = GestorVehiculos.realizar_reemplacamiento(
                vin, nueva_placa.strip().upper(), self.usuario_actual.id_usuario
            )
            if exito:
                QMessageBox.information(self, "Éxito", msj)
                self.mod_placa.setText(nueva_placa.strip().upper())
            else:
                QMessageBox.warning(self, "Trámite Denegado", msj)

    def abrir_ventana_cambio_propietario(self):
        """Ejecuta la transferencia de propiedad"""
        vin = self.input_buscar_vin.text().strip().upper()
        
        id_nuevo, ok = QInputDialog.getInt(
            self, "Cambio de Propietario", 
            "Ingrese el ID del nuevo propietario registrado:",
        )
        
        if ok:
            exito, msj = GestorVehiculos.transferir_propiedad(
                vin, id_nuevo, self.usuario_actual.id_usuario
            )
            if exito:
                QMessageBox.information(self, "Éxito", msj)
                self.mod_id_propietario.setText(f"PRP-{id_nuevo:05d}")
            else:
                QMessageBox.warning(self, "Trámite Denegado", msj)
                
    # ==========================================
    # MÉTODOS LÓGICOS
    # ==========================================
    def procesar_busqueda_vehiculo(self):
        """Busca el vehículo y rellena el formulario"""
        criterio_buscado = self.input_buscar_vin.text().strip().upper()
        
        if not criterio_buscado:
            QMessageBox.warning(self, "Atención", "Por favor, ingrese un VIN o Placa para buscar.")
            return
            
        exito, resultado = GestorVehiculos.buscar_vehiculo_universal(criterio_buscado)
        
        if exito:
            self.input_buscar_vin.setText(resultado["vin"]) 
            self.mod_placa.setText(resultado["placa"])
            self.mod_marca.setText(resultado["marca"])
            self.mod_modelo.setText(resultado["modelo"])
            self.mod_anio.setText(str(resultado["anio"]))
            self.mod_clase.setText(resultado["clase"])
            id_prop = resultado["id_propietario"]
            self.mod_id_propietario.setText(f"PRP-{id_prop:05d}")
            self.mod_color.setCurrentText(resultado["color"])
            self.mod_estado.setCurrentText(resultado["estado_legal"])
            
            # Mostrar auditoría
            creador = resultado["creador"]
            modificador = resultado["modificador"]
            self.lbl_auditoria.setText(f"Registro original por: {creador} | Última modificación por: {modificador}")
            self.lbl_auditoria.show()
            
        else:
            self.limpiar_formulario_modificar()
            self.lbl_auditoria.hide()
            QMessageBox.critical(self, "No encontrado", resultado)

    def limpiar_formulario_modificar(self):
        """Vacía las cajas de texto"""
        self.mod_placa.clear()
        self.mod_marca.clear()
        self.mod_modelo.clear()
        self.mod_anio.clear()
        self.mod_clase.clear()
        self.mod_id_propietario.clear()
        
        self.mod_color.setCurrentIndex(-1)
        self.mod_estado.setCurrentIndex(-1)
        
        self.lbl_auditoria.clear()
        self.lbl_auditoria.hide()
        
    def procesar_actualizacion(self):
        """Actualiza los datos del vehículo"""
        
        if not self.mod_placa.text():
            QMessageBox.warning(self, "Acción Inválida", "Primero debe buscar y cargar un vehículo antes de actualizar.")
            return

        vin_objetivo = self.input_buscar_vin.text().strip().upper()
        color = self.mod_color.currentText()
        nuevo_estado = self.mod_estado.currentText()
        
        if not color:
            QMessageBox.warning(self, "Color requerido", "Seleccione un color")
            return
            
        if not nuevo_estado:
            QMessageBox.warning(self, "Estado requerido", "Seleccione un estado legal")
            return
        
        exito, mensaje = GestorVehiculos.actualizar_vehiculo(
            vin_objetivo, color, nuevo_estado, self.usuario_actual.id_usuario
        )
        
        if exito:
            QMessageBox.information(self, "Actualización Exitosa", mensaje)
            self.limpiar_formulario_modificar()
            self.input_buscar_vin.clear()
        else:
            QMessageBox.critical(self, "Error al Actualizar", mensaje)
            
    # ==========================================
    # SEGURIDAD Y PERMISOS
    # ==========================================
    def aplicar_permisos(self):
        """Bloquea elementos según el rol"""
        rol = self.usuario_actual.rol
        
        if rol in [cat.ROLES_USUARIO[2], cat.ROLES_USUARIO[3]]:  # Agente o Supervisor
            self.btn_actualizar.setVisible(False)
            self.btn_cambiar_propietario.setVisible(False)
            self.btn_cambiar_placa.setVisible(False)
            self.lbl_auditoria.setVisible(False)
            
            self.mod_color.setEnabled(False)
            self.mod_estado.setEnabled(False)