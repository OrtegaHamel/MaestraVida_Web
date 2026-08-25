from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render


def user_login(request):
  if request.GET.get('next'):
    messages.warning(request, 'Debes iniciar sesión para acceder a esa página.')

  if request.method == 'POST':
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)

      # Verificamos si hay un parámetro 'next' seguro en el POST o GET,
      # de lo contrario redirigimos a la ruta nombrada del panel home.
      next_url = request.POST.get('next') or request.GET.get('next')
      if not next_url:
        next_url = 'usuarios:panel_home'

      return redirect(next_url)
    else:
      messages.error(request, 'Usuario o contraseña inválidos.')
  else:
    form = AuthenticationForm()
  return render(request, 'usuarios/login.html', {'form': form})


def user_logout(request):
  logout(request)
  return redirect('usuarios:login')


def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Asignar un grupo por defecto al registrarse (Opcional)
            grupo_base, _ = Group.objects.get_or_create(name='Colaborador')
            user.groups.add(grupo_base)
            
            messages.success(request, 'Cuenta creada con éxito. Un administrador asignará tu rol específico pronto.')
            return redirect('usuarios:login') 
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def panel_home(request):
  # Detectar el primer grupo del usuario para mostrarlo en el panel
  if request.user.is_superuser:
    nombre_grupo = 'Superusuario'
  elif request.user.groups.exists():
    nombre_grupo = request.user.groups.first().name
  else:
    nombre_grupo = 'Colaborador'

  return render(request, 'usuarios/panel_home.html', {'nombre_grupo': nombre_grupo})