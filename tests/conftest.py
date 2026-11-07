import sys
from pathlib import Path

# Agregar directorio raíz y lib al PYTHONPATH para ejecución de tests
root_dir = Path(__file__).resolve().parent.parent
lib_dir = root_dir / "lib"

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))
