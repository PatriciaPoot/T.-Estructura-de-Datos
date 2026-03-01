import sys
import os

# Agregamos la carpeta raíz del proyecto al camino de búsqueda de Python
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ruta_raiz)

from database.conexion import obtener_conexion
def crear_tablas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    
    # 1. Tabla Usuarios (Para el Login y seguridad)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            estado TEXT DEFAULT 'Activo',
            debe_cambiar_password INTEGER DEFAULT 1,
            
            -- COLUMNAS DE AUDITORÍA
            id_usuario_registro INTEGER,
            id_usuario_actualizacion INTEGER,
            
            FOREIGN KEY (id_usuario_registro) REFERENCES usuarios (id_usuario),
            FOREIGN KEY (id_usuario_actualizacion) REFERENCES usuarios (id_usuario)
        )
    ''')
    
    # 2. Tabla Agentes de Tránsito
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agentes (
            id_agente INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_placa TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            cargo TEXT,
            estado TEXT DEFAULT 'Activo',
            
            -- COLUMNAS DE AUDITORÍA
            id_usuario_registro INTEGER NOT NULL,
            id_usuario_actualizacion INTEGER,
            
            FOREIGN KEY (id_usuario_registro) REFERENCES usuarios (id_usuario),
            FOREIGN KEY (id_usuario_actualizacion) REFERENCES usuarios (id_usuario)
        )
    ''')
# 3. Tabla Propietarios [cite: 398, 400]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS propietarios (
            id_propietario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            curp TEXT UNIQUE NOT NULL,
            direccion TEXT,
            telefono TEXT,
            correo_electronico TEXT,
            estado_licencia TEXT,
            estado TEXT DEFAULT 'Activo',
            
            -- COLUMNAS DE AUDITORÍA
            id_usuario_registro INTEGER NOT NULL,
            id_usuario_actualizacion INTEGER,
            
            FOREIGN KEY (id_usuario_registro) REFERENCES usuarios (id_usuario),
            FOREIGN KEY (id_usuario_actualizacion) REFERENCES usuarios (id_usuario)
        )
    ''')
# 4. Tabla Vehículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehiculos (
            vin TEXT PRIMARY KEY,
            placa TEXT UNIQUE NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            anio INTEGER NOT NULL,
            color TEXT,
            clase TEXT NOT NULL,
            estado_legal TEXT DEFAULT 'Activo',
            procedencia TEXT NOT NULL,
            id_propietario INTEGER NOT NULL,
            
            -- COLUMNAS DE AUDITORÍA
            id_usuario_registro INTEGER NOT NULL,
            id_usuario_actualizacion INTEGER,
            
            FOREIGN KEY (id_propietario) REFERENCES propietarios (id_propietario),
            FOREIGN KEY (id_usuario_registro) REFERENCES usuarios (id_usuario),
            FOREIGN KEY (id_usuario_actualizacion) REFERENCES usuarios (id_usuario)
        )
    ''')
    # 5. Tabla Infracciones (Multas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infracciones (
            folio TEXT PRIMARY KEY,
            vin_infractor TEXT NOT NULL,
            id_agente INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            lugar TEXT NOT NULL,
            tipo_infraccion TEXT NOT NULL,
            motivo TEXT,
            monto REAL NOT NULL,
            licencia_conductor TEXT,
            estado TEXT DEFAULT 'Pendiente',
            
            -- NUEVAS COLUMNAS DE AUDITORÍA
            id_usuario_registro INTEGER NOT NULL,
            id_usuario_actualizacion INTEGER,
            
            FOREIGN KEY (vin_infractor) REFERENCES vehiculos (vin),
            FOREIGN KEY (id_agente) REFERENCES agentes (id_agente),
            FOREIGN KEY (id_usuario_registro) REFERENCES usuarios (id_usuario),
            FOREIGN KEY (id_usuario_actualizacion) REFERENCES usuarios (id_usuario)
        )
    ''')
# ==========================================
    # 6. TABLA DE BITÁCORA DE AUDITORÍA (CAJA NEGRA)
    # ==========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bitacora_auditoria (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora DATETIME DEFAULT (datetime('now', 'localtime')),
            tabla_afectada TEXT NOT NULL,
            id_registro_afectado TEXT NOT NULL,
            tipo_accion TEXT NOT NULL, 
            id_usuario INTEGER,
            
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        )
    ''')

    # ==========================================
    # 7. TRIGGERS (DISPARADORES AUTOMÁTICOS)
    # ==========================================

    # --- TRIGGERS PARA VEHÍCULOS ---
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_vehiculos_insert 
        AFTER INSERT ON vehiculos
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('vehiculos', NEW.vin, 'CREACIÓN', NEW.id_usuario_registro);
        END;
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_vehiculos_update 
        AFTER UPDATE ON vehiculos
        -- Solo registra si realmente hubo un cambio de usuario (evita falsos positivos)
        WHEN NEW.id_usuario_actualizacion IS NOT NULL 
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('vehiculos', NEW.vin, 'ACTUALIZACIÓN', NEW.id_usuario_actualizacion);
        END;
    ''')

    # --- TRIGGERS PARA PROPIETARIOS ---
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_propietarios_insert 
        AFTER INSERT ON propietarios
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('propietarios', NEW.curp, 'CREACIÓN', NEW.id_usuario_registro);
        END;
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_propietarios_update 
        AFTER UPDATE ON propietarios
        WHEN NEW.id_usuario_actualizacion IS NOT NULL
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('propietarios', NEW.curp, 'ACTUALIZACIÓN', NEW.id_usuario_actualizacion);
        END;
    ''')

    # --- TRIGGERS PARA INFRACCIONES ---
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_infracciones_insert 
        AFTER INSERT ON infracciones
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('infracciones', NEW.folio, 'CREACIÓN', NEW.id_usuario_registro);
        END;
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_infracciones_update 
        AFTER UPDATE ON infracciones
        WHEN NEW.id_usuario_actualizacion IS NOT NULL
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('infracciones', NEW.folio, 'ACTUALIZACIÓN', NEW.id_usuario_actualizacion);
        END;
    ''')

    # --- TRIGGERS PARA USUARIOS ---
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_usuarios_insert 
        AFTER INSERT ON usuarios
        WHEN NEW.id_usuario_registro IS NOT NULL
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('usuarios', NEW.nombre_usuario, 'CREACIÓN', NEW.id_usuario_registro);
        END;
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_usuarios_update 
        AFTER UPDATE ON usuarios
        WHEN NEW.id_usuario_actualizacion IS NOT NULL
        BEGIN
            INSERT INTO bitacora_auditoria (tabla_afectada, id_registro_afectado, tipo_accion, id_usuario)
            VALUES ('usuarios', NEW.nombre_usuario, 'ACTUALIZACIÓN', NEW.id_usuario_actualizacion);
        END;
    ''')

    conexion.commit()
    conexion.close()
    print("Base de datos y tablas creadas exitosamente.")

if __name__ == "__main__":
    crear_tablas()