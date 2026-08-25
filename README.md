# 🏎️ Telemetria F1

Projeto de análise de telemetria de Fórmula 1 usando dados reais, 
desenvolvido durante a graduação em Matemática Aplicada como porta 
de entrada para a área de Performance Analysis no automobilismo.

## O que o projeto faz

- Compara telemetria entre pilotos (velocidade, acelerador, marcha)
- Calcula delta de tempo acumulado ao longo da volta
- Localiza pontos específicos no traçado da pista
- Gera mapas de velocidade coloridos por trecho do circuito
- Analisa stints e desgaste de pneu durante a corrida
- Ranking completo do grid, comparando os tempos de volta
- Calcula G longitudinal de qualquer piloto em qualquer volta
- Calcula G lateral (com limitações documentadas — ver Módulo 2)
- Analisa o G-G diagram
- Calcula e compara energia de frenagem
- Compara desempenho em setores da pista
- Analisa e compara o uso do DRS pelos pilotos
- Analisa RPM do motor
- Analisa e compara o brake

## Projeto de criação da interface para o programa iniciada
- Arquivo app.py

## Análises feitas
- Análise do GP da Austria 2026, peimeiro GP pós criação do programa
- Análise do GP da Bélgica 2026

## Tecnologias

- Python
- [FastF1](https://github.com/theOehrly/Fast-F1) — dados oficiais de telemetria da F1
- pandas / numpy
- matplotlib

## Como rodar

\`\`\`bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

Abra os notebooks em `notebooks/` no VS Code ou Jupyter.

## Status

🚧 Em desenvolvimento — projeto contínuo ao longo da graduação.