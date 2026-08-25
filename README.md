# 🏎️ Telemetria F1

Projeto de análise de telemetria de Fórmula 1 usando dados reais,
desenvolvido durante a graduação em Matemática Aplicada como porta
de entrada para a área de Performance Analysis no automobilismo.

## O que o projeto faz

### Módulo 1 — Comparação de Pilotos
- Comparação de telemetria entre pilotos (velocidade, acelerador, marcha)
- Delta de tempo acumulado ao longo da volta
- Localização de pontos específicos no traçado da pista
- Mapas de velocidade coloridos por trecho do circuito
- Análise de stints e desgaste de pneu durante a corrida
- Ranking completo do grid por tempo de volta, colorido por equipe
- Comparação de tempos por setor (S1, S2, S3)

### Módulo 2 — Dinâmica do Carro
- G longitudinal (aceleração/frenagem) com filtro de ruído de sensor
- G lateral estimado pela geometria da trajetória (limitação documentada)
- Diagrama G-G (envelope de aderência)
- Cálculo e comparação de energia de frenagem por zona
- Mapa da pista colorido por G longitudinal

### Módulo 3 — Pilotagem e Performance
- Análise e comparação do uso de DRS
- Análise de RPM do motor colorida por marcha
- Análise e comparação de pontos de frenagem (canal Brake)
- Perfil de elevação da pista (canal Z)
- Painel completo de telemetria com todos os canais numa visualização só

### Interface Web (Streamlit)
- App interativo com todas as análises acessíveis via navegador
- Seleção de ano, GP, sessão e pilotos pela sidebar
- 5 seções: Ranking, Comparação de Pilotos, Dinâmica do Carro,
  Estratégia de Corrida e Pilotagem e Performance

### Estudos de caso
- GP da Áustria 2026 (primeiro GP pós-criação do app)
- GP da Bélgica 2026

## Tecnologias

- Python
- [FastF1](https://github.com/theOehrly/Fast-F1) — dados oficiais de telemetria da F1
- pandas / numpy / scipy
- matplotlib
- Streamlit

## Como rodar

### Notebooks
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Abra os notebooks em `notebooks/` no VS Code ou Jupyter.

### Interface Streamlit
```bash
.venv\Scripts\python.exe -m streamlit run app.py
```

## Status

🚧 Em desenvolvimento — projeto contínuo ao longo da graduação.