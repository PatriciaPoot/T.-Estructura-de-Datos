import sqlite3
from database.conexion import obtener_conexion

class GestorUsuarios:

    @staticmethod
    def obtener_todos_los_usuarios():
        """
        Devuelve la lista completa de usuarios. 
        Por seguridad absoluta, la consulta omite la columna de contraseñas.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    u.id_usuario, u.nombre_usuario, u.rol, u.estado,
                    u1.nombre_usuario AS creador,
                    u2.nombre_usuario AS modificador
                FROM usuarios u
                LEFT JOIN usuarios u1 ON u.id_usuario_registro = u1.id_usuario
                LEFT JOIN usuarios u2 ON u.id_usuario_actualizacion = u2.id_usuario
                ORDER BY u.id_usuario ASC
            ''')
            usuarios = cursor.fetchall()
            return True, usuarios
        except Exception as e:
            return False, f"Error al obtener la lista de usuarios: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def actualizar_usuario(id_usuario, nuevo_rol, nuevo_estado, id_usuario_modificador):
        """
        Permite al administrador cambiar el rol o el estado de un empleado.
        Si el rol cambia a "Agente de Tránsito", crea el registro en agentes.
        Si deja de ser "Agente de Tránsito", elimina/inactiva su registro en agentes.
        """
        if id_usuario == 1 and (nuevo_estado != "Activo" or nuevo_rol != "Administrador"):
            return False, "Error de Seguridad: No puede alterar el estado ni el rol del Administrador principal (ID 1)."

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Obtener el rol actual del usuario
            cursor.execute("SELECT rol, nombre_usuario FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Usuario no encontrado"
            
            rol_actual = resultado[0]
            nombre_usuario = resultado[1]
            
            # ===== ACTUALIZAR USUARIO =====
            cursor.execute('''
                UPDATE usuarios 
                SET rol = ?, estado = ?, id_usuario_actualizacion = ?
                WHERE id_usuario = ?
            ''', (nuevo_rol, nuevo_estado, id_usuario_modificador, id_usuario))
            
            # ===== MANEJAR CAMBIOS EN TABLA AGENTES =====
            
            # CASO 1: Ahora es Agente de Tránsito (antes no lo era)
            if nuevo_rol == "Agente de Tránsito" and rol_actual != "Agente de Tránsito":
                # Verificar si ya existe como agente
                cursor.execute("SELECT id_agente FROM agentes WHERE id_usuario_registro = ?", (id_usuario,))
                if not cursor.fetchone():
                    # Crear nuevo agente
                    cursor.execute("SELECT COUNT(*) FROM agentes")
                    total_agentes = cursor.fetchone()[0]
                    numero_placa = f"AG-{total_agentes + 1:03d}"
                    nombre_completo = nombre_usuario.replace("_", " ").title()
                    
                    cursor.execute('''
                        INSERT INTO agentes (numero_placa, nombre_completo, cargo, estado, id_usuario_registro)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (numero_placa, nombre_completo, "Agente de Tránsito", nuevo_estado, id_usuario))
            
            # CASO 2: Dejó de ser Agente de Tránsito
            elif rol_actual == "Agente de Tránsito" and nuevo_rol != "Agente de Tránsito":
                # Opción: Eliminar al agente
                cursor.execute("DELETE FROM agentes WHERE id_usuario_registro = ?", (id_usuario,))
            
            # CASO 3: Sigue siendo Agente, pero cambió estado
            elif nuevo_rol == "Agente de Tránsito" and rol_actual == "Agente de Tránsito":
                cursor.execute("UPDATE agentes SET estado = ? WHERE id_usuario_registro = ?", (nuevo_estado, id_usuario))
            
            conexion.commit()
            return True, "Los permisos del usuario han sido actualizados exitosamente."
            
        except Exception as e:
            return False, f"Error inesperado al actualizar usuario: {str(e)}"
        finally:
            conexion.close()
    
    @staticmethod
    def cambiar_nombre_usuario(id_usuario, nuevo_nombre, id_usuario_modificador):
        """
        Permite a un usuario cambiar su propio nombre de usuario.
        Verifica que el nuevo nombre no esté ya en uso.
        """
        if not nuevo_nombre or len(nuevo_nombre.strip()) < 4:
            return False, "El nombre de usuario debe tener al menos 4 caracteres."
        
        nuevo_nombre = nuevo_nombre.strip()
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Verificar que el nuevo nombre no esté en uso por OTRO usuario
            cursor.execute('''
                SELECT id_usuario FROM usuarios 
                WHERE nombre_usuario = ? AND id_usuario != ?
            ''', (nuevo_nombre, id_usuario))
            
            if cursor.fetchone():
                return False, "El nombre de usuario ya está en uso. Elija otro."
            
            # Actualizar el nombre
            cursor.execute('''
                UPDATE usuarios 
                SET nombre_usuario = ?, id_usuario_actualizacion = ?
                WHERE id_usuario = ?
            ''', (nuevo_nombre, id_usuario_modificador, id_usuario))
            
            conexion.commit()
            return True, "Nombre de usuario actualizado correctamente."
            
        except Exception as e:
            return False, f"Error al cambiar nombre: {str(e)}"
        finally:
            conexion.close()