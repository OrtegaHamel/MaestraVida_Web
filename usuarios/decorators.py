from django.contrib.auth.decorators import user_passes_test


def grupo_required(nombre_grupo):
  """Decorador que permite el acceso si el usuario es superusuario

  o pertenece al grupo indicado (o lista de grupos).
  """
  if isinstance(nombre_grupo, str):
    grupos_permitidos = [nombre_grupo]
  else:
    grupos_permitidos = nombre_grupo

  def check(user):
    if not user.is_authenticated:
      return False
    if user.is_superuser:
      return True
    return user.groups.filter(name__in=grupos_permitidos).exists()

  return user_passes_test(check)