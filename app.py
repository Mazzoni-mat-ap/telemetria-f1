import matplotlib
matplotlib.use('Agg')

import sys
import os
sys.path.append(os.path.abspath('.'))

import streamlit as st
import fastf1

from funcoes_telemetria import (
    comparar_pilotos, ranking_sessao, mapa_velocidade,
    comparar_mapas_velocidade, analisar_stints, obter_dados_corrida,
    comparar_stints, calcular_g_longitudinal, calcular_g_lateral,
    diagrama_gg, calcular_energia_frenagem, mapa_energia_frenagem,
    comparar_energia_frenagem, comparar_setores, mapa_g_longitudinal,
    comparar_mapas_g_longitudinal, analisar_drs, comparar_drs,
    analisar_rpm, analisar_brake, comparar_brake, perfil_elevacao
)

os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')

st.set_page_config(page_title="Telemetria F1", page_icon="🏎️", layout="wide")
st.title("🏎️ Telemetria F1")
st.markdown("Análise de dados reais de telemetria da Fórmula 1")

# --- Sidebar ---
st.sidebar.header("⚙️ Configurações")
ano = st.sidebar.selectbox("Ano", [2026, 2025, 2024])
gp = st.sidebar.text_input("GP", value="Austria")
sessao = st.sidebar.selectbox("Sessão", ["Q", "R", "FP1", "FP2", "FP3"])
piloto1 = st.sidebar.text_input("Piloto 1", value="RUS")
piloto2 = st.sidebar.text_input("Piloto 2", value="VER")

st.sidebar.divider()

secao = st.sidebar.radio("📂 Seção", [
    "🏆 Ranking",
    "🔍 Comparação de Pilotos",
    "⚙️ Dinâmica do Carro",
    "🔄 Estratégia de Corrida",
    "🧠 Pilotagem e Performance",
])

analisar = st.sidebar.button("▶️ Analisar", use_container_width=True)

if analisar:
    with st.spinner("Carregando dados..."):
        session = fastf1.get_session(ano, gp, sessao)
        session.load()

        volta1 = session.laps.pick_driver(piloto1).pick_fastest()
        volta2 = session.laps.pick_driver(piloto2).pick_fastest()
        tel1 = volta1.get_telemetry().add_distance()
        tel2 = volta2.get_telemetry().add_distance()

    # --- Ranking ---
    if secao == "🏆 Ranking":
        st.subheader(f"Ranking — {gp} {ano} {sessao}")
        fig = ranking_sessao(ano, gp, sessao)
        st.pyplot(fig)

    # --- Comparação de Pilotos ---
    elif secao == "🔍 Comparação de Pilotos":
        st.subheader(f"{piloto1} vs {piloto2} — {gp} {ano} {sessao}")
        aba1, aba2, aba3 = st.tabs(["Telemetria", "Setores", "Mapas de Velocidade"])

        with aba1:
            _, _, fig_tel, fig_delta = comparar_pilotos(ano, gp, sessao, piloto1, piloto2)
            st.pyplot(fig_tel)
            st.pyplot(fig_delta)

        with aba2:
            fig_set = comparar_setores(ano, gp, sessao, piloto1, piloto2)
            st.pyplot(fig_set)

        with aba3:
            fig_mapas = comparar_mapas_velocidade(tel1, tel2, piloto1, piloto2, f"{gp} {ano}")
            st.pyplot(fig_mapas)

    # --- Dinâmica do Carro ---
    elif secao == "⚙️ Dinâmica do Carro":
        st.subheader(f"Dinâmica — {piloto1} vs {piloto2} — {gp} {ano} {sessao}")
        aba1, aba2, aba3, aba4 = st.tabs([
            "G Longitudinal", "Diagrama G-G", "Energia de Frenagem", "Mapa G Longitudinal"
        ])

        with aba1:
            import matplotlib.pyplot as plt
            import numpy as np
            for tel, nome, cor in [(tel1, piloto1, '#0090FF'), (tel2, piloto2, '#FF8000')]:
                dist, _, g_suave = calcular_g_longitudinal(tel)
                fig, ax = plt.subplots(figsize=(14, 4))
                ax.plot(dist, g_suave, color=cor)
                ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
                ax.set_xlabel('Distância (m)')
                ax.set_ylabel('G longitudinal')
                ax.set_title(f'{nome} — G longitudinal')
                ax.grid(alpha=0.2)
                st.pyplot(fig)

        with aba2:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(diagrama_gg(tel1, titulo=f'{piloto1} — Diagrama G-G'))
            with col2:
                st.pyplot(diagrama_gg(tel2, titulo=f'{piloto2} — Diagrama G-G'))

        with aba3:
            energia1 = calcular_energia_frenagem(tel1)
            energia2 = calcular_energia_frenagem(tel2)
            st.pyplot(comparar_energia_frenagem(energia1, energia2, piloto1, piloto2,
                                                 titulo=f'Energia de frenagem — {gp} {ano}'))
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{piloto1}**")
                st.dataframe(energia1[['distancia_inicio', 'v_inicial_kmh', 'v_final_kmh', 'energia_kwh']].round(2))
                st.pyplot(mapa_energia_frenagem(tel1, energia1, piloto1))
            with col2:
                st.markdown(f"**{piloto2}**")
                st.dataframe(energia2[['distancia_inicio', 'v_inicial_kmh', 'v_final_kmh', 'energia_kwh']].round(2))
                st.pyplot(mapa_energia_frenagem(tel2, energia2, piloto2))

        with aba4:
            st.pyplot(comparar_mapas_g_longitudinal(tel1, tel2, piloto1, piloto2,
                                                     titulo_geral=f'{gp} {ano} — G longitudinal'))

    # --- Estratégia de Corrida ---
    elif secao == "🔄 Estratégia de Corrida":
        if sessao != "R":
            st.warning("⚠️ Estratégia de corrida só disponível para a sessão de Corrida (R).")
        else:
            st.subheader(f"Estratégia — {gp} {ano}")
            aba1, aba2 = st.tabs(["Stints individuais", "Comparação de stints"])

            with aba1:
                col1, col2 = st.columns(2)
                with col1:
                    _, fig_s1 = analisar_stints(ano, gp, piloto1)
                    st.pyplot(fig_s1)
                with col2:
                    _, fig_s2 = analisar_stints(ano, gp, piloto2)
                    st.pyplot(fig_s2)

            with aba2:
                voltas1 = obter_dados_corrida(ano, gp, piloto1)
                voltas2 = obter_dados_corrida(ano, gp, piloto2)
                st.pyplot(comparar_stints(voltas1, voltas2, piloto1, piloto2,
                                          titulo=f'{piloto1} vs {piloto2} — Stints {gp} {ano}'))

    # --- Pilotagem e Performance ---
    elif secao == "🧠 Pilotagem e Performance":
        st.subheader(f"Pilotagem — {piloto1} vs {piloto2} — {gp} {ano} {sessao}")
        aba1, aba2, aba3, aba4 = st.tabs(["DRS", "RPM", "Frenagem", "Elevação"])

        with aba1:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(analisar_drs(tel1, titulo=f'{piloto1} — DRS'))
            with col2:
                st.pyplot(analisar_drs(tel2, titulo=f'{piloto2} — DRS'))
            st.pyplot(comparar_drs(tel1, tel2, piloto1, piloto2,
                                   titulo=f'DRS: {piloto1} vs {piloto2}'))

        with aba2:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(analisar_rpm(tel1, titulo=f'{piloto1} — RPM'))
            with col2:
                st.pyplot(analisar_rpm(tel2, titulo=f'{piloto2} — RPM'))

        with aba3:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(analisar_brake(tel1, titulo=f'{piloto1} — Frenagem'))
            with col2:
                st.pyplot(analisar_brake(tel2, titulo=f'{piloto2} — Frenagem'))
            st.pyplot(comparar_brake(tel1, tel2, piloto1, piloto2,
                                     titulo=f'Frenagem: {piloto1} vs {piloto2}'))

        with aba4:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(perfil_elevacao(tel1, titulo=f'{piloto1} — Elevação'))
            with col2:
                st.pyplot(perfil_elevacao(tel2, titulo=f'{piloto2} — Elevação'))