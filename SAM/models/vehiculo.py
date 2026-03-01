class Vehiculo:
    """
    Representa una unidad motorizada registrada dentro del municipio.
    """
    def __init__(self, vin, placa, marca, modelo, anio, color, clase, procedencia,
                id_propietario, estado_legal="Activo",
                id_usuario_registro=None, id_usuario_actualizacion=None):
        
        # Atributos estructurales / inmutables
        self.vin = vin  # Identificador único e inmutable
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.clase = clase
        self.procedencia = procedencia
        
        # Atributos modificables
        self.placa = placa  # Única, pero modificable bajo procesos administrativos
        self.color = color
        self.estado_legal = estado_legal
        
        # Llave foránea que lo conecta con el dueño
        self.id_propietario = id_propietario
        
        # Trazabilidad
        self.id_usuario_registro = id_usuario_registro
        self.id_usuario_actualizacion = id_usuario_actualizacion

    def __repr__(self):
        return f"<Vehículo: {self.marca} {self.modelo} ({self.anio}) - Placa: {self.placa} - VIN: {self.vin}>"