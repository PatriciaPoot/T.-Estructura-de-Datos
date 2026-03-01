"""
TODO 
- Evitar que se repita el codigo en registar_propietario, tratar de refactorizar
"""

import sqlite3
from database.conexion import obtener_conexion
from logic.validador import Validador

class GestorPropietarios:
    
    @staticmethod
    def registrar_propietario(propietario):
        """Recibe un objeto Propietario, lo valida y lo guarda en la base de datos."""
        
        valido, msj = Validador.validar_nombre_completo(propietario.nombre_completo)
        if not valido: return False, msj

        valido, msj = Validador.validar_direccion(propietario.direccion)
        if not valido: return False, msj

        # 1. Validar formatos usando nuestra herramienta centralizada
        valido, msj = Validador.validar_curp(propietario.curp)
        if not valido: return False, msj
        
        valido, msj = Validador.validar_telefono(propietario.telefono)
        if not valido: return False, msj

        valido, msj = Validador.validar_estado_licencia(propietario.estado_licencia)
        if not valido: return False, msj
        
        valido, msj = Validador.validar_correo(propietario.correo_electronico)
        if not valido: return False, msj

        valido, msj = Validador.validar_estado_propietario(propietario.estado)
        if not valido: return False, msj
        
        # 2. Guardar en la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # El ID interno no se envía en el INSERT porque es único, inmutable y se asigna automáticamente al registro[cite: 118].
            cursor.execute('''
                INSERT INTO propietarios (nombre_completo, curp, direccion, telefono, correo_electronico, estado_licencia, estado, id_usuario_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (propietario.nombre_completo, propietario.curp, propietario.direccion, 
                propietario.telefono, propietario.correo_electronico, propietario.estado_licencia, propietario.estado, propietario.id_usuario_registro))
            conexion.commit()
            return True, "Propietario registrado exitosamente."
            
        except sqlite3.IntegrityError:
            # Si SQLite detecta que la CURP ya existe (restricción UNIQUE), lanza este error[cite: 119, 184].
            return False, "Error: La CURP ingresada ya se encuentra registrada en el sistema."
        except Exception as e:
            return False, f"Error inesperado al registrar propietario: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def modificar_propietario(id_propietario, nueva_direccion, nuevo_telefono, nuevo_correo, nuevo_estado_licencia, nuevo_estado, id_usuario):
        """
        Actualiza la información de contacto y administrativa de un propietario.
        Bloquea el cambio a estado 'Inactivo' si el propietario tiene vehículos activos.
        No permite modificar atributos inmutables (ID, CURP, Nombre completo).
        """
        # 1. Validaciones de formato y catálogos
        valido, msj = Validador.validar_id_propietario(id_propietario)
        if not valido: return False, msj
        
        valido, msj = Validador.validar_direccion(nueva_direccion)
        if not valido: return False, msj

        valido, msj = Validador.validar_telefono(nuevo_telefono)
        if not valido: return False, msj

        valido, msj = Validador.validar_correo(nuevo_correo)
        if not valido: return False, msj

        valido, msj = Validador.validar_estado_licencia(nuevo_estado_licencia)
        if not valido: return False, msj

        valido, msj = Validador.validar_estado_propietario(nuevo_estado)
        if not valido: return False, msj

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # 2. Regla de negocio: Impedir "eliminación" (Inactivación) si tiene vehículos activos
            if nuevo_estado == "Inactivo":
                cursor.execute('''
                    SELECT COUNT(*) FROM vehiculos 
                    WHERE id_propietario = ? AND estado_legal = 'Activo'
                ''', (id_propietario,))
                
                vehiculos_activos = cursor.fetchone()[0]
                if vehiculos_activos > 0:
                    return False, f"Error: No se puede inactivar al propietario porque tiene {vehiculos_activos} vehículo(s) activo(s) asociado(s)."

            # 3. Ejecutar la actualización solo en los campos permitidos
            cursor.execute('''
                UPDATE propietarios 
                SET direccion = ?, 
                    telefono = ?, 
                    correo_electronico = ?, 
                    estado_licencia = ?, 
                    estado = ?,
                    id_usuario_actualizacion = ?
                WHERE id_propietario = ?
            ''', (nueva_direccion, nuevo_telefono, nuevo_correo, nuevo_estado_licencia, nuevo_estado, id_usuario, id_propietario))

            if cursor.rowcount == 0:
                return False, "Error: No se encontró un propietario con el ID especificado."

            conexion.commit()
            return True, "Datos del propietario actualizados correctamente."

        except Exception as e:
            return False, f"Error inesperado al modificar propietario: {str(e)}"
        finally:
            conexion.close()
            
    @staticmethod
    def buscar_propietario_por_curp(curp):
        """
        Busca un propietario en la base de datos utilizando su CURP.
        Retorna (True, diccionario_con_datos) si lo encuentra, 
        o (False, mensaje_error) si no existe.
        """
        # 1. Validamos que el formato de la CURP que nos mandan sea correcto
        valido, msj = Validador.validar_curp(curp)
        if not valido:
            return False, msj

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            # 2. Buscamos en la base de datos
            cursor.execute('''
                SELECT 
                    p.id_propietario, p.nombre_completo, p.curp, p.direccion, 
                    p.telefono, p.correo_electronico, p.estado_licencia, p.estado,
                    u1.nombre_usuario AS creador,
                    u2.nombre_usuario AS modificador
                FROM propietarios p
                LEFT JOIN usuarios u1 ON p.id_usuario_registro = u1.id_usuario
                LEFT JOIN usuarios u2 ON p.id_usuario_actualizacion = u2.id_usuario
                WHERE p.curp = ?
            ''', (curp,))
            
            fila = cursor.fetchone()
            
            # 3. Empaquetamos y respondemos
            if fila:
                resultado = {
                    "id_propietario": fila[0],
                    "nombre_completo": fila[1],
                    "curp": fila[2],
                    "direccion": fila[3],
                    "telefono": fila[4],
                    "correo": fila[5], 
                    "estado_licencia": fila[6],
                    "estado": fila[7],
                    # Agregamos los datos de auditoría con valores por defecto si vienen vacíos
                    "creador": fila[8] if fila[8] else "Sistema/Desconocido",
                    "modificador": fila[9] if fila[9] else "Sin modificaciones"
                }
                return True, resultado
            else:
                return False, "No se encontró ningún propietario registrado con esa CURP."
                
        except Exception as e:
            return False, f"Error inesperado al buscar propietario: {str(e)}"
        finally:
            conexion.close()