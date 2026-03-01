from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
QComboBox, QDateEdit, QPushButton, QTableWidget, 
QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, QDate
import csv

import logic.catalogos as cat
from logic.gestor_reportes import GestorReportes


class PanelReportes(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.configurar_ui()
        self.aplicar_permisos()

    def configurar_ui(self):
        layout_principal = QVBoxLayout(self)

        # 1. Título
        lbl_titulo = QLabel("Módulo de Reportes Administrativos")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        # 2. Zona de Filtros (Controles superiores)
        layout_controles = QHBoxLayout()
        
        layout_controles.addWidget(QLabel("Seleccionar Reporte:"))
        self.combo_reportes = QComboBox()
        self.combo_reportes.addItem(" ", None)

        # === APLICACIÓN DE ROLES (RBAC) ===
        rol = self.usuario_actual.rol
        
        if rol in ["Administrador", "Supervisor"]:
            # Tienen acceso a todos los reportes
            self.combo_reportes.addItem("1. Vehículos con infracciones pendientes", 1)
            self.combo_reportes.addItem("2. Infracciones por rango de fechas", 2)
            self.combo_reportes.addItem("3. Infracciones emitidas por agente", 3)
            self.combo_reportes.addItem("4. Vehículos por estado legal", 4)
            self.combo_reportes.addItem("5. Propietarios con múltiples vehículos", 5)
            self.combo_reportes.addItem("--- Reportes de Auditoría Interna ---", None) # Separador visual
            self.combo_reportes.addItem("6. Resumen general de infracciones", 6)
            self.combo_reportes.addItem("7. Auditoría de Infracciones", 7)
            self.combo_reportes.addItem("8. Auditoría de Movimientos en Vehículos", 8)
            self.combo_reportes.addItem("9. Auditoría de Trámites de Propietarios", 9)
            self.combo_reportes.addItem("10. Auditoría de Privilegios de Usuarios", 10)
            self.combo_reportes.addItem("11. Historial Completo de Movimientos (Bitácora)", 11)
            
        elif rol == "Operador Administrativo":
            # Solo reportes básicos enfocados a padrón vehicular
            self.combo_reportes.addItem("1. Vehículos con infracciones pendientes", 1)
            self.combo_reportes.addItem("4. Vehículos por estado legal", 4)
            self.combo_reportes.addItem("5. Propietarios con múltiples vehículos", 5)
            
        elif rol == "Agente de Tránsito":
            # Bloqueo total
            self.combo_reportes.setItemText(0, "Sin acceso a reportes")
            self.combo_reportes.setEnabled(False)

        layout_controles.addWidget(self.combo_reportes)  # SOLO UNA VEZ

        # Filtros de Fecha (Ocultos por defecto)
        self.lbl_desde = QLabel("Desde:")
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))

        self.lbl_hasta = QLabel("Hasta:")
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate())

        layout_controles.addWidget(self.lbl_desde)
        layout_controles.addWidget(self.fecha_inicio)
        layout_controles.addWidget(self.lbl_hasta)
        layout_controles.addWidget(self.fecha_fin)
        
        # Botón Generar
        self.btn_generar = QPushButton("Generar Reporte")
        self.btn_generar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        layout_controles.addWidget(self.btn_generar)
        
        # Botón Exportar
        self.btn_exportar = QPushButton("Exportar a CSV")
        self.btn_exportar.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 8px;")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.btn_exportar.setVisible(False) # Oculto por defecto
        layout_controles.addWidget(self.btn_exportar)

        layout_principal.addLayout(layout_controles)

        # 3. Zona de Visualización
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setAlternatingRowColors(True)
        
        # 1. Bloquear la selección de celdas
        self.tabla_resultados.setSelectionMode(QTableWidget.NoSelection)
        
        # 2. Ocultar los números de fila (esto elimina el cuadro superior izquierdo)
        self.tabla_resultados.verticalHeader().setVisible(False)
        
        # 3. Activar colores alternos
        self.tabla_resultados.setAlternatingRowColors(True)
        
        # 4. CSS para Modo Oscuro
        self.tabla_resultados.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #353535;
                color: #ffffff;
                border: 1px solid #444444;
                font-size: 13px;
                gridline-color: #555555;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #444444;
            }
            QTableWidget::corner {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        self.tabla_resultados.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_principal.addWidget(self.tabla_resultados)

        # ==========================================
        # CONEXIÓN DE SEÑALES (Eventos)
        # ==========================================
        self.combo_reportes.currentIndexChanged.connect(self.ajustar_filtros)
        self.btn_generar.clicked.connect(self.procesar_reporte)
        
        # Ocultamos las fechas al arrancar
        self.ocultar_fechas()

    def aplicar_permisos(self):
        """Seguridad extra: Si un agente llega aquí, bloqueamos la generación."""
        if self.usuario_actual.rol == "Agente de Tránsito":
            self.combo_reportes.setEnabled(False)
            self.btn_generar.setEnabled(False)

    # ==========================================
    # LÓGICA DE INTERFAZ
    # ==========================================
    def ocultar_fechas(self):
        self.lbl_desde.setVisible(False)
        self.fecha_inicio.setVisible(False)
        self.lbl_hasta.setVisible(False)
        self.fecha_fin.setVisible(False)

    def mostrar_fechas(self):
        self.lbl_desde.setVisible(True)
        self.fecha_inicio.setVisible(True)
        self.lbl_hasta.setVisible(True)
        self.fecha_fin.setVisible(True)

    def ajustar_filtros(self):
        """Muestra los selectores de fecha SOLO si el reporte oculto es el número 2."""
        reporte_id = self.combo_reportes.currentData()
        if reporte_id == 2:
            self.mostrar_fechas()
        else:
            self.ocultar_fechas()

    def procesar_reporte(self):
        """Ejecuta la consulta correspondiente en el backend y dibuja la tabla."""
        reporte_id = self.combo_reportes.currentData()
        
        if not reporte_id:
            QMessageBox.warning(self, "Atención", "Por favor seleccione un reporte de la lista.")
            return

        self.tabla_resultados.clearContents()
        self.tabla_resultados.setRowCount(0)

        exito = False
        encabezados = []
        filas = []

        if reporte_id == 1:
            exito, encabezados, filas = GestorReportes.reporte_vehiculos_infracciones_pendientes()
        elif reporte_id == 2:
            fecha_ini = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
            exito, encabezados, filas = GestorReportes.reporte_infracciones_por_fecha(fecha_ini, fecha_fin)
        elif reporte_id == 3:
            exito, encabezados, filas = GestorReportes.reporte_infracciones_por_agente()
        elif reporte_id == 4:
            exito, encabezados, filas = GestorReportes.reporte_vehiculos_estado_legal()
        elif reporte_id == 5:
            exito, encabezados, filas = GestorReportes.reporte_propietarios_multiples_vehiculos()
        elif reporte_id == 6:
            exito, encabezados, filas = GestorReportes.reporte_resumen_infracciones()
        elif reporte_id == 7:
            exito, encabezados, filas = GestorReportes.reporte_auditoria_infracciones()
        elif reporte_id == 8:
            exito, encabezados, filas = GestorReportes.reporte_auditoria_vehiculos()
        elif reporte_id == 9:
            exito, encabezados, filas = GestorReportes.reporte_auditoria_propietarios()
        elif reporte_id == 10:
            exito, encabezados, filas = GestorReportes.reporte_auditoria_usuarios()
        elif reporte_id == 11:
            exito, encabezados, filas = GestorReportes.reporte_bitacora_completa()
            
        if exito:
            self.btn_exportar.setVisible(True)
            if not filas:
                QMessageBox.information(self, "Sin Resultados", "El reporte se generó correctamente pero no hay datos para mostrar en este momento.")
                return
            
            self.tabla_resultados.setColumnCount(len(encabezados))
            self.tabla_resultados.setHorizontalHeaderLabels(encabezados)
            self.tabla_resultados.setRowCount(len(filas))

            for fila_idx, datos_fila in enumerate(filas):
                for col_idx, dato in enumerate(datos_fila):
                    nombre_columna = encabezados[col_idx].lower()
                    if "monto" in nombre_columna or "dinero" in nombre_columna:
                        if dato is not None:
                            texto_celda = f"${float(dato):,.2f}"
                        else:
                            texto_celda = "$0.00"
                    else:
                        texto_celda = str(dato) if dato is not None else "N/A"

                    item = QTableWidgetItem(texto_celda)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla_resultados.setItem(fila_idx, col_idx, item)
                    
        else:
            error_msg = filas[0][0] if filas else "Error desconocido"
            QMessageBox.critical(self, "Error al Generar", f"Hubo un problema de base de datos:\n{error_msg}")
            
    def exportar_csv(self):
        """Abre un cuadro de diálogo y guarda la tabla en un archivo .csv"""
        if self.tabla_resultados.rowCount() == 0:
            QMessageBox.warning(self, "Sin datos", "Genere un reporte primero antes de exportar.")
            return

        ruta_archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "reporte_transito.csv", "Archivos CSV (*.csv)")

        if not ruta_archivo:
            return

        try:
            with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                encabezados = [self.tabla_resultados.horizontalHeaderItem(i).text() for i in range(self.tabla_resultados.columnCount())]
                writer.writerow(encabezados)

                for fila in range(self.tabla_resultados.rowCount()):
                    datos_fila = []
                    for col in range(self.tabla_resultados.columnCount()):
                        item = self.tabla_resultados.item(fila, col)
                        datos_fila.append(item.text() if item else "")
                    writer.writerow(datos_fila)

            QMessageBox.information(self, "Éxito", "El reporte se ha guardado correctamente y puede abrirse en Excel.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")