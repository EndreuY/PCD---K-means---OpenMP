# Projeto PCD: K-means 1D Paralelo (OpenMP)

Implementação paralela do algoritmo K-means 1D com OpenMP para o projeto da disciplina de Programação Concorrente e Distribuída (PCD) - UNIFESP.

Este repositório contém o código-fonte da versão serial, da versão paralela, e os scripts para executar os testes e gerar os gráficos de análise de desempenho.

## Como Executar

O projeto foi desenvolvido e testado no ambiente Linux (Ubuntu via WSL2).

**1. Clone o Repositório:**
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
2. Instale as Dependências:

Bash

# Instala o compilador GCC e as ferramentas do Python
sudo apt update && sudo apt install -y build-essential python3-full python3-venv
3. Configure o Ambiente Python:

Bash

# Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as bibliotecas necessárias
pip install numpy pandas scikit-learn matplotlib seaborn
4. Execute os Scripts: Os scripts devem ser executados na seguinte ordem:

Bash

# 1. Gerar os dados de teste (cria dados.csv e centroides_iniciais.csv)
python3 gera_dados.py

# 2. Compilar e rodar todos os testes (cria omp_results.csv)
chmod +x run_tests.sh
./run_tests.sh

# 3. Gerar os gráficos de análise (cria os arquivos .png)
python3 analysis.py
Após esses passos, os gráficos comparativos de desempenho estarão salvos como arquivos .png na pasta do projeto.
