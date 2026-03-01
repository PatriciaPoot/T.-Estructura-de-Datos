import sys
import os
import time

# Aseguramos que Python encuentre tus módulos
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ruta_raiz)

from database.conexion import obtener_conexion
from logic.auth import Auth
from models.usuario import Usuario

def generar_datos_prueba():
    print("==================================================")
    print("🚀 INICIANDO CARGA DE DATOS PARA ENTORNO DE PRUEBAS")
    print("==================================================")
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # 1. USUARIOS
        usuarios_test = [
            ("admin_central", "admin123", "Administrador"),
            ("operador_1", "operador123", "Operador Administrativo"),
            ("agente_007", "agente123", "Agente de Tránsito"),
            ("supervisor_general", "super123", "Supervisor")
        ]
        for nom, pwd, rol in usuarios_test:
            u = Usuario(nombre_usuario=nom, password=pwd, rol=rol, id_usuario_registro=1)
            Auth.registrar_usuario(u)

        # 2. AGENTES
        agentes = [
            ("AG-101", "Oficial Ricardo Milos", "Patrullero", "Activo", 1), 
            ("AG-102", "Oficial Sarah Connor", "Vialidad", "Activo", 1)
        ]
        cursor.executemany('''INSERT OR IGNORE INTO agentes 
            (numero_placa, nombre_completo, cargo, estado, id_usuario_registro) 
            VALUES (?,?,?,?,?)''', agentes)

        # 3. PROPIETARIOS
        propietarios = [
            ("Juan Pérez López", "PELJ800101HDFRRN01", "Calle 60 #123", "9991234567", "juan@mail.com", "Vigente", 1),
            ("María García Sosa", "GASM900505MDFRRN02", "Av. Itzaes #456", "9997654321", "maria@mail.com", "Vigente", 1),
            ("Carlos López Ruiz", "LORC750312HDFRRN03", "Calle 50 #789", "9995551122", "carlos.lopez@mail.com", "Suspendida", 1) # <-- OJO: Suspendida
        ]
        cursor.executemany('''INSERT OR IGNORE INTO propietarios 
            (nombre_completo, curp, direccion, telefono, correo_electronico, estado_licencia, id_usuario_registro) 
            VALUES (?,?,?,?,?,?,?)''', propietarios)

        # 4. VEHÍCULOS
        vehiculos = [
            ("VIN00000000000001", "YUC-1001", "Toyota", "Corolla", 2022, "Gris", "Sedán", "Nacional", 1, 1), # De Juan
            ("VIN00000000000002", "YUC-2001", "Nissan", "NP300", 2023, "Blanco", "Camioneta", "Nacional", 2, 1), # De María
            ("VIN00000000000003", "YUC-3001", "Chevrolet", "Chevy", 2010, "Negro", "Hatchback", "Fronterizo", 3, 1) # De Carlos
        ]
        cursor.executemany('''INSERT OR IGNORE INTO vehiculos 
            (vin, placa, marca, modelo, anio, color, clase, procedencia, id_propietario, id_usuario_registro) 
            VALUES (?,?,?,?,?,?,?,?,?,?)''', vehiculos)

        # 5. INFRACCIONES
        infracciones = [
            ("FOL-00001", "VIN00000000000001", 1, "2026-02-20", "10:30", "Centro Histórico", "Exceso de velocidad", "Art. 45", 1500.0, "Pendiente", 1),
            ("FOL-00002", "VIN00000000000002", 2, "2026-01-15", "14:15", "Periférico Norte", "Mal estacionado", "Art. 12", 850.0, "Pendiente", 1),
            ("FOL-00003", "VIN00000000000003", 1, "2025-12-31", "23:45", "Paseo de Montejo", "Ebriedad", "Art. 100", 8500.0, "Pendiente", 1)
        ]
        cursor.executemany('''INSERT OR IGNORE INTO infracciones 
            (folio, vin_infractor, id_agente, fecha, hora, lugar, tipo_infraccion, motivo, monto, estado, id_usuario_registro) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', infracciones)

        # 6. SIMULAR EL PASO DEL TIEMPO PARA LA AUDITORÍA
        time.sleep(1) 
        cursor.execute("UPDATE infracciones SET estado = 'Pagada', id_usuario_actualizacion = 2 WHERE folio = 'FOL-00002'") # Operador 1 cobra multa
        cursor.execute("UPDATE vehiculos SET estado_legal = 'Reporte de robo', id_usuario_actualizacion = 1 WHERE vin = 'VIN00000000000003'") # Admin reporta robo de Chevy
        
        conexion.commit()

        # =====================================================================
        # GUÍA DE PRUEBAS PARA IMPRIMIR EN CONSOLA (PARA LOS TESTERS)
        # =====================================================================
        print("\n Base de datos generada con éxito y Triggers disparados.")
        print("\n" + "="*60)
        print(" GUÍA DE PRUEBAS PARA QA (TESTERS) 📋")
        print("="*60)
        
        print("\n🔹 CASO 1: SEGURIDAD Y PERMISOS DE ROLES (Expected: ÉXITO PARCIAL)")
        print("  Acción: Inicia sesión con 'operador_1' (pass: operador123).")
        print("  Prueba: Revisa el menú lateral izquierdo.")
        print("  Debe pasar: NO debes poder ver los botones de 'Usuarios' ni 'Infracciones'.")
        print("  Debe pasar: En las pantallas de vehículos, NO debes ver quién modificó los registros.")

        print("\n🔹 CASO 2: BLOQUEO POR MULTAS PENDIENTES (Expected: FALLO INTENCIONAL)")
        print("  Acción: Ve a 'Vehículos' -> 'Modificar' y busca la placa 'YUC-1001'.")
        print("  Prueba: Intenta hacerle un Cambio de Propietario o Reemplacamiento.")
        print("  Debe pasar: El sistema DEBE BLOQUEARTE y arrojar un error rojo porque el auto tiene la multa FOL-00001 PENDIENTE.")

        print("\n🔹 CASO 3: REGLA DE NEGOCIO - LICENCIA SUSPENDIDA (Expected: FALLO INTENCIONAL)")
        print("  Acción: Ve a 'Vehículos' -> 'Modificar' y busca la placa 'YUC-2001'.")
        print("  Prueba: Intenta transferirle este auto a la CURP 'LORC750312HDFRRN03' (Carlos López).")
        print("  Debe pasar: El sistema DEBE RECHAZAR el trámite porque Carlos tiene la licencia 'Suspendida'.")

        print("\n🔹 CASO 4: ETIQUETAS DE AUDITORÍA (Expected: ÉXITO)")
        print("  Acción: Cierra sesión e ingresa como 'admin_central' (pass: admin123).")
        print("  Prueba: Ve a buscar el vehículo 'YUC-3001'.")
        print("  Debe pasar: El auto debe salir con 'Reporte de robo'.")
        print("  Debe pasar: En la parte inferior, DEBE APARECER un texto chiquito diciendo que 'admin_central' fue quien lo modificó por última vez.")

        print("\n🔹 CASO 5: LA CAJA NEGRA - REPORTE 11 (Expected: ÉXITO)")
        print("  Acción: Estando como Admin, ve a la pestaña 'Reportes'.")
        print("  Prueba: Genera el Reporte número '11. Historial Completo de Movimientos'.")
        print("  Debe pasar: Debes ver una tabla detallada con todas las 'CREACIONES' iniciales de este script, y arriba deben salir las 'ACTUALIZACIONES' simuladas.")
        print("  Prueba extra: Haz clic en 'Exportar CSV' y verifica que el Excel se abra bien y no esté vacío.")
        
        print("\n" + "="*60)
        print("Porfa testeen todo ;v")

    except Exception as e:
        print(f"\n❌ Error grave al cargar semilla: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    generar_datos_prueba()