"""
Funções reutilizáveis para análise de telemetria de F1.
Usadas nos notebooks dos módulos do projeto.
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging
import warnings
logging.disable(logging.CRITICAL)
warnings.filterwarnings('ignore')


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
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(voltas_segundos.index, voltas_segundos.values, color=cores_barras)
    ax.invert_yaxis()
    
    margem = 0.3
    ax.set_xlim(voltas_segundos.min() - margem, voltas_segundos.max() + margem)
    ax.set_xlabel('Tempo de volta (s)')
    ax.set_title(f'{gp} {ano} {sessao} — Classificação (volta mais rápida)')
    ax.grid(alpha=0.2, axis='x')
    
    plt.tight_layout()
    return fig


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

def diagrama_gg(telemetria, titulo='Diagrama G-G'):
    """
    Plota o diagrama G-G (G lateral vs G longitudinal) de uma volta,
    mostrando o envelope de aderência explorado pelo piloto.
    
    NOTA: o G lateral aqui é uma aproximação (ver limitação documentada
    em calcular_g_lateral). Use para comparação relativa entre pilotos.
    """
    dist_long, g_bruto_long, g_suave_long = calcular_g_longitudinal(telemetria)
    dist_lat, g_bruto_lat, g_suave_lat = calcular_g_lateral(telemetria)
    
    g_lat_interp = np.interp(dist_long, dist_lat, g_suave_lat)
    
    plt.figure(figsize=(7, 7))
    sc = plt.scatter(g_lat_interp, g_suave_long, c=dist_long, cmap='viridis', s=8, alpha=0.7)
    plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
    plt.axvline(0, color='gray', linestyle='--', alpha=0.3)
    plt.colorbar(sc, label='Distância (m)')
    plt.xlabel('G lateral (aproximado)')
    plt.ylabel('G longitudinal')
    plt.title(titulo)
    plt.axis('equal')
    plt.grid(alpha=0.2)
    plt.show()


def calcular_energia_frenagem(telemetria, massa_kg=768, duracao_minima_pontos=3):
    """
    Identifica zonas de frenagem na volta e calcula a energia cinética
    dissipada em cada uma (em Joules e em kWh para referência).
    
    Filtra falsos positivos exigindo que a velocidade final seja
    realmente menor que a inicial (evita ruído residual do G longitudinal).
    """
    dist, g_bruto, g_suave = calcular_g_longitudinal(telemetria)
    
    freando = g_suave < -0.3
    mudancas = np.diff(freando.astype(int))
    inicios = np.where(mudancas == 1)[0] + 1
    fins = np.where(mudancas == -1)[0] + 1
    
    if freando[0]:
        inicios = np.insert(inicios, 0, 0)
    if freando[-1]:
        fins = np.append(fins, len(freando) - 1)
    
    resultados = []
    velocidade_ms = telemetria['Speed'].values / 3.6
    distancia_full = telemetria['Distance'].values
    
    for ini, fim in zip(inicios, fins):
        if fim - ini < duracao_minima_pontos:
            continue
        
        v_inicial = velocidade_ms[ini]
        v_final = velocidade_ms[fim]
        
        if v_final >= v_inicial:
            continue
        
        energia_j = 0.5 * massa_kg * (v_inicial**2 - v_final**2)
        
        resultados.append({
            'distancia_inicio': distancia_full[ini],
            'distancia_fim': distancia_full[fim],
            'v_inicial_kmh': v_inicial * 3.6,
            'v_final_kmh': v_final * 3.6,
            'energia_joules': energia_j,
            'energia_kwh': energia_j / 3_600_000
        })
    
    df_resultado = pd.DataFrame(resultados)
    return df_resultado


def mapa_energia_frenagem(telemetria, df_energia, titulo='Energia de frenagem por zona'):
    """
    Plota o traçado da pista com marcadores nas zonas de frenagem,
    onde o tamanho do marcador é proporcional à energia dissipada.
    """
    plt.figure(figsize=(10, 8))
    plt.plot(telemetria['X'], telemetria['Y'], color='gray', linewidth=2, alpha=0.4)
    
    for _, zona in df_energia.iterrows():
        x_ini, y_ini = encontrar_ponto_na_pista(telemetria, zona['distancia_inicio'])
        tamanho = zona['energia_kwh'] * 800
        plt.scatter(x_ini, y_ini, s=tamanho, color='crimson', alpha=0.6, edgecolors='black')
        plt.annotate(f"{zona['energia_kwh']:.2f} kWh", (x_ini, y_ini),
                     textcoords="offset points", xytext=(10, 10), fontsize=8)
    
    plt.title(titulo)
    plt.axis('equal')
    plt.axis('off')
    plt.show()


def comparar_energia_frenagem(df1, df2, nome1, nome2, titulo='Comparação de energia de frenagem'):
    """
    compara a energia dissipada em frenagem entre dois pilotos,
    mostrando barras lado a lado para cada zona de frenagem.
    
    
    NOTA: as zonas de frenagem podem não coincidir exatamente entre pilotos,"""

    zonas = pd.concat([df1[['distancia_inicio', 'energia_kwh']].rename(columns={'energia_kwh': nome1}),
                       df2[['distancia_inicio', 'energia_kwh']].rename(columns={'energia_kwh': nome2})],
                      axis=1)
    
    zonas = zonas.loc[:,~zonas.columns.duplicated()]
    zonas = zonas.sort_values('distancia_inicio')
    
    x = np.arange(len(zonas))
    largura = 0.35
    
    plt.figure(figsize=(12, 6))
    plt.bar(x - largura/2, zonas[nome1], width=largura, label=nome1, color='orange')
    plt.bar(x + largura/2, zonas[nome2], width=largura, label=nome2, color='blue')
    
    plt.xticks(x, [f"{d:.0f} m" for d in zonas['distancia_inicio']], rotation=45)
    plt.ylabel('Energia dissipada (kWh)')
    plt.title(titulo)
    plt.legend()
    plt.grid(alpha=0.2, axis='y')
    plt.tight_layout()
    plt.show()


def comparar_setores(ano, gp, sessao, piloto1, piloto2):
    """
    
    Compara os tempos de setor da volta mais rápida de dois pilotos
    numa sessão, mostrando onde cada um ganha ou perde tempo.
    """
    session = fastf1.get_session(ano, gp, sessao)
    session.load()
    
    volta1 = session.laps.pick_driver(piloto1).pick_fastest()
    volta2 = session.laps.pick_driver(piloto2).pick_fastest()
    
    setores = ['Sector1Time', 'Sector2Time', 'Sector3Time']
    labels = ['Setor 1', 'Setor 2', 'Setor 3']
    
    tempos1 = [volta1[s].total_seconds() for s in setores]
    tempos2 = [volta2[s].total_seconds() for s in setores]
    
    # Delta: positivo = piloto1 mais lento, negativo = piloto1 mais rápido
    deltas = [t1 - t2 for t1, t2 in zip(tempos1, tempos2)]
    cores = ['#0090FF' if d < 0 else '#FF8000' for d in deltas]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Gráfico 1: tempos absolutos por setor
    x = np.arange(len(labels))
    largura = 0.35
    axes[0].bar(x - largura/2, tempos1, largura, label=piloto1, color='#0090FF', alpha=0.85)
    axes[0].bar(x + largura/2, tempos2, largura, label=piloto2, color='#FF8000', alpha=0.85)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel('Tempo (s)')
    axes[0].set_title('Tempo por setor')
    axes[0].legend()
    axes[0].grid(alpha=0.2, axis='y')
    
    # Gráfico 2: delta por setor (piloto1 - piloto2)
    axes[1].bar(labels, deltas, color=cores, alpha=0.85)
    axes[1].axhline(0, color='gray', linestyle='--', alpha=0.5)
    axes[1].set_ylabel(f'Delta (s) — negativo = {piloto1} mais rápido')
    axes[1].set_title(f'Delta por setor: {piloto1} vs {piloto2}')
    axes[1].grid(alpha=0.2, axis='y')
    
    fig.suptitle(f'{gp} {ano} {sessao} — Comparação de setores', fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    # Imprime resumo textual também
    print(f"\n{'Setor':<10} {piloto1:>10} {piloto2:>10} {'Delta':>10}")
    print('-' * 42)
    for label, t1, t2, d in zip(labels, tempos1, tempos2, deltas):
        vencedor = '← mais rápido' if d < 0 else ('→ mais rápido' if d > 0 else 'empate')
        print(f"{label:<10} {t1:>10.3f} {t2:>10.3f} {d:>+10.3f}  {vencedor}")
    
    total1 = sum(tempos1)
    total2 = sum(tempos2)
    print('-' * 42)
    print(f"{'Total':<10} {total1:>10.3f} {total2:>10.3f} {total1-total2:>+10.3f}")


def mapa_g_longitudinal(telemetria, titulo='Mapa G longitudinal'):
    """
    Plota o traçado da pista colorido pelo G longitudinal em cada ponto.
    Vermelho = frenagem forte, verde = aceleração forte, amarelo = neutro.
    """
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    
    dist_g, g_bruto, g_suave = calcular_g_longitudinal(telemetria)
    
    # Interpola as coordenadas X, Y nos mesmos pontos do G longitudinal
    # (que tem tamanho ligeiramente diferente por causa do filtro de dt)
    x_interp = np.interp(dist_g, telemetria['Distance'].values, telemetria['X'].values)
    y_interp = np.interp(dist_g, telemetria['Distance'].values, telemetria['Y'].values)
    
    points = np.array([x_interp, y_interp]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Escala simétrica em torno do zero
    g_abs_max = np.abs(g_suave).max()
    norm = Normalize(vmin=-g_abs_max, vmax=g_abs_max)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    lc = LineCollection(segments[:-1], cmap='RdYlGn', norm=norm)
    lc.set_array(g_suave)
    lc.set_linewidth(4)
    
    ax.add_collection(lc)
    ax.set_xlim(x_interp.min() - 200, x_interp.max() + 200)
    ax.set_ylim(y_interp.min() - 200, y_interp.max() + 200)
    ax.axis('equal')
    ax.axis('off')
    ax.set_title(titulo)
    
    cbar = fig.colorbar(lc, ax=ax)
    cbar.set_label('G longitudinal (negativo = frenagem, positivo = aceleração)')
    
    plt.show()

def comparar_mapas_g_longitudinal(tel1, tel2, nome1, nome2, titulo_geral=''):
    """
    Plota dois mapas de G longitudinal lado a lado, na mesma escala de cor,
    para comparação direta entre dois pilotos.
    Vermelho = frenagem forte, verde = aceleração forte, amarelo = neutro.
    """
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    
    def extrair_dados(telemetria):
        dist_g, g_bruto, g_suave = calcular_g_longitudinal(telemetria)
        x_interp = np.interp(dist_g, telemetria['Distance'].values, telemetria['X'].values)
        y_interp = np.interp(dist_g, telemetria['Distance'].values, telemetria['Y'].values)
        return x_interp, y_interp, g_suave
    
    x1, y1, g1 = extrair_dados(tel1)
    x2, y2, g2 = extrair_dados(tel2)
    
    # Escala simétrica compartilhada entre os dois pilotos
    g_abs_max = max(np.abs(g1).max(), np.abs(g2).max())
    norm = Normalize(vmin=-g_abs_max, vmax=g_abs_max)
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    for ax, x, y, g, nome in zip(axes, [x1, x2], [y1, y2], [g1, g2], [nome1, nome2]):
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        lc = LineCollection(segments[:-1], cmap='RdYlGn', norm=norm)
        lc.set_array(g)
        lc.set_linewidth(4)
        
        ax.add_collection(lc)
        ax.set_xlim(x.min() - 200, x.max() + 200)
        ax.set_ylim(y.min() - 200, y.max() + 200)
        ax.axis('equal')
        ax.axis('off')
        ax.set_title(nome)
    
    fig.suptitle(titulo_geral, fontsize=14, fontweight='bold')
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='RdYlGn'), ax=axes, fraction=0.03)
    cbar.set_label('G longitudinal (negativo = frenagem, positivo = aceleração)')
    
    plt.show()