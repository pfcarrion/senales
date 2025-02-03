from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .forms import SubscriptionForm
from .models import Subscription, Blog    # Asegúrate de importar los modelos necesarios
from django.contrib.auth.decorators import login_required  # Importa login_required
from django.views.generic.edit import CreateView
from django.conf import settings
from django.urls import reverse
import base64
from django.http import JsonResponse
from django.shortcuts import render
from django.middleware.csrf import get_token
from django.utils import timezone
import json


# Funcion para realizar un testeo a paypal para conexion
def payment_test(request):
    return render(request, 'payment_test.html')


# Función para cifrar los datos
def encrypt_response(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

# Vista para enviar datos cifrados
def get_secure_data(request):
    sensitive_data = "Información sensible"
    encrypted_data = encrypt_response(sensitive_data)
    return JsonResponse({"data": encrypted_data})

#def secure_data_view(request):
    # Ejemplo de datos complejos
#    data = {
#        'user_info': {
#            'usuario': request.user.usuario,
#            'correo': request.user.correo,
#            'is_active': request.user.is_active
#        },
#        'last_login': request.user.last_login.strftime('%Y-%m-%d %H:%M:%S') if request.user.last_login else 'Nunca',
#        'messages': ['Mensaje 1', 'Mensaje 2', 'Mensaje 3']
#    }
#    return JsonResponse(data)

#def secure_data_view(request):
#    return render(request, 'core/secure_data.html')
#    return HttpResponse("Página de datos seguros")

#@login_required
def secure_data_view(request):
    data = {
        'status': 'success',
        'message': 'Aquí están los datos cifrados',
        'encrypted_data': 'Toda la información se encuentra cifrada ☺─«㋡»─☺'
    }
    return JsonResponse(data)

def payment_view(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)

    # Asegúrate de que el monto venga desde el modelo
    monto = subscription.monto  # Esto debe estar definido en tu modelo Subscription

    context = {
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'subscription': subscription,
        'monto': monto,
        'csrf_token': get_token(request),
    }

    return render(request, 'core/payment.html', context)

def payment_success(request, subscription_id):
    if request.method == "POST":
        subscription = get_object_or_404(Subscription, id=subscription_id)

        data = json.loads(request.body)
        transaction_id = data.get("transactionId")
        status = data.get("status")

        if status == "COMPLETED":  # Asegúrate de validar el estado del pago
            subscription.estado = "pagado"
            subscription.fecha_pago = timezone.now()
            subscription.transaction_id = transaction_id
            subscription.save()
            return JsonResponse({"message": "Pago procesado con éxito"}, status=200)
        else:
            return JsonResponse({"error": "El estado del pago no es válido"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)


def payment_cancel(request):
    return render(request, 'core/payment_cancel.html')

@login_required
def crear_suscripcion(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            suscripcion = form.save(commit=False)
            suscripcion.usuario = request.user  # Asocia al usuario logueado
            suscripcion.save()
            return redirect("suscripciones")
    else:
        form = SubscriptionForm()
    return render(request, "core/crear_suscripcion.html", {"form": form})


@login_required  # Asegúrate de que solo usuarios autenticados puedan suscribirse
def subscribe(request):
    if request.method == "POST":
        # Crear una instancia del formulario con los datos enviados
        form = SubscriptionForm(request.POST)

        if form.is_valid():
            # Crear la instancia pero no guardarla todavía
            subscription = form.save(commit=False)

            # Asignar el monto basado en el plan seleccionado
            precios = {
                "mensual": Decimal("10.00"),
                "trimestral": Decimal("25.00"),
                "semestral": Decimal("50.00"),
                "anual": Decimal("100.00"),
            }

            # Asignar el monto correspondiente al plan seleccionado
            subscription.monto = precios.get(subscription.plan, Decimal("0.00"))
#            subscription.usuario = request.user

            # No asignar el usuario aún si no está autenticado
            if request.user.is_authenticated:
               subscription.usuario = request.user
               usuario_id=request.user.id  # Asigna el ID del usuario autenticado

            subscription.es_recursiva = True  # Valor predeterminado

            # Guardar la suscripción en la base de datos
            subscription.save()

            # Mensaje de éxito
            messages.success(
                request, "¡Te has suscrito con éxito! Ahora procede al pago."
            )

            return redirect("seleccionar_metodo_pago", subscription_id=subscription.id)

            # Redirigir al usuario a la página de pago
            #return redirect("payment", subscription_id=subscription.id)
        else:
            # Mostrar los errores del formulario en la consola
            print(form.errors)

            # Si el formulario no es válido, muestra un mensaje de error
            messages.error(
                request, "Hubo un error en el formulario. Por favor, revisa los campos."
            )
    else:
        # Si no es un POST, mostrar un formulario vacío
        form = SubscriptionForm()

    # Renderizar la plantilla con el formulario
    return render(request, "core/subscribe.html", {"form": form})

def crear_usuario(request):
    # Lógica para crear un usuario después del pago
    return render(request, 'core/crear_usuario.html')

@login_required
def payment(request, subscription_id):
    # Obtener la suscripción asociada al ID
    subscription = get_object_or_404(Subscription, id=subscription_id)

    # Si la suscripción ya está pagada, redirigir al éxito
    if subscription.estado == "pagado":
        messages.info(request, "Esta suscripción ya está activa.")
        return redirect(reverse("payment_success"))  # Cambia 'payment_success' por tu URL de éxito

    if request.method == "POST":
        # Simula un pago exitoso (esto se reemplaza con integración a PayPal o similares)
        subscription.estado = "pagado"
        subscription.usuario = request.user
        subscription.save()

        # Mensaje de éxito y redirección
        messages.success(request, "¡Pago exitoso! Tu suscripción está activa.")
        return redirect(reverse("crear_usuario"))  # Cambia 'crear_usuario' por la vista que corresponda

    # Si el método es GET, renderiza la página de pago
    context = {
        "subscription": subscription,
        "monto": subscription.monto,
    }
    return render(request, "core/payment.html", context)
@login_required
def binance_payment(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    context = {"subscription": subscription}
    return render(request, "core/binance_payment.html", context)

def confirmar_pago(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)

    # Verifica el estado del pago (por ahora, manual)
    # Lógica futura: conectar con la API de Binance para validar automáticamente
    if request.method == "POST":
        subscription.estado = "pagado"
        subscription.save()
        messages.success(request, "¡Pago confirmado con éxito!")
        return redirect("payment_success", subscription_id=subscription.id)

    return render(request, "core/confirmar_pago.html", {"subscription": subscription})


def register_after_payment(request, subscription_id):
    """ Maneja el registro después del pago si el usuario no está autenticado """
    subscription = get_object_or_404(Subscription, id=subscription_id)

    # Si el usuario ya está autenticado, no necesita registrarse
    if request.user.is_authenticated:
        return redirect(reverse("payment", args=[subscription.id]))

    if request.method == "POST":
        # Procesar el formulario de registro
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request, user)  # Autenticar automáticamente al usuario recién registrado

            # Asociar la suscripción al usuario y marcarla como activa
            subscription.usuario = user
            subscription.estado = "pagado"
            subscription.save()

            messages.success(request, "¡Registro y pago completados exitosamente!")
            return redirect(reverse("payment_success"))  # Cambia 'payment_success' por tu vista final
        else:
            messages.error(request, "Hubo un error al registrar tu cuenta. Por favor, intenta nuevamente.")
    else:
        user_form = UserCreationForm()

    return render(
        request,
        "core/register_after_payment.html",
        {"user_form": user_form, "subscription": subscription},
    )

def seleccionar_metodo_pago(request, subscription_id):
    if request.method == "POST":
        metodo_pago = request.POST.get("metodo_pago")
        if metodo_pago == "paypal":
            return redirect("payment", subscription_id=subscription_id)
        elif metodo_pago == "binance":
            return redirect("binance_payment", subscription_id=subscription_id)
    else:
        return render(request, "core/seleccionar_metodo_pago.html", {"subscription_id": subscription_id})

