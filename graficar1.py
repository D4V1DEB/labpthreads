import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

def main():
    if not os.path.exists("tiempos_secuencial.csv") or not os.path.exists("tiempos_pthreads.csv"):
        print("Error: No se encontraron los archivos CSV.")
        return

    df_sec = pd.read_csv("tiempos_secuencial.csv")
    df_pth = pd.read_csv("tiempos_pthreads.csv")

    # mapear tiempo secuencial por tamaño N
    sec_times = dict(zip(df_sec['n'], df_sec['tiempo']))

    # calcular Speedup respecto al secuencial y Eficiencia
    df_pth['t_sec'] = df_pth['n'].map(sec_times)
    df_pth['speedup'] = df_pth['t_sec'] / df_pth['tiempo']
    df_pth['eficiencia'] = (df_pth['speedup'] / df_pth['threads']) * 100.0

    df_pth.to_csv("resultados_completos.csv", index=False)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    threads_list = sorted(df_pth['threads'].unique())
    unique_n = sorted(df_pth['n'].unique())

    # Mapeo de índices para espaciar uniformemente los hilos (2, 4, 8, 16, 32)
    x_indices = list(range(len(threads_list)))
    thread_to_x = {t: i for i, t in enumerate(threads_list)}
    thread_labels = [f'{t} threads' for t in threads_list]

    # 1
    plt.figure(figsize=(10, 6))
    plt.plot(df_sec['n'], df_sec['tiempo'], marker='o', linewidth=2.5, markersize=7, color='black', label='Secuencial')

    for t in threads_list:
        sub = df_pth[df_pth['threads'] == t]
        plt.plot(sub['n'], sub['tiempo'], marker='s', linewidth=2, markersize=6, label=f'{t} threads')

    plt.xscale('log')
    plt.yscale('log')
    plt.title('Tiempo de Ejecución vs Tamaño del Problema (N)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Tamaño del Problema N (Iteraciones)', fontsize=12)
    plt.ylabel('Tiempo de Ejecución (segundos, escala log)', fontsize=12)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_tiempos.png", dpi=300)
    plt.close()

    # 2
    plt.figure(figsize=(10, 6))
    for n_val in unique_n:
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        xs = [thread_to_x[t] for t in sub['threads']]
        plt.plot(xs, sub['speedup'], marker='o', linewidth=2.5, markersize=8, label=f'N = {n_val:.0e}')

    plt.title('Cálculo de PI: Speedup vs Número de Threads', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Speedup (S = T_sec / T_par)', fontsize=12)
    plt.xticks(x_indices, thread_labels, fontsize=11)
    max_sp = df_pth['speedup'].max()
    plt.ylim(0, max_sp * 1.15)
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, ls="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("grafica_speedup.png", dpi=300)
    plt.close()

    # 3
    plt.figure(figsize=(10, 6))
    for n_val in unique_n:
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        xs = [thread_to_x[t] for t in sub['threads']]
        plt.plot(xs, sub['eficiencia'], marker='^', linewidth=2.5, markersize=8, label=f'N = {n_val:.0e}')

    plt.title('Cálculo de PI: Eficiencia (%) vs Número de Threads', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Eficiencia (%)', fontsize=12)
    plt.xticks(x_indices, thread_labels, fontsize=11)
    max_ef = df_pth['eficiencia'].max()
    plt.ylim(0, min(100.0, max_ef * 1.15))
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, ls="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("grafica_eficiencia.png", dpi=300)
    plt.close()

    print("Procesamiento Parte I completado:")
    print("- CSV generado: resultados_completos.csv")
    print("- Gráficas generadas: grafica_tiempos.png, grafica_speedup.png, grafica_eficiencia.png")

if __name__ == "__main__":
    main()
