import streamlit as st

from utils import calcular_kpis, consultar, formatar_numero, formatar_percentual, obter_dados_filtrados

df = obter_dados_filtrados()

st.title("Dados e conclusão")

# ---------- tabela dinâmica ----------
st.subheader("Tabela dinâmica")
st.markdown("Monte a sua própria tabela escolhendo as linhas, as colunas e a métrica.")

dimensoes = {
    "Plataforma": "plataforma",
    "Perfil": "perfil",
    "Categoria": "categoria",
    "Tipo de conteúdo": "tipo_conteudo",
    "Horário": "horario_publicacao",
    "Ano": "ano",
    "Mês": "mes",
    "Trimestre": "trimestre",
}
valores = {
    "Taxa de engajamento (%)": "taxa_engajamento",
    "Seguidores": "seguidores",
    "Curtidas": "curtidas",
    "Comentários": "comentarios",
    "Compartilhamentos": "compartilhamentos",
    "Visualizações": "visualizacoes",
    "Alcance": "alcance",
    "Interações": "interacoes",
}
agregacoes = {"Média": "mean", "Soma": "sum", "Máximo": "max", "Mínimo": "min", "Contagem": "count"}

col1, col2, col3, col4 = st.columns(4)
linhas = col1.selectbox("Linhas", list(dimensoes.keys()), index=0)
opcoes_colunas = ["(nenhuma)"] + [d for d in dimensoes if d != linhas]
colunas = col2.selectbox("Colunas", opcoes_colunas, index=opcoes_colunas.index("Tipo de conteúdo"))
valor = col3.selectbox("Valor", list(valores.keys()))
agregacao = col4.selectbox("Cálculo", list(agregacoes.keys()))

tabela = df.pivot_table(
    index=dimensoes[linhas],
    columns=None if colunas == "(nenhuma)" else dimensoes[colunas],
    values=valores[valor],
    aggfunc=agregacoes[agregacao],
)
if colunas == "(nenhuma)":
    tabela.columns = [f"{agregacao} de {valor.lower()}"]

casas = 2 if valor.startswith("Taxa") and agregacao != "Contagem" else 0
st.dataframe(
    tabela.style.format(lambda v: formatar_numero(v, casas)).background_gradient(cmap="Blues", axis=None),
    use_container_width=True,
)

st.divider()

# ---------- consultas SQL ----------
st.subheader("Consultas ao banco de dados (SQLite + SQLAlchemy)")
st.markdown("Consultas SQL executadas diretamente no banco `database/redes_sociais.db`, sobre a base completa.")

consultas = {
    "Engajamento médio por plataforma": """
SELECT plataforma,
       COUNT(*) AS publicacoes,
       ROUND(AVG(taxa_engajamento), 2) AS engajamento_medio,
       SUM(visualizacoes) AS visualizacoes_totais
FROM publicacoes
GROUP BY plataforma
ORDER BY engajamento_medio DESC""",
    "Evolução anual": """
SELECT ano,
       ROUND(AVG(taxa_engajamento), 2) AS engajamento_medio,
       ROUND(AVG(seguidores)) AS seguidores_medios,
       SUM(visualizacoes) AS visualizacoes_totais
FROM publicacoes
GROUP BY ano
ORDER BY ano""",
    "Melhores combinações de perfil e formato": """
SELECT perfil,
       tipo_conteudo,
       COUNT(*) AS publicacoes,
       ROUND(AVG(taxa_engajamento), 2) AS engajamento_medio
FROM publicacoes
GROUP BY perfil, tipo_conteudo
ORDER BY engajamento_medio DESC
LIMIT 10""",
    "Publicações virais por plataforma": """
SELECT plataforma,
       SUM(viral) AS publicacoes_virais,
       ROUND(100.0 * SUM(viral) / COUNT(*), 1) AS percentual_viral
FROM publicacoes
GROUP BY plataforma
ORDER BY percentual_viral DESC""",
    "Engajamento por horário": """
SELECT horario_publicacao,
       ROUND(AVG(taxa_engajamento), 2) AS engajamento_medio,
       ROUND(AVG(alcance)) AS alcance_medio
FROM publicacoes
GROUP BY horario_publicacao
ORDER BY horario_publicacao""",
}

escolha = st.selectbox("Escolha uma consulta", list(consultas.keys()))
st.code(consultas[escolha].strip(), language="sql")
st.dataframe(consultar(consultas[escolha]), use_container_width=True, hide_index=True)

st.divider()

# ---------- dados filtrados ----------
st.subheader("Dados filtrados")
colunas_exibidas = ["data", "plataforma", "perfil", "categoria", "tipo_conteudo", "horario_publicacao",
                    "seguidores", "curtidas", "comentarios", "compartilhamentos", "visualizacoes",
                    "alcance", "taxa_engajamento", "viral"]
st.dataframe(df[colunas_exibidas], use_container_width=True, hide_index=True, height=350,
             column_config={"data": st.column_config.DateColumn("data", format="DD/MM/YYYY")})

csv = df[colunas_exibidas].to_csv(index=False).encode("utf-8-sig")
st.download_button("Baixar dados filtrados (CSV)", csv, file_name="redes_sociais_filtrado.csv",
                   mime="text/csv")

st.divider()

# ---------- conclusão executiva ----------
st.subheader("Conclusão executiva")
kpis = calcular_kpis(df)
engajamento_plataforma = df.groupby("plataforma")["taxa_engajamento"].mean()
amplitude = engajamento_plataforma.max() - engajamento_plataforma.min()

st.markdown(
    f"""
- **Engajamento estável:** a taxa média é de **{formatar_percentual(kpis['engajamento_medio'])}** e quase não muda
  ao longo dos anos.
- **Plataformas parecidas:** **{kpis['plataforma_top']}** lidera, mas a diferença entre a melhor e a pior
  plataforma é de só **{formatar_numero(amplitude, 2)} ponto percentual**.
- **Formato e horário:** **{kpis['conteudo_maior_alcance']}** tem o maior alcance médio e as
  **{kpis['melhor_horario']}** é o horário com maior engajamento, mas o melhor horário varia por plataforma.
- **Seguidores e frequência não garantem resultado:** não há correlação entre seguidores e engajamento,
  nem entre quantidade de publicações e alcance.
- **Base simulada:** os dados foram gerados de forma aleatória, por isso as diferenças são pequenas.
  O principal aprendizado é não tomar decisões com base em diferenças mínimas sem testar antes.

**Recomendações:** testar (A/B) as combinações de perfil e formato com melhor desempenho, definir horários
por plataforma, acompanhar engajamento e alcance além dos seguidores e, em dados reais, incluir informações
de campanha e investimento para medir o retorno.
"""
)
