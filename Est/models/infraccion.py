class Infraccion:
    """
    Registro administrativo generado por una falta cometida por un vehículo.
    """
    def __init__(self, vin_infractor, id_agente, fecha, hora, lugar, 
                tipo_infraccion, motivo, monto, licencia_conductor=None, 
                estado="Pendiente", folio=None, id_usuario_registro=None):
        
        self.folio = folio # Identificador único generado automáticamente 
        self.vin_infractor = vin_infractor # Llave foránea hacia el vehículo 
        self.id_agente = id_agente # Llave foránea hacia el agente emisor 
        
        # Datos inmutables del hecho
        self.fecha = fecha
        self.hora = hora
        self.lugar = lugar
        self.tipo_infraccion = tipo_infraccion
        self.motivo = motivo
        self.monto = monto
        
        self.licencia_conductor = licencia_conductor # Opcional (ej. fotomultas) 
        self.estado = estado # Pendiente / Pagada / Cancelada 
        self.id_usuario_registro = id_usuario_registro

    def __repr__(self):
        return f"<Infracción {self.folio} - VIN: {self.vin_infractor} - ${self.monto} ({self.estado})>"