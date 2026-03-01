class Propietario:
    """
    Representa a la persona física responsable legal de uno o más vehículos
    """
    def __init__(self, nombre_completo, curp, direccion, telefono, 
            correo_electronico, estado_licencia, estado="Activo", id_propietario=None,
            id_usuario_registro=None, id_usuario_actualizacion=None):
        
        # El ID es None al crear uno nuevo, pero se llena cuando lo leemos de la base de datos
        self.id_propietario = id_propietario 
        self.nombre_completo = nombre_completo
        self.curp = curp
        self.direccion = direccion
        self.telefono = telefono
        self.correo_electronico = correo_electronico
        self.estado_licencia = estado_licencia
        self.estado = estado

        # Trazabilidad
        self.id_usuario_registro = id_usuario_registro
        self.id_usuario_actualizacion = id_usuario_actualizacion
    def __repr__(self):
        # Esto es solo para que si imprimes el objeto en consola, se lea bonito
        return f"<Propietario: {self.nombre_completo} - CURP: {self.curp}>"