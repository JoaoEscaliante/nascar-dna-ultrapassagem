#%%
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import seaborn as sns
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')


BASE_DIR = Path(__file__).parent


# Configuração da página Streamlit:

st.set_page_config(
    page_title='NASCAR  DNA de Ultrapassagem',
    page_icon='🏁',
    layout='wide',
)

# Configuração visual global do matplotlib:

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#f8f9fa',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.spines.top': False,
    'axes.spines.right':False,
    'font.size': 11,
})

AZUL = '#378ADD'
VERDE = '#1D9E75'
AMBAR = '#BA7517'
VERMELHO = '#E24B4A'
CINZA = '#888780'
ROXO = '#7F77DD'

# Paleta de cores por piloto  centralizada aqui pra não repetir em cada aba:

PILOTOS_MAPA = {
    'Jimmie Johnson': '#378ADD',
    'Kyle Busch': '#E24B4A',
    'Kevin Harvick': '#1D9E75',
    'Denny Hamlin': '#BA7517',
    'Kurt Busch': '#7F77DD',
    'Jeff Gordon': '#E8873A',
    'Brad Keselowski': '#28BAC0',
    'Chase Elliott': '#C84BA0',
    'Tony Stewart': '#A0522D',
    'Joey Logano': '#FFD700',
    'Carl Edwards': '#5F9EA0',
    'Christopher Bell': '#FF6B6B',
    'Dale Earnhardt Jr.': '#F0A500',
}
COR_OUTROS = '#888780'



# Carregamento e cache dos dados:

@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df['PassEfficiency']  = df['QualityPasses']  / df['GreenFlagPasses'].replace(0, float('nan')) * 100
    df['AggressionIndex'] = df['GreenFlagPasses'] / df['TotalLaps'].replace(0, float('nan'))       * 100
    return df



# Agregação de carreira também cacheada:

@st.cache_data
def agregar_carreira(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby('Driver')
        .agg(
            GreenFlagPasses = ('GreenFlagPasses', 'sum'),
            GreenFlagPassed = ('GreenFlagPassed', 'sum'),
            PassDiff = ('PassDiff', 'sum'),
            QualityPasses = ('QualityPasses', 'sum'),
            PercentQualityPasses = ('PercentQualityPasses', 'mean'),
            TotalLaps = ('TotalLaps', 'sum'),
            Wins = ('Wins', 'sum'),
            DriverRating = ('DriverRating', 'mean'),
            Seasons = ('Year', 'count'),
        )
        .query('Seasons >= 3')
        .assign(
            PassEfficiency = lambda x: (x['QualityPasses'] / x['GreenFlagPasses'] * 100).round(2),
            AggressionIndex = lambda x: (x['GreenFlagPasses'] / x['TotalLaps'] * 100).round(2),
        )
        .sort_values('PassDiff', ascending=False)
        .reset_index()
    )



# Campeão de eficiência por temporada também cacheado:

@st.cache_data
def agregar_best_ano(df: pd.DataFrame) -> pd.DataFrame:
    validos = df[df['TotalLaps'] > 1000].copy()
    return (
        validos.loc[validos.groupby('Year')['PassEfficiency'].idxmax()]
        [['Year', 'Driver', 'PassEfficiency', 'Wins', 'DriverRating']]
        .reset_index(drop=True)
    )



# Funções auxiliares  mantidas exatamente como no original:

def faixa_vitorias(w):
    if w >= 30: return '30+ vitórias'
    if w >= 10: return '10–29 vitórias'
    return '1–9 vitórias'

def perfil_piloto(row, lim_agg, lim_eff):
    agg = row['AggressionIndex'] >= lim_agg
    eff = row['PassEfficiency']  >= lim_eff
    if     agg and     eff: return 'Agressivo + Eficiente'
    if     agg and not eff: return 'Agressivo + Volume'
    if not agg and     eff: return 'Calculado + Eficiente'
    return                          'Conservador'



# Carregando tudo:

df = carregar_dados(str(BASE_DIR / 'nascar_driver_statistics.csv'))
carreira = agregar_carreira(df)
best_ano = agregar_best_ano(df)

# Dados compartilhados entre abas  calculados uma vez só aqui em cima:
top5 = carreira.head(5)['Driver'].tolist()
df5 = df[df['Driver'].isin(top5)].copy()

top30 = carreira.head(30).copy()
top30['faixa'] = top30['Wins'].apply(faixa_vitorias)
paleta = {
    '30+ vitórias': AMBAR,
    '10–29 vitórias': VERDE,
    '1–9 vitórias': AZUL,
}

quad = carreira.head(20).copy()
lim_agg = quad['AggressionIndex'].median()
lim_eff = quad['PassEfficiency'].median()
quad['perfil'] = quad.apply(lambda r: perfil_piloto(r, lim_agg, lim_eff), axis=1)
cores_perfil = {
    'Agressivo + Eficiente': VERDE,
    'Agressivo + Volume': VERMELHO,
    'Calculado + Eficiente': AZUL,
    'Conservador': CINZA,
}

# Cabeçalho do app:

st.title('🏁 NASCAR  DNA de Ultrapassagem (2007–2022)')
st.caption(
    f"Dataset: **{len(df):,}** registros · **{df['Driver'].nunique()}** pilotos · "
    f"{df['Year'].min()}–{df['Year'].max()}"
)
st.divider()


# Insights rápidos no topo:

lider = carreira.iloc[0]
mais_eficiente = carreira.loc[carreira['PassEfficiency'].idxmax()]
mais_agressivo = carreira.loc[carreira['AggressionIndex'].idxmax()]

col1, col2, col3, col4 = st.columns(4)
col1.metric('👑 Maior PassDiff', lider['Driver'], f"{lider['PassDiff']:,} passes")
col2.metric('🎯 Mais eficiente', mais_eficiente['Driver'], f"{mais_eficiente['PassEfficiency']:.1f}% quality")
col3.metric('⚡ Mais agressivo', mais_agressivo['Driver'], f"{mais_agressivo['AggressionIndex']:.2f} passes/volta%")
col4.metric('📊 Correlação qualidade×wins', '0.57', 'quem ultrapassa bem vence mais')

st.divider()



# Tabs organizam melhor o conteúdo do que uma página linear:

aba_dashboard, aba_correlacao, aba_ranking, aba_eficiencia, aba_evolucao, aba_quadrante, aba_campeao = st.tabs([
    '📊 Dashboard Geral',
    '🔥 Correlação',
    '🏆 Ranking Top 15',
    '🎯 Eficiência × Vitórias',
    '📈 Evolução Anual',
    '🗺️ Quadrante de Perfis',
    '🥇 Campeão por Temporada',
])



# ABA 1 Dashboard interativo Plotly:

with aba_dashboard:
    st.subheader('Visão geral  4 gráficos em um painel')

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Ranking PassDiff  top 15',
            'Eficiência  ×  Vitórias',
            'Evolução anual  PassDiff (top 5)',
            'Quadrante de perfis',
        ],
        vertical_spacing=0.14,
        horizontal_spacing=0.10,
    )

    # Ranking:
    t15 = carreira.head(15).sort_values('PassDiff')
    fig.add_trace(go.Bar(
        y=t15['Driver'], x=t15['PassDiff'],
        orientation='h',
        marker_color=AZUL,
        text=t15['PassDiff'].apply(lambda v: f'{v:,}'),
        textposition='outside',
        name='PassDiff',
        hovertemplate='<b>%{y}</b><br>PassDiff: %{x:,}<extra></extra>',
    ), row=1, col=1)

    # Eficiência × vitórias:
    for faixa, cor in paleta.items():
        sub = top30[top30['faixa'] == faixa]
        fig.add_trace(go.Scatter(
            x=sub['PassEfficiency'], y=sub['Wins'],
            mode='markers+text',
            marker=dict(color=cor, size=10, opacity=0.8),
            text=sub['Driver'].str.split().str[-1],
            textposition='top center',
            textfont=dict(size=8),
            name=faixa,
            hovertemplate='<b>%{text}</b><br>Eficiência: %{x:.1f}%<br>Vitórias: %{y}<extra></extra>',
        ), row=1, col=2)

    # Evolução anual:
    cores_evo = [AZUL, VERDE, AMBAR, VERMELHO, ROXO]
    for piloto, cor in zip(top5, cores_evo):
        dados = df5[df5['Driver'] == piloto].sort_values('Year')
        fig.add_trace(go.Scatter(
            x=dados['Year'], y=dados['PassDiff'],
            mode='lines+markers',
            name=piloto.split()[-1],
            line=dict(color=cor, width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{piloto}</b><br>Ano: %{{x}}<br>PassDiff: %{{y}}<extra></extra>',
        ), row=2, col=1)

    # Quadrante:
    for perfil, cor in cores_perfil.items():
        sub = quad[quad['perfil'] == perfil]
        fig.add_trace(go.Scatter(
            x=sub['AggressionIndex'], y=sub['PassEfficiency'],
            mode='markers+text',
            marker=dict(
                color=cor,
                size=(sub['PassDiff'] / quad['PassDiff'].max() * 28 + 10).clip(lower=10),
                opacity=0.8,
            ),
            text=sub['Driver'].str.split().str[-1],
            textposition='top center',
            textfont=dict(size=8),
            name=perfil,
            hovertemplate='<b>%{text}</b><br>Agressividade: %{x:.1f}%<br>Eficiência: %{y:.1f}%<extra></extra>',
        ), row=2, col=2)

    fig.add_hline(y=lim_eff, line_dash='dash', line_color='#555555', line_width=1, opacity=0.7, row=2, col=2)
    fig.add_vline(x=lim_agg, line_dash='dash', line_color='#555555', line_width=1, opacity=0.7, row=2, col=2)

    # Tema escuro  combina com o fundo do Streamlit e melhora muito a legibilidade:
    BG_ESCURO = '#0E1117'  
    BG_SUBPLOT = '#1A1D27'
    GRID_ESCURO = 'rgba(255,255,255,0.06)'
    TEXTO_CLARO = '#FAFAFA'

    fig.update_layout(
        title=dict(
            text='NASCAR  DNA de Ultrapassagem (2007–2022)',
            font=dict(size=18, color=TEXTO_CLARO),
            x=0.5,
        ),
        height=950,
        paper_bgcolor=BG_ESCURO,
        plot_bgcolor=BG_SUBPLOT,
        font=dict(family='Arial, sans-serif', size=11, color=TEXTO_CLARO),
        legend=dict(
            orientation='h',
            yanchor='bottom', y=-0.12,
            xanchor='center', x=0.5,
            font=dict(size=9, color=TEXTO_CLARO),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
        ),
    )
    # Grade e eixos no tema escuro:
    fig.update_xaxes(
        showgrid=True, gridcolor=GRID_ESCURO,
        zeroline=False,
        tickfont=dict(color=TEXTO_CLARO),
        title_font=dict(color=TEXTO_CLARO),
        linecolor='rgba(255,255,255,0.1)',
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=GRID_ESCURO,
        zeroline=False,
        tickfont=dict(color=TEXTO_CLARO),
        title_font=dict(color=TEXTO_CLARO),
        linecolor='rgba(255,255,255,0.1)',
    )
    # Títulos dos subplots também precisam ficar claros:
    for annotation in fig.layout.annotations:
        annotation.font.color = TEXTO_CLARO

    st.plotly_chart(fig, use_container_width=True)



# ABA 2  Heatmap de correlação:

with aba_correlacao:
    st.subheader('Correlação entre métricas de ultrapassagem  carreira')

    cols_corr = [
        'GreenFlagPasses', 'GreenFlagPassed', 'PassDiff',
        'QualityPasses', 'PercentQualityPasses',
        'PassEfficiency', 'AggressionIndex', 'Wins', 'DriverRating'
    ]

    # Tabela de correlação com Wins mais legível que um print():
    corr_wins = carreira[cols_corr].corr()['Wins'].drop('Wins').sort_values(ascending=False).round(3)
    st.write('**Correlação com Wins:**')
    st.dataframe(corr_wins.rename('r'), use_container_width=False)

    fig_corr, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        carreira[cols_corr].corr(),
        annot=True, fmt='.2f',
        cmap='RdYlGn', center=0, vmin=-1, vmax=1,
        ax=ax, linewidths=0.5,
        annot_kws={'size': 9},
    )
    ax.set_title('Correlação entre métricas de ultrapassagem  carreira', fontsize=13, pad=15)
    plt.tight_layout()
    st.pyplot(fig_corr)



# ABA 3  Ranking top 15:

with aba_ranking:
    st.subheader('Top 15 pilotos  saldo de ultrapassagens (2007–2022)')

    top15 = carreira.head(15)

    fig_rank, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(
        top15['Driver'], top15['PassDiff'],
        color=AZUL, alpha=0.85, edgecolor='white'
    )
    for bar, val in zip(bars, top15['PassDiff']):
        ax.text(
            bar.get_width() + 30,
            bar.get_y() + bar.get_height() / 2,
            f'{val:,}',
            va='center', fontsize=9, color=AZUL
        )

    ax.invert_yaxis()
    ax.set_xlabel('PassDiff acumulado na carreira')
    ax.set_title('Top 15 pilotos  saldo de ultrapassagens (2007–2022)', fontsize=13, pad=15)
    plt.tight_layout()
    st.pyplot(fig_rank)

    # Tabela de dados abaixo do gráfico bônus de usabilidade:
    st.dataframe(
        top15[['Driver', 'PassDiff', 'PassEfficiency', 'AggressionIndex', 'Wins', 'Seasons']]
        .reset_index(drop=True),
        use_container_width=True,
    )



# ABA 4 Eficiência × Vitórias:

with aba_eficiencia:
    st.subheader('Qualidade das ultrapassagens × vitórias (2007–2022)')

    fig_ef, ax = plt.subplots(figsize=(11, 7))

    for faixa, cor in paleta.items():
        sub = top30[top30['faixa'] == faixa]
        ax.scatter(sub['PassEfficiency'], sub['Wins'],
                   c=cor, s=90, alpha=0.85, label=faixa, zorder=3)

    # Linha de regressão:
    slope, intercept, r, p, _ = stats.linregress(top30['PassEfficiency'], top30['Wins'])
    x_range = pd.Series([top30['PassEfficiency'].min(), top30['PassEfficiency'].max()])
    ax.plot(x_range, slope * x_range + intercept,
            '--', color=CINZA, lw=1.5, alpha=0.7,
            label=f'regressão  r = {r:.2f}')

    # Rótulo dos top 5 pra identificar facilmente:
    for _, row in top30.nlargest(5, 'Wins').iterrows():
        ax.annotate(
            row['Driver'].split()[-1],
            (row['PassEfficiency'], row['Wins']),
            textcoords='offset points', xytext=(6, 4), fontsize=8
        )

    ax.set_xlabel('Eficiência de ultrapassagem  % quality passes')
    ax.set_ylabel('Vitórias na carreira')
    ax.set_title('Qualidade das ultrapassagens  ×  vitórias (2007–2022)', fontsize=13, pad=15)
    ax.legend(fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_ef)

    # Resultado da regressão como métrica visual:
    col_r, col_p = st.columns(2)
    col_r.metric('Correlação PassEfficiency × Wins', f'r = {r:.4f}')
    col_p.metric('p-value', f'{p:.4f}', 'estatisticamente significativo' if p < 0.05 else 'não significativo')



# ABA 5 Evolução anual top 5:

with aba_evolucao:
    st.subheader('Evolução anual  PassDiff e vitórias | top 5 pilotos')

    cores_pilotos = dict(zip(top5, [AZUL, VERDE, AMBAR, VERMELHO, ROXO]))

    fig_evo, axes = plt.subplots(5, 1, figsize=(13, 18), sharex=False)
    fig_evo.suptitle('Evolução anual  PassDiff e vitórias | top 5 pilotos', fontsize=14, y=1.01)

    for ax, piloto in zip(axes, top5):
        dados = df5[df5['Driver'] == piloto].sort_values('Year')
        cor = cores_pilotos[piloto]

        # Barras negativas em vermelho pra indicar anos ruins:
        cores_bar = [cor if v >= 0 else VERMELHO for v in dados['PassDiff']]
        ax.bar(dados['Year'], dados['PassDiff'], color=cores_bar, alpha=0.7, width=0.6)
        ax.axhline(0, color='black', lw=0.5)

        ax2 = ax.twinx()
        ax2.plot(dados['Year'], dados['Wins'],
                 'o--', color='black', lw=1.2, ms=5, alpha=0.7)
        ax2.set_ylabel('vitórias', fontsize=9)
        ax2.set_ylim(0, dados['Wins'].max() * 2.2 + 1)

        ax.set_title(piloto, fontsize=11, fontweight='bold', color=cor)
        ax.set_ylabel('PassDiff', fontsize=9)
        ax.set_xticks(dados['Year'])
        ax.tick_params(axis='x', labelsize=8, rotation=45)

    plt.tight_layout()
    st.pyplot(fig_evo)



# ABA 6 Quadrante de perfis:
    # mediana como limiar para dividir os quadrantes
    # tamanho da bolha proporcional ao total de carreira

with aba_quadrante:
    st.subheader('Quadrante de perfis de ultrapassagem  top 20 pilotos')

    fig_quad, ax = plt.subplots(figsize=(12, 8))
    for perfil, cor in cores_perfil.items():
        sub = quad[quad['perfil'] == perfil]
        tam = (sub['PassDiff'] / quad['PassDiff'].max() * 600 + 80).clip(lower=80)
        ax.scatter(
            sub['AggressionIndex'], sub['PassEfficiency'],
            s=tam, c=cor, alpha=0.75,
            edgecolors='white', lw=0.8,
            label=perfil, zorder=3
        )
    for _, row in quad.iterrows():
        ax.annotate(
            row['Driver'].split()[-1],
            (row['AggressionIndex'], row['PassEfficiency']),
            textcoords='offset points', xytext=(5, 5), fontsize=8
        )

    # Linhas dos quadrantes:
    ax.axvline(lim_agg, color=CINZA, ls='--', lw=1, alpha=0.6)
    ax.axhline(lim_eff, color=CINZA, ls='--', lw=1, alpha=0.6)

    # Rótulos dos quadrantes:
    kw = dict(fontsize=9, alpha=0.75)
    ax.text(lim_agg + 0.05, quad['PassEfficiency'].max() - 0.6, 'Agressivo + Eficiente', color=VERDE, **kw)
    ax.text(lim_agg + 0.05, quad['PassEfficiency'].min() + 0.4, 'Agressivo + Volume', color=VERMELHO, **kw)
    ax.text(quad['AggressionIndex'].min() + 0.05, quad['PassEfficiency'].max() - 0.6, 'Calculado + Eficiente', color=AZUL, **kw)
    ax.text(quad['AggressionIndex'].min() + 0.05, quad['PassEfficiency'].min() + 0.4, 'Conservador', color=CINZA, **kw)

    ax.set_xlabel('Agressividade  passes / voltas totais (%)')
    ax.set_ylabel('Eficiência  quality passes (%)')
    ax.set_title(
        'Quadrante de perfis de ultrapassagem  top 20 pilotos\n'
        '(tamanho da bolha = PassDiff de carreira)',
        fontsize=13, pad=15
    )
    ax.legend(fontsize=9, loc='lower right')
    plt.tight_layout()
    st.pyplot(fig_quad)

    # Distribuição por perfil como tabela:
    st.write('**Distribuição por perfil:**')
    st.dataframe(
        quad.groupby('perfil')[['Driver', 'PassDiff', 'Wins']]
        .apply(lambda g: g.set_index('Driver'))
        .reset_index(),
        use_container_width=True,
    )



# ABA 7 Campeão de eficiência por temporada:
    # cada barra = piloto com maior % quality passes naquele ano

with aba_campeao:
    st.subheader('NASCAR  Campeão de Eficiência por Temporada (2007–2022)')

    anos = best_ano['Year'].tolist()
    efic = best_ano['PassEfficiency'].tolist()
    drivers = best_ano['Driver'].tolist()
    wins = best_ano['Wins'].tolist()
    cores = [PILOTOS_MAPA.get(d, COR_OUTROS) for d in drivers]

    fig_camp, ax = plt.subplots(figsize=(16, 7), facecolor='#0D0D0D')
    ax.set_facecolor('#111111')
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Grade:
    for y in [60, 62, 64, 66, 68, 70, 72, 74]:
        ax.axhline(y, color='#2A2A2A', lw=0.8, zorder=0)

    # Barras:
    bars = ax.bar(anos, efic, color=cores, alpha=0.85, width=0.6,
                  edgecolor='#0D0D0D', linewidth=0.8, zorder=2)

    # Linha de tendência dourada:
    ax.plot(anos, efic, color='#FFD700', lw=1.5, alpha=0.5,
            linestyle='--', marker='o', markersize=4, zorder=3)

    # Rótulos em cima de cada barra:
    for ano, ef, driver, win, cor in zip(anos, efic, drivers, wins, cores):
        sobrenome = driver.split()[-1]
        ax.text(ano, ef + 0.3, f'{ef:.1f}%',
            ha='center', va='bottom', fontsize=8, color='white', fontweight='bold', zorder=5,
            path_effects=[pe.withStroke(linewidth=2, foreground='#0D0D0D')])
        ax.text(ano, ef - 1.2, sobrenome,
            ha='center', va='top', fontsize=7.5, color=cor, fontweight='bold', zorder=5,
            path_effects=[pe.withStroke(linewidth=2, foreground='#0D0D0D')])
        if win > 0:
            ax.text(ano, 58.8, f'{win}v',
                ha='center', va='bottom', fontsize=7, color=cor, zorder=5)

    ax.set_xticks(anos)
    ax.set_xticklabels(anos, color='#AAAAAA', fontsize=9)
    ax.set_ylim(58, 76)
    ax.set_yticks([60, 62, 64, 66, 68, 70, 72, 74])
    ax.set_yticklabels([f'{y}%' for y in [60, 62, 64, 66, 68, 70, 72, 74]], color='#555555', fontsize=8)
    ax.tick_params(length=0)

    ax.set_title('NASCAR  Campeão de Eficiência por Temporada (2007–2022)',
        fontsize=14, fontweight='bold', color='white', pad=18)
    ax.text(0.5, -0.1, 'barra = % quality passes  |  número abaixo = vitórias na temporada',
        ha='center', transform=ax.transAxes, fontsize=8.5, color='#555555')

    # Linha de média:
    media = pd.Series(efic).mean()
    ax.axhline(media, color='#888780', lw=1, linestyle=':', alpha=0.6, zorder=1)
    ax.text(anos[-1] + 0.1, media, f'média {media:.1f}%',
        va='center', fontsize=7.5, color='#888780')

    plt.tight_layout()
    st.pyplot(fig_camp)

    # Tabela de vencedores por ano pra consulta rápida:
    st.write('**Ranking de campeões por temporada:**')
    st.dataframe(best_ano, use_container_width=True)
