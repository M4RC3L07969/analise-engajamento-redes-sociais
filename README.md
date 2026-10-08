# Análise de Engajamento em Redes Sociais

Projeto da G1 de Linguagem de Programação (Análise e Visualização de Dados com Python), tema 20: Redes Sociais e Engajamento Digital.

A ideia é analisar publicações de 2015 a 2024 e ver quais plataformas, formatos e horários dão mais engajamento, como os seguidores evoluíram e quais métricas importam mais.

## Links

- Página do projeto: https://m4rc3l07969.github.io/analise-engajamento-redes-sociais/
- Dashboard: https://engajamento-redes-sociais.streamlit.app
- Notebook: [notebooks/analise_redes_sociais.ipynb](notebooks/analise_redes_sociais.ipynb)

## Base de dados

`dados/simulacao_redes_sociais_brasil.csv`, a base simulada que o professor passou (4.440 linhas e 15 colunas: ano, mês, data, plataforma, perfil, categoria, tipo de conteúdo, seguidores, curtidas, comentários, compartilhamentos, visualizações, alcance, taxa de engajamento e horário).

Depois do tratamento no notebook, os dados são salvos no banco SQLite `database/redes_sociais.db` (tabela `publicacoes`), que é de onde o dashboard lê usando SQLAlchemy.

## O que tem no projeto

**Notebook:** leitura e limpeza dos dados, criação de colunas novas, KPIs, gráficos com Matplotlib e Seaborn, interpretação e conclusão. Os gráficos ficam salvos na pasta `imagens/`.

**Dashboard (Streamlit + Plotly):** 4 páginas (Visão geral, Plataformas e conteúdo, Horários e correlações, Dados e conclusão), filtros por ano, mês, plataforma, categoria, tipo de conteúdo e perfil, KPIs que mudam com os filtros, tabela dinâmica, consultas SQL no banco e download dos dados filtrados.

## Resultados principais

- Taxa média de engajamento de 6,24%, bem estável de 2015 a 2024
- LinkedIn tem o maior engajamento (6,32%), mas a diferença pro último é só 0,15 ponto percentual
- Live tem o maior alcance médio e 21h é o horário com mais engajamento, mas o melhor horário muda por plataforma
- Não tem correlação entre seguidores e engajamento nem entre frequência de postagem e alcance
- Melhor combinação de perfil e formato: ModaHoje + Vídeo (6,76%)

Como a base é simulada com valores aleatórios, as diferenças são pequenas mesmo.

## Estrutura

```
analise-engajamento-redes-sociais/
├── app.py              # dashboard (navegação e filtros)
├── utils.py            # funções de carregar dados, filtros e KPIs
├── paginas/            # páginas do dashboard
├── requirements.txt
├── README.md
├── index.html          # página do projeto (GitHub Pages)
├── dados/              # CSV
├── database/           # banco SQLite
├── notebooks/          # notebook de análise
└── imagens/            # gráficos do notebook
```

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Pra abrir o notebook: `pip install notebook` e `jupyter notebook notebooks/analise_redes_sociais.ipynb`.

## Tecnologias

Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit, SQLAlchemy, SQLite, GitHub Pages e Streamlit Community Cloud.

---

Marcelo de Moura Maia Júnior
