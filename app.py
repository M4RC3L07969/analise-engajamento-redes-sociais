import streamlit as st

from utils import aplicar_filtros, carregar_dados

st.set_page_config(page_title="Engajamento em Redes Sociais", page_icon="📊", layout="wide")

df = carregar_dados()
st.session_state["df_completo"] = df
st.session_state["df_filtrado"] = aplicar_filtros(df)

pagina = st.navigation([
    st.Page("paginas/visao_geral.py", title="Visão geral", icon=":material/dashboard:", default=True),
    st.Page("paginas/plataformas_conteudo.py", title="Plataformas e conteúdo", icon=":material/bar_chart:"),
    st.Page("paginas/horarios_tendencias.py", title="Horários e correlações", icon=":material/schedule:"),
    st.Page("paginas/dados_conclusao.py", title="Dados e conclusão", icon=":material/table_chart:"),
])

st.caption(
    "**Nome:** Marcelo de Moura Maia Júnior  |  "
    "**Professor:** Alexandre Neves Louzada  |  "
    "**Matéria:** Linguagens de Programação  |  "
    "Projeto G1 - Análise e Visualização de Dados com Python"
)

pagina.run()