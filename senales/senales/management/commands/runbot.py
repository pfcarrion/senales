import sys
import os
import django
from django.conf import settings
from telethon import TelegramClient, events
import logging
import re

# Configurar Django
sys.path.append('/opt/senales_trading')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'senales_trading.settings')
django.setup()

from senales.models import Senal

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

# Función para cargar formatos desde un archivo
def cargar_formatos(archivo):
    patrones = []
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            formato_actual = None
            patron_actual = ""
            for line in f:
                line = line.strip()
                if line.startswith('#Formato'):
                    if formato_actual and patron_actual:
                        patrones.append((formato_actual, patron_actual))
                    formato_actual = line
                    patron_actual = ""
                elif line.startswith('•') or line.startswith('💶'):
                    patron_actual += line + r"\s*"
            if formato_actual and patron_actual:
                patrones.append((formato_actual, patron_actual))
        logging.info(f"Formatos cargados: {patrones}")
    except Exception as e:
        logging.error(f"Error al cargar formatos: {e}")
    return patrones

# Cargar formatos desde el archivo
archivo_formatos = '/opt/senales_trading/senales/management/commands/formatodegrupos.txt'
formatos = cargar_formatos(archivo_formatos)

# Expresiones regulares
regex_para_formato = re.compile(
    r"([A-Z]{3}\/[A-Z]{3}|[A-Z]{6}(?:-OTC)?)\s*(⬆️|⬇️|arriba|bajo|up|down|call|put)\s*(\d+)\s*MINUTES?",
    re.IGNORECASE
)
regex_tiempos = re.compile(
    r"(M\d+|m\d+|\d+\s*MINUTOS?|\d+\s*MINUTES?|caducidad de \d+ minutos|vencimiento: m\d+|time:\s*\d+\s*min)",
    re.IGNORECASE
)

# Función para procesar mensajes
def procesar_mensaje(mensaje, horario_envio):
    senal_formateada = {'Proceso': 0}

    # Buscar coincidencia con algún formato
    for formato, patron in formatos:
        if re.search(patron, mensaje, re.IGNORECASE):
            logging.info(f"Mensaje coincide con {formato}: {mensaje}")
            senal_formateada['Proceso'] = 1
            break

    # Capturar datos específicos de divisa, dirección y tiempo
    match = regex_para_formato.search(mensaje)
    tiempo_match = regex_tiempos.search(mensaje)

    if match and tiempo_match:
        moneda = match.group(1)
        direccion = direccion_map.get(match.group(2).lower(), "DESCONOCIDO")
        tiempo = tiempo_match.group(0)

        # Validar si ya existe una señal con los mismos datos y horario
        if not Senal.objects.filter(
            divisa=moneda,
            direccion=direccion,
            tiempo=tiempo,
            horario_envio=horario_envio
        ).exists():
            # Guardar la señal en la base de datos
            senal = Senal(
                divisa=moneda,
                direccion=direccion,
                tiempo=tiempo,
                horario_envio=horario_envio,
                proceso=1  # Asumiendo que la señal se procesó
            )
            senal.save()  # Guardar en la base de datos
            logging.info(f"Señal guardada en la base de datos: {moneda}, {direccion}, {tiempo}, {horario_envio}")
            return True  # Indica que la señal fue procesada
        else:
            logging.warning("Señal duplicada detectada, no se guardará.")
            return False  # Señal duplicada, no procesada

    return False  # Si no es una señal válida

# Manejar mensajes de Telegram
async def main():
    try:
        await client.start(phone=phone_number)
        logging.info("Conexión exitosa con Telegram.")
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
        -1001963256084,
        -1002119599326
    ]))
    async def handler(event):
        mensaje = event.message.message
        horario_envio = event.message.date  # Capturar la hora exacta del mensaje
        logging.info(f"Mensaje recibido: {mensaje} (Hora: {horario_envio})")
        
        señal_formateada = procesar_mensaje(mensaje, horario_envio)

        if señal_formateada:
            logging.info(f"Señal guardada en la base de datos.")
        else:
            logging.warning("No se encontró ninguna línea relevante para procesar.")

    logging.info("Escuchando mensajes... Presiona Ctrl+C para detener.")
    await client.run_until_disconnected()

# Ejecutar el cliente de Telethon
with client:
    client.loop.run_until_complete(main())

