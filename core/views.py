from datetime import datetime, timedelta
import os

from django.conf import settings
from django.shortcuts import render
from django.db.models import Count
from django.templatetags.static import static

from bandas.models import FotoBanda, Album
from eventos.models import CarteleraMensual, Evento


def home(request):
    return render(request, 'core/index.html')


def nosotros(request):
    """
    Vista 'nosotros' que suministra las mismas variables que cartelera.html:
    cartelera, eventos, fotos — y además 'albums' para la sección 'Nuestro local'.

    Además busca imágenes para el carrusel de historia en:
      core/static/core/images/historia/   (preferido)
    o, si no existe, en:
      core/static/core/images/           (archivos que empiecen por 'historia' o 'nosotros')

    Las rutas se convierten a URLs usando templatetag static() para que funcionen
    en desarrollo y producción (después de collectstatic).
    """
    ahora = datetime.now()
    hoy = ahora.date()
    dia_semana = hoy.weekday()

    # Lógica para calcular inicio/fin de la "cartelera semanal" (martes->jueves)
    if dia_semana in [4, 5, 6, 0]:
        dias_hasta_proximo_martes = (1 - dia_semana) % 7
        inicio_cartelera = hoy + timedelta(days=dias_hasta_proximo_martes)
    else:
        inicio_cartelera = hoy - timedelta(days=(dia_semana - 1))

    fin_cartelera = inicio_cartelera + timedelta(days=2)

    eventos_semana = Evento.objects.filter(
        hora__date__gte=inicio_cartelera,
        hora__date__lte=fin_cartelera
    ).order_by("hora")

    cartelera = CarteleraMensual.vigente()

    # Fotos para la galería principal (igual que antes)
    fotos_recientes = (
        FotoBanda.objects
        .select_related('evento', 'evento__banda')
        .filter(imagen__isnull=False)
        .order_by('-evento__hora', '-creado_en')[:48]
    )

    # Álbumes — sólo los que tienen fotos, con prefetch para mejorar rendimiento
    albums_qs = (
        Album.objects
        .annotate(num_fotos=Count('fotos'))
        .filter(num_fotos__gt=0)
        .prefetch_related('fotos')
        .order_by('-creado_en')[:12]
    )

    # --- Construir lista de imágenes para el carrusel de "Nuestra Historia" ---
    historia_imgs = []
    allowed_ext = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

    # Preferimos una subcarpeta 'historia' dentro de core/static/core/images
    images_root = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'images')
    historia_subdir = os.path.join(images_root, 'historia')

    try:
        if os.path.isdir(historia_subdir):
            # tomar todos los archivos de la subcarpeta historia
            for fname in sorted(os.listdir(historia_subdir)):
                if fname.lower().endswith(allowed_ext):
                    rel_path = f'core/images/historia/{fname}'
                    historia_imgs.append(static(rel_path))
        else:
            # Si no existe la subcarpeta, buscar archivos con prefijo 'historia' o 'nosotros'
            if os.path.isdir(images_root):
                for fname in sorted(os.listdir(images_root)):
                    low = fname.lower()
                    if low.endswith(allowed_ext) and (low.startswith('historia') or low.startswith('nosotros')):
                        rel_path = f'core/images/{fname}'
                        historia_imgs.append(static(rel_path))
    except Exception:
        # En caso de cualquier error con el FS, dejamos historia_imgs vacío para que
        # la plantilla use el fallback (cartelera.imagen o imagen por defecto).
        historia_imgs = []

    contexto = {
        'cartelera': cartelera,
        'eventos': eventos_semana,
        'fotos': fotos_recientes,
        'albums': albums_qs,
        'historia_imgs': historia_imgs,
    }
    return render(request, 'core/nosotros.html', contexto)