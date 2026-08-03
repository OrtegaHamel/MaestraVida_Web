# D:\dev\maestra_webpage\bandas\forms.py
from django import forms
from .models import Banda, Album  # Importamos Album y dejamos fuera GaleriaGeneral

# ==========================================
# WIDGET PERSONALIZADO PARA MÚLTIPLES ARCHIVOS
# ==========================================
class MultipleFileInput(forms.FileInput):
    """
    Widget personalizado que habilita la selección de múltiples archivos 
    en el explorador del sistema de manera compatible con Django.
    """
    allow_multiple_selected = True


# ==========================================
# FORMULARIO DE BANDAS
# ==========================================
class BandaForm(forms.ModelForm):
    class Meta:
        model = Banda
        # Mapeamos exactamente los campos de tu modelo Banda
        fields = [
            'nombre', 
            'responsable', 
            'telefono', 
            'correo', 
            'redes_sociales', 
            'dossier', 
            'notas_confidenciales'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la banda'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del responsable'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. +56912345678'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'redes_sociales': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/mi_banda'
            }),
            'dossier': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Breve descripción, biografía o dossier de prensa de la banda...'
            }),
            'notas_confidenciales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '🔒 Notas internas de producción (no visibles al público)'
            }),
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