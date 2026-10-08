# Análise de Engajamento em Redes Sociais

Projeto de análise e visualização de dados sobre engajamento digital em redes sociais (2015–2024), desenvolvido para a avaliação G1 da disciplina **Linguagem de Programação: Análise e Visualização de Dados com Python** (Tema 20).

## Links

| O quê | Link |
|---|---|
| Página do projeto (GitHub Pages) | https://m4rc3l07969.github.io/analise-engajamento-redes-sociais/ |
| Dashboard (Streamlit Cloud) | https://engajamento-redes-sociais.streamlit.app |
| Notebook de análise | [`notebooks/analise_redes_sociais.ipynb`](notebooks/analise_redes_sociais.ipynb) |

## Perguntas orientadoras

- Quais plataformas apresentam maior engajamento?
- Quais tipos de conteúdo têm melhor desempenho?
- Existem horários mais favoráveis para publicar?
- Como o número de seguidores evoluiu ao longo do tempo?
- Existe relação entre frequência de postagem e alcance?
- Quais campanhas apresentaram melhores resultados?
- Quais métricas são mais relevantes para o engajamento?

## Base de dados

`dados/simulacao_redes_sociais_brasil.csv`: base simulada fornecida pelo professor, com 4.440 registros e 15 colunas (ano, mês, data, plataforma, perfil, categoria, tipo de conteúdo, seguidores, curtidas, comentários, compartilhamentos, visualizações, alcance, taxa de engajamento e horário de publicação).

Depois do tratamento feito no notebook, a base é gravada no banco SQLite `database/redes_sociais.db` (tabela `publicacoes`), que é lido pelo dashboard com SQLAlchemy.

## Principais resultados

- Taxa média de engajamento de **6,24%**, estável entre 2015 e 2024.
- **LinkedIn** é a plataforma com maior engajamento médio (6,32%), mas a diferença para a última colocada é de só 0,15 ponto percentual.
- **Live** é o formato com maior alcance médio e **21:00** o horário com maior engajamento. O melhor horário, porém, muda de plataforma para plataforma.
- Não há correlação entre seguidores e engajamento, nem entre frequência de postagem e alcance.
- A melhor combinação de perfil e formato foi **ModaHoje + Vídeo** (6,76%).

## Dashboard

O dashboard tem quatro páginas e filtros por ano, mês, plataforma, categoria, tipo de conteúdo e perfil:

- **Visão geral:** descrição do problema, KPIs dinâmicos e evolução do engajamento e dos seguidores
- **Plataformas e conteúdo:** comparações entre plataformas e formatos, ranking de perfis e melhores campanhas
- **Horários e correlações:** heatmap de horários, dispersão seguidores x engajamento, frequência x alcance, matriz de correlação e conteúdos virais
- **Dados e conclusão:** tabela dinâmica, consultas SQL no banco, download dos dados filtrados e conclusão executiva

## Estrutura

```
analise-engajamento-redes-sociais/
├── app.py              # dashboard Streamlit (navegação e filtros)
├── utils.py            # funções de carga dos dados, filtros e KPIs
├── paginas/            # páginas do dashboard
├── requirements.txt    # dependências
├── README.md
├── index.html          # página do projeto (GitHub Pages)
├── dados/              # base CSV
├── database/           # banco SQLite
├── notebooks/          # notebook de análise (.ipynb)
└── imagens/            # gráficos exportados pelo notebook
```

## Tecnologias

Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit, SQLAlchemy + SQLite, GitHub, GitHub Pages e Streamlit Community Cloud.

## Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app.py
```

Para abrir o notebook: `pip install notebook` e depois `jupyter notebook notebooks/analise_redes_sociais.ipynb`.

## Autor

Marcelo de Moura Maia Júnior
