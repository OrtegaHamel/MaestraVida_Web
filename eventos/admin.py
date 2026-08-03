from django.contrib import admin
from .models import Evento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['id', 'banda', 'hora', 'precio_preventa', 'precio_puerta']
    # Esto permite que al hacer clic en el evento dentro del admin, se puedan ver y editar las notas secretas
    fields = ['banda', 'hora', 'precio_preventa', 'precio_puerta', 'descripcion', 'poster', 'link_entrada', 'asistencia', 'notas_confidenciales', 'slug']
    readonly_fields = ['slug'] # El slug se genera solo, mejor dejarlo de solo lectura en el admin