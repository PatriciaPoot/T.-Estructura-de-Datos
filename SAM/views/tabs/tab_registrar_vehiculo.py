from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
QLineEdit, QPushButton, QComboBox, QFormLayout, 
QMessageBox, QSpinBox)
from PySide6.QtCore import Qt

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
        """Construye el formulario garantizando la integridad de los datos mediante catálogos cerrados."""
        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        
        # 1. Entradas de texto restringidas
        self.input_vin = QLineEdit()
        self.input_vin.setMaxLength(17) 
        self.input_vin.setPlaceholderText("Ej: 3G1SE516X3S205891")
        
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Ej: YYU-021-A")
        
        self.input_id_propietario = QLineEdit()
        self.input_id_propietario.setPlaceholderText("ID numérico del propietario")
        
        self.input_anio = QSpinBox()
        self.input_anio.setRange(1899, 2030)
        self.input_anio.setSpecialValueText(" ")
        self.input_anio.setValue(1899)
        self.input_anio.setButtonSymbols(QSpinBox.PlusMinus)
        
        # 2. Listas Desplegables (QComboBox) conectadas a catalogos.py
        self.combo_marca = QComboBox()
        self.combo_marca.addItems(cat.MARCAS_MODELOS_VEHICULO.keys())    
        self.combo_marca.setCurrentIndex(-1) 
        
        self.combo_modelo = QComboBox()
        self.combo_modelo.setCurrentIndex(-1) 
        
        self.combo_color = QComboBox()
        self.combo_color.addItems(cat.COLORES_VEHICULO)
        self.combo_color.setCurrentIndex(-1) 
        
        self.combo_clase = QComboBox()
        self.combo_clase.setCurrentIndex(-1) 
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(cat.ESTADOS_VEHICULO)
        self.combo_estado.setCurrentIndex(-1)
        
        self.combo_procedencia = QComboBox()  # <--- ESTABA FALTANDO ESTA LÍNEA
        self.combo_procedencia.addItems(cat.PROCEDENCIAS_VEHICULO)
        self.combo_procedencia.setCurrentIndex(-1)
        
        # 3. CONEXIÓN DINÁMICA (Cascada Doble)
        self.combo_marca.currentTextChanged.connect(self.actualizar_modelos)
        self.combo_modelo.currentTextChanged.connect(self.actualizar_clases)
        
        # 4. Ensamblaje del Formulario
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
    # MÉTODOS LÓGICOS
    # ==========================================

    def actualizar_modelos(self, marca_seleccionada):
        """Primera cascada: Llena los modelos basados en la marca."""
        self.combo_modelo.clear() 
        if marca_seleccionada in cat.MARCAS_MODELOS_VEHICULO:
            modelos_permitidos = list(cat.MARCAS_MODELOS_VEHICULO[marca_seleccionada].keys())
            self.combo_modelo.addItems(modelos_permitidos)
    
    def actualizar_clases(self, modelo_seleccionado):
        """Segunda cascada: Llena las clases y bloquea el campo si solo hay una opción."""
        self.combo_clase.clear()
        marca_actual = self.combo_marca.currentText()
        
        if marca_actual in cat.MARCAS_MODELOS_VEHICULO and modelo_seleccionado in cat.MARCAS_MODELOS_VEHICULO[marca_actual]:
            clases_permitidas = cat.MARCAS_MODELOS_VEHICULO[marca_actual][modelo_seleccionado]
            self.combo_clase.addItems(clases_permitidas)
            
            if len(clases_permitidas) == 1:
                self.combo_clase.setEnabled(False) 
            else:
                self.combo_clase.setEnabled(True) 
    
    def procesar_registro(self):
        """Extrae los datos de la interfaz, los empaqueta y los envía al backend."""
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

        if not vin or not placa or not id_propietario_str:
            QMessageBox.warning(self, "Campos Incompletos", "Por favor, llene el VIN, Placa y el ID del Propietario.")
            return

        try:
            id_propietario = int(id_propietario_str)
        except ValueError:
            QMessageBox.warning(self, "Error de Formato", "El ID del propietario debe ser un número entero válido.")
            return

        nuevo_vehiculo = Vehiculo(
            vin=vin, placa=placa, marca=marca, modelo=modelo, anio=anio, 
            color=color, clase=clase, estado_legal=estado, 
            procedencia=procedencia, id_propietario=id_propietario,
            id_usuario_registro=self.usuario_actual.id_usuario
        )

        exito, mensaje = GestorVehiculos.registrar_vehiculo(nuevo_vehiculo)

        if exito:
            QMessageBox.information(self, "Registro Exitoso", mensaje)
            self.limpiar_formulario() 
        else:
            QMessageBox.critical(self, "Error al Guardar", mensaje)

    def limpiar_formulario(self):
        """Limpia las cajas de texto después de un guardado exitoso."""
        self.input_vin.clear()
        self.input_placa.clear()
        self.input_id_propietario.clear()
        self.input_anio.setValue(2024) 
        self.combo_marca.setCurrentIndex(0)