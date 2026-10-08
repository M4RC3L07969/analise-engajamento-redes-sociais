import plotly.express as px
import streamlit as st

from utils import (COR_PRINCIPAL, CORES_PLATAFORMA, METRICAS, agrupar, formatar_compacto, formatar_metrica,
                   formatar_numero, formatar_percentual, obter_dados_filtrados)

df = obter_dados_filtrados()

st.title("Plataformas e conteúdo")
st.markdown("Comparação do desempenho entre plataformas, tipos de conteúdo e perfis.")

metrica = st.selectbox("Métrica para comparar", list(METRICAS.keys()))

# ---------- plataformas ----------
st.subheader("Comparação entre plataformas")
por_plataforma = agrupar(df, "plataforma", metrica)
por_plataforma["rotulo"] = por_plataforma["valor"].apply(lambda v: formatar_metrica(v, metrica))

fig = px.bar(por_plataforma, x="plataforma", y="valor", color="plataforma", text="rotulo",
             color_discrete_map=CORES_PLATAFORMA, labels={"plataforma": "", "valor": metrica})
fig.update_traces(textposition="outside", hovertemplate="%{x}: %{text}<extra></extra>")
fig.update_layout(template="plotly_white", showlegend=False, height=400, margin=dict(t=30, b=10))
st.plotly_chart(fig, use_container_width=True)

if len(por_plataforma) > 1:
    melhor, pior = por_plataforma.iloc[0], por_plataforma.iloc[-1]
    diferenca_pct = (melhor["valor"] / pior["valor"] - 1) * 100
    st.info(
        f"**Interpretação:** em *{metrica.lower()}*, **{melhor['plataforma']}** lidera com "
        f"{melhor['rotulo']} e **{pior['plataforma']}** fica em último com {pior['rotulo']}, "
        f"uma diferença de apenas {formatar_numero(diferenca_pct, 1)}%. As plataformas têm desempenho "
        "muito parecido, então a escolha da plataforma sozinha não explica o engajamento."
    )

# ---------- tipos de conteúdo ----------
st.subheader("Comparação entre tipos de conteúdo")
col1, col2 = st.columns([3, 2])

por_conteudo = agrupar(df, "tipo_conteudo", metrica)
por_conteudo["rotulo"] = por_conteudo["valor"].apply(lambda v: formatar_metrica(v, metrica))
fig = px.bar(por_conteudo, x="valor", y="tipo_conteudo", orientation="h", text="rotulo",
             labels={"tipo_conteudo": "", "valor": metrica})
fig.update_traces(marker_color=COR_PRINCIPAL, textposition="outside",
                  hovertemplate="%{y}: %{text}<extra></extra>")
fig.update_layout(template="plotly_white", height=360, margin=dict(t=20, b=10),
                  yaxis=dict(categoryorder="total ascending"))
col1.plotly_chart(fig, use_container_width=True)

resumo = df.groupby("tipo_conteudo").agg(
    publicacoes=("taxa_engajamento", "size"),
    engajamento=("taxa_engajamento", "mean"),
    alcance=("alcance", "mean"),
).sort_values("engajamento", ascending=False)
col2.dataframe(
    resumo,
    use_container_width=True,
    column_config={
        "publicacoes": st.column_config.NumberColumn("Publicações"),
        "engajamento": st.column_config.NumberColumn("Engajamento (%)", format="%.2f"),
        "alcance": st.column_config.NumberColumn("Alcance médio", format="%.0f"),
    },
)
melhor_eng = resumo["engajamento"].idxmax()
melhor_alc = resumo["alcance"].idxmax()
col2.info(
    f"**{melhor_eng}** tem o maior engajamento médio ({formatar_percentual(resumo['engajamento'].max())}) "
    f"e **{melhor_alc}** o maior alcance médio ({formatar_compacto(resumo['alcance'].max())} de pessoas)."
)

# ---------- plataforma x conteúdo ----------
st.subheader("Engajamento por plataforma e tipo de conteúdo")
tabela = df.pivot_table(index="tipo_conteudo", columns="plataforma", values="taxa_engajamento", aggfunc="mean")
fig = px.imshow(tabela, text_auto=".2f", color_continuous_scale="Blues", aspect="auto",
                labels={"x": "", "y": "", "color": "Engajamento (%)"})
fig.update_layout(height=380, margin=dict(t=20, b=10))
st.plotly_chart(fig, use_container_width=True)

combinacoes = tabela.stack().sort_values(ascending=False)
if len(combinacoes) > 1:
    (tipo_top, plat_top), valor_top = combinacoes.index[0], combinacoes.iloc[0]
    st.info(
        f"**Interpretação:** a melhor combinação é **{tipo_top} no {plat_top}** "
        f"({formatar_percentual(valor_top)}). Como cada combinação tem bem menos publicações do que o total, "
        "parte dessas diferenças pode ser só variação aleatória e precisaria ser confirmada com mais dados."
    )

# ---------- ranking de perfis ----------
st.subheader("Ranking de perfis")
ranking = df.groupby("perfil").agg(
    engajamento=("taxa_engajamento", "mean"),
    visualizacoes=("visualizacoes", "sum"),
    interacoes=("interacoes", "sum"),
    seguidores=("seguidores", "mean"),
    publicacoes=("taxa_engajamento", "size"),
).sort_values("engajamento", ascending=False)
ranking.insert(0, "posicao", range(1, len(ranking) + 1))

st.dataframe(
    ranking,
    use_container_width=True,
    column_config={
        "posicao": st.column_config.NumberColumn("Posição", format="%dº"),
        "engajamento": st.column_config.ProgressColumn(
            "Engajamento médio (%)", format="%.2f", min_value=0, max_value=12),
        "visualizacoes": st.column_config.NumberColumn("Visualizações", format="%d"),
        "interacoes": st.column_config.NumberColumn("Interações", format="%d"),
        "seguidores": st.column_config.NumberColumn("Seguidores (média)", format="%.0f"),
        "publicacoes": st.column_config.NumberColumn("Publicações"),
    },
)

# campanhas = combinação de perfil e formato (a base não tem coluna de campanha)
st.subheader("Melhores campanhas (perfil + formato)")
campanhas = (df.groupby(["perfil", "tipo_conteudo"])
             .agg(publicacoes=("taxa_engajamento", "size"),
                  engajamento=("taxa_engajamento", "mean"),
                  alcance=("alcance", "mean"))
             .reset_index()
             .sort_values("engajamento", ascending=False)
             .head(5))
st.dataframe(
    campanhas,
    use_container_width=True,
    hide_index=True,
    column_config={
        "perfil": "Perfil",
        "tipo_conteudo": "Formato",
        "publicacoes": "Publicações",
        "engajamento": st.column_config.NumberColumn("Engajamento médio (%)", format="%.2f"),
        "alcance": st.column_config.NumberColumn("Alcance médio", format="%.0f"),
    },
)
st.caption("Como a base não possui uma coluna de campanha, cada combinação de perfil e tipo de conteúdo "
           "foi tratada como uma estratégia de campanha.")
