## Optimización de Rendimiento del Juego de la Vida con Numba Tarea 4
Este proyecto implementa el Juego de la Vida de Conway y un conjunto de herramientas para analizar su rendimiento. Se incluye una versión optimizada con Numba para demostrar cómo se puede acelerar el código Python intensivo en cómputo.

# Estructura del Código
El script principal, tarea4.py, contiene dos clases principales:

GameOfLife: La implementación original del Juego de la Vida.

GameOfLifeNumba: Una versión optimizada de la clase, donde las funciones principales de cálculo (_count_neighbors_numba y _update_state_numba) han sido decoradas con @jit de Numba.

## Uso y Análisis de Rendimiento
El script utiliza argparse para permitirte ejecutar diferentes tipos de análisis de rendimiento desde la línea de comandos.

1. Comparación con Numba

Esta es la herramienta principal para entender el impacto de la optimización. Este comando ejecuta tanto la versión original como la versión con Numba y mide sus tiempos de ejecución.

Comando: python tarea4.py compare-numba --nx 1024 --ny 1024 --steps 500

# Resultados Esperados:

Al ejecutar este comando, se generará un archivo llamado Performance.md en el mismo directorio. Este archivo contendrá una tabla que muestra la diferencia de rendimiento.

Ejemplo de Performance.md: 
# Análisis de Rendimiento: Juego de la Vida

## Comparación de rendimiento: Versión Original vs. Numba

Tamaño de la cuadrícula: 1024x1024
Número de pasos de simulación: 500

| Versión | Tiempo de Ejecución (s) | Aceleración (Speedup) |
|---------|-------------------------|-----------------------|
| Original | `25.5432` | `1.0` |
| Numba | `0.4578` | `55.80` |


2. Perfilado de Código (cProfile)

Este comando utiliza el módulo cProfile para perfilar la ejecución del código original e identificar cuellos de botella.

Comando: python tarea4.py profile --nx 512 --ny 512 --steps 100
Resultados Esperados:

perf.pstats: Un archivo binario con los datos del perfil.

cprofile.txt: Un archivo de texto con un resumen legible de las llamadas a funciones, tiempo total y tiempo acumulado. Este archivo te ayudará a ver qué funciones consumen más tiempo, 
confirmando por qué la optimización de _count_neighbors y _update_state es efectiva.

3. Perfilado de Líneas (line-profiler)

Este comando utiliza kernprof para un análisis más granular, mostrando el tiempo de ejecución línea por línea dentro de las funciones decoradas con @profile.
python tarea4.py line
Resultados Esperados:
Se generará una salida en la consola que te mostrará cuánto tiempo y cuántas veces se ejecutó cada línea de las funciones _count_neighbors y _update_state, permitiendo una inspección detallada.

4. Benchmarking de Escalabilidad
Usando el comando : python tarea4.py strong / python tarea4.py weak
Resultado genera un CSV

6. Generación de Gráficas
comando: python tarea4.py plot
