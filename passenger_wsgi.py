import os
import sys

# 1. Agrega la ruta limpia de tu proyecto al path de Python
sys.path.insert(0, '/home/maestrav/maestra_webpage')

# 2. Define el módulo de configuración de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# 3. Importa la aplicación WSGI nativa de Django
from config.wsgi import application