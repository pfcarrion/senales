import json
import re
from datetime import datetime

# Limpia los mensajes antes de pasarlos por la expresión regular:
def limpiar_mensaje(mensaje):
    # Eliminar caracteres especiales que pueden interferir con la detección
    caracteres_a_remover = ["•", ":", "⏰", "📊", "🚥", "🥇🏆", "💶", "⌛️", "🕖", "✅", "🟥", "🟢", "📲", "¿", "?", "➡️"]
    for char in caracteres_a_remover:
        mensaje = mensaje.replace(char, "")

    # Eliminar espacios dobles y limpiar
    mensaje = re.sub(r'\s+', ' ', mensaje).strip()

    # Eliminar comillas simples o dobles
    mensaje = mensaje.replace("'", "").replace('"', '')

    return mensaje

# Función para cargar patrones de exclusión desde un archivo
def cargar_patrones_exclusion(ruta_archivo="noprocesar.txt"):
    """Carga patrones de exclusión desde un archivo de texto."""
    patrones = []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            bloque = []
            for line in archivo:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignorar comentarios
                    bloque.append(line)
                else:
                    if bloque:
                        patrones.append(" ".join(bloque))  # Une líneas en un solo patrón
                        bloque = []
            if bloque:
                patrones.append(" ".join(bloque))  # Para capturar el último bloque
        print(f"Patrones cargados: {len(patrones)}")
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo '{ruta_archivo}'. No se aplicarán exclusiones.")
    except Exception as e:
        print(f"Error al cargar los patrones: {e}")
    return patrones

# Mejora en la Exclusión de Mensajes
def mensaje_excluido(mensaje, patrones_exclusion):
    """Verifica si un mensaje debe ser excluido comparándolo con los patrones cargados."""
    mensaje = normalizar_mensaje(mensaje)  # Normaliza el mensaje antes de compararlo
    if any(patron in mensaje for patron in patrones_exclusion):
        print(f"Mensaje excluido: {mensaje[:50]}...")  # Solo muestra los primeros 50 caracteres
        return True
    return False

# Normalizar mensaje
def normalizar_mensaje(mensaje):
    """Limpia y normaliza un mensaje de señal de trading."""
    mensaje = limpiar_mensaje(mensaje)
    return " ".join(mensaje.split()).strip()

# Expresión regular para el tiempo (ajuste final)
regex_tiempo = re.compile(r"(\d+\s*min(?:utes)?|\d+\s*m\d+|\d+min|M\d+|\d+)", re.IGNORECASE)

# Expresiones regulares ajustadas
regex_formato_general = re.compile(r"(\w{3,6}(?:\/\w{3,6}|OTC))\s*(\d{1,2}:\d{2}|\d{1,2})?\s*(⬆️|⬇️|CALL|PUT)?")

# Patrón para formato básico:
regex_formato_basico = re.compile(r"(\w{3,6}(?:\/\w{3,6}|OTC))\s*(\d{1,2}:\d{2})?\s*(⬆️|⬇️|CALL|PUT)")

# Patrón para formato avanzado (con más detalles):
regex_formato_avanzado = re.compile(
    r"""
    (?P<divisa>[A-Z]{3}[/-]?[A-Z]{3}(?:-OTC)?)      # Divisa (GBPJPY, EUR/USD, EURUSD-OTC)
    .*?                                            # Cualquier texto intermedio
    (?P<direccion>Venta|Compra|⬆️|⬇️|🔼|🔻|arriba|bajo|up|down|call|put)? # Dirección opcional
    .*?                                            # Cualquier texto intermedio
    (?P<entrada>\d{2}:\d{2})                       # Hora de entrada (HH:MM)
    .*?                                            # Cualquier texto intermedio
    (?P<expiracion>M\d+)                           # Expiración (M5, M10, etc.)
    """,
    re.IGNORECASE | re.VERBOSE
)

# Patrón para formato más complejo (con protección de pérdida y más texto adicional):
regex_formato_complejo = re.compile(
    r"""
    (?P<divisa>[A-Z]{3}[\/-]?[A-Z]{3}(?:-OTC)?)       # Divisa (GBPJPY, EUR/USD, EURUSD-OTC)
    .*                                              # Cualquier texto intermedio
    (?P<direccion>Venta|Compra|⬆️|⬇️|🔼|🔻|⬆|⬇|arriba|bajo|up|down|call|put)?  # Dirección opcional
    .*                                              # Cualquier texto intermedio
    (?P<entrada>\d{2}:\d{2})                         # Hora de entrada (Formato HH:MM)
    .*                                              # Cualquier texto intermedio
    (?P<expiracion>M\d+)                             # Expiración (M5, M10, etc.)
    .*                                              # Cualquier texto intermedio
    (?P<proteccion>Hasta \d+ protección en caso de derrota)  # Protección de pérdida
    """,
    re.IGNORECASE | re.VERBOSE
)

# Expresión regular para la dirección
regex_direccion = re.compile(r"(⬆️|⬇️|🔼|🔻|⬆|⬇|arriba|bajo|up|down|call|put|llamar|poner|llamada|pon)", re.IGNORECASE)

# Diccionario de divisas ISO 4217
divisas_iso4217 = {
    'USD': 'Dólar estadounidense',
    'EUR': 'Euro',
    'JPY': 'Yen japonés',
    'GBP': 'Libra esterlina',
    'AUD': 'Dólar australiano',
    'CAD': 'Dólar canadiense',
    'CHF': 'Franco suizo',
    'CNY': 'Yuan chino',
    'MXN': 'Peso mexicano',
    'NZD': 'Dólar neozelandés',
    'INR': 'Rupia india',
    # Agrega más divisas según sea necesario
}

# Validacion de divisas (todas las divisas con el formato correcto)
divisas_validas = re.compile(r"([A-Z]{3}/?[A-Z]{3}(?:\s?-?\s?OTC|\s?\(OTC\))?)", re.IGNORECASE)

# Expresión regular para las divisas (más precisa)
regex_divisa = re.compile(r"\b((?!MONEDA|GRATIS|TRADER|QUOTEX)[A-Z]{3}/?[A-Z]{3}(?:\s?-?\s?OTC|\s?\(OTC\))?)\b", re.IGNORECASE)

# Nuevas Regex para mensajes no reconocidos
regex_divisa_nuevo = re.compile(r"([A-Z]{3,6}(?:-OTC)?)\s", re.IGNORECASE)
regex_tiempo_nuevo = re.compile(r"(m\d+|\d+\s*min)", re.IGNORECASE)

# Regex nuevas para los mensajes no reconocidos
regex_formato_libre = re.compile(r"Huso horario: UTC[+-]?\d+\s*•\s*([A-Z]{3,6}(?:-OTC)?)\s*-\s*(PUT|CALL)\s*-\s*(\d{1,2}:\d{2})\s*•\s*Caducidad:\s*(\d+\s*minutos|\d+\s*min|M\d+)", re.IGNORECASE)
#Regex para los mensajes de Quotex (Simplificada)
regex_formato_quotex = re.compile(r"Horario: UTC[+-]?\d+\s*\(COLOMBIA\)\s*•\s*(M\d+\s*[A-Z]{3,6}(?:\s?OTC)?)\s*•\s*(\d{1,2}:\d{2})\s*(arriba)", re.IGNORECASE)
regex_formato_time = re.compile(r"([A-Z]{3}\/?(?:[A-Z]{3}|OTC))\s*Time:\s*(\d+\s*min)\s*(call)", re.IGNORECASE)
#Regex para los mensajes con "down" (Simplificada)
regex_formato_down = re.compile(r"([A-Z]{3,6}(?:-OTC)?(?: - OTC)?)\s*(m\d+|\d+)\s*(down|⬇️)", re.IGNORECASE)
#Regex para los mensajes con "Abajo" (Simplificada)
regex_formato_abajo = re.compile(r"Par de divisas:\s*([A-Z]{3}\/[A-Z]{3}\s*\(OTC\))\s*-\s*Abajo\s*Tiempo de negociaci\u00f3n:\s*(\d+\s*Minuto)", re.IGNORECASE)
#Regex para los mensajes con "MINUTES DOWN" (Simplificada)
regex_formato_minutes_down = re.compile(r"([A-Z]{3}\/?(?:[A-Z]{3}|OTC))\s*(\d+\s*MINUTES)\s*DOWN", re.IGNORECASE)

# Nueva regex para la señal específica con SELL, BUY, UP, DOWN
regex_formato_zar = re.compile(r"([A-Z]{3,}(?:\/[A-Z]{3,})?(?:\s?OTC)?)\s*Candle &Expiry Time = (\d+)\s*min\s*(SELL|BUY|UP|DOWN)", re.IGNORECASE)

# Nueva regex especifica para SELL/BUY con "on the next candle" opcional
regex_formato_sell_buy = re.compile(r"([A-Z]{3,}(?:\/[A-Z]{3,})?(?:\s?OTC)?)\s*Candle &Expiry Time = (\d+)\s*min\s*(SELL|BUY)(?:\s*on the next Candle)?", re.IGNORECASE)


# Nueva Regex generica para capturar cualquier mensaje
regex_generica = re.compile(r"(.+)")

# Normalizar dirección (CALL/PUT)
def normalizar_direccion(direccion):
    print(f"Normalizando dirección: {direccion}")
    if direccion in {"call", "arriba", "⬆️", "🔼", "⬆", "up", "compra", "llamar", "alto", "llamada", "buy"}:
        return "CALL"
    elif direccion in {"put", "bajo", "⬇️", "🔻", "⬇", "down", "venta", "poner", "abajo", "pon", "sell"}:
        return "PUT"
    return direccion

# Consolidar extracción de datos (Evitar duplicación):
def extraer_datos(mensaje):
    datos = {}

    # Primero verificar si coincide con regex_generica
    match_generica = regex_generica.search(mensaje)
    if match_generica:
       print(f"Mensaje capturado por regex_generica: {match_generica.group(0)}")

    # Luego verificar si coincide con regex_formato_sell_buy
    match_sell_buy = regex_formato_sell_buy.search(mensaje)
    if match_sell_buy:
         datos["divisa"] = match_sell_buy.group(1).strip() # Eliminamos espacios en blanco
         datos["tiempo"] = match_sell_buy.group(2) + " min"
         datos["direccion"] = match_sell_buy.group(3)
         print(f"Datos extraidos con regex_formato_sell_buy: {datos}")
         return datos

    # Luego verificar si coincide con regex_formato_zar
    match_zar = regex_formato_zar.search(mensaje)
    if match_zar:
        datos["divisa"] = match_zar.group(1).strip() # Eliminamos espacios en blanco
        datos["tiempo"] = match_zar.group(2) + " min"
        datos["direccion"] = match_zar.group(3)
        print(f"Datos extraidos con regex_formato_zar: {datos}")
        return datos

    # Si no coincide con regex_formato_zar, buscar otros patrones
    match_divisa = regex_divisa.search(mensaje)
    datos["divisa"] = match_divisa.group(1) if match_divisa else "INDEFINIDA"

    match_tiempo = regex_tiempo.search(mensaje)
    datos["tiempo"] = match_tiempo.group(0) if match_tiempo else "Indefinido"

    match_direccion = regex_direccion.search(mensaje)
    datos["direccion"] = match_direccion.group(0) if match_direccion else "INDEFINIDA"

    if "INDEFINIDA" in list(datos.values()):
        match_libre = regex_formato_libre.search(mensaje)
        if match_libre:
            datos["divisa"] = match_libre.group(1)
            datos["direccion"] = match_libre.group(2)
            datos["tiempo"] = match_libre.group(3)
            return datos

        match_quotex = regex_formato_quotex.search(mensaje)
        if match_quotex:
            datos["divisa"] = match_quotex.group(1)
            datos["direccion"] = "CALL"
            datos["tiempo"] = match_quotex.group(2)
            return datos

        match_time = regex_formato_time.search(mensaje)
        if match_time:
            datos["divisa"] = match_time.group(1)
            datos["direccion"] = "CALL"
            datos["tiempo"] = match_time.group(2)
            return datos

        match_down = regex_formato_down.search(mensaje)
        if match_down:
            datos["divisa"] = match_down.group(1)
            datos["direccion"] = "PUT"
            datos["tiempo"] = match_down.group(2)
            return datos

        match_abajo = regex_formato_abajo.search(mensaje)
        if match_abajo:
            datos["divisa"] = match_abajo.group(1)
            datos["direccion"] = "PUT"
            datos["tiempo"] = match_abajo.group(2)
            return datos

        match_minutes_down = regex_formato_minutes_down.search(mensaje)
        if match_minutes_down:
           datos["divisa"] = match_minutes_down.group(1)
           datos["direccion"] = "PUT"
           datos["tiempo"] = match_minutes_down.group(2)
           return datos

    return datos

# 🔹 Función para corregir el par de divisas cuando falta la "C"
def corregir_otc(par):
    if re.search(r'\bOT\b', par):  # Si encuentra "OT" sin "C"
        return par.replace(" OT", " OTC")  # Corrige a "OTC"
    return par

# Función para extraer el par de divisas con corrección automática
def extraer_divisa(mensaje):
    match = re.search(r'\b([A-Z]{2,4}\/[A-Z]{2,4}|[A-Z]{3,5}-OTC)\b', mensaje.upper())
    if match:
        return match.group(0).replace(" ", "").replace("-", "")
    return None

# Procesar mensajes
def procesar_mensajes(mensajes):
    señales = []
    mensajes_no_reconocidos = []

    for mensaje in mensajes:
        mensaje_normalizado = normalizar_mensaje(mensaje)

        # Extraer datos utilizando las expresiones regulares definidas
        datos = extraer_datos(mensaje_normalizado)

        # Normalizamos la dirección después de la extracción
        direccion_normalizada = normalizar_direccion(datos["direccion"])

        # Generamos el timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        señal = {
            "divisa": datos["divisa"],
            "tiempo": datos["tiempo"],
            "direccion": direccion_normalizada,
            "timestamp": timestamp
        }

        # Si toda la información fue extraída correctamente agregamos la señal a la lista
        if "INDEFINIDA" not in list(señal.values()):
           señales.append(señal)
        else:
           mensajes_no_reconocidos.append(mensaje)

    # Guardamos las señales procesadas en un archivo JSON
    with open("senales.json", "w") as json_file:
        json.dump(señales, json_file, indent=4)
        print(f"Señales guardadas en senales.json ({len(señales)} señales procesadas)")

    # Guardamos los mensajes no reconocidos en un archivo JSON
    if mensajes_no_reconocidos:
        with open("mensajes_no_reconocidos.json", "w") as json_file:
           json.dump(mensajes_no_reconocidos, json_file, indent=4)
           print(f"Mensajes no reconocidos guardados en mensajes_no_reconocidos.json ({len(mensajes_no_reconocidos)} mensajes)")

def leer_mensajes_desde_archivo(ruta_archivo="prueba.txt"):
    """Lee los mensajes desde un archivo de texto, agrupando líneas que forman un mensaje."""
    mensajes = []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            bloque_mensaje = []
            for line in archivo:
                line = line.strip()
                if line:  # Si la línea no está vacía, la agrega al bloque
                    bloque_mensaje.append(line)
                elif bloque_mensaje:  # Si la línea está vacía y hay un bloque, une el bloque y lo agrega a mensajes
                    mensajes.append(" ".join(bloque_mensaje))
                    bloque_mensaje = []
            if bloque_mensaje: # Agrega el último bloque si existe
                mensajes.append(" ".join(bloque_mensaje))
        print(f"Mensajes cargados desde '{ruta_archivo}': {len(mensajes)}")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
    return mensajes

if __name__ == "__main__":
    try:
        # Cargar patrones de exclusión
        patrones_exclusion = cargar_patrones_exclusion()

        # Leer mensajes desde el archivo prueba.txt
        mensajes = leer_mensajes_desde_archivo()

        # Filtrar mensajes que se deben excluir
        mensajes_a_procesar = [mensaje for mensaje in mensajes if not mensaje_excluido(mensaje, patrones_exclusion)]

        # Procesar los mensajes restantes
        procesar_mensajes(mensajes_a_procesar)

    except Exception as e:
        print(f"Error procesando mensajes: {e}")
