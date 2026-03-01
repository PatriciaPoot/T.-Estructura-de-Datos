import sqlite3
from database.conexion import obtener_conexion

class GestorReportes:

    @staticmethod
    def ejecutar_consulta(query, parametros=()):
        """
        Función auxiliar para no repetir el código de conexión en cada reporte.
        Retorna: (exito: bool, encabezados: list, filas: list)
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            cursor.execute(query, parametros)
            filas = cursor.fetchall()
            
            # Extraemos los nombres de las columnas directamente de la base de datos
            encabezados = [descripcion[0].replace("_", " ").title() for descripcion in cursor.description]
            
            return True, encabezados, filas
        except Exception as e:
            return False, ["Error"], [[str(e)]]
        finally:
            conexion.close()

    # 1. Vehículos con infracciones pendientes [cite: 350]
    @staticmethod
    def reporte_vehiculos_infracciones_pendientes():
        query = '''
            SELECT v.placa, v.vin, v.marca, v.modelo, COUNT(i.folio) as total_multas_pendientes
            FROM vehiculos v
            JOIN infracciones i ON v.vin = i.vin_infractor
            WHERE i.estado = 'Pendiente'
            GROUP BY v.vin
            ORDER BY total_multas_pendientes DESC
        '''
        return GestorReportes.ejecutar_consulta(query)

    # 2. Infracciones por rango de fechas [cite: 351]
    @staticmethod
    def reporte_infracciones_por_fecha(fecha_inicio, fecha_fin):
        query = '''
            SELECT folio, fecha, hora, lugar, tipo_infraccion, monto, estado
            FROM infracciones
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        '''
        return GestorReportes.ejecutar_consulta(query, (fecha_inicio, fecha_fin))

    # 3. Infracciones emitidas por agente [cite: 353]
    @staticmethod
    def reporte_infracciones_por_agente():
        query = '''
            SELECT a.numero_placa as ID_Oficial, a.nombre_completo, COUNT(i.folio) as multas_emitidas
            FROM agentes a
            LEFT JOIN infracciones i ON a.id_agente = i.id_agente
            GROUP BY a.id_agente
            ORDER BY multas_emitidas DESC
        '''
        return GestorReportes.ejecutar_consulta(query)

    # 4. Vehículos por estado legal [cite: 354]
    @staticmethod
    def reporte_vehiculos_estado_legal():
        query = '''
            SELECT estado_legal, COUNT(vin) as cantidad_vehiculos
            FROM vehiculos
            GROUP BY estado_legal
            ORDER BY cantidad_vehiculos DESC
        '''
        return GestorReportes.ejecutar_consulta(query)

    # 5. Propietarios con múltiples vehículos [cite: 356]
    @staticmethod
    def reporte_propietarios_multiples_vehiculos():
        # Usamos HAVING para filtrar a los que tienen estrictamente más de 1
        query = '''
            SELECT p.curp, p.nombre_completo, COUNT(v.vin) as vehiculos_registrados
            FROM propietarios p
            JOIN vehiculos v ON p.id_propietario = v.id_propietario
            GROUP BY p.id_propietario
            HAVING COUNT(v.vin) > 1
            ORDER BY vehiculos_registrados DESC
        '''
        return GestorReportes.ejecutar_consulta(query)

    # 6. Resumen general de infracciones [cite: 357]
    @staticmethod
    def reporte_resumen_infracciones():
        query = '''
            SELECT estado as Situacion, COUNT(folio) as Total_Multas, SUM(monto) as Dinero_Acumulado
            FROM infracciones
            GROUP BY estado
        '''
        return GestorReportes.ejecutar_consulta(query)
    
    @staticmethod
    def reporte_auditoria_infracciones():
        # Hacemos un JOIN doble con la tabla usuarios para obtener los nombres reales
        query = '''
            SELECT 
                i.folio as Folio, 
                i.estado as Estado_Actual,
                u1.nombre_usuario as Creado_Por,
                IFNULL(u2.nombre_usuario, 'Sin modificaciones') as Modificado_Por,
                i.monto as Monto
            FROM infracciones i
            LEFT JOIN usuarios u1 ON i.id_usuario_registro = u1.id_usuario
            LEFT JOIN usuarios u2 ON i.id_usuario_actualizacion = u2.id_usuario
            ORDER BY i.folio DESC
        '''
        return GestorReportes.ejecutar_consulta(query)
    
    # 8. Auditoría Masiva de Vehículos
    @staticmethod
    def reporte_auditoria_vehiculos():
        query = '''
            SELECT 
                v.placa as Placa,
                v.vin as VIN,
                v.estado_legal as Estado_Legal,
                u1.nombre_usuario as Creado_Por,
                IFNULL(u2.nombre_usuario, 'Sin modificaciones') as Modificado_Por
            FROM vehiculos v
            LEFT JOIN usuarios u1 ON v.id_usuario_registro = u1.id_usuario
            LEFT JOIN usuarios u2 ON v.id_usuario_actualizacion = u2.id_usuario
            ORDER BY v.vin DESC
        '''
        return GestorReportes.ejecutar_consulta(query)

    # 9. Auditoría Masiva de Propietarios
    @staticmethod
    def reporte_auditoria_propietarios():
        query = '''
            SELECT 
                p.curp as CURP,
                p.nombre_completo as Nombre_Propietario,
                p.estado_licencia as Estado_Licencia,
                u1.nombre_usuario as Creado_Por,
                IFNULL(u2.nombre_usuario, 'Sin modificaciones') as Modificado_Por
            FROM propietarios p
            LEFT JOIN usuarios u1 ON p.id_usuario_registro = u1.id_usuario
            LEFT JOIN usuarios u2 ON p.id_usuario_actualizacion = u2.id_usuario
            ORDER BY p.id_propietario DESC
        '''
        return GestorReportes.ejecutar_consulta(query)

    # 10. Auditoría Masiva de Usuarios
    @staticmethod
    def reporte_auditoria_usuarios():
        query = '''
            SELECT 
                u.nombre_usuario as Usuario,
                u.rol as Rol_Asignado,
                u.estado as Estado_Cuenta,
                IFNULL(u1.nombre_usuario, 'Sistema') as Creado_Por,
                IFNULL(u2.nombre_usuario, 'Sin modificaciones') as Modificado_Por
            FROM usuarios u
            LEFT JOIN usuarios u1 ON u.id_usuario_registro = u1.id_usuario
            LEFT JOIN usuarios u2 ON u.id_usuario_actualizacion = u2.id_usuario
            ORDER BY u.id_usuario DESC
        '''
        return GestorReportes.ejecutar_consulta(query)
    
    # 11. Bitácora Completa de Movimientos (Caja Negra)
    @staticmethod
    def reporte_bitacora_completa():
        """
        Extrae el historial inmutable generado por los Triggers de SQLite.
        Muestra cada acción (Creación/Actualización) con su fecha, hora y autor.
        """
        query = '''
            SELECT 
                b.id_evento as ID_Evento,
                b.fecha_hora as Fecha_Hora,
                UPPER(b.tabla_afectada) as Modulo_Afectado,
                b.id_registro_afectado as Registro_Afectado,
                b.tipo_accion as Accion_Realizada,
                IFNULL(u.nombre_usuario, 'Sistema/Desconocido') as Usuario_Responsable
            FROM bitacora_auditoria b
            LEFT JOIN usuarios u ON b.id_usuario = u.id_usuario
            ORDER BY b.fecha_hora DESC
        '''
        return GestorReportes.ejecutar_consulta(query)