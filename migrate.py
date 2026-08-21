import subprocess
import sys
import os

# Cambia al directorio del proyecto
os.chdir('/home/maestrav/public_html/honest-olive-crane.74-50-73-10.cpanel.site/app')

# Ejecuta las migraciones
result = subprocess.run(
    [sys.executable, "manage.py", "migrate"],
    capture_output=True,
    text=True
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)