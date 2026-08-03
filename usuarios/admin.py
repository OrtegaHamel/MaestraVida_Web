from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    
    # 1. Agregamos las columnas que queremos ver en la tabla principal
    # Aquí es donde añadimos 'email' y tu campo personalizado 'telefono'
    list_display = ('username', 'email', 'telefono', 'is_staff')

    # 2. Mantenemos la configuración para ver el teléfono al editar el usuario
    # (El email ya viene incluido por defecto en UserAdmin.fieldsets)
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Extra (Maestra)', {
            'fields': (
                'telefono', 
            )
        }),
    )
