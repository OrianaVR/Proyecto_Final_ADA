# Nota de cierre - ÉPICA 5: Grafo visual, integración y cierre (Integrante 5)

1. `PantallaGrafo(grafo, ruta_seleccionada=None, on_volver=None)`: dibuja los destinos en círculo y anima la ruta.
2. Nodos en círculo con `x = cx + r·cos(2πk/n)`, `y = cy + r·sin(2πk/n)`; conexiones dibujadas como líneas sin etiquetas de peso; origen resaltado. (HU-13)
3. Botón «Ver en grafo» en `PantallaResultados` (parámetro `on_ver_en_grafo`) que abre el grafo con esa ruta. (HU-14)
4. «Simular recorrido» ilumina los tramos en orden; refleja ida y vuelta y ciudades de paso usando `ruta.tramos`. (HU-14)
5. Separación de capas: la pantalla solo dibuja; no contiene lógica de algoritmos.
6. Pruebas: suite completa en verde (100 tests), incluida la validación de los algoritmos de optimización. (HU-15)
7. Casos obligatorios de la sección 11 cubiertos en la capa lógica (ver mapa en el PR); B&B vs fuerza bruta en 100 casos.
8. Documentación: `README.md` (instalación/ejecución/arquitectura), `docs/manual_uso.md` y `docs/tabla_poda.md` (informe de poda).
9. `requirements.txt` fija `flet[all]>=0.27,<0.28` (las 1.x rompen la API); `preview_grafo.py` previsualiza el grafo aislado.
10. Pendiente de equipo: unir a `main`, revisión de 15 min y aprobación final.
