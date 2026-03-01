from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
QLineEdit, QPushButton, QComboBox, QMessageBox)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

# Importamos el backend real
from models.propietario import Propietario
from logic.gestor_propietarios import GestorPropietarios
class TabRegistrarPropietario(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()

    def configurar_ui(self):
        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        
        # ==========================================
        # CAMPOS DE TEXTO CON VALIDACIONES FRONTEND
        # ==========================================
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre completo (Ej. Juan Pérez Gómez)")
        
        self.input_curp = QLineEdit()
        self.input_curp.setMaxLength(18) # Especificación: Máximo 18 caracteres
        self.input_curp.setPlaceholderText("18 caracteres alfanuméricos")
        
        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Calle, Número, Colonia, C.P.")
        
        self.input_telefono = QLineEdit()
        self.input_telefono.setMaxLength(10)
        self.input_telefono.setPlaceholderText("10 dígitos numéricos")
        # Frontend Defensivo: Forzamos a que SOLO se puedan escribir números
        validador_numeros = QRegularExpressionValidator(QRegularExpression(r"^[0-9]+$"))
        self.input_telefono.setValidator(validador_numeros)
        
        self.input_correo = QLineEdit()
        self.input_correo.setPlaceholderText("ejemplo@correo.com")
        
        # ==========================================
        # MENÚS DESPLEGABLES (Catálogos)
        # ==========================================
        self.combo_licencia = QComboBox()
        # Especificación: Vigente, Suspendida, Cancelada / Vencida
        self.combo_licencia.addItems(["Vigente", "Suspendida", "Cancelada / Vencida"])
        
        # Nota: El Estado del propietario (Activo/Inactivo) no lo ponemos aquí.
        # Por regla de negocio, un propietario nuevo nace siendo "Activo" por defecto.

        # Ensamblamos el formulario
        formulario.addRow("Nombre Completo:", self.input_nombre)
        formulario.addRow("CURP:", self.input_curp)
        formulario.addRow("Dirección:", self.input_direccion)
        formulario.addRow("Teléfono (10 dígitos):", self.input_telefono)
        formulario.addRow("Correo Electrónico:", self.input_correo)
        formulario.addRow("Estado de Licencia:", self.combo_licencia)
        
        layout.addLayout(formulario)

        # Botón de guardado
        self.btn_guardar = QPushButton("Registrar Propietario")
        self.btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_guardar.clicked.connect(self.procesar_registro)
        
        layout.addStretch()
        layout.addWidget(self.btn_guardar, alignment=Qt.AlignRight)

    # ==========================================
    # LÓGICA DE INTERFAZ
    # ==========================================
    def procesar_registro(self):
        """Valida que los campos no estén vacíos y tengan el formato correcto antes de enviar."""
        
        nombre = self.input_nombre.text().strip().upper()
        curp = self.input_curp.text().strip().upper() # Siempre en mayúsculas
        direccion = self.input_direccion.text().strip().upper()
        telefono = self.input_telefono.text().strip()
        correo = self.input_correo.text().strip().lower() # Siempre en minúsculas
        licencia = self.combo_licencia.currentText()

        # 1. Validación de campos vacíos
        if not nombre or not curp or not direccion or not telefono:
            QMessageBox.warning(self, "Campos Incompletos", "Por favor llene todos los campos obligatorios.")
            return

        # 2. Validación de longitud de CURP
        if len(curp) != 18:
            QMessageBox.warning(self, "CURP Inválida", "La CURP debe tener exactamente 18 caracteres.")
            return

        # 3. Validación básica de correo (que tenga un @ y un punto)
        if correo and ("@" not in correo or "." not in correo):
            QMessageBox.warning(self, "Correo Inválido", "Por favor ingrese un correo electrónico válido.")
            return

        # 4. Empaquetado y envío al backend
        nuevo_propietario = Propietario(
            nombre_completo=nombre, 
            curp=curp, 
            direccion=direccion,
            telefono=telefono, 
            correo_electronico=correo, 
            estado_licencia=licencia,
            estado="Activo",
            id_usuario_registro=self.usuario_actual.id_usuario
        )
        
        # Llamamos al gestor
        exito, mensaje = GestorPropietarios.registrar_propietario(nuevo_propietario)
        
        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
            self.limpiar_formulario()
        else:
            # Si la CURP se repite o falla algo, el gestor nos mandará el mensaje de error [cite: 140, 437-440]
            QMessageBox.critical(self, "Error al Guardar", mensaje)

    def limpiar_formulario(self):
        self.input_nombre.clear()
        self.input_curp.clear()
        self.input_direccion.clear()
        self.input_telefono.clear()
        self.input_correo.clear()
        self.combo_licencia.setCurrentIndex(0)