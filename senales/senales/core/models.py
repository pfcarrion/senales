from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils import timezone  # Necesario para usar timezone.now()
from django.contrib import admin
from django.core.validators import EmailValidator
from django.db import models
from blog.models import Blog
from django_countries.fields import CountryField  # Importar campo de países
import logging
from django.contrib.auth.models import User  # Importa el modelo User

class Subscription(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('suspendido', 'Suspendido'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    )

#    tipo = models.CharField(max_length=100)  # Ejemplo: Mensual, Trimestral, Semestral y Anual
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Usuario relacionado con la suscripción
    nombre = models.CharField(
        max_length=100,
        validators=[RegexValidator(regex='^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', message='El nombre solo puede contener letras y espacios.')]
    )
    apellido = models.CharField(
        max_length=100,
        validators=[RegexValidator(regex='^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', message='El nombre solo puede contener letras y espacios.')]
    )
    pais = CountryField(blank_label='Selecciona un país...')  # Dropdown para países

    correo = models.EmailField(
        max_length=100,
        validators=[EmailValidator(message="Debe ingresar un correo válido.")]
    )
    plan = models.CharField(
        max_length=20,
        choices=[
            ('mensual', 'Mensual'),
            ('trimestral', 'Trimestral'),
            ('semestral', 'Semestral'),
            ('anual', 'Anual')
        ],
        default='mensual',  # Valor predeterminado
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)    # Fecha de inicio de la suscripción
    fecha_fin = models.DateTimeField(null=True, blank=True)    # Fecha de fin de la suscripción
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')  # Estado de la suscripción
    monto = models.DecimalField(max_digits=10, decimal_places=2)    # Monto asociado al plan
    fecha_pago = models.DateTimeField(null=True, blank=True)    # Fecha en la que se realizó el pago
    es_recursiva = models.BooleanField(default=False)    # Indica si la suscripción es recurrente
    transaction_id = models.CharField(max_length=255, null=True, blank=True)  # ID de transacción de PayPal
    payer_email = models.EmailField(null=True, blank=True)  # Correo electrónico del pagador (PayPal)
    metodo_pago = models.CharField(
        max_length=20,
        choices=[('paypal', 'PayPal'), ('tarjeta', 'Tarjeta de crédito por PayPal'), ('binance', 'Binance')],
        default='paypal'
    )

    def __str__(self):
        return f"Suscripción de {self.nombre} {self.apellido} - {self.tipo} ({self.estado} - {self.plan})"

    # Se utiliza un logger para registrar información para depuración:
    def save(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.info(f"Guardando suscripción: Plan: {self.plan}, Monto: {self.monto}, Estado: {self.estado}")
        super().save(*args, **kwargs)


    def esta_activa(self):
        """
        Verifica si la suscripción está activa.
        Comprueba que el estado sea 'activo' y que la fecha de fin no haya pasado (si existe).
        """
        if self.estado == 'activo' and (self.fecha_fin is None or self.fecha_fin > timezone.now()):
            return True
        return False

    @admin.display(boolean=True, description='¿Está Activa?')
    def es_activa_admin(self):
        """
        Método para mostrar en el admin si la suscripción está activa.
        """
        return self.esta_activa()

class Blog(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

