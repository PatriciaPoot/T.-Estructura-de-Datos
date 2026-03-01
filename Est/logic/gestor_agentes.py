import sqlite3
from database.conexion import obtener_conexion
import logic.catalogos as cat

class GestorAgentes:
    
    @staticmethod
    def registrar_agente(agente):
        """
        Registra un nuevo agente de tránsito. 
        El ID interno se genera automáticamente en la base de datos.
        """
        # Validar que el estado inicial sea válido según el catálogo
        if agente.estado not in cat.ESTADOS_AGENTE:
            return False, "Error: El estado del agente no es válido."

        # Validar que el número de placa oficial no esté vacío
        if not agente.numero_placa or len(agente.numero_placa.strip()) == 0:
            return False, "Error: El número de placa (identificación oficial) es obligatorio."

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO agentes (nombre_completo, numero_placa, cargo, estado, id_usuario_registro)
                VALUES (?, ?, ?, ?, ?)
            ''', (agente.nombre_completo, agente.numero_placa, agente.cargo, agente.estado, agente.id_usuario_registro))
            
            conexion.commit()
            return True, "Agente registrado exitosamente."
            
        except sqlite3.IntegrityError:
            return False, "Error: El número de placa ingresado ya está asignado a otro agente."
        except Exception as e:
            return False, f"Error inesperado al registrar el agente: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def modificar_agente(id_agente, nuevo_cargo, nuevo_estado, id_usuario):
        """
        Modifica únicamente el cargo y el estado de un agente.
        """
        if nuevo_estado not in cat.ESTADOS_AGENTE:
            return False, "Error: El estado proporcionado no es válido."

        if not nuevo_cargo or len(nuevo_cargo.strip()) < 3:
            return False, "Error: El cargo proporcionado no es válido."

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute('''
                UPDATE agentes 
                SET cargo = ?, estado = ?, id_usuario_actualizacion = ?
                WHERE id_agente = ?
            ''', (nuevo_cargo, nuevo_estado, id_usuario, id_agente))

            if cursor.rowcount == 0:
                return False, "Error: No se encontró un agente con el ID especificado."

            conexion.commit()
            return True, "Datos del agente actualizados correctamente."

        except Exception as e:
            return False, f"Error inesperado al modificar el agente: {str(e)}"
        finally:
            conexion.close()
            
    @staticmethod
    def obtener_agentes_para_combo():
        """Devuelve la lista de agentes activos para llenar el formulario de multas."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id_agente, numero_placa, nombre_completo FROM agentes WHERE estado = 'Activo'")
            return True, cursor.fetchall()
        except Exception as e:
            return False, []
        finally:
            conexion.close()