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

    #grafica 1
    plt.figure(figsize=(10, 6))
    plt.plot(df_sec['n'], df_sec['tiempo'], marker='o', linewidth=2.5, color='black', label='Secuencial')

    for t in threads_list:
        sub = df_pth[df_pth['threads'] == t]
        plt.plot(sub['n'], sub['tiempo'], marker='s', label=f'{t} threads')

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

    # grafica 2
    plt.figure(figsize=(10, 6))
    min_t, max_t = min(threads_list), max(threads_list)
    plt.plot([min_t, max_t], [min_t, max_t], 'k--', linewidth=2, label='Speedup Ideal (Lineal)')

    for n_val in unique_n:
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        plt.plot(sub['threads'], sub['speedup'], marker='o', linewidth=2, label=f'N = {n_val:.0e}')

    plt.title('Speedup vs Número de Threads (Referencia Secuencial)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Speedup (S = T_sec / T_par)', fontsize=12)
    plt.xticks(threads_list)
    plt.legend(fontsize=10)
    plt.grid(True, ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_speedup.png", dpi=300)
    plt.close()

    # grafica 3
    plt.figure(figsize=(10, 6))
    plt.axhline(y=100, color='k', linestyle='--', linewidth=2, label='Eficiencia Ideal (100%)')

    for n_val in unique_n:
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        plt.plot(sub['threads'], sub['eficiencia'], marker='^', linewidth=2, label=f'N = {n_val:.0e}')

    plt.title('Eficiencia (%) vs Número de Threads', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Eficiencia (%)', fontsize=12)
    plt.xticks(threads_list)
    plt.ylim(0, 115)
    plt.legend(fontsize=10)
    plt.grid(True, ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("grafica_eficiencia.png", dpi=300)
    plt.close()

    print("Procesamiento completado:")
    print("- CSV generado: resultados_completos.csv")
    print("- Gráficas generadas: grafica_tiempos.png, grafica_speedup.png, grafica_eficiencia.png")

if __name__ == "__main__":
    main()
