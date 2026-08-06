# D:\dev\maestra_webpage\eventos\urls.py
from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # 1. RUTAS DE ADMINISTRACIÓN (Tienen palabras clave fijas como 'crear', 'editar', etc.)
    path('', views.lista_eventos, name='lista_eventos'),
    path('buscar/', views.busqueda_eventos, name='busqueda_eventos'),
    path('crear/', views.crear_evento, name='crear_evento'),
    
    # Aquí usamos el ID sin problemas de choques
    path('editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('eliminar/<int:evento_id>/', views.eliminar_evento, name='eliminar_evento'),
    path('hoy/', views.eventos_hoy, name='eventos_hoy'),
    path('asistencia/<int:evento_id>/', views.registrar_asistencia, name='registrar_asistencia'),

    path("cartelera/", views.cartelera, name="cartelera"),

    path('carteleras/', views.lista_carteleras, name='lista_carteleras'),
    path('carteleras/nueva/', views.crear_cartelera, name='crear_cartelera'),
    path(
        "carteleras/<int:cartelera_id>/editar/",
        views.editar_cartelera,
        name="editar_cartelera",
    ),

    path(
        "carteleras/<int:cartelera_id>/eliminar/",
        views.eliminar_cartelera,
        name="eliminar_cartelera",
    ),

    # 2. RUTAS PÚBLICAS DINÁMICAS (Siempre al final)
    # Al estar abajo, Django solo usará el comodín <slug> si la URL NO contenía 'crear', 'editar', etc.
    path('<slug:slug>/', views.detalle_evento_publico, name='detalle_evento_publico'),
]