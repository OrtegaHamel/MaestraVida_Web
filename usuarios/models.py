from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)

    # Añadimos campos para identificar los roles
    es_productor = models.BooleanField(default=False)
    es_fotografo = models.BooleanField(default=False)
    es_puerta = models.BooleanField(default=False)
    es_redes_sociales = models.BooleanField(default=False)
    
    # Un campo extra por si quieres guardar su teléfono o algo específico
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.email})"
