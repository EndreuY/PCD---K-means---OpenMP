#!/bin/bash

# Força o formato numérico para o padrão C (com ponto decimal)
export LC_NUMERIC="en_US.UTF-8"

# ==============================================================================
# Script de Teste Comparativo: Serial (Naive) vs. OpenMP
# ==============================================================================

# --- PASSO 1: COMPILAÇÃO DE AMBAS AS VERSÕES ---
echo "Compilando a versão Serial (kmeans_1d_naive.c)..."
gcc -O2 -std=c99 kmeans_1d_naive.c -o kmeans_1d_naive -lm
if [ $? -ne 0 ]; then echo "ERRO: Falha na compilação do código serial!"; exit 1; fi

echo "Compilando a versão OpenMP (kmeans_1d_omp.c)..."
gcc -O2 -fopenmp -std=c99 kmeans_1d_omp.c -o kmeans_1d_omp -lm
if [ $? -ne 0 ]; then echo "ERRO: Falha na compilação do código OpenMP!"; exit 1; fi
echo "Compilações bem-sucedidas."
echo "----------------------------------------------------"


# --- PASSO 2: CONFIGURAÇÃO DOS TESTES ---
DATA_FILE="dados.csv"
CENTROIDS_FILE="centroides_iniciais.csv"
RESULTS_FILE="omp_results.csv"
MAX_ITER=100
EPS="1e-6"


# --- PASSO 3: EXECUÇÃO DA VERSÃO SERIAL (BASELINE) ---
echo "Executando a versão Serial para obter o baseline..."
# Roda o executável serial e captura a saída
output_serial=$(./kmeans_1d_naive $DATA_FILE $CENTROIDS_FILE $MAX_ITER $EPS)
metrics_serial=$(echo "$output_serial" | grep "Tempo:")

iters_serial=$(echo "$metrics_serial" | awk '{print $2}')
sse_serial=$(echo "$metrics_serial" | awk '{print $6}')
time_ms_serial=$(echo "$metrics_serial" | awk '{print $9}')

# Cria o cabeçalho e adiciona a linha do resultado serial
echo "Threads,Schedule,Chunk,Tempo_ms,SSE_Final,Iteracoes" > $RESULTS_FILE
echo "1,Serial,N/A,$time_ms_serial,$sse_serial,$iters_serial" >> $RESULTS_FILE
echo "Resultado Serial: ${time_ms_serial}ms"
echo "----------------------------------------------------"


# --- PASSO 4: EXECUÇÃO DOS TESTES OPENMP ---
for threads in 1 2 4 8 16; do
    export OMP_NUM_THREADS=$threads
    echo "EXECUTANDO TESTES OPENMP COM $threads THREAD(S)..."

    for schedule in "static" "dynamic"; do
        # O programa C trata chunk <= 0 como "padrão".
        for chunk in "default" 100 1000 10000; do
            chunk_val=$chunk
            if [ "$chunk" == "default" ]; then
                chunk_val="-1"
            fi
            
            echo "  -> Testando: Schedule=$schedule, Chunk=$chunk"
            output_omp=$(./kmeans_1d_omp $DATA_FILE $CENTROIDS_FILE $MAX_ITER $EPS \
                        assign.csv centroids.csv $schedule $chunk_val)
            
            metrics_omp=$(echo "$output_omp" | tail -n 1)
            iters_omp=$(echo "$metrics_omp" | awk '{print $2}')
            sse_omp=$(echo "$metrics_omp" | awk '{print $6}')
            time_ms_omp=$(echo "$metrics_omp" | awk '{print $9}')
            
            echo "$threads,$schedule,$chunk,$time_ms_omp,$sse_omp,$iters_omp" >> $RESULTS_FILE
        done
    done
    echo "----------------------------------------------------"
done

echo "Testes finalizados! Resultados em $RESULTS_FILE"