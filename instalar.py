import subprocess
import sys

# Ejecuta pip install usando el mismo intérprete de tu entorno virtual
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
    capture_output=True,
    text=True
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)