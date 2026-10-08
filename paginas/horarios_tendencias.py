import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (COR_PRINCIPAL, CORES_PLATAFORMA, formatar_compacto, formatar_correlacao, formatar_numero,
                   formatar_percentual, obter_dados_filtrados)

df = obter_dados_filtrados()

st.title("Horários e correlações")
st.markdown("Quando publicar, o que influencia o alcance e quais conteúdos viralizaram.")

# ---------- horários ----------
st.subheader("Engajamento por horário de publicação")
tabela = df.pivot_table(index="horario_publicacao", columns="plataforma", values="taxa_engajamento",
                        aggfunc="mean")
fig = px.imshow(tabela, text_auto=".2f", color_continuous_scale="Blues", aspect="auto",
                labels={"x": "", "y": "Horário", "color": "Engajamento (%)"})
fig.update_layout(height=360, margin=dict(t=20, b=10))
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

por_horario = df.groupby("horario_publicacao").agg(
    engajamento=("taxa_engajamento", "mean"),
    alcance=("alcance", "mean"),
).reset_index()
fig = px.bar(por_horario, x="horario_publicacao", y="alcance",
             text=por_horario["alcance"].apply(formatar_compacto),
             labels={"horario_publicacao": "Horário", "alcance": "Alcance médio"})
fig.update_traces(marker_color=COR_PRINCIPAL, textposition="outside",
                  hovertemplate="%{x}: %{text} pessoas<extra></extra>")
fig.update_layout(template="plotly_white", height=340, margin=dict(t=40, b=10),
                  title=dict(text="Alcance médio por horário", font_size=15))
col1.plotly_chart(fig, use_container_width=True)

melhor_por_plataforma = tabela.idxmax().rename("Melhor horário").to_frame()
melhor_por_plataforma["Engajamento (%)"] = tabela.max().round(2)
col2.markdown("**Melhor horário para cada plataforma**")
col2.dataframe(melhor_por_plataforma, use_container_width=True)

melhor_horario = por_horario.loc[por_horario["engajamento"].idxmax()]
maior_alcance = por_horario.loc[por_horario["alcance"].idxmax()]
st.info(
    f"**Interpretação:** no geral, publicações às **{melhor_horario['horario_publicacao']}** têm o maior "
    f"engajamento médio ({formatar_percentual(melhor_horario['engajamento'])}) e às "
    f"**{maior_alcance['horario_publicacao']}** o maior alcance. Mas o melhor horário muda conforme a "
    "plataforma (tabela ao lado), então o ideal é definir o horário de cada rede separadamente."
)

st.divider()

if len(df) < 10:
    st.warning("Poucas publicações selecionadas para calcular correlações. Amplie os filtros para ver o restante da página.")
    st.stop()

# ---------- seguidores x engajamento ----------
st.subheader("Seguidores x engajamento")
correlacao = df["seguidores"].corr(df["taxa_engajamento"])

fig = px.scatter(df, x="seguidores", y="taxa_engajamento", color="plataforma", opacity=0.5,
                 color_discrete_map=CORES_PLATAFORMA,
                 hover_data={"perfil": True, "tipo_conteudo": True, "data": "|%m/%Y"},
                 labels={"seguidores": "Seguidores", "taxa_engajamento": "Taxa de engajamento (%)",
                         "plataforma": "Plataforma", "perfil": "Perfil", "tipo_conteudo": "Formato",
                         "data": "Data"})
fig.update_traces(marker_size=6)

# linha de tendência (regressão linear simples com numpy)
if len(df) > 2:
    inclinacao, intercepto = np.polyfit(df["seguidores"], df["taxa_engajamento"], 1)
    x_linha = np.array([df["seguidores"].min(), df["seguidores"].max()])
    fig.add_trace(go.Scatter(x=x_linha, y=inclinacao * x_linha + intercepto, mode="lines",
                             name="Tendência", line=dict(color="black", width=2)))
fig.update_layout(template="plotly_white", height=450, margin=dict(t=20, b=10), separators=",.")
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns([1, 3])
col1.metric("Correlação de Pearson", formatar_correlacao(correlacao))
col2.info(
    "**Interpretação:** a correlação fica perto de zero, ou seja, ter mais seguidores **não** significa "
    "ter uma taxa de engajamento maior. A linha de tendência é praticamente horizontal."
)

# ---------- frequência x alcance ----------
st.subheader("Frequência de postagem x alcance")
frequencia = df.groupby(["perfil", "ano_mes"]).agg(
    publicacoes=("alcance", "size"),
    alcance=("alcance", "mean"),
).reset_index()
correlacao_freq = frequencia["publicacoes"].corr(frequencia["alcance"])

fig = px.box(frequencia, x="publicacoes", y="alcance", points="all",
             labels={"publicacoes": "Publicações do perfil no mês", "alcance": "Alcance médio das publicações"})
fig.update_traces(marker_color=COR_PRINCIPAL, line_color=COR_PRINCIPAL)
fig.update_layout(template="plotly_white", height=400, margin=dict(t=20, b=10), separators=",.")
st.plotly_chart(fig, use_container_width=True)
st.info(
    f"**Interpretação:** a correlação entre quantidade de publicações no mês e alcance médio é de "
    f"**{formatar_correlacao(correlacao_freq)}**. Publicar mais vezes não aumentou o alcance de cada publicação."
)

# ---------- matriz de correlação ----------
st.subheader("Correlação entre as métricas")
colunas = ["seguidores", "curtidas", "comentarios", "compartilhamentos", "visualizacoes", "alcance",
           "interacoes", "taxa_engajamento"]
matriz = df[colunas].corr().round(2)
fig = px.imshow(matriz, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
fig.update_layout(height=480, margin=dict(t=20, b=10))
st.plotly_chart(fig, use_container_width=True)

correlacoes_taxa = matriz["taxa_engajamento"].drop("taxa_engajamento").dropna()
if not correlacoes_taxa.empty:
    mais_forte = correlacoes_taxa.abs().idxmax()
    st.info(
        f"**Interpretação:** a métrica mais correlacionada com a taxa de engajamento é **{mais_forte}**, "
        f"com apenas {formatar_numero(correlacoes_taxa[mais_forte], 2)}. Nenhuma métrica isolada explica o "
        "engajamento nesta base. A única correlação forte é entre interações e curtidas, porque as curtidas "
        "fazem parte do cálculo das interações."
    )

st.divider()

# ---------- conteúdos virais ----------
st.subheader("Conteúdos virais")
st.markdown("São consideradas virais as **5% publicações com mais visualizações** da base completa.")

virais = df[df["viral"]]
col1, col2, col3 = st.columns(3)
col1.metric("Publicações virais", formatar_numero(len(virais)))
col2.metric("% das publicações filtradas", formatar_percentual(df["viral"].mean() * 100, 1))
if not virais.empty:
    col3.metric("Formato que mais viraliza", virais["tipo_conteudo"].value_counts().idxmax())

col1, col2 = st.columns(2)
taxa_plataforma = (df.groupby("plataforma")["viral"].mean() * 100).sort_values(ascending=False).reset_index()
fig = px.bar(taxa_plataforma, x="plataforma", y="viral", color="plataforma",
             color_discrete_map=CORES_PLATAFORMA, text_auto=".1f",
             labels={"plataforma": "", "viral": "% de publicações virais"})
fig.update_layout(template="plotly_white", showlegend=False, height=340, margin=dict(t=40, b=10),
                  title=dict(text="% de virais por plataforma", font_size=15))
col1.plotly_chart(fig, use_container_width=True)

taxa_conteudo = (df.groupby("tipo_conteudo")["viral"].mean() * 100).sort_values(ascending=False).reset_index()
fig = px.bar(taxa_conteudo, x="tipo_conteudo", y="viral", text_auto=".1f",
             labels={"tipo_conteudo": "", "viral": "% de publicações virais"})
fig.update_traces(marker_color=COR_PRINCIPAL)
fig.update_layout(template="plotly_white", height=340, margin=dict(t=40, b=10),
                  title=dict(text="% de virais por tipo de conteúdo", font_size=15))
col2.plotly_chart(fig, use_container_width=True)

st.markdown("**Top 10 publicações mais vistas**")
top10 = df.nlargest(10, "visualizacoes")[["data", "plataforma", "perfil", "tipo_conteudo",
                                           "horario_publicacao", "visualizacoes", "alcance", "taxa_engajamento"]]
st.dataframe(
    top10,
    use_container_width=True,
    hide_index=True,
    column_config={
        "data": st.column_config.DateColumn("Data", format="MM/YYYY"),
        "plataforma": "Plataforma",
        "perfil": "Perfil",
        "tipo_conteudo": "Formato",
        "horario_publicacao": "Horário",
        "visualizacoes": st.column_config.NumberColumn("Visualizações", format="%d"),
        "alcance": st.column_config.NumberColumn("Alcance", format="%d"),
        "taxa_engajamento": st.column_config.NumberColumn("Engajamento (%)", format="%.2f"),
    },
)
