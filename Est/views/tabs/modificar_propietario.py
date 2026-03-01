from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
QLineEdit, QPushButton, QComboBox, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

import logic.catalogos as cat
from logic.gestor_propietarios import GestorPropietarios
# Importaremos el Gestor más adelante
# from logic.gestor_propietarios import GestorPropietarios

class TabModificarPropietario(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()
        self.aplicar_permisos() # Activamos los candados de seguridad al nacer

    def configurar_ui(self):
        layout = QVBoxLayout(self)
        
        # ==========================================
        # 1. ZONA DE BÚSQUEDA
        # ==========================================
        layout_busqueda = QHBoxLayout()
        self.input_buscar_curp = QLineEdit()
        self.input_buscar_curp.setPlaceholderText("Ingrese la CURP a buscar...")
        self.input_buscar_curp.setMaxLength(18)
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.procesar_busqueda)

        layout_busqueda.addWidget(QLabel("CURP del Propietario:"))
        layout_busqueda.addWidget(self.input_buscar_curp)
        layout_busqueda.addWidget(btn_buscar)
        
        layout.addLayout(layout_busqueda)

        # ==========================================
        # 2. FORMULARIO DE MODIFICACIÓN
        # ==========================================
        formulario = QFormLayout()
        
        # --- CAMPOS DE SOLO LECTURA (Estructurales) ---
        self.mod_id = QLineEdit()
        self.mod_id.setReadOnly(True)
        self.mod_id.setPlaceholderText("Se llenará automáticamente")
        
        self.mod_nombre = QLineEdit()
        self.mod_nombre.setReadOnly(True)
        
        self.mod_curp = QLineEdit()
        self.mod_curp.setReadOnly(True)

        # --- CAMPOS EDITABLES (Contacto) ---
        self.mod_direccion = QLineEdit()
        
        self.mod_telefono = QLineEdit()
        self.mod_telefono.setMaxLength(10)
        validador_numeros = QRegularExpressionValidator(QRegularExpression(r"^[0-9]+$"))
        self.mod_telefono.setValidator(validador_numeros)
        
        self.mod_correo = QLineEdit()

        # --- CAMPOS EDITABLES (Administrativos) ---
        self.mod_licencia = QComboBox()
        self.mod_licencia.setPlaceholderText("Seleccione un estado...")
        self.mod_licencia.addItems(["Vigente", "Suspendida", "Cancelada / Vencida"])
        self.mod_licencia.setCurrentIndex(-1)
        
        self.mod_estado = QComboBox()
        self.mod_estado.setPlaceholderText("Seleccione un estado...")
        self.mod_estado.addItems(["Activo", "Inactivo"])
        self.mod_estado.setCurrentIndex(-1)

        # --- ENSAMBLAJE DEL FORMULARIO ---
        formulario.addRow("ID Interno:", self.mod_id)
        formulario.addRow("Nombre Completo:", self.mod_nombre)
        formulario.addRow("CURP:", self.mod_curp)
        
        formulario.addRow("Dirección:", self.mod_direccion)
        formulario.addRow("Teléfono:", self.mod_telefono)
        formulario.addRow("Correo Electrónico:", self.mod_correo)
        formulario.addRow("Estado de Licencia:", self.mod_licencia)
        formulario.addRow("Estado en Sistema:", self.mod_estado)
        
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
    # SEGURIDAD Y PERMISOS (RBAC)
    # ==========================================
    def aplicar_permisos(self):
        """Bloquea los elementos editables si el usuario es Agente o Supervisor."""
        rol = self.usuario_actual.rol
        
        
        if rol not in ["Administrador", "Supervisor"]:
            self.lbl_auditoria.setVisible(False)
        
        # Agente de Tránsito [2] o Supervisor [3]
        if rol in [cat.ROLES_USUARIO[2], cat.ROLES_USUARIO[3]]:
            self.btn_actualizar.setVisible(False)
            
            # Bloqueamos físicamente los campos para que sean de solo lectura
            self.mod_direccion.setReadOnly(True)
            self.mod_telefono.setReadOnly(True)
            self.mod_correo.setReadOnly(True)
            
            # Apagamos los combos
            self.mod_licencia.setEnabled(False)
            self.mod_estado.setEnabled(False)

    # ==========================================
    # LÓGICA DE INTERFAZ
    # ==========================================
    def procesar_busqueda(self):
        curp_buscada = self.input_buscar_curp.text().strip().upper()
        
        if not curp_buscada:
            QMessageBox.warning(self, "Atención", "Por favor, ingrese una CURP para buscar.")
            return
            
        exito, resultado = GestorPropietarios.buscar_propietario_por_curp(curp_buscada)
        
        if exito:
            id_real = resultado["id_propietario"]
            self.mod_id.setText(f"PRP-{id_real:05d}")
            self.mod_nombre.setText(resultado["nombre_completo"])
            self.mod_curp.setText(resultado["curp"])
            self.mod_direccion.setText(resultado["direccion"])
            self.mod_telefono.setText(resultado["telefono"])
            self.mod_correo.setText(resultado["correo"])
            
            self.mod_licencia.setCurrentText(resultado["estado_licencia"])
            self.mod_estado.setCurrentText(resultado["estado"])
            
            # MOSTRAR AUDITORÍA
            creador = resultado["creador"]
            modificador = resultado["modificador"]
            self.lbl_auditoria.setText(f"Registro original por: {creador} | Última modificación por: {modificador}")
            self.lbl_auditoria.show()
            
            QMessageBox.information(self, "Propietario Encontrado", "Datos cargados correctamente.")
        else:
            self.limpiar_formulario()
            self.lbl_auditoria.hide()
            QMessageBox.critical(self, "No encontrado", "No existe un propietario con esa CURP.")

    def limpiar_formulario(self):
        """Vacía las cajas de texto."""
        self.mod_id.clear()
        self.mod_nombre.clear()
        self.mod_curp.clear()
        self.mod_direccion.clear()
        self.mod_telefono.clear()
        self.mod_correo.clear()
        
        self.mod_licencia.setCurrentIndex(-1)
        self.mod_estado.setCurrentIndex(-1)
        
        self.lbl_auditoria.clear()
        self.lbl_auditoria.hide()

    def procesar_actualizacion(self):
        if not self.mod_curp.text():
            QMessageBox.warning(self, "Acción Inválida", "Primero debe buscar un propietario.")
            return

        # Extraemos los datos editables
        direccion = self.mod_direccion.text().strip().upper()
        telefono = self.mod_telefono.text().strip()
        correo = self.mod_correo.text().strip().lower()
        licencia = self.mod_licencia.currentText()
        estado = self.mod_estado.currentText()
        
        # Extraemos el ID numérico que el backend exige
        texto_id = self.mod_id.text().replace("PRP-", "")
        id_objetivo = int(texto_id)

        # Validaciones básicas antes de enviar
        if not direccion or not telefono:
            QMessageBox.warning(self, "Campos Vacíos", "La dirección y el teléfono no pueden quedar vacíos.")
            return

        exito, mensaje = GestorPropietarios.modificar_propietario(
            id_objetivo, direccion, telefono, correo, licencia, estado,
            self.usuario_actual.id_usuario
        )
        
        # Retroalimentación visual según el resultado
        if exito:
            QMessageBox.information(self, "Actualización Exitosa", mensaje)
            self.limpiar_formulario()
            self.input_buscar_curp.clear()
        else:
            # Si falla (ej. intentar inactivar a alguien con vehículos activos o error de BD)
            QMessageBox.critical(self, "Error al Actualizar", mensaje)

