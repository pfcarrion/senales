from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'fecha_inicio', 'fecha_fin', 'monto', 'es_recursiva', 'nombre', 'apellido')
    list_filter = ('estado', 'es_recursiva')
    search_fields = ('usuario__username','estado')
