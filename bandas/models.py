# D:\dev\maestra_webpage\bandas\models.py
import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# ==========================================
# UTILIDAD DE OPTIMIZACIÓN E IMAGEN WEBP
# ==========================================
def validar_peso_imagen(archivo):
    """
    Evita que se suban archivos excesivamente pesados que saturen el servidor.
    Límite máximo: 5 MB.
    """
    limite_mb = 5
    if archivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"El archivo es demasiado pesado. El límite máximo es de {limite_mb}MB.")

def procesar_y_optimizar_a_webp(imagen_field, max_size=(1600, 1600), quality=80, prefijo_nombre=None):
    """
    Toma un ImageField, lo redimensiona proporcionalmente, lo convierte
    a formato WebP, lo comprime y lo renombra usando el prefijo provisto (ej: slug del evento).
    """
    if not imagen_field:
        return None

    img = Image.open(imagen_field)
    
    # Manejar canales de transparencia
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Redimensionar
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Comprimir en memoria
    output = BytesIO()
    img.save(output, format='WEBP', quality=quality)
    output.seek(0)

    # Renombrado inteligente
    if prefijo_nombre:
        import uuid
        # Generamos un sufijo único corto para evitar colisiones entre las fotos subidas juntas
        sufijo_unico = uuid.uuid4().hex[:6]
        nuevo_nombre = f"{prefijo_nombre}_{sufijo_unico}.webp"
    else:
        nombre_original, _ = os.path.splitext(imagen_field.name)
        nuevo_nombre = f"{nombre_original}.webp"

    return ContentFile(output.read(), name=nuevo_nombre)

# ==========================================
# MODELO: BANDA
# ==========================================
class Banda(models.Model):
    nombre = models.CharField(max_length=100)
    responsable = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    redes_sociales = models.URLField(blank=True, null=True)
    dossier = models.TextField(blank=True, null=True, help_text="Descripción o reseña tipo dossier de la banda")
    notas_confidenciales = models.TextField(blank=True, null=True, help_text="Notas privadas de Producción")

    def __str__(self):
        return self.nombre


# ==========================================
# MODELO: FOTO BANDA (ASOCIADAS A EVENTOS/BANDA)
# ==========================================
class FotoBanda(models.Model):
    banda = models.ForeignKey('bandas.Banda', on_delete=models.CASCADE, related_name='fotos')
    evento = models.ForeignKey('eventos.Evento', on_delete=models.SET_NULL, null=True, blank=True, related_name='fotos_galeria')
    imagen = models.ImageField(upload_to='galeria_bandas/', null=False, blank=False, validators=[validar_peso_imagen])
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    link_extra = models.URLField(max_length=500, blank=True, null=True)
    
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de la banda {self.banda.nombre} (ID: {self.id})"

    def save(self, *args, **kwargs):
        # Si se subió una nueva imagen o fue modificada, la comprimimos a WebP
        if self.imagen and (not self.pk or FotoBanda.objects.get(pk=self.pk).imagen != self.imagen):
            self.imagen = procesar_y_optimizar_a_webp(self.imagen)
        super().save(*args, **kwargs)


# ==========================================
# MODELO: GALERÍA GENERAL (MURALES, EXPOSICIONES, LOCAL)
# ==========================================
class Album(models.Model):
    titulo = models.CharField(max_length=150, verbose_name="Título del Álbum")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción o Reseña")
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo


class FotoAlbum(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='galeria_general/', null=False, blank=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.album.titulo} (ID: {self.id})"