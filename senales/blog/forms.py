from django import forms
from .models import Comentario  # Asegúrate de que tienes un modelo llamado 'Comentario'

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido', 'autor']  # Ajusta estos campos según tu modelo

