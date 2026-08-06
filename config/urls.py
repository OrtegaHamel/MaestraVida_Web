from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from eventos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),        # Raíz del sitio en la app core
    path('eventos/', include('eventos.urls', namespace='eventos')),
    path('bandas/', include('bandas.urls', namespace='bandas')),
    path('usuarios/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)