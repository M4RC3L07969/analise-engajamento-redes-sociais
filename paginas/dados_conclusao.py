import streamlit as st

from utils import calcular_kpis, consultar, formatar_numero, formatar_percentual, obter_dados_filtrados

df = obter_dados_filtrados()

st.title("Dados e conclusão")

# tabela dinâmica
st.subheader("Tabela dinâmica")
st.write("Escolha o que vai nas linhas, nas colunas e qual métrica calcular.")

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
    width="stretch",
)

st.divider()

# consultas SQL
st.subheader("Consultas no banco de dados (SQLite + SQLAlchemy)")
st.write("Consultas SQL feitas direto no banco `database/redes_sociais.db`, com a base completa (sem os filtros).")

consultas = {
    "Engajamento médio por plataforma": """
SELECT plataforma,
       COUNT(*) AS publicacoes,
       ROUND(AVG(taxa_engajamento), 2) AS engajamento_medio,
       SUM(visualizacoes) AS visualizacoes_totais
FROM publicacoes
GROUP BY plataforma
ORDER BY engajamento_medio DESC""",
    "Evolução por ano": """
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

escolha = st.selectbox("Consulta", list(consultas.keys()))
st.code(consultas[escolha].strip(), language="sql")
st.dataframe(consultar(consultas[escolha]), width="stretch", hide_index=True)

st.divider()

# dados filtrados
st.subheader("Dados filtrados")
colunas_exibidas = ["data", "plataforma", "perfil", "categoria", "tipo_conteudo", "horario_publicacao",
                    "seguidores", "curtidas", "comentarios", "compartilhamentos", "visualizacoes",
                    "alcance", "taxa_engajamento", "viral"]
st.dataframe(df[colunas_exibidas], width="stretch", hide_index=True, height=350,
             column_config={"data": st.column_config.DateColumn("data", format="DD/MM/YYYY")})

csv = df[colunas_exibidas].to_csv(index=False).encode("utf-8-sig")
st.download_button("Baixar dados filtrados (CSV)", csv, file_name="redes_sociais_filtrado.csv", mime="text/csv")

st.divider()

# conclusão
st.subheader("Conclusão")
kpis = calcular_kpis(df)
eng_plataforma = df.groupby("plataforma")["taxa_engajamento"].mean()
amplitude = eng_plataforma.max() - eng_plataforma.min()

st.markdown(
    f"""
- A taxa média de engajamento é de {formatar_percentual(kpis['engajamento_medio'])} e quase não muda de um ano
  pro outro.
- O {kpis['plataforma_top']} é a plataforma com mais engajamento, mas a diferença entre a melhor e a pior é de só
  {formatar_numero(amplitude, 2)} ponto percentual.
- {kpis['conteudo_maior_alcance']} é o formato com maior alcance médio e {kpis['melhor_horario']} é o horário com
  mais engajamento, mas o melhor horário muda conforme a plataforma.
- Não tem correlação entre seguidores e engajamento, nem entre quantidade de posts e alcance.
- Como a base é simulada com valores aleatórios, as diferenças são pequenas. O principal aprendizado é não
  tomar decisão em cima de diferenças tão pequenas sem testar antes.

**Recomendações:** testar (teste A/B) as combinações de perfil e formato que foram melhor, escolher o horário de
cada plataforma separado, acompanhar engajamento e alcance e não só seguidores e, com dados reais, incluir
informações de campanha e investimento pra medir o retorno.
"""
)
