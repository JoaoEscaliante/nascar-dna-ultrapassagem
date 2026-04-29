# 🏁 NASCAR — DNA de Ultrapassagem (2007–2022)

Análise de dados sobre eficiência e estilo de ultrapassagens de 230 pilotos ao longo de 16 temporadas da NASCAR CUP SERIES.

## Sobre o projeto:

O objetivo foi ir além dos dados brutos e descobrir o que realmente diferencia um piloto vencedor, a conclusão principal: qualidade das ultrapassagens (r=0.57) 
prevê vitórias melhor do que volume bruto (r=0,35).

## Métricas criadas:

- **PassEfficiency**: % de ultrapassagens em posições decisivas;
- **AggressionIndex**: frequência de ultrapassagens por volta disputada;
- **SaldoUltrapassagens**: ultrapassagens feitas em menos sofridas

## Análises:

- Ranking de saldo de ultrapassagens de carreira (top15);
- Correlação entre eficiência e vitórias com regressão linear;
- Quadrante de perfils de ultrapassagens (4 estilos);
- Campeão de eficiência por temporada (2007-2022);
- Dashboard interativo com Streamlit + Ploty

## Visualizações:

![Ranking PassDiff](outputs/passo5_ranking_passdiff.png)
![Quadrante de Perfis](outputs/passo8_quadrante_perfis.png)
![Campeão por Temporada](outputs/grafico_campeao_por_temporada.png)

## Stack

Python · Pandas · Matplotlib · Seaborn · Scipy · Plotly · Streamlit

## Dataset:

NASCAR Driver Statistics 2007–2022 — Kaggle









