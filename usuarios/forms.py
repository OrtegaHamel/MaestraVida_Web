from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Obtenemos tu modelo de usuario personalizado de forma segura
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario de registro que reemplaza al predeterminado de Django
    para que funcione con nuestro usuario personalizado e incluya email y teléfono.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        # Agregamos 'email' y 'telefono' además de los campos base (username)
        fields = UserCreationForm.Meta.fields + ('email', 'telefono',)