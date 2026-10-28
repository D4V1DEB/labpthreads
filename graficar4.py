import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

def main():
    archivos = {
        'Busy-Waiting': 'tiempos_barrera_busywait.csv',
        'Semaforos': 'tiempos_barrera_semaforo.csv',
        'Variables_Condicion': 'tiempos_barrera_condvar.csv'
    }

    dfs = []
    for tipo, f in archivos.items():
        if os.path.exists(f):
            d = pd.read_csv(f)
            d['tipo_barrera'] = tipo
            dfs.append(d)

    if not dfs:
        return

    df = pd.concat(dfs, ignore_index=True)
    df.to_csv("resultados_barreras_completos.csv", index=False)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    threads_list = sorted(df['threads'].unique())
    x = range(len(threads_list))
    thread_to_x = {t: i for i, t in enumerate(threads_list)}
    thread_labels = [f'{t} threads' for t in threads_list]

    tipos = ['Busy-Waiting', 'Semaforos', 'Variables_Condicion']
    estilos = {
        'Busy-Waiting': {'color': 'crimson', 'marker': 'o'},
        'Semaforos': {'color': 'royalblue', 'marker': 's'},
        'Variables_Condicion': {'color': 'forestgreen', 'marker': '^'}
    }

    # 1
    plt.figure(figsize=(10, 6))
    for tipo in tipos:
        sub = df[df['tipo_barrera'] == tipo].sort_values('threads')
        if not sub.empty:
            xs = [thread_to_x[t] for t in sub['threads']]
            est = estilos[tipo]
            plt.plot(xs, sub['tiempo'], marker=est['marker'], linewidth=2.5, markersize=8, color=est['color'], label=tipo.replace('_', ' '))

    plt.yscale('log')
    plt.title('Comparativa de Barreras: Tiempo Total de Sincronización', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Tiempo Total (segundos, escala log)', fontsize=12)
    plt.xticks(x, thread_labels, fontsize=11)
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_barreras_tiempos.png", dpi=300)
    plt.close()

    # 2
    plt.figure(figsize=(10, 6))
    for tipo in tipos:
        sub = df[df['tipo_barrera'] == tipo].sort_values('threads')
        if not sub.empty:
            xs = [thread_to_x[t] for t in sub['threads']]
            est = estilos[tipo]
            plt.plot(xs, sub['costo_us'], marker=est['marker'], linewidth=2.5, markersize=8, color=est['color'], label=tipo.replace('_', ' '))

    plt.yscale('log')
    plt.title('Costo de Sincronización Promedio por Barrera (µs)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Costo Promedio por Barrera (µs, escala log)', fontsize=12)
    plt.xticks(x, thread_labels, fontsize=11)
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_barreras_costo.png", dpi=300)
    plt.close()

    print("Gráficas de barreras generadas exitosamente.")

if __name__ == "__main__":
    main()
