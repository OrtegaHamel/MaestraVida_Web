from django.urls import path
from . import views

app_name = 'bandas'
urlpatterns = [
    path('', views.lista_bandas, name='lista_bandas'),
    path('<int:banda_id>/', views.detalle_banda, name='detalle_banda'),
    path('crear/', views.crear_banda, name='crear_banda'),
    path('editar/<int:banda_id>/', views.editar_banda, name='editar_banda'),
    path('eliminar/<int:banda_id>/', views.eliminar_banda, name='eliminar_banda'),
    path('evento/<int:evento_id>/subir-fotos/', views.subir_fotos_evento, name='subir_fotos_evento'),
    path('evento/<int:evento_id>/editar-fotos/', views.editar_fotos_evento, name='editar_fotos_evento'),
    path('foto/<int:foto_id>/eliminar/', views.eliminar_foto, name='eliminar_foto'),
    path('panel-eventos/', views.panel_fotografo_eventos, name='panel_fotografo_eventos'),
    path('album/<int:album_id>/subir/', views.subir_fotos_album, name='subir_fotos_album'),
    path('albumes/', views.lista_albumes, name='lista_albumes'),
    path('album/crear/', views.crear_album, name='crear_album'),
    path('album/<int:album_id>/editar/', views.editar_album, name='editar_album'),
    path('album/<int:album_id>/eliminar/', views.eliminar_album, name='eliminar_album'),
    path('album/<int:album_id>/gestionar-fotos/', views.gestionar_fotos_album, name='gestionar_fotos_album'),
    path('foto-album/<int:foto_id>/eliminar/', views.eliminar_foto_album, name='eliminar_foto_album'),
    ]
