from django import forms
from .models import Subscription
from django.core.exceptions import ValidationError
from decimal import Decimal
from allauth.account.forms import LoginForm

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['nombre', 'apellido', 'pais', 'correo', 'plan', 'monto', 'es_recursiva']  # Excluye otros campos si es necesario
        widgets = {
            'correo': forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
        }
        monto = forms.DecimalField(max_digits=10, decimal_places=2, required=True) 

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

    def clean_correo(self):
        """
        Acepta cualquier correo válido, pero emite una advertencia si el dominio no es común.
        """
        correo = self.cleaned_data.get('correo')
        dominios_comunes = ['gmail.com', 'hotmail.com', 'yahoo.com']

        # Validar formato básico
        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise ValidationError("Por favor, ingrese un correo válido.")

        # Emitir advertencia para dominios no comunes
        dominio = correo.split("@")[-1]
        if dominio not in dominios_comunes:
            # Advertencia no bloqueante
            self.add_error('correo', "Advertencia: el dominio de su correo no es común, asegúrese de que sea válido.")

        return correo

    # Asignar un valor predeterminado al campo es_recursiva
    def clean_es_recursiva(self):
        return self.cleaned_data.get('es_recursiva', False)  # Valor predeterminado

    def clean(self):
        cleaned_data = super().clean()
        plan = cleaned_data.get('plan')
        precios = {
            'mensual': 10.00,
            'trimestral': 25.00,
            'semestral': 50.00,
            'anual': 100.00,
        }

        # Calcula el monto según el plan seleccionado
        cleaned_data['monto'] = precios.get(plan, Decimal(0.00))
        return cleaned_data

