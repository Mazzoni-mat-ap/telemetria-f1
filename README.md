# 🏎️ Telemetria F1

Projeto de análise de telemetria de Fórmula 1 usando dados reais, 
desenvolvido durante a graduação em Matemática Aplicada como porta 
de entrada para a área de Performance Analysis no automobilismo.

## O que o projeto faz

- Compara telemetria entre pilotos (velocidade, acelerador, marcha)
- Calcula delta de tempo acumulado ao longo da volta
- Localiza pontos específicos no traçado da pista
- Gera mapas de velocidade coloridos por trecho do circuito
- Analisa instints e desgaste de pneu durante a corrida
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

Abra o notebook em `notebooks/` no VS Code ou Jupyter.

## Status

🚧 Em desenvolvimento — projeto contínuo ao longo da graduação.