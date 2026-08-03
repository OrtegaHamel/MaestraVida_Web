# D:\dev\maestra_webpage\eventos\views.py
from datetime import datetime, timedelta

from bandas.models import FotoBanda
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from usuarios.decorators import grupo_required

from .forms import AsistenciaEventoForm, BusquedaEventosForm, EventoForm
from .models import Evento

# ==========================================
# VISTA PÚBLICA (INDEX / CARTELERA)
# ==========================================


def home_publico(request):
    ahora = datetime.now()
    hoy = ahora.date()
    dia_semana = hoy.weekday() # Lunes = 0, Martes = 1, Miércoles = 2, Jueves = 3, Viernes = 4, Sábado = 5, Domingo = 6

    # Si es Viernes (4), Sábado (5), Domingo (6) o Lunes (0), miramos hacia la PRÓXIMA semana
    if dia_semana in [4, 5, 6, 0]:
        dias_hasta_proximo_martes = (1 - dia_semana) % 7
        inicio_cartelera = hoy + timedelta(days=dias_hasta_proximo_martes)
    # Si es Martes (1), Miércoles (2) o Jueves (3), miramos la semana ACTUAL
    else:
        inicio_cartelera = hoy - timedelta(days=(dia_semana - 1))

    # SOLUCIÓN: Sumamos solo 2 días al martes para que el fin de la cartelera sea el JUEVES
    fin_cartelera = inicio_cartelera + timedelta(days=2)

    # Filtramos los eventos que ocurran entre ese martes y ese jueves
    eventos_semana = Evento.objects.filter(
        hora__date__gte=inicio_cartelera, 
        hora__date__lte=fin_cartelera
    ).order_by('hora')

    # Obtenemos las últimas 8 fotos para la galería
    fotos_recientes = FotoBanda.objects.all().order_by('-creado_en')[:8]

    return render(
        request,
        'core/index.html',
        {
            'eventos': eventos_semana,
            'fotos': fotos_recientes,
            'inicio_cartelera': inicio_cartelera,
            'fin_cartelera': fin_cartelera,
        },
    )

def detalle_evento_publico(request, slug):
  evento = get_object_or_404(Evento, slug=slug)
  return render(request, 'eventos/detalle_evento.html', {'evento': evento})


# ==========================================
# PANEL INTERNO: LISTA DE EVENTOS
# ==========================================

@login_required
@grupo_required('Productores')
def lista_eventos(request):
    eventos = Evento.objects.all().order_by('-hora')
    
    nombre_banda = request.GET.get('banda')
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    
    if nombre_banda:
        eventos = eventos.filter(banda__nombre__icontains=nombre_banda)
    if fecha_desde:
        eventos = eventos.filter(hora__date__gte=fecha_desde)
    if fecha_hasta:
        eventos = eventos.filter(hora__date__lte=fecha_hasta)
        
    paginator = Paginator(eventos, 10) 
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)
    
    # --- NUEVA LÓGICA PARA PRESERVAR FILTROS ---
    # 1. Hacemos una copia de los parámetros GET actuales (es inmutable por defecto)
    parametros_get = request.GET.copy()
    
    # 2. Si ya existe la clave 'page', la eliminamos para que no colisione con nuestros botones
    if 'page' in parametros_get:
        del parametros_get['page']
        
    # 3. Convertimos el diccionario nuevamente a un formato de URL (ej: banda=Salsa&desde=2024-01-01)
    parametros_url = parametros_get.urlencode()
    # -------------------------------------------
        
    contexto = {
        'eventos': page_obj, 
        'parametros_url': parametros_url, # Lo enviamos a la plantilla
    }
    
    return render(request, 'eventos/lista_eventos.html', contexto)


# ==========================================
# ACCIONES EXCLUSIVAS DEL PRODUCTOR
# ==========================================


@login_required
@grupo_required('Productores')
def crear_evento(request):
  if request.method == 'POST':
    form = EventoForm(request.POST, request.FILES)
    if form.is_valid():
      evento = form.save(commit=False)
      evento.creado_por = request.user
      evento.save()
      return redirect(
          f"{reverse('eventos:lista_eventos')}?mensaje=Evento+creado+exitosamente&tipo=success"
      )
  else:
    form = EventoForm()
  return render(request, 'eventos/crear_evento.html', {'form': form})


@login_required
@grupo_required('Productores')
def editar_evento(request, evento_id):
  evento = get_object_or_404(Evento, id=evento_id)
  if request.method == 'POST':
    form = EventoForm(request.POST, request.FILES, instance=evento)
    if form.is_valid():
      form.save()
      return redirect(
          f"{reverse('eventos:lista_eventos')}?mensaje=Evento+actualizado+exitosamente&tipo=success"
      )
  else:
    form = EventoForm(instance=evento)
  return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})


@login_required
@grupo_required('Productores')
def eliminar_evento(request, evento_id):
  evento = get_object_or_404(Evento, id=evento_id)
  if request.method == 'POST':
    evento.delete()
    return redirect(
        f"{reverse('eventos:lista_eventos')}?mensaje=Evento+eliminado+exitosamente&tipo=success"
    )
  return render(request, 'eventos/eliminar_evento.html', {'evento': evento})


# ==========================================
# ROL DE LA PUERTA (Control de Asistencia de Hoy)
# ==========================================


@login_required
@grupo_required(['Puerta', 'Productores'])
def eventos_hoy(request):
    ahora = datetime.now()
    
    # 1. Determinamos la "jornada operativa"
    # Si la hora actual es menor a las 12:00 hrs (madrugada/mañana),
    # el evento activo pertenece a la jornada del día anterior.
    if ahora.hour < 12:
        fecha_operativa = (ahora - timedelta(days=1)).date()
    else:
        fecha_operativa = ahora.date()

    # 2. Obtenemos los eventos correspondientes a la jornada operativa actual
    eventos = Evento.objects.filter(hora__date=fecha_operativa).order_by('hora')

    # 3. Calculamos los eventos pendientes tomando como referencia la fecha operativa
    limite_atras = fecha_operativa - timedelta(days=7)
    eventos_pendientes = (
        Evento.objects.filter(hora__date__lt=fecha_operativa, hora__date__gte=limite_atras)
        .filter(Q(asistencia=0) | Q(asistencia__isnull=True))
        .order_by('-hora')
    )

    return render(
        request,
        'eventos/eventos_hoy.html',
        {
            'eventos': eventos,
            'eventos_pendientes': eventos_pendientes,
            # Pasamos 'fecha_operativa' en la clave 'hoy' para mantener compatibilidad con la plantilla
            'hoy': fecha_operativa,
        },
    )


@login_required
@grupo_required(['Puerta', 'Productores'])
def registrar_asistencia(request, evento_id):
  evento = get_object_or_404(Evento, id=evento_id)

  if request.method == 'POST':
    form = AsistenciaEventoForm(request.POST, instance=evento)
    if form.is_valid():
      form.save()
      return redirect(
          f"{reverse('eventos:eventos_hoy')}?mensaje=Asistencia+guardada+correctamente&tipo=success"
      )
  else:
    form = AsistenciaEventoForm(instance=evento)

  return render(
      request,
      'eventos/registrar_asistencia.html',
      {'form': form, 'evento': evento},
  )


# ==========================================
# BÚSQUEDAS Y REPORTES ENFOQUE PRODUCCIÓN
# ==========================================

@login_required
@grupo_required('Productores')
def busqueda_eventos(request):
  form = BusquedaEventosForm(request.GET or None)
  eventos = Evento.objects.all().order_by('hora')

  reporte_banda = None
  banda_seleccionada = None

  if form.is_valid():
    banda = form.cleaned_data.get('banda')
    fecha_inicio = form.cleaned_data.get('fecha_inicio')
    fecha_fin = form.cleaned_data.get('fecha_fin')

    if banda:
      banda_seleccionada = banda
      eventos = eventos.filter(banda=banda)
      reporte_banda = Evento.objects.filter(banda=banda).aggregate(
          total_shows=Count('id'), total_asistentes=Sum('asistencia')
      )

    if fecha_inicio:
      eventos = eventos.filter(hora__date__gte=fecha_inicio)
    if fecha_fin:
      eventos = eventos.filter(hora__date__lte=fecha_fin)

  return render(
      request,
      'eventos/busqueda_eventos.html',
      {
          'form': form,
          'eventos': eventos,
          'reporte_banda': reporte_banda,
          'banda_seleccionada': banda_seleccionada,
      },
  )