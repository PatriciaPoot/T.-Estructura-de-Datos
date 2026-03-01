"""
Catálogos oficiales del sistema.

Este módulo centraliza todos los valores predefinidos utilizados por el sistema
para garantizar consistencia entre la interfaz, la validación y la lógica de negocio.

NO contiene lógica.
NO realiza validaciones.
NO accede a base de datos.
"""

# =========================
# VEHÍCULOS
# =========================

ESTADOS_VEHICULO = [
    "Activo",
    "Baja temporal",
    "Reporte de robo",
    "Recuperado",
    "En corralón"
]

CLASES_VEHICULO = [
    "Sedán",
    "Motocicleta",
    "Camión",
    "Camioneta",
    "Autobús",
    "Hatchback"
]

PROCEDENCIAS_VEHICULO = [
    "Nacional",
    "Importado"
]

# =========================
# MARCAS, MODELOS Y SUS CLASES PERMITIDAS (Cascada Doble)
# =========================
# Diccionario donde la clave es la Marca y el valor es otro diccionario.
# Cada Modelo contiene una LISTA con las clases en las que se fabrica.

MARCAS_MODELOS_VEHICULO = {
    # ===== MARCAS GENERALES =====
    "Nissan": {
        "Versa": ["Sedán"],      # El más vendido de México
        "Sentra": ["Sedán"],      # Clásico
        "Tsuru": ["Sedán"],       # Icono mexicano
        "Altima": ["Sedán"],      # Mediano
        "March": ["Hatchback"],   # Popular
        "NP300": ["Camioneta"],   # La reina de las pickups
        "Kicks": ["Camioneta"],   # SUV
        "Frontier": ["Camioneta"] # Pickup mediana
    },
    "Toyota": {
        "Corolla": ["Sedán"],          # El auto más vendido del mundo
        "Camry": ["Sedán"],            # Best seller en USA
        "Prius": ["Sedán", "Hatchback"], # Híbrido famoso
        "Yaris": ["Sedán", "Hatchback"], # Económico
        "Hilux": ["Camioneta"],         # Pickup indestructible
        "RAV4": ["Camioneta"],          # SUV pionero
        "Tacoma": ["Camioneta"],        # Pickup mediana
        "4Runner": ["Camioneta"],       # SUV off-road
        "Supra": ["Hatchback"]          # Deportivo
    },
    "Honda": {
        "Civic": ["Sedán", "Hatchback"], # Icono juvenil
        "City": ["Sedán", "Hatchback"],  # Popular en México
        "Accord": ["Sedán"],             # Sedán familiar
        "Fit": ["Hatchback"],            # Compacto
        "CR-V": ["Camioneta"],           # SUV familiar
        "HR-V": ["Camioneta"],           # SUV subcompacto
        "Pilot": ["Camioneta"],          # SUV grande
        "Odyssey": ["Autobús"]           # Minivan
    },
    "Chevrolet": {
        "Aveo": ["Sedán", "Hatchback"],  # El segundo más vendido
        "Chevy": ["Sedán", "Hatchback"], # Icono mexicano
        "Spark": ["Hatchback"],          # City car
        "Onix": ["Sedán", "Hatchback"],  # Moderno
        "Beat": ["Hatchback"],           # Joven
        "Camaro": ["Sedán"],             # Muscle car
        "Silverado": ["Camioneta"],      # Pickup grande
        "S10": ["Camioneta"],            # Pickup mediana
        "Captiva": ["Camioneta"],        # SUV
        "Trax": ["Camioneta"],           # SUV pequeño
        "Blazer": ["Camioneta"]          # SUV clásico
    },
    "Volkswagen": {
        "Jetta": ["Sedán"],          # El alemán más vendido en México
        "Vento": ["Sedán"],          # Sedán económico
        "Gol": ["Hatchback"],        # Popular
        "Polo": ["Hatchback"],       # Europeo
        "Golf": ["Hatchback"],       # Icono
        "Beetle": ["Hatchback"],     # Escarabajo, clásico
        "Tiguan": ["Camioneta"],     # SUV
        "Taos": ["Camioneta"],       # SUV nuevo
        "Amarok": ["Camioneta"],     # Pickup
        "Combibus": ["Autobús"]      # Clásico
    },
    "Mazda": {
        "Mazda 2": ["Sedán", "Hatchback"], # Compacto
        "Mazda 3": ["Sedán", "Hatchback"], # Best seller
        "Mazda 6": ["Sedán"],              # Sedán grande
        "MX-5": ["Sedán"],                  # Miata, deportivo
        "CX-3": ["Camioneta"],              # SUV pequeño
        "CX-5": ["Camioneta"],              # SUV familiar
        "CX-30": ["Camioneta"],             # SUV moderno
        "CX-50": ["Camioneta"]              # SUV aventurero
    },
    "Kia": {
        "K3": ["Sedán"],              # Best seller en México
        "K5": ["Sedán"],              # Sedán deportivo
        "Rio": ["Sedán", "Hatchback"], # Económico
        "Forte": ["Sedán"],           # Compacto
        "Soul": ["Hatchback"],        # Cuadrado peculiar
        "Seltos": ["Camioneta"],      # SUV
        "Sportage": ["Camioneta"],    # SUV clásico
        "Sorento": ["Camioneta"],     # SUV grande
        "Telluride": ["Camioneta"]    # SUV lujoso
    },
    "Hyundai": {
        "Grand i10": ["Sedán", "Hatchback"], # City car
        "Accent": ["Sedán", "Hatchback"],    # Económico
        "Elantra": ["Sedán"],                 # Compacto
        "Sonata": ["Sedán"],                  # Mediano
        "Tucson": ["Camioneta"],              # SUV
        "Creta": ["Camioneta"],                # SUV pequeño
        "Santa Fe": ["Camioneta"],             # SUV grande
        "Kona": ["Camioneta"]                  # SUV moderno
    },
    "Ford": {
        "Fiesta": ["Sedán", "Hatchback"], # Popular
        "Focus": ["Sedán", "Hatchback"],  # Compacto
        "Fusion": ["Sedán"],              # Mediano
        "Mustang": ["Sedán"],             # Muscle car legendario
        "Ranger": ["Camioneta"],          # Pickup
        "F-150": ["Camioneta"],           # La pickup más vendida
        "Maverick": ["Camioneta"],        # Pickup pequeña
        "Escape": ["Camioneta"],          # SUV
        "Explorer": ["Camioneta"],        # SUV grande
        "Bronco": ["Camioneta"]           # Off-road clásico
    },
    "Suzuki": {
        "Swift": ["Sedán", "Hatchback"], # Deportivo económico
        "Dzire": ["Sedán"],               # Sedán
        "Baleno": ["Hatchback"],          # Compacto
        "Ignis": ["Hatchback"],           # Aventurero pequeño
        "Vitara": ["Camioneta"],          # SUV
        "Jimny": ["Camioneta"],           # 4x4 pequeño
        "A-Cross": ["Camioneta"]          # SUV híbrido
    },
    "BMW": {
        "Serie 1": ["Hatchback"],      # Compacto premium
        "Serie 2": ["Sedán"],          # Coupé
        "Serie 3": ["Sedán"],          # El deportivo ejecutivo
        "Serie 4": ["Sedán"],          # Gran Coupé
        "Serie 5": ["Sedán"],          # Ejecutivo
        "Serie 7": ["Sedán"],          # Lujo
        "X1": ["Camioneta"],           # SUV pequeño
        "X3": ["Camioneta"],           # SUV mediano
        "X5": ["Camioneta"],           # SUV grande
        "X6": ["Camioneta"],           # SUV coupé
        "Z4": ["Sedán"]                 # Roadster
    },
    "Mercedes-Benz": {
        "Clase A": ["Hatchback", "Sedán"], # Compacto
        "Clase C": ["Sedán"],              # El ejecutivo
        "Clase E": ["Sedán"],              # Sedán de lujo
        "Clase S": ["Sedán"],              # El pináculo
        "CLA": ["Sedán"],                   # Coupé 4 puertas
        "GLA": ["Camioneta"],               # SUV pequeño
        "GLC": ["Camioneta"],               # SUV mediano
        "GLE": ["Camioneta"],               # SUV grande
        "GLS": ["Camioneta"],               # SUV de lujo
        "Sprinter": ["Autobús", "Camión"]   # Van
    },
    "Audi": {
        "A1": ["Hatchback"],        # Pequeño
        "A3": ["Sedán", "Hatchback"], # Compacto premium
        "A4": ["Sedán"],            # El ejecutivo
        "A5": ["Sedán"],            # Coupé
        "A6": ["Sedán"],            # Mediano
        "A7": ["Sedán"],            # Sportback
        "A8": ["Sedán"],            # Lujo
        "Q3": ["Camioneta"],        # SUV pequeño
        "Q5": ["Camioneta"],        # SUV mediano
        "Q7": ["Camioneta"],        # SUV grande
        "R8": ["Sedán"]             # Superdeportivo
    },
    "Tesla": {
        "Model S": ["Sedán"],       # El que empezó todo
        "Model 3": ["Sedán", "Hatchback"], # El popular
        "Model X": ["Camioneta"],   # SUV con alas
        "Model Y": ["Camioneta"],   # SUV compacto
        "Cybertruck": ["Camioneta"] # El futurista
    },
    "Jeep": {
        "Wrangler": ["Camioneta"],    # El off-road por excelencia
        "Cherokee": ["Camioneta"],    # Clásico
        "Grand Cherokee": ["Camioneta"], # Lujo off-road
        "Compass": ["Camioneta"],      # SUV compacto
        "Renegade": ["Camioneta"],     # SUV pequeño
        "Gladiator": ["Camioneta"]     # Pickup off-road
    },
    "Volvo": {
        "XC40": ["Camioneta"],   # SUV pequeño
        "XC60": ["Camioneta"],   # SUV mediano
        "XC90": ["Camioneta"],   # SUV grande
        "S60": ["Sedán"],        # Sedán mediano
        "S90": ["Sedán"],        # Sedán grande
        "V60": ["Hatchback"]     # Wagon
    },
    "Porsche": {
        "911": ["Sedán"],        # El deportivo iconico
        "Cayenne": ["Camioneta"], # SUV deportivo
        "Macan": ["Camioneta"],   # SUV compacto
        "Panamera": ["Sedán"],    # Sedán deportivo
        "Taycan": ["Sedán"]       # Eléctrico deportivo
    },
    "Lexus": {
        "ES": ["Sedán"],          # Sedán de lujo
        "IS": ["Sedán"],          # Deportivo
        "LS": ["Sedán"],          # Sedán ultra lujo
        "NX": ["Camioneta"],      # SUV compacto
        "RX": ["Camioneta"],      # SUV mediano
        "LX": ["Camioneta"]       # SUV grande off-road
    },
    
    # ===== MARCAS CHINAS =====
    "MG": {
        "MG3": ["Hatchback"],  # City car
        "MG5": ["Sedán"],      # Sedán
        "MG6": ["Sedán"],      # Sedán deportivo
        "MG ZS": ["Camioneta"], # SUV
        "MG RX5": ["Camioneta"], # SUV
        "MG HS": ["Camioneta"]   # SUV
    },
    "BYD": {
        "Dolphin": ["Hatchback"],   # Eléctrico pequeño
        "Dolphin Mini": ["Hatchback"], # Más pequeño
        "Seal": ["Sedán"],          # Sedán eléctrico
        "Han": ["Sedán"],           # Sedán de lujo
        "Yuan": ["Camioneta"],       # SUV eléctrico
        "Tang": ["Camioneta"],       # SUV grande
        "Song": ["Camioneta"]        # SUV mediano
    },
    "Changan": {
        "Alsvin": ["Sedán"],     # Económico
        "CS35": ["Camioneta"],   # SUV pequeño
        "CS55": ["Camioneta"],   # SUV mediano
        "CS75": ["Camioneta"]    # SUV grande
    },
    
    # ===== MOTOCICLETAS =====
    "Yamaha": {
        "FZ25": ["Motocicleta"],
        "MT-07": ["Motocicleta"],
        "MT-09": ["Motocicleta"],
        "R3": ["Motocicleta"],
        "R6": ["Motocicleta"],
        "R1": ["Motocicleta"],
        "Crypton": ["Motocicleta"]
    },
    "Honda": {
        "CB190": ["Motocicleta"],
        "CB300": ["Motocicleta"],
        "CB500": ["Motocicleta"],
        "CBR500": ["Motocicleta"],
        "CBR600": ["Motocicleta"],
        "XR150": ["Motocicleta"],
        "Africa Twin": ["Motocicleta"]
    },
    "Italika": {
        "FT150": ["Motocicleta"],
        "DM200": ["Motocicleta"],
        "WS150": ["Motocicleta"],
        "RC250": ["Motocicleta"]
    }
}

# =========================
# COLORES DE VEHÍCULO
# =========================
COLORES_VEHICULO = [
    "Blanco",
    "Negro",
    "Gris",
    "Plateado",
    "Azul",
    "Rojo",
    "Marrón",
    "Beige",
    "Verde",
    "Amarillo",
    "Naranja",
    "Dorado",
    "Vino",
    "Burdeos",
    "Turquesa",
    "Celeste",
    "Morado",
    "Violeta",
    "Rosa",
    "Fucsia",
    "Magenta",
    "Cian",
    "Lima",
    "Oliva",
    "Teja",
    "Terracota",
    "Caqui",
    "Mostaza",
    "Coral",
    "Lavanda",
    "Melón",
    "Grafito",
    "Bronce",
    "Cobre",
    "Champán"
]

# =========================
# PROPIETARIOS
# =========================

ESTADOS_LICENCIA = [
    "Vigente",
    "Suspendida",
    "Cancelada / Vencida"
]

ESTADOS_PROPIETARIO = [
    "Activo",
    "Inactivo"
]

# =========================
# INFRACCIONES
# =========================

ESTADOS_INFRACCION = [
    "Pendiente",
    "Pagada",
    "Cancelada"
]

TIPOS_INFRACCION = [
    "Exceso de velocidad",
    "Estacionamiento prohibido",
    "No portar cinturón",
    "Uso de celular",
    "Conducir en estado de ebriedad",
    "Falta de documentos",
    "Otro"
]

TIPOS_CAPTURA_INFRACCION = [
    "En sitio",
    "Fotomulta"
]

# =========================
# AGENTES DE TRÁNSITO
# =========================

ESTADOS_AGENTE = [
    "Activo",
    "Inactivo"
]

# =========================
# USUARIOS DEL SISTEMA
# =========================

ROLES_USUARIO = [
    "Administrador",
    "Operador Administrativo",
    "Agente de Tránsito",
    "Supervisor"
]

TABULADOR_INFRACCIONES = {
    "EXCESO_VELOCIDAD": {
        "descripcion": "Exceso de velocidad",
        "articulo": "Art. 64",
        "multa": {"min": 1200.00, "max": 2500.00},
        "puntos": 3,
        "corralon": False
    },
    "ESTACIONAMIENTO_PROHIBIDO": {
        "descripcion": "Estacionamiento prohibido",
        "articulo": "Art. 75",
        "multa": {"min": 600.00, "max": 1200.00},
        "puntos": 1,
        "corralon": True
    },
    "CINTURON_SEGURIDAD": {
        "descripcion": "No portar cinturón",
        "articulo": "Art. 52",
        "multa": {"min": 900.00, "max": 1500.00},
        "puntos": 2,
        "corralon": False
    },
    "USO_CELULAR": {
        "descripcion": "Uso de celular",
        "articulo": "Art. 53",
        "multa": {"min": 2000.00, "max": 3500.00},
        "puntos": 4,
        "corralon": False
    },
    "ALCOHOL_EBRIEDAD": {
        "descripcion": "Conducir en estado de ebriedad",
        "articulo": "Art. 99",
        "multa": {"min": 4500.00, "max": 7000.00},
        "puntos": 6,
        "corralon": True,
        "suspension_licencia": True
    },
    "FALTA_DOCUMENTOS": {
        "descripcion": "Falta de documentos",
        "articulo": "Art. 34",
        "multa": {"min": 800.00, "max": 1500.00},
        "puntos": 0,
        "corralon": False
    },
    "OTRO": {
        "descripcion": "Otro",
        "articulo": "Art. 1 (General)",
        "multa": {"min": 100.00, "max": 10000.00},
        "puntos": 0,
        "corralon": False
    }
}

TIPOS_INFRACCION = [datos["descripcion"] for datos in TABULADOR_INFRACCIONES.values()]