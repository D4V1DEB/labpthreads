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

    # 1. Gráfica de Tiempos (Cuadrícula 2x2 por tamaño de problema en escala lineal)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    target_ns = [1000000, 10000000, 100000000, 1000000000]
    titles = ['N = 1 Millón (10^6)', 'N = 10 Millones (10^7)', 
              'N = 100 Millones (10^8)', 'N = 1000 Millones (10^9)']

    all_x_labels = ['Sec'] + [f'{t}th' for t in threads_list]
    x_positions = list(range(len(all_x_labels)))

    for idx, n_val in enumerate(target_ns):
        ax = axes[idx // 2, idx % 2]
        t_sec = sec_times[n_val]
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        
        y_vals = [t_sec] + list(sub['tiempo'])
        use_ms = (t_sec < 0.05)
        scale = 1000.0 if use_ms else 1.0
        unit = 'ms' if use_ms else 's'
        y_scaled = [y * scale for y in y_vals]
        
        ax.plot(x_positions, y_scaled, marker='o', linewidth=2.5, markersize=8, color='#1f77b4')
        ax.plot(0, y_scaled[0], marker='s', markersize=10, color='crimson', label='Secuencial')
        ax.plot(x_positions[1:], y_scaled[1:], marker='o', markersize=8, color='#1f77b4', linestyle='None', label='Pthreads')
        
        for i, (xp, yp) in enumerate(zip(x_positions, y_scaled)):
            ax.annotate(f'{yp:.2f}{unit}', (xp, yp), textcoords="offset points", 
                        xytext=(0, 8 if (i % 2 == 0) else -14), ha='center', fontsize=9, fontweight='bold')
        
        ax.set_title(titles[idx], fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel('Configuración de Hilos', fontsize=11)
        ax.set_ylabel(f'Tiempo de Ejecución ({unit})', fontsize=11)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(all_x_labels, fontsize=10)
        ax.set_ylim(0, max(y_scaled) * 1.25)
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, ls="--", alpha=0.6)

    plt.suptitle('Tiempo de Ejecución: Secuencial vs Pthreads (Por Tamaño del Problema)', fontsize=15, fontweight='bold', y=0.995)
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
