import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (COR_PRINCIPAL, CORES_PLATAFORMA, formatar_compacto, formatar_correlacao, formatar_numero,
                   formatar_percentual, obter_dados_filtrados)

df = obter_dados_filtrados()

st.title("Horários e correlações")
st.write("Quando publicar, o que tem relação com o alcance e quais conteúdos viralizaram.")

# horários
st.subheader("Engajamento por horário")
tabela = df.pivot_table(index="horario_publicacao", columns="plataforma", values="taxa_engajamento",
                        aggfunc="mean")
fig = px.imshow(tabela, text_auto=".2f", color_continuous_scale="Blues", aspect="auto",
                labels={"x": "", "y": "Horário", "color": "Engajamento (%)"})
fig.update_layout(height=360, margin=dict(t=20, b=10))
st.plotly_chart(fig, width="stretch")

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
fig.update_layout(height=340, margin=dict(t=40, b=10), title=dict(text="Alcance médio por horário", font_size=15))
col1.plotly_chart(fig, width="stretch")

melhor_por_plataforma = tabela.idxmax().rename("Melhor horário").to_frame()
melhor_por_plataforma["Engajamento (%)"] = tabela.max().round(2)
col2.markdown("**Melhor horário em cada plataforma**")
col2.dataframe(melhor_por_plataforma, width="stretch")

melhor = por_horario.loc[por_horario["engajamento"].idxmax()]
maior_alcance = por_horario.loc[por_horario["alcance"].idxmax()]
st.info(
    f"No geral, quem publica às {melhor['horario_publicacao']} tem o maior engajamento médio "
    f"({formatar_percentual(melhor['engajamento'])}) e às {maior_alcance['horario_publicacao']} o maior alcance. "
    "Mas o melhor horário muda de uma plataforma pra outra (tabela ao lado), então faz mais sentido escolher "
    "o horário de cada rede separadamente."
)

if len(df) < 10:
    st.warning("Tem poucas publicações selecionadas pra calcular as correlações. Amplia os filtros pra ver o resto.")
    st.stop()

st.divider()

# seguidores x engajamento
st.subheader("Seguidores x engajamento")
correlacao = df["seguidores"].corr(df["taxa_engajamento"])

fig = px.scatter(df, x="seguidores", y="taxa_engajamento", color="plataforma", opacity=0.5,
                 color_discrete_map=CORES_PLATAFORMA,
                 hover_data={"perfil": True, "tipo_conteudo": True, "data": "|%m/%Y"},
                 labels={"seguidores": "Seguidores", "taxa_engajamento": "Taxa de engajamento (%)",
                         "plataforma": "Plataforma", "perfil": "Perfil", "tipo_conteudo": "Formato",
                         "data": "Data"})
fig.update_traces(marker_size=6)

# linha de tendência com regressão linear (numpy)
inclinacao, intercepto = np.polyfit(df["seguidores"], df["taxa_engajamento"], 1)
x_linha = np.array([df["seguidores"].min(), df["seguidores"].max()])
fig.add_trace(go.Scatter(x=x_linha, y=inclinacao * x_linha + intercepto, mode="lines",
                         name="Tendência", line=dict(color="#888888", width=3)))
fig.update_layout(height=450, margin=dict(t=20, b=10), separators=",.")
st.plotly_chart(fig, width="stretch")

col1, col2 = st.columns([1, 3])
col1.metric("Correlação de Pearson", formatar_correlacao(correlacao))
col2.info(
    "A correlação é praticamente zero e a linha de tendência fica quase reta. Ter mais seguidores "
    "não quer dizer ter uma taxa de engajamento maior."
)

# frequência x alcance
st.subheader("Frequência de postagem x alcance")
frequencia = df.groupby(["perfil", "ano_mes"]).agg(
    publicacoes=("alcance", "size"),
    alcance=("alcance", "mean"),
).reset_index()
correlacao_freq = frequencia["publicacoes"].corr(frequencia["alcance"])

fig = px.box(frequencia, x="publicacoes", y="alcance", points="all",
             labels={"publicacoes": "Publicações do perfil no mês", "alcance": "Alcance médio das publicações"})
fig.update_traces(marker_color=COR_PRINCIPAL, line_color=COR_PRINCIPAL)
fig.update_layout(height=400, margin=dict(t=20, b=10), separators=",.")
st.plotly_chart(fig, width="stretch")
st.write(
    f"Cada ponto é um perfil em um mês. A correlação entre a quantidade de publicações e o alcance médio é de "
    f"**{formatar_correlacao(correlacao_freq)}**, então postar mais vezes não aumentou o alcance de cada post."
)

# matriz de correlação
st.subheader("Correlação entre as métricas")
colunas = ["seguidores", "curtidas", "comentarios", "compartilhamentos", "visualizacoes", "alcance",
           "interacoes", "taxa_engajamento"]
matriz = df[colunas].corr().round(2)
fig = px.imshow(matriz, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
fig.update_layout(height=480, margin=dict(t=20, b=10))
st.plotly_chart(fig, width="stretch")

correlacoes_taxa = matriz["taxa_engajamento"].drop("taxa_engajamento").dropna()
if not correlacoes_taxa.empty:
    mais_forte = correlacoes_taxa.abs().idxmax()
    st.info(
        f"A métrica com maior correlação com a taxa de engajamento é {mais_forte}, e mesmo assim é só "
        f"{formatar_numero(correlacoes_taxa[mais_forte], 2)}. Nenhuma métrica sozinha explica o engajamento "
        "nessa base. A única correlação forte é entre interações e curtidas, mas isso é porque as curtidas "
        "entram na conta das interações."
    )

st.divider()

# conteúdos virais
st.subheader("Conteúdos virais")
st.write("Considerei como viral as 5% publicações com mais visualizações da base inteira.")

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
fig.update_layout(showlegend=False, height=340, margin=dict(t=40, b=10),
                  title=dict(text="% de virais por plataforma", font_size=15))
col1.plotly_chart(fig, width="stretch")

taxa_conteudo = (df.groupby("tipo_conteudo")["viral"].mean() * 100).sort_values(ascending=False).reset_index()
fig = px.bar(taxa_conteudo, x="tipo_conteudo", y="viral", text_auto=".1f",
             labels={"tipo_conteudo": "", "viral": "% de publicações virais"})
fig.update_traces(marker_color=COR_PRINCIPAL)
fig.update_layout(height=340, margin=dict(t=40, b=10),
                  title=dict(text="% de virais por tipo de conteúdo", font_size=15))
col2.plotly_chart(fig, width="stretch")

st.markdown("**Top 10 publicações mais vistas**")
top10 = df.nlargest(10, "visualizacoes")[["data", "plataforma", "perfil", "tipo_conteudo",
                                           "horario_publicacao", "visualizacoes", "alcance", "taxa_engajamento"]]
st.dataframe(
    top10,
    width="stretch",
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
