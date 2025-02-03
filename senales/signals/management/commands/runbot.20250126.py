import sys
import os
import django
from django.conf import settings
from telethon import TelegramClient, events
import logging
import re
from datetime import datetime
import json
from django.utils.timezone import now
from signals.models import Senal  # Asegúrate de que el modelo está correctamente importado

# Verificar rutas y configuración inicial
print("sys.path antes:", sys.path)
sys.path.append('/opt/senales')  # Ruta del proyecto Django
print("sys.path después:", sys.path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'senales.settings')  # Configuración de Django
print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))

# Configurar Django
django.setup()

# Confirmar que el modelo se importó correctamente
print("Modelo Senal importado correctamente")

# Configurar el archivo de señales
SEÑALES_HTML_PATH = "/opt/senales/senales/signals/static/senales/senales.json"

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
archivo_formatos = '/opt/senales/senales/management/commands/formatodegrupos.txt'
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

# Función para obtener señales recientes (máximo 5 minutos de vida)
def obtener_senales_recientes():
    tiempo_actual = now()
    señales = []

    # Consulta las señales creadas en los últimos 5 minutos
    from senales.models import Senal  # Importa el modelo necesario
    senales_recientes = Senal.objects.filter(
        horario_envio__gte=tiempo_actual - datetime.timedelta(minutes=5)
    ).order_by("-horario_envio")  # Ordenar por la más reciente primero

    # Convertir señales a un formato JSON
    for señal in señales_recientes:
        señales.append({
            "divisa": señal.divisa,
            "direccion": señal.direccion,
            "tiempo": señal.tiempo,
            "timestamp": señal.horario_envio.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return señales

# Función para guardar las señales recientes en un archivo JSON
def guardar_senales_html(senales):
    try:
        os.makedirs(os.path.dirname(SENALES_HTML_PATH), exist_ok=True)
        with open(SENALES_HTML_PATH, "w", encoding="utf-8") as file:
            json.dump(senales, file, ensure_ascii=False, indent=4)
        logging.info(f"Señales guardadas exitosamente en {SENALES_HTML_PATH}")
    except Exception as e:
        logging.error(f"Error al guardar señales: {e}")

# Función para procesar mensajes
def procesar_mensaje(mensaje, horario_envio):
    senal_formateada = {'Proceso': 0}

    # Buscar coincidencia con algún formato
    for formato, patron in formatos:
        if re.search(patron, mensaje, re.IGNORECASE):
            logging.info(f"Mensaje coincide con {formato}: {mensaje}")
            senal_formateada['Proceso'] = 1
            break

    # Si se encuentra un mensaje válido, actualizar señales y generar HTML
    if senal_formateada["Proceso"] == 1:
        # Guardar la nueva señal en la base de datos
        match = regex_para_formato.search(mensaje)
        tiempo_match = regex_tiempos.search(mensaje)

        if match and tiempo_match:
            moneda = match.group(1)
            direccion = direccion_map.get(match.group(2).lower(), "DESCONOCIDO")
            tiempo = tiempo_match.group(0)

            # Validar si la señal ya existe
            if not Senal.objects.filter(
                divisa=moneda,
                direccion=direccion,
                tiempo=tiempo,
                horario_envio=horario_envio
            ).exists():
                # Crear la nueva señal
                nueva_senal = Senal(
                    divisa=moneda,
                    direccion=direccion,
                    tiempo=tiempo,
                    horario_envio=horario_envio,
                    proceso=1
                )
                nueva_senal.save()
                logging.info(f"Nueva señal guardada: {moneda}, {direccion}, {tiempo}")

        # Actualizar las señales recientes
        senales = obtener_senales_recientes()
        guardar_senales_html(senales)

        # Actualizar señales en el archivo JSON
        actualizar_señales_json()
        logging.info(f"Señal guardada: {moneda}, {direccion}, {tiempo}")

    else:
        logging.warning("No se encontró ningún formato válido en el mensaje.")


# Función para actualizar señales en archivo JSON
def actualizar_señales_json():
    señales = Senal.objects.all().order_by('-horario_envio')[:20]  # Últimas 20 señales
    señales_dict = [
        {
            "divisa": senal.divisa,
            "direccion": senal.direccion,
            "tiempo": senal.tiempo,
            "horario_envio": senal.horario_envio.strftime('%Y-%m-%d %H:%M:%S')
        }
        for senal in señales
    ]

    with open(SEÑALES_HTML_PATH, 'w', encoding='utf-8') as f:
        json.dump(señales_dict, f, indent=4)
    logging.info("Señales actualizadas en el archivo JSON.")


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
