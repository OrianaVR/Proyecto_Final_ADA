"""Punto de entrada de la aplicación TravelPath."""

import sys
from pathlib import Path

# Agregar raíz y lib a sys.path
root_dir = Path(__file__).resolve().parent
lib_dir = root_dir / "lib"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

import flet as ft
from lib.ui.app import main

if __name__ == "__main__":
    ft.app(target=main)
