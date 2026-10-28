# Laboratorio 5: Programación con Pthreads — Concurrencia y Sincronización

## Instrucciones de compilación y ejecución

### 1. Compilación de programas C++
Compilar los programas secuenciales y multithreading utilizando `g++` con optimización `-O3` y la bandera `-pthread`:

```bash
# Cálculo de Pi
g++ -O3 -pthread pisecuencial.cpp -o pisecuencial
g++ -O3 -pthread pipthreads.cpp -o pipthreads

# Multiplicación Matriz-Vector
g++ -O3 -pthread matvecsecuencial.cpp -o matvecsecuencial
g++ -O3 -pthread matvecpthreads.cpp -o matvecpthreads

# Lista Enlazada
g++ -O3 -pthread listasinsync.cpp -o listasinsync
g++ -O3 -pthread listaconsync.cpp -o listaconsync

# Barreras de Sincronización
g++ -O3 -pthread barrerabusywait.cpp -o barrerabusywait
g++ -O3 -pthread barreracondvar.cpp -o barreracondvar
g++ -O3 -pthread barrerasemaforo.cpp -o barrerasemaforo
```

### 2. Ejecución de los benchmarks
Ejecutar los binarios para recolectar las métricas de rendimiento en archivos CSV:

```bash
./pisecuencial && ./pipthreads

./matvecsecuencial && ./matvecpthreads

./listasinsync && ./listaconsync

./barrerabusywait && ./barreracondvar && ./barrerasemaforo
```

### 3. Generación de gráficas
Ejecutar los scripts de Python para procesar los datos de los CSV y generar las figuras de rendimiento:

```bash
python3 graficar1.py  # Gráficas de Pi: tiempos, speedup y eficiencia
python3 graficar2.py  # Gráficas de Matriz-Vector: tiempos, speedup y eficiencia
python3 graficar3.py  # Gráficas de Lista: consistencia, tiempos y throughput
python3 graficar4.py  # Gráficas de Barreras: tiempos y costo de sincronización
```