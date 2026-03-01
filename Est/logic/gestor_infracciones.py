import sqlite3
import uuid
from datetime import datetime
from database.conexion import obtener_conexion
from logic.validador import Validador

class GestorInfracciones:
    
    @staticmethod
    def registrar_infraccion(infraccion, tipo_captura):
        """
        Recibe un objeto Infraccion y el tipo de captura (ej. 'En sitio' o 'Fotomulta').
        Aplica reglas de negocio inter-entidades, genera el folio automático y guarda.
        """
        # 1. Validaciones de formato y catálogos usando la herramienta centralizada
        valido, msj = Validador.validar_monto(infraccion.monto)
        if not valido: return False, msj

        valido, msj = Validador.validar_tipo_infraccion(infraccion.tipo_infraccion)
        if not valido: return False, msj

        valido, msj = Validador.validar_tipo_captura(tipo_captura)
        if not valido: return False, msj

        valido, msj = Validador.validar_fecha_hora_pasada(infraccion.fecha, infraccion.hora)
        if not valido: return False, msj

        valido, msj = Validador.validar_lugar_motivo(infraccion.lugar, infraccion.motivo)
        if not valido: return False, msj

        valido, msj = Validador.validar_id_agente(infraccion.id_agente)
        if not valido: return False, msj

        valido, msj = Validador.validar_licencia_conductor(infraccion.licencia_conductor)
        if not valido: return False, msj

        # 2. Regla de negocio: Obligatoriedad de la licencia
        if tipo_captura == "En sitio" and (not infraccion.licencia_conductor or infraccion.licencia_conductor.strip() == ""):
            return False, "Error: Para infracciones de tipo 'En sitio', el número de licencia del conductor es obligatorio."

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # 3. Regla de negocio: El vehículo debe existir
            cursor.execute("SELECT vin FROM vehiculos WHERE vin = ?", (infraccion.vin_infractor,))
            if not cursor.fetchone():
                return False, "Error: El vehículo asociado (VIN) no existe en el sistema."

            # 4. Regla de negocio: El agente debe existir y estar 'Activo'
            cursor.execute("SELECT estado FROM agentes WHERE id_agente = ?", (infraccion.id_agente,))
            resultado_agente = cursor.fetchone()
            
            if not resultado_agente:
                return False, "Error: El agente emisor no existe en el sistema."
            if resultado_agente[0] != "Activo":
                return False, "Error: Solo los agentes con estado 'Activo' pueden registrar nuevas infracciones."

            # 5. Generación automática del Folio Único
            folio_generado = f"FOL-{uuid.uuid4().hex[:6].upper()}"
            
            # 6. Guardar en la base de datos
            estado_inicial = "Pendiente"

            cursor.execute('''
                INSERT INTO infracciones (folio, fecha, hora, lugar, tipo_infraccion, motivo, monto, estado, vin_infractor, id_agente, licencia_conductor, id_usuario_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (folio_generado, infraccion.fecha, infraccion.hora, infraccion.lugar, 
                infraccion.tipo_infraccion, infraccion.motivo, infraccion.monto, 
                estado_inicial, infraccion.vin_infractor, infraccion.id_agente, infraccion.licencia_conductor, infraccion.id_usuario_registro))
            
            conexion.commit()
            return True, f"Infracción registrada exitosamente.\n\nEl Folio asignado es: {folio_generado}"
            
        except sqlite3.IntegrityError as e:
            return False, f"Error de integridad en la base de datos: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado al registrar la infracción: {str(e)}"
        finally:
            conexion.close()
            
    @staticmethod
    def cambiar_estado_infraccion(folio, nuevo_estado, id_usuario):
        """
        Cambia el estado de una infracción asegurando que se respeten 
        las reglas de transición del negocio.
        """
        # 1. Validar que el nuevo estado sea válido según el catálogo
        valido, msj = Validador.validar_estado_infraccion(nuevo_estado)
        if not valido: return False, msj

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # 2. Consultar el estado actual de la infracción
            cursor.execute("SELECT estado FROM infracciones WHERE folio = ?", (folio,))
            resultado = cursor.fetchone()

            if not resultado:
                return False, "Error: No se encontró una infracción con el folio proporcionado."

            estado_actual = resultado[0]

            # 3. Reglas de negocio para el cambio de estado
            if estado_actual == nuevo_estado:
                return False, f"La infracción ya se encuentra en estado '{estado_actual}'."

            # Regla explícita: No podrá marcarse como Pagada una infracción ya cancelada.
            if estado_actual == "Cancelada" and nuevo_estado == "Pagada":
                return False, "Error: No se puede marcar como 'Pagada' una infracción que ya ha sido 'Cancelada'."

            # Regla: El estado podrá cambiar de Pendiente a Pagada o Cancelada.
            if estado_actual == "Pagada":
                return False, "Error: La infracción ya se encuentra 'Pagada' y su estado es definitivo."

            # 4. Ejecutar la actualización en la base de datos
            cursor.execute('''
                UPDATE infracciones 
                SET estado = ?, id_usuario_actualizacion = ?
                WHERE folio = ?
            ''', (nuevo_estado, id_usuario, folio))

            conexion.commit()
            return True, f"El estado de la infracción #{folio} se ha actualizado correctamente a '{nuevo_estado}'."

        except Exception as e:
            return False, f"Error inesperado al cambiar el estado de la infracción: {str(e)}"
        finally:
            conexion.close()

    # ==========================================
    # NUEVO MÉTODO AÑADIDO: BUSCADOR POR PLACA
    # ==========================================
    @staticmethod
    def obtener_infracciones_por_vehiculo(criterio: str):
        """
        Busca todas las infracciones asociadas a un vehículo, ya sea por su Placa o su VIN.
        Hace un cruce (JOIN) con la tabla de vehículos para identificar la placa.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                SELECT i.folio, i.fecha, i.tipo_infraccion, i.monto, i.estado
                FROM infracciones i
                JOIN vehiculos v ON i.vin_infractor = v.vin
                WHERE v.placa = ? OR v.vin = ?
                ORDER BY i.fecha DESC
            ''', (criterio, criterio))
            
            resultados = cursor.fetchall()
            return True, resultados
            
        except Exception as e:
            return False, f"Error al buscar infracciones: {str(e)}"
        finally:
            if 'conexion' in locals():
                conexion.close()