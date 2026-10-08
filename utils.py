from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

PASTA_PROJETO = Path(__file__).parent
CAMINHO_CSV = PASTA_PROJETO / "dados" / "simulacao_redes_sociais_brasil.csv"
CAMINHO_BANCO = PASTA_PROJETO / "database" / "redes_sociais.db"

# mesmas cores do notebook
CORES_PLATAFORMA = {
    "Facebook": "#2a78d6",
    "Instagram": "#eb6834",
    "LinkedIn": "#1baf7a",
    "TikTok": "#eda100",
    "X": "#e87ba4",
    "YouTube": "#008300",
}
CORES_PERFIL = {
    "EducaOnline": "#2a78d6",
    "GamesBR": "#eb6834",
    "ModaHoje": "#1baf7a",
    "TechBrasil": "#e87ba4",
}
COR_PRINCIPAL = "#2a78d6"

NOMES_MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
               7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

# nome que aparece na tela: (coluna, agregação)
METRICAS = {
    "Taxa média de engajamento (%)": ("taxa_engajamento", "mean"),
    "Alcance médio": ("alcance", "mean"),
    "Visualizações totais": ("visualizacoes", "sum"),
    "Interações totais": ("interacoes", "sum"),
    "Número de publicações": ("taxa_engajamento", "count"),
}


@st.cache_resource
def obter_engine():
    return create_engine(f"sqlite:///{CAMINHO_BANCO}")


# mesmo tratamento do notebook, usado só se o banco não existir
def preparar_base(df):
    df = df.copy()
    df["hora"] = df["horario_publicacao"].str[:2].astype(int)
    df["interacoes"] = df["curtidas"] + df["comentarios"] + df["compartilhamentos"]
    df["inconsistente"] = df["interacoes"] > df["alcance"]
    df["trimestre"] = pd.to_datetime(df["data"]).dt.quarter
    df["ano_mes"] = df["data"].str[:7]
    df["nome_mes"] = df["mes"].map(NOMES_MESES)
    df["viral"] = df["visualizacoes"] >= df["visualizacoes"].quantile(0.95)
    return df


def criar_banco(engine):
    df = pd.read_csv(CAMINHO_CSV, encoding="utf-8-sig")
    df = preparar_base(df)
    CAMINHO_BANCO.parent.mkdir(exist_ok=True)
    df.to_sql("publicacoes", engine, if_exists="replace", index=False)


@st.cache_data
def carregar_dados():
    if not CAMINHO_BANCO.exists():
        criar_banco(obter_engine())

    df = pd.read_sql("SELECT * FROM publicacoes", obter_engine())
    df["data"] = pd.to_datetime(df["data"])
    df["viral"] = df["viral"].astype(bool)
    df["inconsistente"] = df["inconsistente"].astype(bool)
    return df


def consultar(sql):
    return pd.read_sql(sql, obter_engine())


def aplicar_filtros(df):
    st.sidebar.header("Filtros")

    ano_min, ano_max = int(df["ano"].min()), int(df["ano"].max())
    anos = st.sidebar.slider("Ano", ano_min, ano_max, (ano_min, ano_max), key="filtro_ano")

    todos_meses = list(NOMES_MESES.values())
    meses = st.sidebar.multiselect("Mês", todos_meses, default=todos_meses, key="filtro_mes")

    plataformas = sorted(df["plataforma"].unique())
    plataformas = st.sidebar.multiselect("Plataforma", plataformas, default=plataformas, key="filtro_plataforma")

    categorias = sorted(df["categoria"].unique())
    categorias = st.sidebar.multiselect("Categoria", categorias, default=categorias, key="filtro_categoria")

    tipos = sorted(df["tipo_conteudo"].unique())
    tipos = st.sidebar.multiselect("Tipo de conteúdo", tipos, default=tipos, key="filtro_tipo")

    perfis = sorted(df["perfil"].unique())
    perfis = st.sidebar.multiselect("Perfil", perfis, default=perfis, key="filtro_perfil")

    filtro = (
        df["ano"].between(anos[0], anos[1])
        & df["nome_mes"].isin(meses)
        & df["plataforma"].isin(plataformas)
        & df["categoria"].isin(categorias)
        & df["tipo_conteudo"].isin(tipos)
        & df["perfil"].isin(perfis)
    )
    df_filtrado = df[filtro]

    st.sidebar.caption(f"{formatar_numero(len(df_filtrado))} de {formatar_numero(len(df))} publicações")
    return df_filtrado


# as páginas pegam a base já filtrada no app.py
def obter_dados_filtrados():
    df = st.session_state.get("df_filtrado")
    if df is None or df.empty:
        st.warning("Nenhuma publicação com esses filtros. Muda alguma opção na barra lateral.")
        st.stop()
    return df


def formatar_numero(valor, casas=0):
    # 1,234.5 -> 1.234,5
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_compacto(valor):
    if valor >= 1_000_000_000:
        return f"{formatar_numero(valor / 1_000_000_000, 2)} bi"
    if valor >= 1_000_000:
        return f"{formatar_numero(valor / 1_000_000, 2)} mi"
    if valor >= 1_000:
        return f"{formatar_numero(valor / 1_000, 1)} mil"
    return formatar_numero(valor)


def formatar_percentual(valor, casas=2):
    return f"{formatar_numero(valor, casas)}%"


def formatar_correlacao(valor):
    if pd.isna(valor):
        return "-"
    return formatar_numero(valor, 3)


def calcular_kpis(df):
    eng_plataforma = df.groupby("plataforma")["taxa_engajamento"].mean()
    alcance_conteudo = df.groupby("tipo_conteudo")["alcance"].mean()
    eng_horario = df.groupby("horario_publicacao")["taxa_engajamento"].mean()

    return {
        "total_seguidores": df["seguidores"].sum(),
        "media_seguidores": df["seguidores"].mean(),
        "engajamento_medio": df["taxa_engajamento"].mean(),
        "plataforma_top": eng_plataforma.idxmax(),
        "plataforma_top_valor": eng_plataforma.max(),
        "conteudo_maior_alcance": alcance_conteudo.idxmax(),
        "conteudo_maior_alcance_valor": alcance_conteudo.max(),
        "total_visualizacoes": df["visualizacoes"].sum(),
        "melhor_horario": eng_horario.idxmax(),
        "melhor_horario_valor": eng_horario.max(),
    }


def agrupar(df, coluna, metrica):
    nome_coluna, agregacao = METRICAS[metrica]
    resultado = df.groupby(coluna)[nome_coluna].agg(agregacao).reset_index(name="valor")
    return resultado.sort_values("valor", ascending=False)


def formatar_metrica(valor, metrica):
    if "%" in metrica:
        return formatar_percentual(valor)
    return formatar_compacto(valor)
