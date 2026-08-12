from django.urls import path
from eventos import views as eventos_views
from . import views as core_views

urlpatterns = [
    # La raíz del sitio ejecuta tu vista de eventos y se llama 'index' para el HTML
    path('', eventos_views.home_publico, name='index'),
    path('nosotros/', core_views.nosotros, name='nosotros'),
]