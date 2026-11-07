# TravelPath - Planificador de Rutas y Optimización de Viajes

TravelPath es una aplicación desarrollada en **Python** con arquitectura limpia y desacoplada, utilizando **Flet** (el framework de Flutter para Python) para la interfaz gráfica y visualización del grafo.

---

## 🏗️ Arquitectura por Capas

El proyecto mantiene la separación estricta de responsabilidades:

```text
travelpath/
├── assets/
│   └── destinos.json           # Matriz fuente de 10 ciudades (costos en pesos y tiempos en horas)
├── lib/
│   ├── data/                   # Repositorio de lectura y validación de matrices fuente
│   │   └── destinos_repository.py
│   ├── models/                 # Modelos de dominio
│   │   ├── destino.py
│   │   ├── arista.py
│   │   ├── ruta.py
│   │   ├── entrada.py
│   │   └── restricciones.py
│   ├── structures/             # Estructuras de datos
│   │   ├── grafo.py            # Grafo ponderado, normalización y peso combinado configurable
│   │   └── tabla_precedencias.py # Tabla hash de orden parcial, O(1) y detección de ciclos
│   ├── algorithms/             
│   ├── services/              
│   └── ui/                     # Estructura del framework Flet 
│       ├── pantalla_formulario.py
│       ├── pantalla_resultados.py
│       ├── pantalla_grafo.py
│       └── app.py
├── tests/                      # Pruebas unitarias con pytest
│   ├── test_carga_datos.py
│   ├── test_grafo.py
│   └── test_tabla_precedencias.py
├── docs/
│   └── nota_traspaso_integrante1.md # Nota de traspaso (10 líneas de firmas públicas)
├── pyproject.toml              # Configuración del proyecto y pytest
├── requirements.txt            # Dependencias (flet, pytest)
└── main.py                     # Punto de inicio de la aplicación
```

---

## 🚀 Instalación y Pruebas

### 1. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecución de pruebas unitarias
```bash
pytest
```

### 3. Ejecución de la aplicación visual (Flet)
```bash
python main.py
```

---
