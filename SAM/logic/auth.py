import sqlite3
import hashlib
from database.conexion import obtener_conexion
from models.usuario import Usuario
import logic.catalogos as cat

class Auth:
    
    @staticmethod
    def _hashear_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def registrar_usuario(usuario):
        """
        Registra un nuevo usuario en el sistema.
        Si es Agente de Tránsito, también crea su registro en agentes.
        """
        # 1. Validar reglas básicas
        if not usuario.nombre_usuario or len(usuario.nombre_usuario.strip()) < 4:
            return False, "Error: El nombre de usuario debe tener al menos 4 caracteres."
            
        if not usuario.password or len(usuario.password) < 6:
            return False, "Error: La contraseña debe tener al menos 6 caracteres."

        if usuario.rol not in cat.ROLES_USUARIO:
            return False, "Error: El rol seleccionado no es válido."

        # 2. Encriptar la contraseña
        password_hash = Auth._hashear_password(usuario.password)

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # ===== INSERTAR USUARIO =====
            cursor.execute('''
                INSERT INTO usuarios (nombre_usuario, password, rol, estado, id_usuario_registro)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario.nombre_usuario, password_hash, usuario.rol, usuario.estado, usuario.id_usuario_registro))
            
            # Obtener el ID del usuario recién creado
            id_usuario_nuevo = cursor.lastrowid
            
            # ===== Si es AGENTE DE TRÁNSITO, crear también en AGENTES =====
            if usuario.rol == "Agente de Tránsito":
                # Contar cuántos agentes hay
                cursor.execute("SELECT COUNT(*) FROM agentes")
                total_agentes = cursor.fetchone()[0]
                
                # Generar número de placa
                numero_placa = f"AG-{total_agentes + 1:03d}"
                
                # Usar el nombre de usuario para el nombre completo
                nombre_completo = usuario.nombre_usuario.replace("_", " ").title()
                
                cursor.execute('''
                    INSERT INTO agentes (numero_placa, nombre_completo, cargo, estado, id_usuario_registro)
                    VALUES (?, ?, ?, ?, ?)
                ''', (numero_placa, nombre_completo, "Agente de Tránsito", "Activo", id_usuario_nuevo))
            
            conexion.commit()
            
            if usuario.rol == "Agente de Tránsito":
                return True, f"Usuario y agente registrados. Placa: {numero_placa}"
            else:
                return True, "Usuario registrado exitosamente."
            
        except sqlite3.IntegrityError:
            return False, "Error: El nombre de usuario ya está en uso."
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def autenticar_usuario(nombre_usuario, password_plana):
        if not nombre_usuario or not password_plana:
            return False, None, "Error: Debe ingresar usuario y contraseña.", False

        password_hash = Auth._hashear_password(password_plana)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute('''
                SELECT id_usuario, nombre_usuario, rol, estado, debe_cambiar_password 
                FROM usuarios 
                WHERE nombre_usuario = ? AND password = ?
            ''', (nombre_usuario, password_hash))
            
            resultado = cursor.fetchone()

            if not resultado:
                return False, None, "Error: Credenciales incorrectas.", False

            id_usuario, nombre_db, rol_db, estado_db, debe_cambiar = resultado

            if estado_db != "Activo":
                return False, None, "Error: Su cuenta está inactiva.", False

            usuario_autenticado = Usuario(
                id_usuario=id_usuario, nombre_usuario=nombre_db, 
                password="***", rol=rol_db, estado=estado_db
            )

            return True, usuario_autenticado, f"Bienvenido, {nombre_db}.", bool(debe_cambiar)

        except Exception as e:
            return False, None, f"Error inesperado: {str(e)}", False
        finally:
            conexion.close()
            
    @staticmethod
    def cambiar_password_obligatorio(id_usuario, nueva_password):
        if len(nueva_password) < 6:
            return False, "La nueva contraseña debe tener al menos 6 caracteres."
            
        password_hash = Auth._hashear_password(nueva_password)
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                UPDATE usuarios 
                SET password = ?, debe_cambiar_password = 0 
                WHERE id_usuario = ?
            ''', (password_hash, id_usuario))
            conexion.commit()
            return True, "Contraseña actualizada exitosamente."
        except Exception as e:
            return False, f"Error al actualizar: {str(e)}"
        finally:
            conexion.close()