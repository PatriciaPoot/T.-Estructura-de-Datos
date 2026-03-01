import re
from datetime import datetime
import logic.catalogos as cat
from database.conexion import obtener_conexion  # <-- AGREGADO

class Validador:
    """
    Clase centralizada para validaciones de formato, longitud y catálogos.
    No interactúa con la base de datos (excepto las nuevas funciones de verificación).
    Retorna siempre una tupla: (es_valido: bool, mensaje_error: str)
    """

    # =========================
    # VALIDACIONES DE VEHÍCULOS
    # =========================
    
    @staticmethod
    def validar_vin(vin: str) -> tuple[bool, str]:
        if len(vin) != 17:
            return False, "El VIN debe tener exactamente 17 caracteres."
        return True, ""

    @staticmethod
    def validar_placa(placa: str) -> tuple[bool, str]:
        if not placa or placa.strip() == "":
            return False, "La placa no puede quedar vacía."
            
        placa_limpia = placa.strip().upper()
        
        # Patrón Regex para placas oficiales
        patron_placa = r"^[A-Z]{3}-\d{3}-[A-Z]$|^[A-Z]{3}-\d{2}-\d{2}$|^[A-Z]{3}-\d{4}$"
        
        if not re.match(patron_placa, placa_limpia):
            return False, "Formato inválido. Use guiones (Ej. YAA-123-A, YAB-12-34 o ABC-1234)."
            
        return True, ""

    @staticmethod
    def validar_anio_vehiculo(anio: int) -> tuple[bool, str]:
        anio_actual = datetime.now().year
        if not isinstance(anio, int):
            return False, "El año del vehículo debe ser un valor numérico."
        if anio < 1900 or anio > anio_actual:
            return False, f"El año debe estar en el rango de 1900 a {anio_actual}."
        return True, ""

    @staticmethod
    def validar_clase_vehiculo(clase: str) -> tuple[bool, str]:
        if clase not in cat.CLASES_VEHICULO:
            return False, "La clase de vehículo seleccionada no es válida."
        return True, ""

    @staticmethod
    def validar_procedencia_vehiculo(clase: str) -> tuple[bool, str]:
        if clase not in cat.PROCEDENCIAS_VEHICULO:
            return False, "La procedencia de vehículo seleccionada no es válida."
        return True, ""

    @staticmethod
    def validar_estado_vehiculo(estado: str) -> tuple[bool, str]:
        if estado not in cat.ESTADOS_VEHICULO:
            return False, "El estado legal del vehículo seleccionado no es válido."
        return True, ""

    @staticmethod
    def validar_marca_modelo_clase(marca: str, modelo: str, clase: str) -> tuple[bool, str]:
        # 1. Validar Marca
        if marca not in cat.MARCAS_MODELOS_VEHICULO:
            return False, f"La marca '{marca}' no está registrada en el sistema."
        
        # 2. Validar Modelo
        modelos_de_la_marca = cat.MARCAS_MODELOS_VEHICULO[marca]
        if modelo not in modelos_de_la_marca:
            return False, f"El modelo '{modelo}' no es válido para la marca '{marca}'."
            
        # 3. Validar Clase
        clases_permitidas_del_modelo = modelos_de_la_marca[modelo]
        if clase not in clases_permitidas_del_modelo:
            return False, f"Un '{modelo}' no puede ser clasificado como '{clase}'. Opciones válidas: {', '.join(clases_permitidas_del_modelo)}."
            
        return True, ""

    @staticmethod
    def validar_color_vehiculo(color: str) -> tuple[bool, str]:
        if color not in cat.COLORES_VEHICULO:
            return False, "El color ingresado no es válido. Seleccione uno de la lista."
        return True, ""
    
    @staticmethod
    def validar_id_propietario(id_propietario: int) -> tuple[bool, str]:
        if not isinstance(id_propietario, int) or isinstance(id_propietario, bool):
            return False, "El ID del propietario debe ser un valor numérico entero."
        if id_propietario <= 0:
            return False, "El ID del propietario debe ser mayor a cero."
        return True, ""

    # =========================
    # VALIDACIONES DE PROPIETARIOS
    # =========================

    @staticmethod
    def validar_curp(curp: str) -> tuple[bool, str]:
        if not curp or curp.strip() == "":
            return False, "La CURP no puede quedar vacía."

        curp_limpia = curp.strip().upper()

        # Patrón oficial de la CURP en México
        patron_curp = r"^[A-Z]{4}\d{6}[HMX][A-Z]{2}[A-Z]{3}[A-Z0-9]\d$"
        if not re.match(patron_curp, curp_limpia):
            return False, "Formato de CURP inválido. Verifique las letras, fecha de nacimiento y homoclave."
            
        return True, ""

    @staticmethod
    def validar_correo(correo: str) -> tuple[bool, str]:
        if not correo or correo.strip() == "":
            return False, "El correo electrónico no puede quedar vacío."
        patron_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(patron_correo, correo):
            return False, "El correo electrónico no cumple con el formato estándar."
        return True, ""

    @staticmethod
    def validar_telefono(telefono: str) -> tuple[bool, str]:
        if not telefono or telefono.strip() == "":
            return False, "El teléfono no puede quedar vacío."
        if not telefono.isdigit():
            return False, "El teléfono debe contener únicamente dígitos."
        if len(telefono) != 10:
            return False, "El teléfono debe tener 10 dígitos."
        return True, ""

    @staticmethod
    def validar_nombre_completo(nombre: str) -> tuple[bool, str]:
        if not nombre or len(nombre.strip()) < 5:
            return False, "El nombre completo debe tener al menos 5 caracteres."
        
        patron_nombre = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$'
        if not re.match(patron_nombre, nombre.strip()):
            return False, "El nombre solo debe contener letras y espacios (sin números ni símbolos especiales)."
        
        return True, ""

    @staticmethod
    def validar_direccion(direccion: str) -> tuple[bool, str]:
        if not direccion or len(direccion.strip()) < 10:
            return False, "La dirección debe contener al menos 10 caracteres válidos."
        return True, ""

    @staticmethod
    def validar_estado_licencia(estado: str) -> tuple[bool, str]:
        if estado not in cat.ESTADOS_LICENCIA:
            return False, "El estado de la licencia seleccionado no es válido."
        return True, ""

    @staticmethod
    def validar_estado_propietario(estado: str) -> tuple[bool, str]:
        if estado not in cat.ESTADOS_PROPIETARIO:
            return False, "El estado del propietario seleccionado no es válido."
        return True, ""

    # =========================
    # NUEVAS FUNCIONES PARA VERIFICAR DUPLICADOS
    # =========================

    @staticmethod
    def verificar_telefono_existe(telefono, id_propietario=None):
        """
        Verifica si un teléfono ya está registrado.
        Si se proporciona id_propietario, excluye ese propietario de la búsqueda.
        Retorna: (existe: bool, mensaje: str)
        """
        if not telefono:
            return False, ""
            
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            if id_propietario:
                cursor.execute('''
                    SELECT id_propietario FROM propietarios 
                    WHERE telefono = ? AND id_propietario != ?
                ''', (telefono, id_propietario))
            else:
                cursor.execute('''
                    SELECT id_propietario FROM propietarios 
                    WHERE telefono = ?
                ''', (telefono,))
            
            resultado = cursor.fetchone()
            return resultado is not None, "El teléfono ya está registrado por otro propietario."
        except Exception as e:
            return False, str(e)
        finally:
            conexion.close()

    @staticmethod
    def verificar_correo_existe(correo, id_propietario=None):
        """
        Verifica si un correo ya está registrado.
        Si se proporciona id_propietario, excluye ese propietario de la búsqueda.
        Retorna: (existe: bool, mensaje: str)
        """
        if not correo:
            return False, ""
            
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            if id_propietario:
                cursor.execute('''
                    SELECT id_propietario FROM propietarios 
                    WHERE correo_electronico = ? AND id_propietario != ?
                ''', (correo, id_propietario))
            else:
                cursor.execute('''
                    SELECT id_propietario FROM propietarios 
                    WHERE correo_electronico = ?
                ''', (correo,))
            
            resultado = cursor.fetchone()
            return resultado is not None, "El correo electrónico ya está registrado por otro propietario."
        except Exception as e:
            return False, str(e)
        finally:
            conexion.close()

    # =========================
    # VALIDACIONES DE INFRACCIONES Y AGENTES
    # =========================

    @staticmethod
    def validar_monto(monto) -> tuple[bool, str]:
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return False, "El monto de la infracción debe ser mayor a $0.00."
            return True, ""
        except ValueError:
            return False, "El monto debe ser un valor numérico válido."

    @staticmethod
    def validar_tipo_infraccion(tipo: str) -> tuple[bool, str]:
        if tipo not in cat.TIPOS_INFRACCION:
            return False, "El tipo de infracción seleccionado no es válido."
        return True, ""

    @staticmethod
    def validar_estado_infraccion(estado: str) -> tuple[bool, str]:
        if estado not in cat.ESTADOS_INFRACCION:
            return False, "El estado de la infracción seleccionado no es válido."
        return True, ""

    @staticmethod
    def validar_tipo_captura(tipo_captura: str) -> tuple[bool, str]:
        if tipo_captura not in cat.TIPOS_CAPTURA_INFRACCION:
            return False, "El tipo de captura seleccionado no es válido."
        return True, ""

    @staticmethod
    def validar_fecha_hora_pasada(fecha_str: str, hora_str: str) -> tuple[bool, str]:
        try:
            fecha_hora_infraccion = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            fecha_hora_actual = datetime.now()
            
            if fecha_hora_infraccion > fecha_hora_actual:
                return False, "La fecha y hora de la infracción no pueden ser en el futuro."
                
            return True, ""
        except ValueError:
            return False, "Formato de fecha u hora incorrecto. Use YYYY-MM-DD para fecha y HH:MM para hora."

    @staticmethod
    def validar_lugar_motivo(lugar: str, motivo: str) -> tuple[bool, str]:
        if not lugar or len(lugar.strip()) < 5:
            return False, "El lugar de la infracción debe ser más específico (mínimo 5 caracteres)."
            
        if not motivo or len(motivo.strip()) < 5:
            return False, "El motivo de la infracción debe ser detallado (mínimo 5 caracteres)."
            
        return True, ""

    @staticmethod
    def validar_licencia_conductor(licencia: str) -> tuple[bool, str]:
        if not licencia or licencia.strip() == "":
            return True, ""
            
        if len(licencia.strip()) < 5:
            return False, "Si se proporciona, la licencia debe tener al menos 5 caracteres válidos."
            
        return True, ""

    @staticmethod
    def validar_id_agente(id_agente: int) -> tuple[bool, str]:
        if not isinstance(id_agente, int) or isinstance(id_agente, bool):
            return False, "El ID del agente debe ser un valor numérico entero."
        if id_agente <= 0:
            return False, "El ID del agente debe ser mayor a cero."
        return True, ""