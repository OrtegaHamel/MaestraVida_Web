from django.contrib import admin
from .models import Banda, FotoBanda

@admin.register(Banda)
class BandaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'responsable', 'telefono', 'correo', 'redes_sociales')
    search_fields = ('nombre', 'responsable')

@admin.register(FotoBanda)
class FotoBandaAdmin(admin.ModelAdmin):
    list_display = ('banda', 'titulo', 'subido_por', 'creado_en')
    list_filter = ('banda', 'creado_en')
    search_fields = ('banda__nombre', 'titulo')