# bandas/forms.py
from django import forms
from django.core.validators import URLValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.conf import settings
import re

from .models import Banda, Album

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class BandaForm(forms.ModelForm):
    """
    Formulario de Banda con validaciones:
      - clean_nombre: nombre obligatorio y único (excluye la instancia si existe)
      - clean_telefono: normaliza dígitos, añade código de país por defecto opcional y formatea +<digits>
      - clean_correo: valida e-mail
      - clean_redes_sociales: añade esquema https:// si falta
      - clean: requiere al menos un canal de contacto (teléfono o correo o redes_sociales)
    """

    class Meta:
        model = Banda
        fields = [
            'nombre',
            'responsable',
            'telefono',
            'correo',
            'redes_sociales',
            'dossier',
            'notas_confidenciales',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la banda'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del responsable'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. +56912345678'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'redes_sociales': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/mi_banda'}),
            'dossier': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Breve descripción o dossier'}),
            'notas_confidenciales': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '🔒 Notas internas (no públicas)'}),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre de la banda es obligatorio.',
            },
        }

    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        if not nombre:
            raise ValidationError('El nombre de la banda no puede estar vacío.')
        # Unicidad: si existe otra banda con el mismo nombre (case-insensitive)
        qs = Banda.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe una banda con ese nombre.')
        return nombre

    def clean_telefono(self):
        telefono = (self.cleaned_data.get('telefono') or '').strip()
        if not telefono:
            return ''  # no obligatorio, lo comprobaremos en clean()

        # Extraer solo dígitos y posible prefijo '+'
        cleaned = re.sub(r'[^\d+]', '', telefono)
        # quitar espacios y paréntesis ya hecho; ahora obtener sólo dígitos
        digits = cleaned.lstrip('+')
        if not digits.isdigit():
            raise ValidationError('Número de teléfono inválido. Sólo se permiten dígitos y el prefijo +.')

        # Heurística de longitud: entre 7 y 15 dígitos (E.164)
        if not (7 <= len(digits) <= 15):
            raise ValidationError('Longitud de teléfono inesperada. Incluye el código de país si corresponde.')

        # Si el número parece local (ej. menos de 10 dígitos) y hay DEFAULT_PHONE_COUNTRY_CODE, anteponerlo
        if len(digits) < 10:
            default_cc = getattr(settings, 'DEFAULT_PHONE_COUNTRY_CODE', None)
            if default_cc:
                # Evitar duplicar si ya venía con el mismo prefijo
                if not digits.startswith(default_cc):
                    digits = f"{default_cc}{digits}"

        # Guardamos con formato +<digits> (E.164-like)
        return f"+{digits}"

    def clean_correo(self):
        correo = (self.cleaned_data.get('correo') or '').strip()
        if not correo:
            return ''
        validator = EmailValidator()
        try:
            validator(correo)
        except ValidationError:
            raise ValidationError('Introduce una dirección de correo válida.')
        return correo

    def clean_redes_sociales(self):
        url = (self.cleaned_data.get('redes_sociales') or '').strip()
        if not url:
            return ''
        # Si no tiene esquema, añadimos https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError('Introduce una URL válida (ej: https://instagram.com/mi_banda).')
        return url

    def clean(self):
        cleaned = super().clean()
        telefono = cleaned.get('telefono') or ''
        correo = cleaned.get('correo') or ''
        redes = cleaned.get('redes_sociales') or ''

        if not (telefono or correo or redes):
            raise ValidationError('Debes indicar al menos un medio de contacto: teléfono, correo o redes sociales.')

        return cleaned


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['titulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del álbum'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción breve'}),
        }

# ==========================================
# FORMULARIO DE ÁLBUM (NUEVO CONTENEDOR)
# ==========================================
class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['titulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del álbum'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción breve'}),
        }

# ==========================================
# FORMULARIO DE CARGA MASIVA PARA EVENTOS
# ==========================================

class CustomMultipleFileInput(forms.FileInput):
    allow_multiple_selected = True  # Esto elimina el ValueError

    def value_from_datadict(self, data, files, name):
        # Aseguramos que Django siempre devuelva una lista de archivos
        return files.getlist(name)

class SubirFotosEventoForm(forms.Form):
    imagenes = forms.ImageField(
        widget=CustomMultipleFileInput(attrs={
            'class': 'form-control d-none', 
            'id': 'input-imagenes',
            'accept': 'image/*'
        }),
        label="Fotos del Evento",
        required=True
    )


# ==========================================
# FORMULARIO DE CARGA MASIVA PARA ÁLBUMES
# ==========================================
class SubirFotosAlbumForm(forms.Form):
    imagenes = forms.ImageField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control d-none', # Oculto para usar con Drag & Drop
            'id': 'input-imagenes',
            'accept': 'image/*'
        }),
        label="Fotos del Álbum"
    )