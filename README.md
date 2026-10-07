# Análise de Engajamento em Redes Sociais

Projeto de análise e visualização de dados sobre engajamento digital em redes sociais (2015–2024), desenvolvido para a avaliação G1 da disciplina **Linguagem de Programação: Análise e Visualização de Dados com Python** (Tema 20).

## Links

| O quê | Link |
|---|---|
| Página do projeto (GitHub Pages) | https://m4rc3l07969.github.io/analise-engajamento-redes-sociais/ |
| Dashboard (Streamlit Cloud) | _em breve_ |
| Notebook de análise | [`notebooks/`](notebooks/) |

## Perguntas orientadoras

- Quais plataformas apresentam maior engajamento?
- Quais tipos de conteúdo têm melhor desempenho?
- Existem horários mais favoráveis para publicar?
- Como o número de seguidores evoluiu ao longo do tempo?
- Existe relação entre frequência de postagem e alcance?
- Quais métricas são mais relevantes para o engajamento?

## Base de dados

`dados/simulacao_redes_sociais_brasil.csv`: base simulada fornecida pelo professor, com 4.440 registros e 15 colunas (ano, mês, data, plataforma, perfil, categoria, tipo de conteúdo, seguidores, curtidas, comentários, compartilhamentos, visualizações, alcance, taxa de engajamento e horário de publicação).

## Estrutura

```
analise-engajamento-redes-sociais/
├── app.py              # dashboard Streamlit
├── requirements.txt    # dependências
├── README.md
├── index.html          # página do projeto (GitHub Pages)
├── dados/              # base CSV
├── database/           # banco SQLite
├── notebooks/          # notebook de análise (.ipynb)
└── imagens/            # gráficos exportados
```

## Tecnologias

Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit, SQLAlchemy + SQLite, GitHub e GitHub Pages.

## Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app.py
```

## Autor

Marcelo de Moura Maia Júnior
