"""
Funções reutilizáveis para análise de telemetria de F1.
Usadas nos notebooks dos módulos do projeto.
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def comparar_pilotos(ano, gp, sessao, piloto1, piloto2):
    """
    Compara a telemetria de dois pilotos numa sessão específica.
    Plota velocidade, acelerador, marcha (3 painéis) e delta de tempo.
    """
    session = fastf1.get_session(ano, gp, sessao)
    session.load()
    
    volta1 = session.laps.pick_driver(piloto1).pick_fastest()
    volta2 = session.laps.pick_driver(piloto2).pick_fastest()
    
    tel1 = volta1.get_telemetry().add_distance()
    tel2 = volta2.get_telemetry().add_distance()
    
    fastf1.plotting.setup_mpl()
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    axes[0].plot(tel1['Distance'], tel1['Speed'], color='#FF8000', label=piloto1)
    axes[0].plot(tel2['Distance'], tel2['Speed'], color='#0090FF', label=piloto2, linestyle='--', alpha=0.8)
    axes[0].set_ylabel('Velocidade (km/h)')
    axes[0].legend()
    axes[0].grid(alpha=0.2)
    
    axes[1].plot(tel1['Distance'], tel1['Throttle'], color='#FF8000', label=piloto1)
    axes[1].plot(tel2['Distance'], tel2['Throttle'], color='#0090FF', label=piloto2, linestyle='--', alpha=0.8)
    axes[1].set_ylabel('Acelerador (%)')
    axes[1].legend()
    axes[1].grid(alpha=0.2)
    
    axes[2].plot(tel1['Distance'], tel1['nGear'], color='#FF8000', label=piloto1)
    axes[2].plot(tel2['Distance'], tel2['nGear'], color='#0090FF', label=piloto2, linestyle='--', alpha=0.8)
    axes[2].set_ylabel('Marcha')
    axes[2].set_xlabel('Distância (m)')
    axes[2].legend()
    axes[2].grid(alpha=0.2)
    
    fig.suptitle(f'{gp} {ano} {sessao} — {piloto1} vs {piloto2}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    tempo2_interp = np.interp(tel1['Distance'], tel2['Distance'], tel2['Time'].dt.total_seconds())
    tempo1 = tel1['Time'].dt.total_seconds()
    delta = tempo2_interp - tempo1
    
    plt.figure(figsize=(14, 4))
    plt.plot(tel1['Distance'], delta, color='purple')
    plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
    plt.xlabel('Distância (m)')
    plt.ylabel(f'Delta (s) — positivo = {piloto1} na frente')
    plt.title(f'{gp} {ano} {sessao} — Delta de tempo: {piloto1} vs {piloto2}')
    plt.grid(alpha=0.2)
    plt.show()
    
    return tel1, tel2


def encontrar_ponto_na_pista(telemetria, distancia_alvo):
    """
    Recebe a telemetria de uma volta e uma distância (em metros),
    e retorna as coordenadas X, Y do ponto mais próximo dessa distância.
    """
    idx = (telemetria['Distance'] - distancia_alvo).abs().idxmin()
    x = telemetria.loc[idx, 'X']
    y = telemetria.loc[idx, 'Y']
    return x, y


def mapa_velocidade(telemetria, titulo='Mapa de velocidade'):
    """
    Plota o traçado da pista colorido pela velocidade em cada ponto.
    """
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    
    x = telemetria['X'].values
    y = telemetria['Y'].values
    speed = telemetria['Speed'].values
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    norm = Normalize(vmin=speed.min(), vmax=speed.max())
    lc = LineCollection(segments, cmap='plasma', norm=norm)
    lc.set_array(speed)
    lc.set_linewidth(4)
    
    line = ax.add_collection(lc)
    ax.set_xlim(x.min() - 200, x.max() + 200)
    ax.set_ylim(y.min() - 200, y.max() + 200)
    ax.axis('equal')
    ax.axis('off')
    ax.set_title(titulo)
    
    cbar = fig.colorbar(line, ax=ax)
    cbar.set_label('Velocidade (km/h)')
    
    plt.show()


def comparar_mapas_velocidade(tel1, tel2, nome1, nome2, titulo_geral=''):
    """
    Plota dois mapas de velocidade lado a lado, na mesma escala de cor,
    para comparação direta entre dois pilotos.
    """
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    
    speed_min = min(tel1['Speed'].min(), tel2['Speed'].min())
    speed_max = max(tel1['Speed'].max(), tel2['Speed'].max())
    norm = Normalize(vmin=speed_min, vmax=speed_max)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    for ax, tel, nome in zip(axes, [tel1, tel2], [nome1, nome2]):
        x = tel['X'].values
        y = tel['Y'].values
        speed = tel['Speed'].values
        
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        lc = LineCollection(segments, cmap='plasma', norm=norm)
        lc.set_array(speed)
        lc.set_linewidth(4)
        
        ax.add_collection(lc)
        ax.set_xlim(x.min() - 200, x.max() + 200)
        ax.set_ylim(y.min() - 200, y.max() + 200)
        ax.axis('equal')
        ax.axis('off')
        ax.set_title(nome)
    
    fig.suptitle(titulo_geral, fontsize=14, fontweight='bold')
    
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='plasma'), ax=axes, fraction=0.03)
    cbar.set_label('Velocidade (km/h)')
    
    plt.show()


def analisar_stints(ano, gp, piloto):
    """
    Plota a evolução do tempo de volta por stint numa corrida,
    colorido por composto de pneu usado.
    """
    session = fastf1.get_session(ano, gp, 'R')
    session.load()
    
    voltas = session.laps.pick_driver(piloto)
    
    cores_composto = {'SOFT': 'red', 'MEDIUM': 'gold', 'HARD': 'gray',
                       'INTERMEDIATE': 'green', 'WET': 'blue'}
    
    plt.figure(figsize=(14, 6))
    
    for stint_num in voltas['Stint'].unique():
        stint_data = voltas[voltas['Stint'] == stint_num]
        composto = stint_data['Compound'].iloc[0]
        cor = cores_composto.get(composto, 'black')
        
        plt.plot(stint_data['LapNumber'], stint_data['LapTime'].dt.total_seconds(),
                  marker='o', color=cor, label=f'Stint {int(stint_num)} ({composto})')
    
    plt.xlabel('Volta')
    plt.ylabel('Tempo de volta (s)')
    plt.title(f'{gp} {ano} — Evolução do tempo de volta por stint ({piloto})')
    plt.legend()
    plt.grid(alpha=0.2)
    plt.show()
    
    return voltas


def obter_dados_corrida(ano, gp, piloto):
    """
    Carrega a corrida e retorna as voltas de um piloto específico,
    sem plotar nada.
    """
    session = fastf1.get_session(ano, gp, 'R')
    session.load()
    voltas = session.laps.pick_driver(piloto)
    return voltas


def comparar_stints(voltas1, voltas2, nome1, nome2, titulo=''):
    """
    Sobrepõe a evolução do tempo de volta de dois pilotos no mesmo gráfico,
    diferenciando por estilo de linha e colorindo por composto.
    """
    cores_composto = {'SOFT': 'red', 'MEDIUM': 'gold', 'HARD': 'gray',
                       'INTERMEDIATE': 'green', 'WET': 'blue'}
    
    plt.figure(figsize=(14, 6))
    
    for stint_num in voltas1['Stint'].unique():
        stint_data = voltas1[voltas1['Stint'] == stint_num]
        composto = stint_data['Compound'].iloc[0]
        cor = cores_composto.get(composto, 'black')
        plt.plot(stint_data['LapNumber'], stint_data['LapTime'].dt.total_seconds(),
                  marker='o', color=cor, linestyle='-', alpha=0.9,
                  label=f'{nome1} - Stint {int(stint_num)} ({composto})')
    
    for stint_num in voltas2['Stint'].unique():
        stint_data = voltas2[voltas2['Stint'] == stint_num]
        composto = stint_data['Compound'].iloc[0]
        cor = cores_composto.get(composto, 'black')
        plt.plot(stint_data['LapNumber'], stint_data['LapTime'].dt.total_seconds(),
                  marker='^', color=cor, linestyle='--', alpha=0.6,
                  label=f'{nome2} - Stint {int(stint_num)} ({composto})')
    
    plt.xlabel('Volta')
    plt.ylabel('Tempo de volta (s)')
    plt.title(titulo)
    plt.legend(fontsize=8, ncol=2)
    plt.grid(alpha=0.2)
    plt.show()


def ranking_sessao(ano, gp, sessao):
    """
    Mostra o ranking de todos os pilotos pela volta mais rápida
    numa sessão específica, colorido pela cor da equipe.
    """
    session = fastf1.get_session(ano, gp, sessao)
    session.load()
    
    voltas_rapidas = session.laps.groupby('Driver')['LapTime'].min().sort_values()
    voltas_segundos = voltas_rapidas.dt.total_seconds()
    
    cores_equipe = fastf1.plotting.get_driver_color_mapping(session=session)
    cores_barras = [cores_equipe.get(piloto, 'gray') for piloto in voltas_segundos.index]
    
    plt.figure(figsize=(10, 8))
    plt.barh(voltas_segundos.index, voltas_segundos.values, color=cores_barras)
    plt.gca().invert_yaxis()
    
    margem = 0.3
    plt.xlim(voltas_segundos.min() - margem, voltas_segundos.max() + margem)
    
    plt.xlabel('Tempo de volta (s)')
    plt.title(f'{gp} {ano} {sessao} — Classificação (volta mais rápida)')
    plt.grid(alpha=0.2, axis='x')
    plt.show()
    
    return voltas_rapidas


def calcular_g_longitudinal(telemetria, dt_minimo=0.01, janela_suavizacao=5):
    """
    Calcula a força G longitudinal a partir da telemetria de uma volta.
    Filtra amostras com intervalo de tempo anormalmente pequeno (erro de sensor)
    e suaviza o resultado com média móvel.
    """
    v_ms = telemetria['Speed'].values / 3.6
    t_s = telemetria['Time'].dt.total_seconds().values
    distancia = telemetria['Distance'].values
    
    dv = np.diff(v_ms)
    dt = np.diff(t_s)
    dist_pontos = distancia[1:]
    
    mascara_valida = dt >= dt_minimo
    dv_f = dv[mascara_valida]
    dt_f = dt[mascara_valida]
    dist_f = dist_pontos[mascara_valida]
    
    aceleracao = dv_f / dt_f
    g_bruto = aceleracao / 9.81
    
    g_suave = pd.Series(g_bruto).rolling(window=janela_suavizacao, center=True, min_periods=1).mean().values
    
    return dist_f, g_bruto, g_suave


def calcular_g_lateral(telemetria, janela_suavizacao=3):
    """
    Estima a força G lateral a partir da geometria da trajetória (X, Y),
    usando a distância percorrida como referência (mais estável que tempo).
    
    LIMITAÇÃO CONHECIDA: a derivação numérica de 2ª ordem tende a subestimar
    picos de curvatura em curvas fechadas. Use como aproximação relativa
    (comparação entre pilotos/curvas), não como valor absoluto preciso.
    """
    x = telemetria['X'].values
    y = telemetria['Y'].values
    v_ms = telemetria['Speed'].values / 3.6
    s = telemetria['Distance'].values
    
    dx = np.gradient(x, s)
    dy = np.gradient(y, s)
    ddx = np.gradient(dx, s)
    ddy = np.gradient(dy, s)
    
    numerador = np.abs(dx * ddy - dy * ddx)
    denominador = (dx**2 + dy**2)**1.5
    denominador = np.where(denominador < 1e-9, 1e-9, denominador)
    curvatura = numerador / denominador
    
    raio = 1 / np.where(curvatura < 1e-6, 1e-6, curvatura)
    aceleracao_lateral = (v_ms**2) / raio
    g_lateral = aceleracao_lateral / 9.81
    
    g_suave = pd.Series(g_lateral).rolling(window=janela_suavizacao, center=True, min_periods=1).mean().values
    
    return s, g_lateral, g_suave