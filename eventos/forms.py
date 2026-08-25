# D:\dev\maestra_webpage\eventos\forms.py
from django import forms
from django.forms import ModelChoiceField
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils import timezone
import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import re

from bandas.models import Banda
from .models import CarteleraMensual, Evento


# ==========================================
# 1. FORMULARIO PARA EL PRODUCTOR
# ==========================================
class EventoForm(forms.ModelForm):
    banda = ModelChoiceField(
        queryset=Banda.objects.all().order_by('nombre'),
        empty_label="Seleccione una banda",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select select2-bandas'})
    )

    # Mantener el widget URL para compatibilidad con la UI, pero lo tratamos en clean_link_entrada
    link_entrada = forms.CharField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://... o número de WhatsApp'})
    )

    # (Opcional) exponemos el campo hora aquí si quieres controlar input_formats directamente
    hora = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    class Meta:
        model = Evento
        fields = ['banda', 'hora', 'precio_preventa', 'precio_puerta', 'descripcion', 'poster', 'link_entrada', 'asistencia', 'notas_confidenciales']
        widgets = {
            'precio_preventa': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Ej: 5000'}),
            'precio_puerta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Ej: 7000'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
            'asistencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notas_confidenciales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Solo visible para producción...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        crear_banda_url = reverse_lazy('bandas:crear_banda')
        self.fields['banda'].help_text = mark_safe(
            f'Si la banda no está en la lista, <a href="{crear_banda_url}">crea una nueva banda aquí</a>.'
        )

        if not self.instance.pk and not self.initial.get('hora'):
            ahora_aware = timezone.now()
            hoy_a_las_23_aware = ahora_aware.replace(hour=23, minute=0, second=0, microsecond=0)
            self.initial['hora'] = hoy_a_las_23_aware

    def clean_link_entrada(self):
        """
        Normaliza link_entrada:
        - Si es URL válida (con http/https) la deja.
        - Si es un número (con/sin +, con espacios, paréntesis o guiones), lo convierte a https://wa.me/<number_sin_signos>
          Si el número no incluye código de país y has configurado DEFAULT_PHONE_COUNTRY_CODE en settings, lo antepone.
        - Si no puede normalizar, lanza ValidationError con mensaje claro.
        """
        val = self.cleaned_data.get('link_entrada')
        if not val:
            return ''

        val = val.strip()

        # Si ya parece una URL con esquema, validamos y devolvemos
        if val.startswith('http://') or val.startswith('https://'):
            validator = URLValidator()
            try:
                validator(val)
            except ValidationError:
                raise forms.ValidationError('Introduzca una URL válida (ej: https://ejemplo.com).')
            return val

        # Si contiene espacios o caracteres no URL, comprobamos si es un número telefónico
        # Extraemos sólo dígitos y signo + inicial si lo hubiese
        cleaned = re.sub(r'[^\d+]', '', val)

        # Si empieza con '+' mantén el '+' por ahora para contar dígitos; luego lo quitamos
        digits = cleaned.lstrip('+')

        # Si lo que queda son solo dígitos, tratamos como teléfono candidato
        if digits.isdigit():
            # Validamos longitud razonable (entre 7 y 15 dígitos)
            if not (7 <= len(digits) <= 15):
                raise forms.ValidationError(
                    'Número de teléfono inválido o con longitud inesperada. Incluya el código de país si corresponde.'
                )

            # Si el número no tiene código de país (heurística: longitud <10) y existe DEFAULT_PHONE_COUNTRY_CODE, anteponemos
            default_cc = getattr(settings, 'DEFAULT_PHONE_COUNTRY_CODE', None)
            if len(digits) < 10 and default_cc:
                # Evitamos duplicar el código de país si ya estaba
                digits = f"{default_cc}{digits}"

            # Finalmente construimos el enlace wa.me (sin el signo '+')
            wa_url = f"https://wa.me/{digits}"
            return wa_url

        # Si no es ni URL ni teléfono, intentamos añadir https:// y validar
        candidate = 'https://' + val
        validator = URLValidator()
        try:
            validator(candidate)
        except ValidationError:
            raise forms.ValidationError(
                'Introduce una URL o un número de teléfono válido (ej: +573001234567 o https://wa.me/573001234567).'
            )
        return candidate
            
# ==========================================
# 2. FORMULARIO EXCLUSIVO PARA LA PUERTA
# ==========================================
class AsistenciaEventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        # El portero SOLO ve y modifica el conteo de personas de esa noche
        fields = ['asistencia']
        widgets = {
            'asistencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


# ==========================================
# 3. FORMULARIO DE BÚSQUEDA / FILTROS
# ==========================================
class BusquedaEventosForm(forms.Form):
    banda = forms.ModelChoiceField(
        queryset=Banda.objects.all(),
        required=False,
        label="Buscar por Banda",
        empty_label="Seleccione una banda",
        widget=forms.Select(attrs={'class': 'form-select select2-bandas'})
    )
    fecha_inicio = forms.DateField(
        required=False,
        label="Fecha Inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        required=False,
        label="Fecha Fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

# ==========================================
# 4. FORMULARIO CARTELERA MENSUAL
# ==========================================

class CarteleraMensualForm(forms.ModelForm):

    class Meta:
        model = CarteleraMensual
        fields = ['mes', 'anio', 'imagen']

        widgets = {
            'mes': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'anio': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 2025,
                    'placeholder': 'Ej: 2026'
                }
            ),

            'imagen': forms.FileInput(
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.initial['anio'] = timezone.now().year