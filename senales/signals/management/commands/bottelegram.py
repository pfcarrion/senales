import sys
import os
import django
from django.conf import settings
from telethon import TelegramClient, events
import logging
import re
from datetime import datetime
import json
import time
from django.utils.timezone import now, make_aware

# Configuración de rutas y Django
print("sys.path antes:", sys.path)
sys.path.append('/opt/senales/senales')
print("sys.path después:", sys.path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'senales.settings')
print("DJANGO_SETTINGS_MODULE:", os.getenv('DJANGO_SETTINGS_MODULE'))

django.setup()

# Importar el modelo de Django
from signals.models import Senal
print("Modelo Senal importado correctamente")

# Configuración de archivos
SEÑALES_HTML_PATH = "senales.json"
MENSAJES_CAPTURADOS_PATH = "capturamensajes.txt"
#FORMATOS_PATH = '/opt/senales/senales/signals/management/commands/formatodegrupos.txt' # Ruta del archivo de chats
FORMATOS_PATH = 'formatodegrupos.txt'   # Ruta del archivo de chats
CHATS_PATH = 'chats.txt'  # Ruta del archivo de chats
DIRECCIONES_PATH = 'direcciones.json' #Ruta del archivo de direcciones

# Configuración de Telegram
api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
phone_number = settings.TELEGRAM_PHONE_NUMBER


# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializar cliente de Telethon
client = TelegramClient('nueva_name', api_id, api_hash)
client.start(phone=phone_number)

 # Expresiones regulares
regex_para_formato = re.compile(
    r"([A-Z]{3}\/[A-Z]{3}|[A-Z]{6}(?:-OTC)?)\s*(⬆️|⬇️|arriba|bajo|up|down|call|put)\s*(\d+)\s*MINUTES?",
    re.IGNORECASE
)
regex_tiempos = re.compile(
    r"(M\d+|m\d+|\d+\s*MINUTOS?|\d+\s*MINUTES?|caducidad de \d+ minutos|vencimiento: m\d+|time:\s*\d+\s*min)",
    re.IGNORECASE
)

# Función para cargar chats desde un archivo
def cargar_chats(archivo):
    chat_ids = []
    try:
       with open(archivo, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    chat_ids.append(line)
       logging.info(f"Chats cargados desde {archivo}: {chat_ids}")
    except FileNotFoundError:
        logging.error(f"Error: El archivo de chats '{archivo}' no fue encontrado.")
        return None
    except Exception as e:
        logging.error(f"Error al cargar chats: {e}")
        return None
    return chat_ids


# Función para cargar diccionario de direcciones desde JSON
def cargar_direcciones(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            direccion_map = json.load(f)
        logging.info(f"Diccionario de direcciones cargado desde {archivo}: {direccion_map}")
        return direccion_map
    except FileNotFoundError:
        logging.error(f"Error: El archivo de direcciones '{archivo}' no fue encontrado.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error: El archivo de direcciones '{archivo}' no es un JSON válido.")
        return None
    except Exception as e:
         logging.error(f"Error al cargar direcciones: {e}")
         return None

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
    except FileNotFoundError:
        logging.error(f"Error: El archivo de formatos '{archivo}' no fue encontrado.")
    except Exception as e:
        logging.error(f"Error al cargar formatos: {e}")
    return patrones

# Función para obtener señales recientes (máximo 5 minutos de vida)
def obtener_senales_recientes():
    tiempo_actual = now()
    señales = []
    try:
        senales_recientes = Senal.objects.filter(
            horario_envio__gte=tiempo_actual - datetime.timedelta(minutes=5)
        ).order_by("-horario_envio")

        for señal in senales_recientes:
            señales.append({
                "divisa": señal.divisa,
                "direccion": señal.direccion,
                "tiempo": señal.tiempo,
                "timestamp": señal.horario_envio.strftime("%Y-%m-%d %H:%M:%S"),
            })
        logging.info(f"Se obtuvieron {len(señales)} señales recientes.")
    except Exception as e:
         logging.error(f"Error al obtener señales recientes: {e}")

    return señales

# Función para guardar las señales recientes en un archivo JSON
def guardar_senales_html(senales):
    try:
        os.makedirs(os.path.dirname(SEÑALES_HTML_PATH), exist_ok=True)
        with open(SEÑALES_HTML_PATH, "w", encoding="utf-8") as file:
            json.dump(senales, file, ensure_ascii=False, indent=4)
        logging.info(f"Señales guardadas exitosamente en {SEÑALES_HTML_PATH}")
    except Exception as e:
         logging.error(f"Error al guardar señales en {SEÑALES_HTML_PATH}: {e}")

# Función para procesar mensajes
def procesar_mensaje(mensaje, horario_envio, direccion_map):
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
                try:
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
                except Exception as e:
                    logging.error(f"Error al guardar señal en la base de datos: {e}")
            else:
                logging.info(f"Señal duplicada detectada: {moneda}, {direccion}, {tiempo} (hora:{horario_envio})")

        # Actualizar las señales recientes
        senales = obtener_senales_recientes()
        guardar_senales_html(senales)

        # Actualizar señales en el archivo JSON
        actualizar_señales_json()
    else:
        logging.warning(f"No se encontró ningún formato válido en el mensaje: {mensaje}")
    return senal_formateada

# Función para actualizar señales en archivo JSON
def actualizar_señales_json():
    try:
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
    except Exception as e:
         logging.error(f"Error al actualizar el archivo JSON de señales: {e}")


# Manejar mensajes de Telegram
async def main():
        # Cargar chats y direcciones
        chats = cargar_chats(CHATS_PATH)
        if not chats:
            logging.error("No se cargaron chats. Saliendo...")
            return

        direccion_map = cargar_direcciones(DIRECCIONES_PATH)
        if not direccion_map:
            logging.error("No se cargo el diccionario de direcciones, Saliendo...")
            return
        try:
            await client.start(phone=phone_number)
            logging.info("Conexión exitosa con Telegram.")
        except Exception as e:
            logging.error(f"Error al conectar con Telegram: {e}")
            return

        @client.on(events.NewMessage(chats=chats))
        async def handler(event):
            try:
                mensaje = event.message.message
                horario_envio = make_aware(event.message.date)  # Capturar la hora exacta del mensaje y hacerla consciente de la zona horaria
                logging.info(f"Mensaje recibido: {mensaje} (Hora: {horario_envio})")

                # Guardar el mensaje en un archivo de texto
                try:
                    os.makedirs(os.path.dirname(MENSAJES_CAPTURADOS_PATH), exist_ok=True)
                    with open(MENSAJES_CAPTURADOS_PATH, 'a', encoding='utf-8') as f:
                        f.write(f"[{horario_envio.strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")
                    logging.info(f"Mensaje guardado en {MENSAJES_CAPTURADOS_PATH}")
                except Exception as e:
                    logging.error(f"Error al guardar el mensaje en {MENSAJES_CAPTURADOS_PATH}: {e}")
                señal_formateada = procesar_mensaje(mensaje, horario_envio, direccion_map)
                if señal_formateada:
                     logging.info(f"Señal guardada en la base de datos.")
                else:
                     logging.warning("No se encontró ninguna línea relevante para procesar.")
            except telethon.errors.FloodWaitError as flood_error:
                 logging.error(f"Error FloodWait: {flood_error}. Esperando {flood_error.seconds} segundos...")
                 await asyncio.sleep(flood_error.seconds)
            except ValueError as ve:
                 logging.error(f"Error al resolver la entidad del chat: {ve}. ChatID: {event.chat_id}")
                 logging.error(f"Chat en Problema: {event.chat}")
            except Exception as e:
                logging.error(f"Error no controlado al procesar el mensaje: {e}")
        # Bucle para recargar cada hora los archivos
        while True:
            logging.info("Recargando chats y direcciones...")
            chats = cargar_chats(CHATS_PATH)
            if not chats:
                logging.error("No se cargaron chats. Manteniendo configuración anterior...")
            else:
                logging.info("Chats recargados exitosamente.")
            direccion_map = cargar_direcciones(DIRECCIONES_PATH)
            if not direccion_map:
                logging.error("No se pudo recargar diccionario de direcciones. Manteniendo configuración anterior...")
            else:
                 logging.info("Diccionario de direcciones recargado exitosamente.")
            await asyncio.sleep(3600) # Espera 1 hora (3600 segundos)
if __name__ == "__main__":
    import asyncio
    # Cargar formatos
    formatos = cargar_formatos(FORMATOS_PATH)
    if not formatos:
        logging.error("No se cargaron formatos. Saliendo...")
        sys.exit(1)

    # Ejecutar el cliente de Telethon
    with client:
        client.loop.run_until_complete(main())
