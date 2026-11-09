# TravelPath - Planificador de Rutas y Optimización de Viajes

TravelPath es una aplicación desarrollada en **Python 3.11+** con arquitectura limpia y desacoplada, utilizando **Flet** (el framework de Flutter para Python) para la interfaz gráfica y visualización del grafo. Resuelve la planificación de itinerarios turísticos combinando costos de transporte, tiempos de viaje, restricciones presupuestarias y orden parcial mediante algoritmos de **Dijkstra** y **Branch and Bound (Ramificación y Poda)** con listado top-K.

---

## Arquitectura por Capas

El proyecto mantiene una separación estricta de responsabilidades:

```text
Proyecto_Final_ADA/
├── assets/
│   └── destinos.json                 # Matriz fuente de 10 ciudades (costos en pesos y tiempos en horas)
├── lib/
│   ├── data/                         # Repositorio de lectura y validación de matrices fuente
│   │   └── destinos_repository.py
│   ├── models/                       # Modelos de dominio
│   │   ├── destino.py
│   │   ├── arista.py
│   │   ├── ruta.py
│   │   ├── entrada.py
│   │   └── restricciones.py
│   ├── structures/                   # Estructuras de datos
│   │   ├── grafo.py                  # Grafo ponderado, normalización y peso combinado configurable
│   │   ├── tabla_precedencias.py     # Tabla hash de orden parcial, O(1) y detección de ciclos
│   │   └── cola_prioridad.py         # Min-heap genérico con desempate FIFO y tuplas de prioridad
│   ├── algorithms/                   # Algoritmos de optimización
│   │   ├── dijkstra.py               # Caminos mínimos con reconstrucción y ciudades prohibidas
│   │   ├── matriz_caminos.py         # Matrices D_peso, D_dinero y D_min entre ciudades seleccionadas
│   │   ├── orden_total.py            # Resolución directa cuando el usuario define la secuencia completa
│   │   ├── branch_and_bound.py       # Branch and Bound con cotas admisibles, podas y listado top-K
│   │   └── fuerza_bruta.py           # Oráculo de evaluación exhaustiva para verificación en tests
│   ├── services/                     # Servicios coordinadores (modalidad y validaciones)
│   │   └── planificador_viaje.py     # Coordinador único y resultado uniforme
│   └── ui/                           # Interfaz de usuario (Flet)
│       ├── pantalla_formulario.py
│       ├── pantalla_resultados.py
│       ├── pantalla_grafo.py
│       └── app.py
├── tests/                            # Pruebas unitarias y de integración con pytest (88 tests)
│   ├── conftest.py
│   ├── utils_grafos.py
│   ├── test_carga_datos.py
│   ├── test_grafo.py
│   ├── test_tabla_precedencias.py
│   ├── test_cola_prioridad.py
│   ├── test_dijkstra.py
│   ├── test_matriz_caminos.py
│   ├── test_orden_total.py
│   ├── test_fuerza_bruta.py
│   └── test_branch_and_bound.py
├── docs/                             # Notas de traspaso y análisis técnico
│   ├── nota_traspaso_integrante1.md  # Traspaso Integrante 1 -> 2
│   ├── nota_traspaso_integrante3.md  # Traspaso Integrante 3 -> 4
│   └── tabla_poda.md                 # Análisis empírico de nodos explorados vs n!
├── pyproject.toml                    # Configuración del proyecto y pytest
├── requirements.txt                  # Dependencias del proyecto
└── main.py                           # Punto de inicio de la aplicación
```

---

## Instalación y Requisitos

### 1. Requisitos previos
- **Python 3.11 o superior**.

### 2. Instalación de dependencias
```bash
pip install -r requirements.txt
```

Las dependencias principales son:
- `flet>=0.25.0`: Framework de interfaz de usuario.
- `pytest>=8.0.0`: Framework de ejecución de pruebas unitarias.

---

## Ejecución de Pruebas Unitarias

Para correr las **pruebas unitarias** del proyecto:

```bash
# Desde la carpeta Proyecto_Final_ADA:
pytest
```

Para una ejecución detallada mostrando cada caso de prueba:
```bash
pytest -v
```

Para ejecutar únicamente las pruebas del módulo **Branch and Bound**:
```bash
pytest tests/test_branch_and_bound.py -v
```

Para ejecutar las pruebas del oráculo de **Fuerza Bruta**:
```bash
pytest tests/test_fuerza_bruta.py -v
```

---

## Ejecución de la Aplicación Visual (Flet)

Para iniciar la interfaz gráfica de usuario:

```bash
python main.py
```

El formulario permite seleccionar hasta 12 destinos, configurar presupuesto,
K, ida y vuelta y las ponderaciones α/β. La pantalla de resultados ordena las
rutas por peso, muestra el sobrante y detalla sus tramos.
