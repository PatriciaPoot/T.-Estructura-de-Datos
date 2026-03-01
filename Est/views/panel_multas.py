from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
QLineEdit, QPushButton, QComboBox, QTabWidget, 
QFormLayout, QDoubleSpinBox, QDateEdit, QTimeEdit, QMessageBox,
QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PySide6.QtCore import Qt, QDate, QTime
import logic.catalogos as cat

#Importaciones backend
from models.infraccion import Infraccion
from logic.gestor_infracciones import GestorInfracciones
from logic.gestor_agentes import GestorAgentes
from logic.gestor_vehiculos import GestorVehiculos

class PanelMultas(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()
        self.aplicar_permisos()

    def configurar_ui(self):
        """
        Configura la estructura principal del panel, dividiéndolo en pestañas
        para separar el registro de nuevas multas y el cobro/cancelación de las existentes.
        """
        layout_principal = QVBoxLayout(self)
        
        lbl_titulo = QLabel("Módulo de Infracciones de Tránsito")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        self.pestanas = QTabWidget()
        
        self.tab_registrar = QWidget()
        self.tab_gestionar = QWidget()
        
        self.construir_tab_registrar()
        self.construir_tab_gestionar()

        # --- APLICACIÓN DE ROLES (RBAC) ---
        rol = self.usuario_actual.rol
        
        if rol == cat.ROLES_USUARIO[0]: # Administrador
            self.pestanas.addTab(self.tab_registrar, "Registrar Infracción")
            self.pestanas.addTab(self.tab_gestionar, "Cobro y Cancelación")
            
        elif rol == cat.ROLES_USUARIO[2]: # Agente de Tránsito
            self.pestanas.addTab(self.tab_registrar, "Registrar Infracción")
            
        elif rol == cat.ROLES_USUARIO[3]: # Supervisor
            self.pestanas.addTab(self.tab_gestionar, "Consultar Infracción")

        layout_principal.addWidget(self.pestanas)

    # ==========================================
    # PESTAÑA 1: REGISTRAR INFRACCIÓN
    # ==========================================
    def construir_tab_registrar(self):
        layout = QVBoxLayout(self.tab_registrar)
        formulario = QFormLayout()
        
        # 1. VIN Infractor
        self.input_vin = QLineEdit()
        self.input_vin.setPlaceholderText("Ingrese VIN o Placa del infractor")
        
        # ===== ComboBox de agentes CON BOTÓN REFRESCAR =====
        layout_agente = QHBoxLayout()
        
        self.combo_agentes = QComboBox()
        self.combo_agentes.addItem("Seleccione al agente que levantó la multa...", None)
        self.combo_agentes.setMinimumHeight(35)
        self.combo_agentes.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e2e;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
        """)
        
        # Botón de refrescar
        self.btn_refrescar_agentes = QPushButton("↻")
        self.btn_refrescar_agentes.setToolTip("Refrescar lista de agentes")
        self.btn_refrescar_agentes.setMaximumWidth(40)
        self.btn_refrescar_agentes.setMinimumHeight(35)
        self.btn_refrescar_agentes.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self.btn_refrescar_agentes.clicked.connect(self.refrescar_agentes)
        
        layout_agente.addWidget(self.combo_agentes, stretch=4)
        layout_agente.addWidget(self.btn_refrescar_agentes, stretch=1)
        
        # Cargar agentes inicialmente
        self.cargar_agentes()
        
        # 3. Fecha del hecho
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())
        
        # 4. Hora del hecho
        self.input_hora = QTimeEdit()
        self.input_hora.setTime(QTime.currentTime())

        # 5. Lugar
        self.input_lugar = QLineEdit()
        
        # 6. Motivo (solo lectura)
        self.input_motivo = QLineEdit()
        self.input_motivo.setReadOnly(True) 
        self.input_motivo.setStyleSheet("background-color: #2c3e50; color: #bdc3c7; font-weight: bold;") 
        
        # 7. Tipo de Infracción
        self.combo_tipo = QComboBox()
        for clave, datos in cat.TABULADOR_INFRACCIONES.items():
            self.combo_tipo.addItem(datos["descripcion"], clave)

        # 8. Rango de monto (label informativo)
        self.lbl_rango_monto = QLabel("Rango permitido: $0.00 - $0.00")
        self.lbl_rango_monto.setStyleSheet("color: #e67e22; font-style: italic; font-weight: bold;")

        # 9. Monto de la multa
        self.input_monto = QDoubleSpinBox()
        self.input_monto.setRange(1.0, 999999.99)
        self.input_monto.setPrefix("$ ")
        self.input_monto.setDecimals(2)

        # 10. Método de Captura
        self.combo_captura = QComboBox()
        self.combo_captura.addItems(cat.TIPOS_CAPTURA_INFRACCION)
        
        # 11. Licencia Conductor
        self.input_licencia = QLineEdit()
        self.input_licencia.setPlaceholderText("Opcional (Obligatorio en sitio)")

        # ===== AGREGAR CAMPOS AL FORMULARIO EN ORDEN =====
        formulario.addRow("VIN Infractor:", self.input_vin)
        formulario.addRow("Agente de Tránsito:", layout_agente)
        formulario.addRow("Fecha del hecho:", self.input_fecha)
        formulario.addRow("Hora del hecho:", self.input_hora)
        formulario.addRow("Lugar:", self.input_lugar)
        formulario.addRow("Tipo de Infracción:", self.combo_tipo)
        formulario.addRow("", self.lbl_rango_monto)
        formulario.addRow("Motivo:", self.input_motivo)
        formulario.addRow("Monto de la multa:", self.input_monto)
        formulario.addRow("Método de Captura:", self.combo_captura)
        formulario.addRow("Licencia Conductor:", self.input_licencia)

        layout.addLayout(formulario)

        # Botón Emitir Infracción
        self.btn_registrar = QPushButton("Emitir Infracción")
        self.btn_registrar.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 10px;")
        self.btn_registrar.clicked.connect(self.procesar_registro)
        
        layout.addWidget(self.btn_registrar, alignment=Qt.AlignRight)

        # Conectar señal para actualizar información de la multa
        self.combo_tipo.currentIndexChanged.connect(self.actualizar_info_multa)
        self.actualizar_info_multa()

    # ==========================================
    # FUNCIONES PARA REFRESCAR AGENTES (SIN PRINTS)
    # ==========================================
    def cargar_agentes(self):
        """Carga la lista de agentes en el ComboBox"""
        self.combo_agentes.clear()
        self.combo_agentes.addItem("Seleccione al agente que levantó la multa...", None)
        
        exito, lista_agentes = GestorAgentes.obtener_agentes_para_combo()
        if exito and lista_agentes:
            for id_agente, placa, nombre in lista_agentes:
                self.combo_agentes.addItem(f"{placa} - {nombre}", id_agente)
        else:
            self.combo_agentes.addItem("⚠️ No hay agentes activos", None)

    def refrescar_agentes(self):
        """Recarga la lista de agentes al hacer clic en el botón"""
        self.cargar_agentes()
        QMessageBox.information(self, "Actualizado", "Lista de agentes actualizada correctamente.")

    # ==========================================
    # EVENTO QUE SE ACTIVA AL MOSTRAR EL PANEL
    # ==========================================
    def showEvent(self, event):
        """Este método se ejecuta CADA VEZ que el panel se hace visible"""
        super().showEvent(event)
        self.cargar_agentes()  # Recargar agentes automáticamente

    def actualizar_info_multa(self):
        clave_seleccionada = self.combo_tipo.currentData()
        
        if clave_seleccionada in cat.TABULADOR_INFRACCIONES:
            datos = cat.TABULADOR_INFRACCIONES[clave_seleccionada]
            
            minimo = datos["multa"]["min"]
            maximo = datos["multa"]["max"]
            self.lbl_rango_monto.setText(f"Rango permitido: ${minimo:,.2f} - ${maximo:,.2f} MXN")
            
            motivo_legal = f"{datos['articulo']} - {datos['descripcion']}"
            self.input_motivo.setText(motivo_legal)
            
            self.input_monto.setValue(minimo)

    # ==========================================
    # PESTAÑA 2: GESTIONAR ESTADO (COBROS)
    # ==========================================
    def construir_tab_gestionar(self):
        layout = QVBoxLayout(self.tab_gestionar)
        
        # ==========================================
        # 1. ZONA PRINCIPAL: COBRO DIRECTO POR FOLIO
        # ==========================================
        lbl_accion = QLabel(" Acción Rápida: Cobro o Cancelación")
        lbl_accion.setStyleSheet("font-weight: bold; color: #cdd6f4; font-size: 16px;")
        layout.addWidget(lbl_accion)

        layout_accion = QHBoxLayout()
        
        # Input del Folio
        self.input_buscar_folio = QLineEdit()
        self.input_buscar_folio.setPlaceholderText("Ingrese el Folio de la Infracción (Ej. FOL-A1B2C3)")
        self.input_buscar_folio.setStyleSheet("font-weight: bold; color: #f9e2af; font-size: 14px;") 
        self.input_buscar_folio.setMinimumHeight(35)
        
        # Combo de Estado
        self.combo_nuevo_estado = QComboBox()
        self.combo_nuevo_estado.addItems(["Pagada", "Cancelada"]) 
        self.combo_nuevo_estado.setMinimumHeight(35)

        # Botón de Aplicar
        self.btn_actualizar_estado = QPushButton("Aplicar Cambio")
        self.btn_actualizar_estado.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 0px 20px;")
        self.btn_actualizar_estado.setMinimumHeight(35)
        self.btn_actualizar_estado.clicked.connect(self.procesar_cambio_estado)

        layout_accion.addWidget(QLabel("Folio:"))
        layout_accion.addWidget(self.input_buscar_folio, stretch=2)
        layout_accion.addWidget(QLabel("Pasar a estado:"))
        layout_accion.addWidget(self.combo_nuevo_estado, stretch=1)
        layout_accion.addWidget(self.btn_actualizar_estado)
        
        layout.addLayout(layout_accion)

        # ==========================================
        # LÍNEA SEPARADORA
        # ==========================================
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: #45475a; margin: 20px 0px;")
        layout.addWidget(linea)

        # ==========================================
        # 2. ZONA SECUNDARIA: BÚSQUEDA POR PLACA (RESCATE)
        # ==========================================
        lbl_ayuda = QLabel(" ¿El ciudadano perdió la boleta? Busque por vehículo:")
        lbl_ayuda.setStyleSheet("font-weight: bold; color: #a6adc8;")
        layout.addWidget(lbl_ayuda)

        layout_busqueda_placa = QHBoxLayout()
        self.input_buscar_placa = QLineEdit()
        self.input_buscar_placa.setPlaceholderText("Ingrese Placa o VIN del vehículo...")
        self.input_buscar_placa.setMinimumHeight(35)
        
        btn_buscar_placa = QPushButton("Buscar Multas")
        btn_buscar_placa.setStyleSheet("background-color: #45475a; color: white;")
        btn_buscar_placa.setMinimumHeight(35)
        btn_buscar_placa.clicked.connect(self.buscar_multas_por_placa)
        
        layout_busqueda_placa.addWidget(self.input_buscar_placa)
        layout_busqueda_placa.addWidget(btn_buscar_placa)
        layout.addLayout(layout_busqueda_placa)

        # TABLA DE RESULTADOS
        self.tabla_multas = QTableWidget()
        self.tabla_multas.setColumnCount(5)
        self.tabla_multas.setHorizontalHeaderLabels(["Folio", "Fecha", "Infracción", "Monto", "Estado"])
        self.tabla_multas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_multas.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_multas.setEditTriggers(QTableWidget.NoEditTriggers) 
        
        # EVENTO CLAVE: Autocompletar el folio al hacer clic
        self.tabla_multas.itemClicked.connect(self.seleccionar_folio_de_tabla)
        layout.addWidget(self.tabla_multas)
        
    def aplicar_permisos(self):
        rol = self.usuario_actual.rol
        if rol == cat.ROLES_USUARIO[3]: 
            self.btn_actualizar_estado.setVisible(False)
            self.combo_nuevo_estado.setEnabled(False)
            
    # ==========================================
    # LÓGICA DE INTERFAZ Y BACKEND
    # ==========================================
    def procesar_registro(self):
        criterio_vehiculo = self.input_vin.text().strip().upper()
        lugar = self.input_lugar.text().strip().upper()
        motivo = self.input_motivo.text().strip().upper()
        tipo_texto = self.combo_tipo.currentText() 
        clave_infraccion = self.combo_tipo.currentData() 
        tipo_captura = self.combo_captura.currentText()
        monto = self.input_monto.value()
        licencia = self.input_licencia.text().strip().upper()
        fecha = self.input_fecha.date().toString("yyyy-MM-dd")
        hora = self.input_hora.time().toString("HH:mm")
        id_agente = self.combo_agentes.currentData()

        if not criterio_vehiculo or not lugar or not motivo:
            QMessageBox.warning(self, "Campos Incompletos", "Por favor llene todos los campos obligatorios.")
            return

        if len(lugar) < 5: 
            QMessageBox.warning(self, "Detalles Insuficientes", "El 'Lugar' debe ser más descriptivo (mínimo 5 caracteres).")
            return
            
        if not id_agente:
            QMessageBox.warning(self, "Agente no seleccionado", "Por favor, seleccione al Agente de Tránsito que levantó la boleta.")
            return

        exito_vehiculo, datos_vehiculo = GestorVehiculos.buscar_vehiculo_universal(criterio_vehiculo)
        
        if not exito_vehiculo:
            QMessageBox.warning(self, "Vehículo No Encontrado", "No existe ningún vehículo registrado con esa Placa o VIN.")
            return
            
        vin_real = datos_vehiculo["vin"] 

        if clave_infraccion in cat.TABULADOR_INFRACCIONES:
            datos_oficiales = cat.TABULADOR_INFRACCIONES[clave_infraccion]
            min_permitido = datos_oficiales["multa"]["min"]
            max_permitido = datos_oficiales["multa"]["max"]
            
            if monto < min_permitido or monto > max_permitido:
                QMessageBox.critical(self, "Monto Ilegal", 
                    f"El monto de ${monto:,.2f} está fuera de la ley.\n"
                    f"Para esta infracción el reglamento exige cobrar entre ${min_permitido:,.2f} y ${max_permitido:,.2f}."
                )
                return

        nueva_infraccion = Infraccion(
            vin_infractor=vin_real, id_agente=id_agente, fecha=fecha, hora=hora,
            lugar=lugar, tipo_infraccion=tipo_texto, motivo=motivo,
            monto=monto, licencia_conductor=licencia,
            id_usuario_registro=self.usuario_actual.id_usuario
        )

        exito, msj = GestorInfracciones.registrar_infraccion(nueva_infraccion, tipo_captura)

        if exito:
            QMessageBox.information(self, "Éxito", msj)
            self.limpiar_formulario_registro()
        else:
            QMessageBox.critical(self, "Error al Registrar", msj)

    def buscar_multas_por_placa(self):
        """Busca las multas en SQLite y las dibuja en la tabla."""
        criterio = self.input_buscar_placa.text().strip().upper()
        if not criterio:
            QMessageBox.warning(self, "Atención", "Ingrese una placa o VIN para buscar.")
            return
            
        exito, lista_multas = GestorInfracciones.obtener_infracciones_por_vehiculo(criterio)
        
        self.tabla_multas.setRowCount(0) 
        
        if exito and lista_multas:
            for fila, multa in enumerate(lista_multas):
                self.tabla_multas.insertRow(fila)
                self.tabla_multas.setItem(fila, 0, QTableWidgetItem(multa[0]))
                self.tabla_multas.setItem(fila, 1, QTableWidgetItem(multa[1]))
                self.tabla_multas.setItem(fila, 2, QTableWidgetItem(multa[2]))
                self.tabla_multas.setItem(fila, 3, QTableWidgetItem(f"${multa[3]:,.2f}"))
                
                item_estado = QTableWidgetItem(multa[4])
                if multa[4] == "Pendiente":
                    item_estado.setForeground(Qt.yellow)
                elif multa[4] == "Pagada":
                    item_estado.setForeground(Qt.green)
                else: 
                    item_estado.setForeground(Qt.red)
                    
                self.tabla_multas.setItem(fila, 4, item_estado)
        else:
            QMessageBox.information(self, "Resultado", "No se encontraron multas para este vehículo.")

    def seleccionar_folio_de_tabla(self, item):
        """Copia el folio de la fila seleccionada a la caja de texto."""
        fila_seleccionada = item.row()
        folio = self.tabla_multas.item(fila_seleccionada, 0).text()
        self.input_buscar_folio.setText(folio)

    def procesar_cambio_estado(self):
        folio = self.input_buscar_folio.text().strip().upper()
        nuevo_estado = self.combo_nuevo_estado.currentText()
        
        if not folio:
            QMessageBox.warning(self, "Falta Folio", "Por favor ingrese el folio de la infracción.")
            return
            
        exito, msj = GestorInfracciones.cambiar_estado_infraccion(folio, nuevo_estado, self.usuario_actual.id_usuario)
        
        if exito:
            QMessageBox.information(self, "Actualización Exitosa", msj)
            self.input_buscar_folio.clear()
            if self.input_buscar_placa.text():
                self.buscar_multas_por_placa()
        else:
            QMessageBox.critical(self, "Error", msj)
            
    def limpiar_formulario_registro(self):
        self.input_vin.clear()
        self.input_lugar.clear()
        self.input_licencia.clear()
        
        self.combo_tipo.setCurrentIndex(0)
        self.combo_captura.setCurrentIndex(0)
        self.combo_agentes.setCurrentIndex(0)