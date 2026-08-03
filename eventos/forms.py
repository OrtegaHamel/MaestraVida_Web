# D:\dev\maestra_webpage\eventos\forms.py
from django import forms
from django.forms import ModelChoiceField
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils import timezone
import datetime
from bandas.models import Banda
from .models import Evento

# ==========================================
# 1. FORMULARIO PARA EL PRODUCTOR
# ==========================================
class EventoForm(forms.ModelForm):
    banda = ModelChoiceField(
        queryset=Banda.objects.all(),
        empty_label="Seleccione una banda",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select select2-bandas'})
    )

    class Meta:
        model = Evento
        fields = ['banda', 'hora', 'precio_preventa', 'precio_puerta', 'descripcion', 'poster', 'link_entrada', 'asistencia', 'notas_confidenciales']
        widgets = {
            # ¡NUEVO!: Le decimos explícitamente al widget cómo formatear la fecha para HTML5
            'hora': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'precio_preventa': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Ej: 5000'}),
            'precio_puerta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Ej: 7000'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
            'link_entrada': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://... o link de WhatsApp'}),
            'asistencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notas_confidenciales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Solo visible para producción...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Link para crear banda si no existe
        crear_banda_url = reverse_lazy('bandas:crear_banda')
        self.fields['banda'].help_text = mark_safe(
            f'Si la banda no está en la lista, '
            f'<a href="{crear_banda_url}">crea una nueva banda aquí</a>.'
        )
        
        # PRESETEO 100% BLINDADO CONTRA ZONAS HORARIAS
        if not self.instance.pk and not self.initial.get('hora'):
            # 1. Obtenemos el momento actual EXACTO, el cual Django garantiza que tiene zona horaria (Aware)
            ahora_aware = timezone.now()
            
            # 2. Reemplazamos la hora y minutos a las 23:00, manteniendo la zona horaria intacta
            hoy_a_las_23_aware = ahora_aware.replace(hour=23, minute=0, second=0, microsecond=0)
            
            # 3. Asignamos el objeto perfecto
            self.initial['hora'] = hoy_a_las_23_aware
            
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