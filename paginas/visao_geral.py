import plotly.express as px
import streamlit as st

from utils import (COR_PRINCIPAL, CORES_PERFIL, calcular_kpis, formatar_compacto, formatar_numero,
                   formatar_percentual, obter_dados_filtrados)

df = obter_dados_filtrados()
df_completo = st.session_state["df_completo"]

st.title("Análise de Engajamento em Redes Sociais")
st.markdown(
    "Dashboard sobre o desempenho de **publicações em redes sociais entre 2015 e 2024**. "
    "O objetivo é entender quais plataformas, formatos e horários geram mais engajamento, "
    "como os seguidores evoluíram e quais métricas realmente importam."
)

with st.expander("Sobre o problema e a base de dados"):
    st.markdown(
        """
        Empresas e criadores de conteúdo precisam decidir **onde, o quê e quando publicar**.
        Para apoiar essa decisão, a análise usa uma base simulada com 4.440 publicações de quatro perfis
        (EducaOnline, GamesBR, ModaHoje e TechBrasil) em seis plataformas (Facebook, Instagram, LinkedIn,
        TikTok, X e YouTube), com curtidas, comentários, compartilhamentos, visualizações, alcance,
        seguidores e taxa de engajamento.

        Use os **filtros da barra lateral** para recortar os dados. Todos os indicadores e gráficos
        são recalculados automaticamente.
        """
    )

# ---------- KPIs ----------
kpis = calcular_kpis(df)
diferenca = kpis["engajamento_medio"] - df_completo["taxa_engajamento"].mean()

st.subheader("Indicadores principais")
col1, col2, col3 = st.columns(3)
col1.metric("Total de seguidores", formatar_compacto(kpis["total_seguidores"]),
            help="Soma dos seguidores registrados em cada publicação. "
                 f"Média por publicação: {formatar_numero(kpis['media_seguidores'])}.")
col2.metric("Taxa média de engajamento", formatar_percentual(kpis["engajamento_medio"]),
            delta=f"{'+' if diferenca >= 0 else ''}{formatar_numero(diferenca, 2)} p.p. em relação à base completa",
            delta_color="normal" if abs(diferenca) >= 0.005 else "off")
col3.metric("Plataforma mais engajada", kpis["plataforma_top"],
            help=f"Engajamento médio de {formatar_percentual(kpis['plataforma_top_valor'])}")

col4, col5, col6 = st.columns(3)
col4.metric("Conteúdo com maior alcance", kpis["conteudo_maior_alcance"],
            help=f"Alcance médio de {formatar_compacto(kpis['conteudo_maior_alcance_valor'])} de pessoas")
col5.metric("Total de visualizações", formatar_compacto(kpis["total_visualizacoes"]))
col6.metric("Melhor horário de postagem", kpis["melhor_horario"],
            help=f"Engajamento médio de {formatar_percentual(kpis['melhor_horario_valor'])}")

st.divider()

# ---------- evolução temporal ----------
st.subheader("Evolução do engajamento ao longo do tempo")
periodo = st.radio("Agrupar por", ["Mês", "Trimestre", "Ano"], horizontal=True, index=2)

if periodo == "Mês":
    serie = df.groupby(df["data"].dt.to_period("M"))["taxa_engajamento"].mean().reset_index()
    serie["periodo"] = serie["data"].dt.to_timestamp()
elif periodo == "Trimestre":
    serie = df.groupby(df["data"].dt.to_period("Q"))["taxa_engajamento"].mean().reset_index()
    serie["periodo"] = serie["data"].dt.to_timestamp()
else:
    serie = df.groupby("ano")["taxa_engajamento"].mean().reset_index()
    serie["periodo"] = serie["ano"].astype(str)

fig = px.line(serie, x="periodo", y="taxa_engajamento", markers=periodo != "Mês",
              labels={"periodo": "", "taxa_engajamento": "Taxa de engajamento (%)"})
fig.update_traces(line_color=COR_PRINCIPAL, line_width=2.5,
                  hovertemplate="%{x}<br>Engajamento: %{y:.2f}%<extra></extra>")
fig.add_hline(y=kpis["engajamento_medio"], line_dash="dash", line_color="gray",
              annotation_text=f"média {formatar_percentual(kpis['engajamento_medio'])}",
              annotation_position="bottom right")
fig.update_layout(template="plotly_white", height=380, margin=dict(t=20, b=10))
st.plotly_chart(fig, use_container_width=True)

engajamento_ano = df.groupby("ano")["taxa_engajamento"].mean()
if len(engajamento_ano) > 1:
    st.info(
        f"**Interpretação:** o melhor ano foi **{engajamento_ano.idxmax()}** "
        f"({formatar_percentual(engajamento_ano.max())}) e o pior foi **{engajamento_ano.idxmin()}** "
        f"({formatar_percentual(engajamento_ano.min())}). A variação entre os anos é pequena e não existe "
        "uma tendência clara de alta ou de queda: o engajamento se manteve estável no período."
    )

# ---------- seguidores ----------
st.subheader("Crescimento de seguidores por perfil")
seguidores = df.groupby(["ano", "perfil"])["seguidores"].mean().reset_index()
fig = px.line(seguidores, x="ano", y="seguidores", color="perfil", markers=True,
              color_discrete_map=CORES_PERFIL,
              labels={"ano": "", "seguidores": "Média de seguidores", "perfil": "Perfil"})
fig.update_traces(hovertemplate="%{x}<br>%{y:,.0f} seguidores<extra>%{fullData.name}</extra>")
fig.update_layout(template="plotly_white", height=380, margin=dict(t=20, b=10), separators=",.",
                  xaxis=dict(dtick=1))
st.plotly_chart(fig, use_container_width=True)

primeiro, ultimo = seguidores["ano"].min(), seguidores["ano"].max()
if primeiro != ultimo:
    tabela = seguidores.pivot(index="perfil", columns="ano", values="seguidores")
    variacao = ((tabela[ultimo] / tabela[primeiro] - 1) * 100).dropna().sort_values(ascending=False)
    if not variacao.empty:
        st.info(
            f"**Interpretação:** entre {primeiro} e {ultimo}, o perfil que mais cresceu foi "
            f"**{variacao.index[0]}** ({formatar_numero(variacao.iloc[0], 1)}%) e o que menos cresceu foi "
            f"**{variacao.index[-1]}** ({formatar_numero(variacao.iloc[-1], 1)}%). As médias oscilam bastante "
            "de um ano para o outro, sem crescimento contínuo."
        )
