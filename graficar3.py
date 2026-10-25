import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

def main():
    if not os.path.exists("tiempos_lista_sin_sync.csv") or not os.path.exists("tiempos_lista_con_sync.csv"):
        print("Error: No se encontraron los archivos CSV de lista enlazada.")
        return

    df_sin = pd.read_csv("tiempos_lista_sin_sync.csv")
    df_con = pd.read_csv("tiempos_lista_con_sync.csv")

    # Porcentaje de consistencia (nodos reales conservados / esperados)
    df_sin['pct_conservados'] = (df_sin['nodos_reales'] / df_sin['nodos_esperados']) * 100.0
    df_con['pct_conservados'] = (df_con['nodos_reales'] / df_con['nodos_esperados']) * 100.0

    df_sin['throughput'] = df_sin['ops_totales'] / df_sin['tiempo']
    df_con['throughput'] = df_con['ops_totales'] / df_con['tiempo']

    # Guardar consolidado
    df_merge = pd.merge(df_sin, df_con, on='threads', suffixes=('_sin_sync', '_con_sync'))
    df_merge.to_csv("resultados_lista_completos.csv", index=False)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    threads_list = sorted(df_sin['threads'].unique())
    x = range(len(threads_list))
    thread_labels = [f'{t} threads' for t in threads_list]
    bar_width = 0.35

    #1
    plt.figure(figsize=(10, 6))

    bars_sin = plt.bar([p - bar_width/2 for p in x], df_sin['pct_conservados'], width=bar_width, color='crimson', label='Sin Sincronización')
    bars_con = plt.bar([p + bar_width/2 for p in x], df_con['pct_conservados'], width=bar_width, color='forestgreen', label='Con Sincronización')

    for bar in bars_sin:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f'{yval:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='darkred')

    for bar in bars_con:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f'{yval:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='darkgreen')

    plt.title('Consistencia de la Lista: Porcentaje de Nodos Conservados', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Nodos Correctamente Conservados (%)', fontsize=12)
    plt.xticks(x, thread_labels, fontsize=11)
    plt.ylim(0, 115)
    plt.legend(fontsize=11, loc='upper right')
    plt.grid(True, ls="--", alpha=0.5, axis='y')
    plt.tight_layout()
    plt.savefig("grafica_lista_consistencia.png", dpi=300)
    plt.close()

    # 2
    plt.figure(figsize=(10, 6))
    plt.plot(x, df_sin['tiempo'], marker='o', linewidth=2.5, markersize=8, color='crimson', label='Sin Sincronización')
    plt.plot(x, df_con['tiempo'], marker='s', linewidth=2.5, markersize=8, color='forestgreen', label='Con Sincronización (Mutex)')

    plt.title('Lista Enlazada: Tiempo de Ejecución vs Threads', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Tiempo de Ejecución (segundos)', fontsize=12)
    plt.xticks(x, thread_labels, fontsize=11)
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_lista_tiempos.png", dpi=300)
    plt.close()

    # 3
    plt.figure(figsize=(10, 6))
    plt.plot(x, df_sin['throughput'], marker='o', linewidth=2.5, markersize=8, color='crimson', label='Sin Sincronización')
    plt.plot(x, df_con['throughput'], marker='^', linewidth=2.5, markersize=8, color='forestgreen', label='Con Sincronización (Mutex)')

    plt.title('Rendimiento (Throughput): Operaciones / Segundo', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Operaciones por Segundo (ops/s)', fontsize=12)
    plt.xticks(x, thread_labels, fontsize=11)
    plt.legend(fontsize=11, loc='upper right')
    plt.grid(True, ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_lista_throughput.png", dpi=300)
    plt.close()

    print("Procesamiento Parte III completado:")
    print("- CSV generado: resultados_lista_completos.csv")
    print("- Gráficas generadas: grafica_lista_consistencia.png, grafica_lista_tiempos.png, grafica_lista_throughput.png")

if __name__ == "__main__":
    main()
