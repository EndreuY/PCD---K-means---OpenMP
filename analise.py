import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# --- Configurações de Estilo para os Gráficos ---
sns.set_theme(style="whitegrid", palette="viridis", font_scale=1.1)
plt.rcParams['figure.figsize'] = (12, 8) # Tamanho da figura
plt.rcParams['savefig.dpi'] = 300       # Alta resolução para o relatório

# --- 1. Carregar Dados do CSV ---
RESULTS_FILE = 'omp_results.csv'
try:
    df = pd.read_csv(RESULTS_FILE)
    df['Tempo_ms'] = pd.to_numeric(df['Tempo_ms'], errors='coerce')
    df.dropna(subset=['Tempo_ms'], inplace=True)
    print(f"Arquivo '{RESULTS_FILE}' carregado com sucesso.")
except FileNotFoundError:
    print(f"ERRO: O arquivo '{RESULTS_FILE}' não foi encontrado.")
    print("Por favor, execute o script 'run_tests.sh' primeiro.")
    sys.exit()

# --- 2. Isolar o Baseline Serial (Naive) ---
try:
    serial_run = df[df['Schedule'] == 'Serial'].iloc[0]
    tempo_serial_baseline = serial_run['Tempo_ms']
    print(f"Baseline (Execução Naive Serial) definido em: {tempo_serial_baseline:.1f} ms")
except (IndexError, KeyError):
    print("Aviso: Execução 'Serial' não encontrada no CSV. Verifique o run_tests.sh. Abortando.")
    sys.exit()

# --- 3. Preparar Dados para Plotagem ---
# Calcula o speedup para todas as execuções OpenMP em relação ao baseline Naive
df_omp = df[df['Schedule'] != 'Serial'].copy()
df_omp['Speedup'] = tempo_serial_baseline / df_omp['Tempo_ms']

# Encontra a melhor execução OMP com 1 thread para destacar o overhead
try:
    omp_1_thread_run = df_omp[df_omp['Threads'] == 1].sort_values('Tempo_ms').iloc[0]
except IndexError:
    omp_1_thread_run = None # Caso não haja teste com 1 thread OMP

# --- 4. Gerar Gráficos ---

# --- GRÁFICO 1: Tempo de Execução vs. Número de Threads ---
print("Gerando gráfico: Tempo de Execução Comparativo...")
plt.figure()
# Plota as linhas apenas para as execuções com chunk 'default' para clareza
df_plot_default = df_omp[df_omp['Chunk'] == 'default']
ax = sns.lineplot(data=df_plot_default, x='Threads', y='Tempo_ms', hue='Schedule', marker='o', style='Schedule', markersize=10, lw=2.5)

# Plota pontos distintos para as execuções com 1 thread
plt.scatter(1, tempo_serial_baseline, s=250, c='red', marker='*', zorder=5, label=f'Serial Naive ({tempo_serial_baseline:.1f} ms)')
if omp_1_thread_run is not None:
    plt.scatter(1, omp_1_thread_run['Tempo_ms'], s=150, facecolors='none', edgecolors='blue', zorder=5, lw=2, label=f'OpenMP 1-Thread ({omp_1_thread_run["Tempo_ms"]:.1f} ms)')

plt.title('Comparativo de Tempo de Execução: Naive vs. OpenMP', fontsize=16, fontweight='bold')
plt.xlabel('Número de Threads', fontsize=12)
plt.ylabel('Tempo de Execução (ms)', fontsize=12)
plt.xticks(sorted(df_omp['Threads'].unique()))
plt.legend(title='Legenda')
plt.grid(True, which='both', linestyle='--')
plt.savefig('grafico_tempo_execucao_comparativo.png')
plt.close()

# --- GRÁFICO 2: Speedup vs. Número de Threads ---
print("Gerando gráfico: Speedup...")
plt.figure()
# Usa os dados de chunk 'default' para o gráfico de speedup principal
sns.lineplot(data=df_plot_default, x='Threads', y='Speedup', hue='Schedule', marker='o', style='Schedule', markersize=8, lw=2.5)
max_threads = df_omp['Threads'].max()
plt.axhline(y=1.0, color='red', linestyle='--', label='Break-Even (vs. Naive Serial)')
plt.title('Speedup do OpenMP em Relação à Versão Naive Serial', fontsize=16, fontweight='bold')
plt.xlabel('Número de Threads', fontsize=12)
plt.ylabel('Speedup (Tempo Naive / Tempo OpenMP)', fontsize=12)
plt.xticks(sorted(df_omp['Threads'].unique()))
plt.legend(title='Legenda')
plt.savefig('grafico_speedup_vs_naive.png')
plt.close()

# --- GRÁFICO 3: Impacto do Chunk Size ---
print("Gerando gráfico: Impacto do Chunk Size...")
max_threads_val = df_omp['Threads'].max()
df_chunk_analysis = df_omp[(df_omp['Threads'] == max_threads_val) & (df_omp['Chunk'] != 'default')].copy()
df_chunk_analysis['Chunk'] = df_chunk_analysis['Chunk'].astype(int)

if not df_chunk_analysis.empty:
    plt.figure()
    ax_chunk = sns.barplot(data=df_chunk_analysis, x='Chunk', y='Tempo_ms', hue='Schedule', dodge=True)
    # Adiciona a linha de base serial para comparação
    ax_chunk.axhline(y=tempo_serial_baseline, color='red', linestyle='--', linewidth=2.5, label=f'Execução Serial ({tempo_serial_baseline:.1f} ms)')
    plt.title(f'Impacto do Chunk Size (com {max_threads_val} Threads) vs. Serial', fontsize=16, fontweight='bold')
    plt.xlabel('Chunk Size', fontsize=12)
    plt.ylabel('Tempo de Execução (ms)', fontsize=12)
    plt.legend(title='Legenda')
    plt.savefig('grafico_chunk_size_comparativo.png')
    plt.close()

print("\nGráficos gerados com sucesso!")
print("Arquivos salvos como .png na pasta do projeto.")