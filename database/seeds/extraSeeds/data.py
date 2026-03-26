import uuid

def generate_id():
    # uuid7 is time-ordered, perfect for DB primary keys
    return str(uuid.uuid7())

# Format: (codigo, nombre)
DATA_TIPO_DOCUMENTO = [
    ("cc", "Cédula de Ciudadanía"),
    ("ce", "Cédula de Extranjería"),
    ("ti", "Tarjeta de Identidad"),
    ("pp", "Pasaporte"),
]
# Password shared across all seed instructors
SEED_PASSWORD = "Sena2024*"
# Format: (correo, nombre_completo, numero_documento, nombres, apellidos, sexo_codigo, ficha_numero)
DATA_INSTRUCTORES = [
    (
        "adriana.suarez@sena.edu.co", 
        "Adriana Lucía Suárez Torres", 
        "10987654", "ADRIANA LUCÍA", "SUÁREZ TORRES", 
        "f", "2900004"
    ),
    (
        "ricardo.mendoza@sena.edu.co", 
        "Ricardo Antonio Mendoza Villa", 
        "88234567", "RICARDO ANTONIO", "MENDOZA VILLA", 
        "m", "2900005"

    ),
    (
        "elena.beltran@sena.edu.co", 
        "Elena Patricia Beltrán Ruiz", 
        "60332119", "ELENA PATRICIA", "BELTRÁN RUIZ", 
        "f", "2900006"
    ),
]
# --- New Companies ---
# (razon_social, nit, sector, correo, telefono)
DATA_EMPRESAS = [
    ("Sistemas Globales E.U.", "9019876543", "Software", "admin@sglobales.com", "6075710011"),
    ("Logística del Norte SAS", "8901122334", "Logística", "rrhh@logisnorte.co", "6075822233"),
]

# --- New Apprentices (2 per Ficha) ---
# Format: (correo, nombre_full, doc, tipo_doc, nombres, apellidos, sexo, ficha_num, lectiva, concluida, productiva)
DATA_APRENDICES = [
    # Ficha 2900001
    ("mario.duarte@aprendiz.sena.edu.co", "Mario Alberto Duarte Casadiego", "1090888777", "cc", "MARIO ALBERTO", "DUARTE CASADIEGO", "m", "2900001", True, False, False),
    ("claudia.nieto@aprendiz.sena.edu.co", "Claudia Marcela Nieto Rojas", "1090999111", "cc", "CLAUDIA MARCELA", "NIETO ROJAS", "f", "2900001", False, True, True),
    
    # Ficha 2900002
    ("felipe.basto@aprendiz.sena.edu.co", "Felipe Andres Basto Leon", "1025777888", "ti", "FELIPE ANDRES", "BASTO LEON", "m", "2900002", True, False, False),
    ("paola.ortiz@aprendiz.sena.edu.co", "Paola Andrea Ortiz Guerrero", "1025666555", "ti", "PAOLA ANDREA", "ORTIZ GUERRERO", "f", "2900002", False, True, True),
    
    # Ficha 2900003
    ("jorge.vivas@aprendiz.sena.edu.co", "Jorge Luis Vivas Mendez", "1090444333", "cc", "JORGE LUIS", "VIVAS MENDEZ", "m", "2900003", True, False, False),
    ("diana.solano@aprendiz.sena.edu.co", "Diana Karime Solano Parra", "1090222888", "cc", "DIANA KARIME", "SOLANO PARRA", "f", "2900003", False, True, False),
]