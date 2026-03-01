class Usuario:
    """
    Representa a una persona con credenciales de acceso al sistema.
    """
    def __init__(self, nombre_usuario, password, rol, estado="Activo", id_usuario=None, 
                id_usuario_registro=None, id_usuario_actualizacion=None):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.password = password  # Nota: En producción esto debería ser un hash, no texto plano.
        
        # El rol determinará qué pantallas puede ver en la interfaz
        # Valores permitidos según doc: Administrador, Operador Administrativo, Agente de Tránsito, Supervisor
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.password = password
        self.rol = rol 
        self.estado = estado

        # Trazabilidad
        self.id_usuario_registro = id_usuario_registro
        self.id_usuario_actualizacion = id_usuario_actualizacion
        
    def __repr__(self):
        return f"<Usuario: {self.nombre_usuario} - Rol: {self.rol} ({self.estado})>"