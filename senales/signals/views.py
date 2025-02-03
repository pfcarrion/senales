from django.shortcuts import render
from .models import Senal
from datetime import datetime
import json
#def mostrar_senales(request):
#    senales = Senal.objects.all()  # Recuperamos todas las señales
#    return render(request, 'senales/mostrar_senales.html', {'senales': senales})

# Para simular la vista de mesnajes recibidos
def señales_view(request):
    # Leer señales desde el archivo JSON
    archivo_json = "senales.json"
    try:
        with open(archivo_json, "r") as json_file:
            señales = json.load(json_file)
    except FileNotFoundError:
        señales = []

    # Renderizar las señales en el HTML
    return render(request, "señales.html", {"señales": señales})


# Produccion
def mostrar_senales(request):
    senales = Senal.objects.all()  # Recuperamos todas las señales
    señales = cargar_senales()

    # Filtrar señales caducadas (aunque esto se puede hacer antes en la carga de JSON)
    señales = [
        señal for señal in señales if datetime.strptime(señal["caducidad"], "%Y-%m-%d %H:%M:%S") > datetime.now()
    ]
    return render(request, 'senales/mostrar_senales.html', {'senales': senales})
