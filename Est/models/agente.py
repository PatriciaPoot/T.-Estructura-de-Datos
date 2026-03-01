class Agente:
    """
    Representa a un funcionario municipal autorizado para emitir infracciones. 
    """
    def __init__(self, numero_placa, nombre_completo, cargo, estado="Activo", id_agente=None,
                id_usuario_registro=None, id_usuario_actualizacion=None):
        
        self.id_agente = id_agente # Generado por la base de datos 
        self.numero_placa = numero_placa # Identificador oficial único 
        self.nombre_completo = nombre_completo
        self.cargo = cargo
        self.estado = estado # Activo / Inactivo
        
        # Trazabilidad
        self.id_usuario_registro = id_usuario_registro
        self.id_usuario_actualizacion = id_usuario_actualizacion

    def __repr__(self):
        return f"<Agente {self.numero_placa}: {self.nombre_completo} - {self.estado}>"