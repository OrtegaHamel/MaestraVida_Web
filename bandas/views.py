# D:\dev\maestra_webpage\bandas\views.py
from datetime import datetime, timedelta
import os
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Count, Max
from eventos.models import Evento
from usuarios.decorators import grupo_required

# Importaciones locales de modelos y utilidades
from .forms import AlbumForm, BandaForm, SubirFotosAlbumForm
from .models import Album, Banda, FotoAlbum, FotoBanda, procesar_y_optimizar_a_webp


def galeria(request):
    """
    Galería pública: muestra:
      - 'albums' : cuadrícula de álbumes (cada album con sus fotos)
      - 'event_albums' : eventos agrupados por fotos (Maestra Vida en Vivo), presentados como 'álbumes'
      - 'fotos'  : fotos sueltas (si las quieres mantener)
    """
    # Álbumes con al menos 1 foto (si deseas mantener la sección de álbumes)
    albums = (
        Album.objects
        .annotate(num_fotos=Count('fotos'), latest_photo=Max('fotos__creado_en'))
        .filter(num_fotos__gt=0)
        .prefetch_related('fotos')
        .order_by('-latest_photo', '-creado_en')[:6]
    )

    # Eventos que tienen fotos (agrupamos fotos de banda por evento)
    event_albums = (
        Evento.objects
        .annotate(num_fotos=Count('fotos_galeria'), latest_photo=Max('fotos_galeria__creado_en'))
        .filter(num_fotos__gt=0)
        .select_related('banda')
        .prefetch_related('fotos_galeria')
        .order_by('-latest_photo')[:9]   # 9 eventos => 3 filas x 3 columnas
    )

    # Fotos recientes sueltas (opcional, si quieres mantener la galería suelta)
    fotos = (
        FotoBanda.objects
        .select_related('evento', 'evento__banda')
        .filter(imagen__isnull=False)
        .order_by('-evento__hora', '-creado_en')[:48]
    )

    context = {
        'albums': albums,
        'event_albums': event_albums,  # nueva variable para la plantilla
        'fotos': fotos,
    }

    return render(request, 'galerias/galeria.html', context)

# ==========================================
# ACCIONES EXCLUSIVAS DEL PRODUCTOR
# ==========================================

@login_required
@grupo_required('Productores')
def lista_bandas(request):
    # Aseguramos el orden por defecto alfabético por nombre
    bandas = Banda.objects.all().order_by('nombre')
    
    # Capturamos el parámetro de búsqueda
    query = request.GET.get('q')
    
    if query:
        bandas = bandas.filter(nombre__icontains=query).order_by('nombre')
        
    # --- NUEVA LÓGICA DE PAGINACIÓN ---
    paginator = Paginator(bandas, 10) 
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)
    
    parametros_get = request.GET.copy()
    if 'page' in parametros_get:
        del parametros_get['page']
    parametros_url = parametros_get.urlencode()
    # ----------------------------------
        
    contexto = {
        'bandas': page_obj, # Enviamos la página en lugar del QuerySet completo
        'parametros_url': parametros_url,
    }
    return render(request, 'bandas/lista_bandas.html', contexto)


@login_required
@grupo_required('Productores')
def detalle_banda(request, banda_id):
    banda = get_object_or_404(Banda, id=banda_id)
    
    # Obtenemos los eventos asociados a la banda
    eventos = Evento.objects.filter(banda=banda)
    
    # Capturamos los parámetros del formulario GET
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    orden = request.GET.get('orden', '-hora') # '-hora' es el valor por defecto
    
    # Aplicamos los filtros de fecha si existen
    if fecha_desde:
        eventos = eventos.filter(hora__date__gte=fecha_desde)
        
    if fecha_hasta:
        eventos = eventos.filter(hora__date__lte=fecha_hasta)
        
    # Definimos las opciones de ordenamiento válidas por seguridad
    opciones_validas = ['-hora', 'hora', '-asistencia', '-precio_puerta']
    
    # Validamos y aplicamos el ordenamiento
    if orden in opciones_validas:
        eventos = eventos.order_by(orden)
    else:
        eventos = eventos.order_by('-hora') # Caída segura por defecto
        
    contexto = {
        'banda': banda,
        'eventos': eventos,
    }
    
    return render(request, 'bandas/detalle_banda.html', contexto)


@login_required
@grupo_required('Productores')
def crear_banda(request):
    if request.method == 'POST':
        form = BandaForm(request.POST, request.FILES)
        if form.is_valid():
            banda = form.save(commit=False)
            # si tienes campos como creado_por, asigna: banda.creado_por = request.user
            banda.save()
            messages.success(request, 'Banda creada correctamente.')
            return redirect(f"{reverse('eventos:lista_eventos')}?mensaje=Banda+creada+exitosamente&tipo=success")
        else:
            # Mostrar errores en consola/log para debugging
            print('Errores formulario Banda:', form.errors.as_json())
            messages.error(request, 'El formulario contiene errores. Revisa los campos marcados.')
    else:
        form = BandaForm()
    return render(request, 'bandas/crear_banda.html', {'form': form})


@login_required
@grupo_required('Productores')
def editar_banda(request, banda_id):
  banda = get_object_or_404(Banda, id=banda_id)
  if request.method == 'POST':
    form = BandaForm(request.POST, instance=banda)
    if form.is_valid():
      form.save()
      return redirect(
          f"{reverse('bandas:lista_bandas')}?mensaje=Banda+actualizada+exitosamente&tipo=success"
      )
  else:
    form = BandaForm(instance=banda)
  return render(
      request, 'bandas/editar_banda.html', {'form': form, 'banda': banda}
  )


@login_required
@grupo_required('Productores')
def eliminar_banda(request, banda_id):
  banda = get_object_or_404(Banda, id=banda_id)
  if request.method == 'POST':
    banda.delete()
    return redirect(
        f"{reverse('bandas:lista_bandas')}?mensaje=Banda+eliminada+exitosamente&tipo=success"
    )
  return render(request, 'bandas/eliminar_banda.html', {'banda': banda})


# ==========================================
# SECCIÓN DEL FOTÓGRAFO (SUBIDA OPTIMIZADA)
# ==========================================

@login_required
@grupo_required('Fotografos')
def panel_fotografo_eventos(request):
    hoy = datetime.now().date()
    
    # Anotamos cada evento con el total de fotos en su galería
    eventos = (
        Evento.objects.filter(hora__date__lte=hoy)
        .annotate(total_fotos=Count('fotos_galeria'))
        .prefetch_related('fotos_galeria')
        .order_by('-hora')
    )

    nombre_banda = request.GET.get('banda')
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    estado_filtro = request.GET.get('estado')

    # Filtros ORM directos
    if nombre_banda:
        eventos = eventos.filter(banda__nombre__icontains=nombre_banda)
    if fecha_desde:
        eventos = eventos.filter(hora__date__gte=fecha_desde)
    if fecha_hasta:
        eventos = eventos.filter(hora__date__lte=fecha_hasta)

    # Filtrado por estado directamente en la base de datos (SQL)
    if estado_filtro == 'pendiente':
        eventos = eventos.filter(total_fotos=0)
    elif estado_filtro == 'con_fotos':
        eventos = eventos.filter(total_fotos__gt=0)

    # Paginación optimizada a nivel SQL (solo trae 10 registros por página desde la DB)
    paginator = Paginator(eventos, 10)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    # Preservar parámetros en los enlaces de paginación
    parametros_get = request.GET.copy()
    if 'page' in parametros_get:
        del parametros_get['page']
    parametros_url = parametros_get.urlencode()

    return render(
        request,
        'galerias/panel_fotografo_eventos.html',
        {
            'eventos': page_obj,
            'parametros_url': parametros_url
        },
    )


# ==========================================
# ALBUM DE FOTOS
# ==========================================


@login_required
@grupo_required('Fotografos')
def lista_albumes(request):
    # Obtenemos todos los álbumes ordenados por fecha de creación descendente por defecto
    albumes = Album.objects.all().order_by('-creado_en')
    
    # Capturamos los parámetros GET
    query_titulo = request.GET.get('q')
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    
    # 1. Filtro por título o nombre del álbum
    if query_titulo:
        albumes = albumes.filter(titulo__icontains=query_titulo)
        
    # 2. Filtro por fecha de creación desde
    if fecha_desde:
        albumes = albumes.filter(creado_en__date__gte=fecha_desde)
        
    # 3. Filtro por fecha de creación hasta
    if fecha_hasta:
        albumes = albumes.filter(creado_en__date__lte=fecha_hasta)
        
    contexto = {
        'albumes': albumes,
    }
    return render(request, 'galerias/lista_albumes.html', contexto)

@login_required
@grupo_required('Fotografos')
def crear_album(request):
  if request.method == 'POST':
    form = AlbumForm(request.POST)
    if form.is_valid():
      album = form.save(commit=False)
      album.creado_por = request.user
      album.save()
      return redirect('bandas:subir_fotos_album', album_id=album.id)
  else:
    form = AlbumForm()

  return render(request, 'galerias/crear_album.html', {'form': form})


@login_required
@grupo_required('Fotografos')
def subir_fotos_album(request, album_id):
  album = get_object_or_404(Album, id=album_id)

  if request.method == 'POST':
    archivos_imagenes = request.FILES.getlist('imagenes')

    if not archivos_imagenes:
      messages.error(
          request, 'No se recibieron imágenes. Intenta seleccionarlas de nuevo.'
      )
      return redirect(request.path)

    prefijo_nombre = slugify(album.titulo)
    fotos_creadas = 0

    for archivo in archivos_imagenes:
      nueva_foto = FotoAlbum(album=album)
      nueva_foto.imagen = procesar_y_optimizar_a_webp(
          archivo, prefijo_nombre=prefijo_nombre
      )
      nueva_foto.save()
      fotos_creadas += 1

    messages.success(
        request, f'¡Se subieron {fotos_creadas} fotos al álbum correctamente!'
    )
    return redirect('bandas:gestionar_fotos_album', album_id=album.id)
  else:
    form = SubirFotosAlbumForm()

  return render(
      request,
      'galerias/subir_fotos_album.html',
      {'form': form, 'album': album},
  )


@login_required
@grupo_required('Fotografos')
def eliminar_album(request, album_id):
  album = get_object_or_404(Album, id=album_id)

  if request.method == 'POST':
    titulo_album = album.titulo
    album.delete()
    messages.success(
        request,
        f"El álbum '{titulo_album}' ha sido eliminado correctamente.",
    )
    return redirect('bandas:lista_albumes')

  return render(request, 'galerias/eliminar_album.html', {'album': album})


@login_required
@grupo_required('Fotografos')
def gestionar_fotos_album(request, album_id):
  album = get_object_or_404(Album, id=album_id)

  if request.method == 'POST':
    archivos = request.FILES.getlist('imagenes')

    if not archivos:
      messages.error(request, 'No se seleccionaron archivos.')
      return redirect(request.path)

    for archivo in archivos:
      FotoAlbum.objects.create(album=album, imagen=archivo)

    messages.success(request, 'Fotos añadidas al álbum con éxito.')
    return redirect('bandas:gestionar_fotos_album', album_id=album.id)

  fotos = album.fotos.all()
  return render(
      request,
      'galerias/editar_fotos_album.html',
      {'album': album, 'fotos': fotos},
  )


@login_required
@grupo_required('Fotografos')
def editar_album(request, album_id):
  album = get_object_or_404(Album, id=album_id)

  if request.method == 'POST':
    form = AlbumForm(request.POST, instance=album)
    if form.is_valid():
      form.save()
      messages.success(request, 'Álbum actualizado con éxito.')
      return redirect('bandas:lista_albumes')
  else:
    form = AlbumForm(instance=album)

  return render(
      request, 'galerias/editar_album.html', {'form': form, 'album': album}
  )


@login_required
@grupo_required('Fotografos')
def eliminar_foto_album(request, foto_id):
  foto = get_object_or_404(FotoAlbum, id=foto_id)
  album_id = foto.album.id
  foto.delete()
  messages.success(request, 'Foto eliminada correctamente.')
  return redirect('bandas:gestionar_fotos_album', album_id=album_id)


# ==========================================
# FOTOS EVENTOS
# ==========================================


@login_required
@grupo_required('Fotografos')
def subir_fotos_evento(request, evento_id):
  evento = get_object_or_404(Evento, id=evento_id)

  if request.method == 'POST':
    archivos_imagenes = request.FILES.getlist('imagenes')

    if not archivos_imagenes:
      messages.error(request, 'No se seleccionaron archivos.')
      return redirect(request.path)

    fotos_creadas = 0
    for archivo in archivos_imagenes:
      nueva_foto = FotoBanda.objects.create(
          banda=evento.banda, evento=evento, subido_por=request.user
      )
      nueva_foto.imagen = procesar_y_optimizar_a_webp(
          archivo, prefijo_nombre=evento.slug
      )
      nueva_foto.save()
      fotos_creadas += 1

    messages.success(request, f'¡{fotos_creadas} fotos subidas con éxito!')
    return redirect('bandas:panel_fotografo_eventos')

  return render(request, 'galerias/subir_foto_banda.html', {'evento': evento})


@login_required
@grupo_required('Fotografos')
def editar_fotos_evento(request, evento_id):
  evento = get_object_or_404(Evento, id=evento_id)
  fotos = evento.fotos_galeria.all()

  context = {'evento': evento, 'fotos': fotos}
  return render(request, 'galerias/editar_fotos.html', context)


@login_required
@grupo_required('Fotografos')
def eliminar_foto(request, foto_id):
  if request.method == 'POST':
    foto = get_object_or_404(FotoBanda, id=foto_id)
    evento_id = foto.evento.id
    foto.delete()
    return redirect('bandas:editar_fotos_evento', evento_id=evento_id)
  return redirect('bandas:panel_fotografo_eventos')


@login_required
@grupo_required('Fotografos')
def subir_foto_galeria(request):
  from .forms import SubirFotoGaleriaForm

  if request.method == 'POST':
    form = SubirFotoGaleriaForm(request.POST, request.FILES)
    if form.is_valid():
      foto = form.save(commit=False)
      foto.subido_por = request.user
      foto.save()
      return redirect(
          f"{reverse('eventos:lista_eventos')}?mensaje=Foto+de+galeria+subida+y+optimizada+exitosamente&tipo=success"
      )
  else:
    form = SubirFotoGaleriaForm()

  return render(
      request, 'galerias/subir_foto_galeria.html', {'form': form, 'tipo': 'galeria'}
  )


