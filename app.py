import matplotlib
matplotlib.use('Agg')

import sys
import os
sys.path.append(os.path.abspath('.'))

import streamlit as st
import fastf1

from funcoes_telemetria import (
    comparar_pilotos, ranking_sessao, mapa_velocidade,
    comparar_mapas_velocidade, calcular_energia_frenagem,
    mapa_energia_frenagem
)

os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')

st.title("🏎️ Telemetria F1")
st.markdown("Análise de dados reais de telemetria da Fórmula 1")

st.sidebar.header("Configurações")
ano = st.sidebar.selectbox("Ano", [2026, 2025, 2024])
gp = st.sidebar.text_input("GP", value="Austria")
sessao = st.sidebar.selectbox("Sessão", ["Q", "R", "FP1", "FP2", "FP3"])
piloto1 = st.sidebar.text_input("Piloto 1", value="RUS")
piloto2 = st.sidebar.text_input("Piloto 2", value="VER")

aba1, aba2, aba3, aba4 = st.tabs(["Ranking", "Telemetria", "Mapa de Velocidade", "Energia de Frenagem"])

if st.sidebar.button("Analisar"):
    session = fastf1.get_session(ano, gp, sessao)
    session.load()

    volta1 = session.laps.pick_driver(piloto1).pick_fastest()
    volta2 = session.laps.pick_driver(piloto2).pick_fastest()
    tel1 = volta1.get_telemetry().add_distance()
    tel2 = volta2.get_telemetry().add_distance()

    with aba1:
        st.subheader(f"Ranking — {gp} {ano} {sessao}")
        fig_ranking = ranking_sessao(ano, gp, sessao)
        st.pyplot(fig_ranking)

    with aba2:
        st.subheader(f"Telemetria — {piloto1} vs {piloto2}")
        _, _, fig_tel, fig_delta = comparar_pilotos(ano, gp, sessao, piloto1, piloto2)
        st.pyplot(fig_tel)
        st.pyplot(fig_delta)

    with aba3:
        st.subheader(f"Mapas de velocidade — {piloto1} vs {piloto2}")
        fig_mapas = comparar_mapas_velocidade(tel1, tel2, piloto1, piloto2, f"{gp} {ano}")
        st.pyplot(fig_mapas)

    with aba4:
        st.subheader(f"Energia de frenagem — {piloto1} vs {piloto2}")
        energia1 = calcular_energia_frenagem(tel1)
        energia2 = calcular_energia_frenagem(tel2)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{piloto1}**")
            st.dataframe(energia1[['distancia_inicio', 'v_inicial_kmh', 'v_final_kmh', 'energia_kwh']].round(2))
            fig1 = mapa_energia_frenagem(tel1, energia1, f"{piloto1} — Energia de frenagem")
            st.pyplot(fig1)
        with col2:
            st.markdown(f"**{piloto2}**")
            st.dataframe(energia2[['distancia_inicio', 'v_inicial_kmh', 'v_final_kmh', 'energia_kwh']].round(2))
            fig2 = mapa_energia_frenagem(tel2, energia2, f"{piloto2} — Energia de frenagem")
            st.pyplot(fig2)