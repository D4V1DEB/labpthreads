import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

def main():
    if not os.path.exists("tiempos_matvec_secuencial.csv") or not os.path.exists("tiempos_matvec_pthreads.csv"):
        print("Error: No se encontraron los archivos CSV de matriz-vector.")
        return

    df_sec = pd.read_csv("tiempos_matvec_secuencial.csv")
    df_pth = pd.read_csv("tiempos_matvec_pthreads.csv")

    # Mapear tiempo secuencial por tamaño N
    sec_times = dict(zip(df_sec['n'], df_sec['tiempo']))

    # Calcular Speedup respecto al secuencial y Eficiencia
    df_pth['t_sec'] = df_pth['n'].map(sec_times)
    df_pth['speedup'] = df_pth['t_sec'] / df_pth['tiempo']
    df_pth['eficiencia'] = (df_pth['speedup'] / df_pth['threads']) * 100.0

    df_pth.to_csv("resultados_matvec_completos.csv", index=False)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    threads_list = sorted(df_pth['threads'].unique())
    unique_n = sorted(df_pth['n'].unique())

    # Mapeo de índices para espaciar uniformemente los hilos (2, 4, 8, 16, 32)
    x_indices = list(range(len(threads_list)))
    thread_to_x = {t: i for i, t in enumerate(threads_list)}
    thread_labels = [f'{t} threads' for t in threads_list]

    # 1. Gráfica de Tiempos por tamaño en escala lineal
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    all_x_labels = ['Sec'] + [f'{t}th' for t in threads_list]
    x_positions = list(range(len(all_x_labels)))
    axes_flat = axes.flatten()

    for idx, n_val in enumerate(unique_n):
        ax = axes_flat[idx]
        t_sec = sec_times[n_val]
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        
        y_vals = [t_sec] + list(sub['tiempo'])
        use_ms = (t_sec < 0.25)
        scale = 1000.0 if use_ms else 1.0
        unit = 'ms' if use_ms else 's'
        y_scaled = [y * scale for y in y_vals]
        
        ax.plot(x_positions, y_scaled, marker='o', linewidth=2.5, markersize=7, color='#1f77b4')
        ax.plot(0, y_scaled[0], marker='s', markersize=9, color='crimson', label='Secuencial')
        ax.plot(x_positions[1:], y_scaled[1:], marker='o', markersize=7, color='#1f77b4', linestyle='None', label='Pthreads')
        
        for i, (xp, yp) in enumerate(zip(x_positions, y_scaled)):
            ax.annotate(f'{yp:.1f}{unit}' if use_ms else f'{yp:.2f}{unit}', (xp, yp), 
                        textcoords="offset points", xytext=(0, 7 if (i % 2 == 0) else -13),
                        ha='center', fontsize=9, fontweight='bold')
        
        ax.set_title(f'Matriz {n_val}x{n_val}', fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('Hilos', fontsize=10)
        ax.set_ylabel(f'Tiempo ({unit})', fontsize=10)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(all_x_labels, fontsize=9)
        ax.set_ylim(0, max(y_scaled) * 1.25)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, ls="--", alpha=0.6)

    fig.delaxes(axes_flat[5])
    plt.suptitle('Multiplicación Matriz-Vector: Tiempo Secuencial vs Pthreads por Tamaño', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig("grafica_matvec_tiempos.png", dpi=300)
    plt.close()

    # 2
    plt.figure(figsize=(10, 6))
    for n_val in unique_n:
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        xs = [thread_to_x[t] for t in sub['threads']]
        plt.plot(xs, sub['speedup'], marker='o', linewidth=2.5, markersize=8, label=f'Matriz {n_val}x{n_val}')

    plt.title('Multiplicación Matriz-Vector: Speedup vs Número de Threads', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Speedup (S = T_sec / T_par)', fontsize=12)
    plt.xticks(x_indices, thread_labels, fontsize=11)
    # Escala vertical ajustada a los datos reales para apreciar claramente la curva
    max_sp = df_pth['speedup'].max()
    plt.ylim(0, max_sp * 1.15)
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, ls="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("grafica_matvec_speedup.png", dpi=300)
    plt.close()

    # 3
    plt.figure(figsize=(10, 6))
    for n_val in unique_n:
        sub = df_pth[df_pth['n'] == n_val].sort_values('threads')
        xs = [thread_to_x[t] for t in sub['threads']]
        plt.plot(xs, sub['eficiencia'], marker='^', linewidth=2.5, markersize=8, label=f'Matriz {n_val}x{n_val}')

    plt.title('Multiplicación Matriz-Vector: Eficiencia (%) vs Número de Threads', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Threads', fontsize=12)
    plt.ylabel('Eficiencia (%)', fontsize=12)
    plt.xticks(x_indices, thread_labels, fontsize=11)
    # Escala vertical ajustada a la eficiencia real obtenida
    max_ef = df_pth['eficiencia'].max()
    plt.ylim(0, min(100.0, max_ef * 1.15))
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, ls="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("grafica_matvec_eficiencia.png", dpi=300)
    plt.close()

    print("Procesamiento Parte II completado:")
    print("- CSV generado: resultados_matvec_completos.csv")
    print("- Gráficas generadas: grafica_matvec_tiempos.png, grafica_matvec_speedup.png, grafica_matvec_eficiencia.png")

if __name__ == "__main__":
    main()
