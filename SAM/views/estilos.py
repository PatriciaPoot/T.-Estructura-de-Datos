# ==========================================
# HOJA DE ESTILOS GLOBAL (QSS)
# ==========================================

TEMA_OSCURO = """
/* Fondo principal y texto general */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI"; /* SOLUCIÓN: Una sola fuente definida */
    font-size: 14px;
}

/* Cajas de texto, numéricas y menús desplegables */
/* (Se agregó QDoubleSpinBox para que el campo de multas se vea oscuro) */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 6px;
    color: #cdd6f4;
}

/* Cuando el usuario selecciona una caja de texto */
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #89b4fa;
}

/* Cajas de texto bloqueadas (Solo lectura) */
QLineEdit[readOnly="true"], QDoubleSpinBox[readOnly="true"] {
    background-color: #181825;
    color: #a6adc8;
    border: 1px dashed #45475a;
}

/* Diseño de las pestañas superiores */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 5px;
    top: -1px;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px 20px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 2px;
}

/* Pestaña activa */
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}

/* Pestaña al pasar el mouse */
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}

/* Estilo base para botones que no tengan color específico */
QPushButton {
    background-color: #45475a;
    color: white;
    border-radius: 5px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #585b70;
}
"""