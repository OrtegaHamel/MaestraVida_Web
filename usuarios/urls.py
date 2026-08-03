# usuarios/urls.py
from django.urls import path
from . import views  # Solo importamos tus vistas locales

app_name = 'usuarios'

urlpatterns = [
    # Autenticación conectada a tus vistas personalizadas
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('registro/', views.registro, name='registro'),
    
    # Dashboard del Panel
    path('panel/', views.panel_home, name='panel_home'),
]
