from django import template
from django.contrib.auth.models import Group

# Registramos nuestra nueva librería de etiquetas
register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Verifica si un usuario pertenece a un grupo en específico.
    Uso en HTML: {% if request.user|has_group:"NombreDelGrupo" %}
    """
    # Si el usuario no ha iniciado sesión, lógicamente no pertenece a ningún grupo
    if not user.is_authenticated:
        return False
        
    # Consultamos si existe el grupo dentro de los grupos asignados a este usuario
    return user.groups.filter(name=group_name).exists()