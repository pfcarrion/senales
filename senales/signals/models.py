from django.db import models
from django.utils.timezone import now

class Senal(models.Model):
    divisa = models.CharField(max_length=10)  # Ejemplo: EUR/USD
    direccion = models.CharField(max_length=10)  # Ejemplo: ARRIBA o BAJO
    tiempo = models.CharField(max_length=20)  # Ejemplo: 5 minutos
#    horario_envio = models.DateTimeField()  # Hora específica de la señal
    horario_envio = models.DateTimeField(null=True, blank=True)
#    horario_envio = models.DateTimeField(null=False)
#    horario_envio = models.DateTimeField(default=lambda: now())
    proceso = models.IntegerField(default=0)  # 0 = no procesado, 1 = procesado
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return f"{self.divisa} - {self.direccion} - {self.tiempo} - {self.horario_envio}"

