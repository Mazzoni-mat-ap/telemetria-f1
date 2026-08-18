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
    comparar_mapas_g_longitudinal
)

os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')

# --- Configuração da página ---
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
])

analisar = st.sidebar.button("▶️ Analisar", use_container_width=True)

# --- Carrega dados ---
if analisar:
    with st.spinner("Carregando dados..."):
        session = fastf1.get_session(ano, gp, sessao)
        session.load()

        volta1 = session.laps.pick_driver(piloto1).pick_fastest()
        volta2 = session.laps.pick_driver(piloto2).pick_fastest()
        tel1 = volta1.get_telemetry().add_distance()
        tel2 = volta2.get_telemetry().add_distance()

        # --- Seção: Ranking ---
        if secao == "🏆 Ranking":
            st.subheader(f"Ranking — {gp} {ano} {sessao}")
            fig = ranking_sessao(ano, gp, sessao)
            st.pyplot(fig)

        # --- Seção: Comparação de Pilotos ---
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

        # --- Seção: Dinâmica do Carro ---
        elif secao == "⚙️ Dinâmica do Carro":
            st.subheader(f"Dinâmica — {piloto1} vs {piloto2} — {gp} {ano} {sessao}")

            aba1, aba2, aba3, aba4 = st.tabs([
                "G Longitudinal", "Diagrama G-G", "Energia de Frenagem", "Mapa G Longitudinal"
            ])

            with aba1:
                st.markdown(f"**{piloto1}**")
                dist1, _, g_suave1 = calcular_g_longitudinal(tel1)
                import matplotlib.pyplot as plt
                import numpy as np
                fig, ax = plt.subplots(figsize=(14, 4))
                ax.plot(dist1, g_suave1, color='#E85D24')
                ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
                ax.set_xlabel('Distância (m)')
                ax.set_ylabel('G longitudinal')
                ax.set_title(f'{piloto1} — G longitudinal')
                ax.grid(alpha=0.2)
                st.pyplot(fig)

                st.markdown(f"**{piloto2}**")
                dist2, _, g_suave2 = calcular_g_longitudinal(tel2)
                fig2, ax2 = plt.subplots(figsize=(14, 4))
                ax2.plot(dist2, g_suave2, color='#0090FF')
                ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
                ax2.set_xlabel('Distância (m)')
                ax2.set_ylabel('G longitudinal')
                ax2.set_title(f'{piloto2} — G longitudinal')
                ax2.grid(alpha=0.2)
                st.pyplot(fig2)

            with aba2:
                col1, col2 = st.columns(2)
                with col1:
                    fig_gg1 = diagrama_gg(tel1, titulo=f'{piloto1} — Diagrama G-G')
                    st.pyplot(fig_gg1)
                with col2:
                    fig_gg2 = diagrama_gg(tel2, titulo=f'{piloto2} — Diagrama G-G')
                    st.pyplot(fig_gg2)

            with aba3:
                energia1 = calcular_energia_frenagem(tel1)
                energia2 = calcular_energia_frenagem(tel2)
                fig_comp = comparar_energia_frenagem(energia1, energia2, piloto1, piloto2,
                                                      titulo=f'Energia de frenagem — {gp} {ano}')
                st.pyplot(fig_comp)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{piloto1}**")
                    st.dataframe(energia1[['distancia_inicio', 'v_inicial_kmh', 'v_final_kmh', 'energia_kwh']].round(2))
                    st.pyplot(mapa_energia_frenagem(tel1, energia1, f"{piloto1}"))
                with col2:
                    st.markdown(f"**{piloto2}**")
                    st.dataframe(energia2[['distancia_inicio', 'v_inicial_kmh', 'v_final_kmh', 'energia_kwh']].round(2))
                    st.pyplot(mapa_energia_frenagem(tel2, energia2, f"{piloto2}"))

            with aba4:
                fig_mapa_g = comparar_mapas_g_longitudinal(tel1, tel2, piloto1, piloto2,
                                                            titulo_geral=f'{gp} {ano} — G longitudinal')
                st.pyplot(fig_mapa_g)

        # --- Seção: Estratégia de Corrida ---
        elif secao == "🔄 Estratégia de Corrida":
            if sessao != "R":
                st.warning("⚠️ Estratégia de corrida só disponível para a sessão de Corrida (R).")
            else:
                st.subheader(f"Estratégia — {gp} {ano}")

                aba1, aba2 = st.tabs(["Stints individuais", "Comparação de stints"])

                with aba1:
                    col1, col2 = st.columns(2)
                    with col1:
                        voltas1, fig_s1 = analisar_stints(ano, gp, piloto1)
                        st.pyplot(fig_s1)
                    with col2:
                        voltas2, fig_s2 = analisar_stints(ano, gp, piloto2)
                        st.pyplot(fig_s2)

                with aba2:
                    voltas1 = obter_dados_corrida(ano, gp, piloto1)
                    voltas2 = obter_dados_corrida(ano, gp, piloto2)
                    fig_comp = comparar_stints(voltas1, voltas2, piloto1, piloto2,
                                               titulo=f'{piloto1} vs {piloto2} — Stints {gp} {ano}')
                    st.pyplot(fig_comp)