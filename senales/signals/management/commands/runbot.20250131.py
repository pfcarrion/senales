import sys
import os
import django
from django.conf import settings
from telethon import TelegramClient, events
import logging
import re
from datetime import datetime, timedelta
import json
from django.utils.timezone import now

# Configuración inicial
#print("sys.path antes:", sys.path)       #Para verificar en pantalla
sys.path.append('/opt/senales/senales')  # Ruta del proyecto Django
#print("sys.path después:", sys.path)     # Para verificar en pantalla

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'senales.settings')
#print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))   #Para verificar en pantalla

# Configurar Django
django.setup()

# Archivo JSON donde se guardarán las señales
SENALES_JSON_PATH = "/opt/senales/senales/signals/static/senales/senales.json"

# Configuración básica de Telegram
api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
phone_number = settings.TELEGRAM_PHONE_NUMBER

# Inicializar cliente de Telethon
client = TelegramClient('nueva_name', api_id, api_hash)
client.start(phone=phone_number)
logging.basicConfig(level=logging.INFO)

# Diccionario de direcciones
direccion_map = {
    'call': 'ARRIBA',
    'put': 'BAJO',
    'arriba': 'ARRIBA',
    'bajo': 'BAJO',
    '⬆️': 'ARRIBA',
    '⬇️': 'BAJO',
    'up': 'ARRIBA',
    'down': 'BAJO'
}

# Expresión regular para capturar señales
regex_para_formato = re.compile(
    r"""
    ([A-Z]{3}[\/-]?[A-Z]{3}(?:-OTC)?|[A-Z]{6}(?:-OTC)?)    # Captura pares como EUR/USD, EURUSD, o EURUSD-OTC
    (?:\s*[-]\s*)?                                         # Opcional: espacio o guion entre el par
    (⬆️|⬇️|🔻|arriba|bajo|up|down|call|put)?                 # Captura la dirección
    \s*(\d{1,2})\s*[mM]?[iI]?[nN]?[uU]?[tT]?[eE]?[sS]?     # Captura el tiempo (Ej: 15 MINUTES o m15)
    """,
    re.IGNORECASE | re.VERBOSE
)


#regex_para_formato = re.compile(
#    r"([A-Z]{3}\/[A-Z]{3}|[A-Z]{6}(?:-OTC)?)\s*(⬆️|⬇️|🔻|arriba|bajo|up|down|call|put)\s*(\d+)\s*MINUTES?",
#    re.IGNORECASE
#)

# Función para cargar señales recientes desde el archivo JSON
def cargar_senales():
    try:
        if os.path.exists(SENALES_JSON_PATH):
            with open(SENALES_JSON_PATH, 'r', encoding='utf-8') as f:
                señales = json.load(f)

            # Filtrar señales caducadas
            señales = [
                señal for señal in señales if datetime.strptime(señal["caducidad"], "%Y-%m-%d %H:%M:%S") > now()
            ]

            return señales
        return []
    except Exception as e:
        logging.error(f"Error al cargar señales desde JSON: {e}")
        return []


# Función para guardar señales en el archivo JSON
def guardar_senales(senales):
    try:
        os.makedirs(os.path.dirname(SENALES_JSON_PATH), exist_ok=True)
        with open(SENALES_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(senales, f, ensure_ascii=False, indent=4)
        logging.info(f"Señales guardadas en {SENALES_JSON_PATH}")
    except Exception as e:
        logging.error(f"Error al guardar señales en JSON: {e}")

# Función para procesar mensajes y actualizar las señales
def procesar_mensaje(mensaje, horario_envio):
    # Buscar coincidencia con algún formato
    for formato, patron in formatos:
        if re.search(patron, mensaje, re.IGNORECASE):
            logging.info(f"Mensaje coincide con {formato}: {mensaje}")
            break
    else:
        logging.warning("No se encontró ninguna coincidencia en el mensaje.")
        return False

    # Detectar divisa, dirección y tiempo
    match = regex_para_formato.search(mensaje)
    tiempo_match = regex_tiempos.search(mensaje)

    if match and tiempo_match:
        divisa = match.group(1)
        direccion = direccion_map.get(match.group(2).lower(), "DESCONOCIDO")
        tiempo = tiempo_match.group(2)
        caducidad = horario_envio + timedelta(minutes=5)

        # Crear la señal en formato JSON
        señal = {
            "divisa": divisa,
            "direccion": direccion,
            "tiempo": tiempo,
            "timestamp": horario_envio.strftime("%Y-%m-%d %H:%M:%S"),
            "caducidad": caducidad.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Guardar señal en el archivo JSON
        try:
            if os.path.exists(SEÑALES_HTML_PATH):
                with open(SEÑALES_HTML_PATH, "r", encoding="utf-8") as file:
                    señales = json.load(file)
            else:
                señales = []

            señales.append(señal)

            # Limitar las señales a las últimas 20
            señales = señales[-20:]

            with open(SEÑALES_HTML_PATH, "w", encoding="utf-8") as file:
                json.dump(señales, file, ensure_ascii=False, indent=4)

            logging.info(f"Señal guardada exitosamente: {señal}")
            return True
        except Exception as e:
            logging.error(f"Error al guardar la señal: {e}")
            return False
    else:
        logging.warning("El mensaje no contiene datos válidos para una señal.")
        return False

# Manejar mensajes de Telegram
async def main():
    try:
        await client.start(phone=phone_number)  # Solo necesitas iniciar el cliente una vez aquí
        logging.info("Conexión exitosa con Telegram.")
        await client.run_until_disconnected()  # Mantener la conexión abierta hasta que se desconecte manualmente
    except Exception as e:
        logging.error(f"Error al conectar: {e}")

    @client.on(events.NewMessage(chats=[
        '@alejandrosinalesgratis',
        '@pocketoptiongratis500',
        '@pocketoptiongratis50',
        '@Amarearnings',
        '@julia_signal',
        '@dashatrade',
        '@freesignalkami',
        '@SenalesGratisQuotex',
        '@senales_trading_quotex_forex1',
        -1001963256084,
        -1002119599326,
        224711174,
        -1001897923732
    ]))

    @client.on(events.NewMessage(chats=[...]))
    async def handler(event):
        # Asegúrate de que solo procesamos mensajes de texto
        if not event.message.text:
            return  # Ignorar si no tiene texto

        # Filtrar mensajes con imágenes
        if 'photo' in event.message:
            return  # Ignorar mensaje si tiene una imagen

        mensaje = event.message.text
        horario_envio = event.message.date
        logging.info(f"Mensaje recibido: {mensaje} (Hora: {horario_envio})")

        # Filtrar cualquier posible enlace a imagen o medios
        texto_limpio = re.sub(r'http[s]?://\S+', '', mensaje)

        # Ahora procesar el texto limpio
        procesar_mensaje(texto_limpio)

        # Procesar el mensaje para extraer la señal
        if procesar_mensaje(mensaje, horario_envio):
            logging.info("Señal procesada y guardada correctamente.")
        else:
            logging.warning("El mensaje no se procesó como señal válida.")


# Ejecutar el cliente de Telethon
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

