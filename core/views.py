from django.shortcuts import render
from datetime import datetime, timedelta
from bandas.models import FotoBanda
from eventos.models import CarteleraMensual, Evento

def home(request):
    return render(request, 'core/index.html')


from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Count
from bandas.models import FotoBanda, Album
from eventos.models import CarteleraMensual, Evento

def nosotros(request):
    """
    Vista 'nosotros' que suministra las mismas variables que cartelera.html:
    cartelera, eventos, fotos — y además 'albums' para la sección 'Nuestro local'.
    """
    ahora = datetime.now()
    hoy = ahora.date()
    dia_semana = hoy.weekday()

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
        .prefetch_related('fotos')  # relacionado FotoAlbum via related_name 'fotos'
        .order_by('-creado_en')[:12]
    )

    contexto = {
        'cartelera': cartelera,
        'eventos': eventos_semana,
        'fotos': fotos_recientes,
        'albums': albums_qs,
    }
    return render(request, 'core/nosotros.html', contexto)