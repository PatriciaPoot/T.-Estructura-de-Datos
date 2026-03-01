from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
QLineEdit, QPushButton, QComboBox, QFormLayout, 
QMessageBox, QSpinBox)
from PySide6.QtCore import Qt
import re  # <-- AÑADIR ESTA IMPORTACIÓN

# Importaciones del backend
import logic.catalogos as cat
from models.vehiculo import Vehiculo
from logic.gestor_vehiculos import GestorVehiculos

class TabRegistrarVehiculo(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()

    def configurar_ui(self):
        """Construye el formulario con selección de marcas y modelos"""
        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        
        # 1. Entradas de texto restringidas
        self.input_vin = QLineEdit()
        self.input_vin.setMaxLength(17) 
        self.input_vin.setPlaceholderText("Ej: 3G1SE516X3S205891")
        
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Ej: YYU-021-A")
        
        self.input_id_propietario = QLineEdit()
        self.input_id_propietario.setPlaceholderText("ID numérico del propietario (Ej: 3 o PRP-00003)")  # <-- MEJORADO
        
        self.input_anio = QSpinBox()
        self.input_anio.setRange(1899, 2030)
        self.input_anio.setSpecialValueText(" ")
        self.input_anio.setValue(1899)
        self.input_anio.setButtonSymbols(QSpinBox.PlusMinus)
        
        # ==========================================
        # MARCA (SOLO SELECCIONAR)
        # ==========================================
        self.combo_marca = QComboBox()
        self.combo_marca.setEditable(False)
        self.combo_marca.addItems(sorted(list(cat.MARCAS_MODELOS_VEHICULO.keys())))
        self.combo_marca.setCurrentIndex(-1)
        self.combo_marca.currentIndexChanged.connect(self.cargar_modelos)
        
        # ==========================================
        # MODELO (SOLO SELECCIONAR)
        # ==========================================
        self.combo_modelo = QComboBox()
        self.combo_modelo.setEditable(False)
        self.combo_modelo.setEnabled(False)
        self.combo_modelo.setCurrentIndex(-1)
        self.combo_modelo.currentIndexChanged.connect(self.actualizar_clases)
        
        # ==========================================
        # CLASE (SE LLENA AUTOMÁTICAMENTE)
        # ==========================================
        self.combo_clase = QComboBox()
        self.combo_clase.setEditable(False)
        self.combo_clase.setEnabled(False)
        self.combo_clase.setCurrentIndex(-1)
        
        # ==========================================
        # OTROS CAMPOS
        # ==========================================
        
        # Color
        self.combo_color = QComboBox()
        self.combo_color.setEditable(False)
        self.combo_color.addItems(cat.COLORES_VEHICULO)
        self.combo_color.setCurrentIndex(-1)
        
        # Estado legal
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(cat.ESTADOS_VEHICULO)
        self.combo_estado.setCurrentIndex(-1)
        
        # Procedencia
        self.combo_procedencia = QComboBox()
        self.combo_procedencia.addItems(cat.PROCEDENCIAS_VEHICULO)
        self.combo_procedencia.setCurrentIndex(-1)
        
        # ==========================================
        # ENSAMBLAJE DEL FORMULARIO
        # ==========================================
        formulario.addRow("VIN (17 caracteres):", self.input_vin)
        formulario.addRow("Placa:", self.input_placa)
        formulario.addRow("Marca:", self.combo_marca)
        formulario.addRow("Modelo:", self.combo_modelo)
        formulario.addRow("Año:", self.input_anio)
        formulario.addRow("Color:", self.combo_color)
        formulario.addRow("Clase:", self.combo_clase)
        formulario.addRow("Estado Legal:", self.combo_estado)
        formulario.addRow("Procedencia:", self.combo_procedencia)
        formulario.addRow("ID Propietario:", self.input_id_propietario)

        layout.addLayout(formulario)

        # Botón de Guardado
        self.btn_guardar = QPushButton("Guardar Vehículo")
        self.btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_guardar.clicked.connect(self.procesar_registro)
        layout.addWidget(self.btn_guardar, alignment=Qt.AlignRight)
        
    # ==========================================
    # MÉTODOS
    # ==========================================
    
    def cargar_modelos(self, index):
        """Carga los modelos de la marca seleccionada"""
        if index >= 0:
            marca = self.combo_marca.currentText()
            if marca in cat.MARCAS_MODELOS_VEHICULO:
                modelos = list(cat.MARCAS_MODELOS_VEHICULO[marca].keys())
                self.combo_modelo.clear()
                self.combo_modelo.addItems(sorted(modelos))
                self.combo_modelo.setEnabled(True)
                self.combo_modelo.setCurrentIndex(-1)
                self.combo_clase.clear()
                self.combo_clase.setEnabled(False)
                self.combo_clase.setCurrentIndex(-1)
        else:
            self.combo_modelo.setEnabled(False)
            self.combo_modelo.clear()
            self.combo_clase.setEnabled(False)
            self.combo_clase.clear()
    
    def actualizar_clases(self, index):
        """Actualiza las clases disponibles según el modelo seleccionado"""
        if index >= 0:
            marca = self.combo_marca.currentText()
            modelo = self.combo_modelo.currentText()
            
            if marca in cat.MARCAS_MODELOS_VEHICULO and modelo in cat.MARCAS_MODELOS_VEHICULO[marca]:
                clases = cat.MARCAS_MODELOS_VEHICULO[marca][modelo]
                self.combo_clase.clear()
                self.combo_clase.addItems(clases)
                self.combo_clase.setEnabled(True)
                
                # Si solo hay una clase, seleccionarla automáticamente
                if len(clases) == 1:
                    self.combo_clase.setCurrentIndex(0)
                else:
                    self.combo_clase.setCurrentIndex(-1)
        else:
            self.combo_clase.setEnabled(False)
            self.combo_clase.clear()
    
    def procesar_registro(self):
        """Extrae los datos de la interfaz y los envía al backend"""
        vin = self.input_vin.text().strip().upper()
        placa = self.input_placa.text().strip().upper()
        marca = self.combo_marca.currentText()
        modelo = self.combo_modelo.currentText()
        anio = self.input_anio.value()
        color = self.combo_color.currentText()
        clase = self.combo_clase.currentText()
        estado = self.combo_estado.currentText()
        procedencia = self.combo_procedencia.currentText()
        id_propietario_str = self.input_id_propietario.text().strip()

        # ===== NUEVA VALIDACIÓN: Extraer solo el número del ID =====
        # Si el usuario ingresó "PRP-00003", extraemos "00003"
        if id_propietario_str.startswith("PRP-"):
            id_propietario_str = id_propietario_str.replace("PRP-", "")
        
        # Eliminar ceros a la izquierda (opcional, pero útil)
        # "00003" -> "3"
        id_propietario_str = id_propietario_str.lstrip('0')
        if id_propietario_str == "":
            id_propietario_str = "0"

        # Validaciones
        if not vin or len(vin) != 17:
            QMessageBox.warning(self, "Error", "El VIN debe tener 17 caracteres")
            return
            
        if not placa:
            QMessageBox.warning(self, "Error", "La placa es obligatoria")
            return
            
        if not marca:
            QMessageBox.warning(self, "Error", "Seleccione una marca")
            return
            
        if not modelo:
            QMessageBox.warning(self, "Error", "Seleccione un modelo")
            return
            
        if not color:
            QMessageBox.warning(self, "Error", "Seleccione un color")
            return
            
        if not clase:
            QMessageBox.warning(self, "Error", "Seleccione una clase")
            return
            
        if not estado:
            QMessageBox.warning(self, "Error", "Seleccione un estado legal")
            return
            
        if not procedencia:
            QMessageBox.warning(self, "Error", "Seleccione una procedencia")
            return
            
        if not id_propietario_str:
            QMessageBox.warning(self, "Error", "Ingrese el ID del propietario")
            return

        try:
            id_propietario = int(id_propietario_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "El ID del propietario debe ser un número (Ej: 3 o PRP-00003)")
            return

        # Validar que la clase sea válida para el modelo
        if marca in cat.MARCAS_MODELOS_VEHICULO and modelo in cat.MARCAS_MODELOS_VEHICULO[marca]:
            clases_permitidas = cat.MARCAS_MODELOS_VEHICULO[marca][modelo]
            if clase not in clases_permitidas:
                QMessageBox.warning(self, "Error", 
                                   f"El modelo {modelo} no puede ser '{clase}'\n"
                                   f"Clases permitidas: {', '.join(clases_permitidas)}")
                return

        # Crear y guardar vehículo
        nuevo_vehiculo = Vehiculo(
            vin=vin, placa=placa, marca=marca, modelo=modelo, anio=anio, 
            color=color, clase=clase, estado_legal=estado, 
            procedencia=procedencia, id_propietario=id_propietario,
            id_usuario_registro=self.usuario_actual.id_usuario
        )

        exito, mensaje = GestorVehiculos.registrar_vehiculo(nuevo_vehiculo)

        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
            self.limpiar_formulario() 
        else:
            QMessageBox.critical(self, "Error", mensaje)

    def limpiar_formulario(self):
        """Limpia el formulario después de un registro exitoso"""
        self.input_vin.clear()
        self.input_placa.clear()
        self.input_id_propietario.clear()
        self.input_anio.setValue(1899)
        self.combo_marca.setCurrentIndex(-1)
        self.combo_modelo.clear()
        self.combo_modelo.setEnabled(False)
        self.combo_color.setCurrentIndex(-1)
        self.combo_clase.clear()
        self.combo_clase.setEnabled(False)
        self.combo_estado.setCurrentIndex(-1)
        self.combo_procedencia.setCurrentIndex(-1)
