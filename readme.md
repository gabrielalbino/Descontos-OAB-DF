# Projeto: Flask + Scrapy + SQLite (FTS) + PySimpleGUI

Este projeto demonstra:

- **Scrapy** coletando convênios do site [CAADF](https://www.caadf.org.br/category/convenios/).
- **Flask** expondo endpoints de scraping, progresso, e busca paginada/filtrada.
- **SQLite** com FTS5 para busca avançada.
- **PySimpleGUI** como interface para interagir com a API.

## Estrutura
meu_projeto/
├── server/
│   ├── init.py
│   ├── app.py
│   ├── routes.py
│   ├── spider.py
│   ├── progress.py
│   └── database.py
├── gui/
│   └── main_gui.py
├── requirements.txt
└── README.md

1. **server/** - Contém a aplicação Flask, o spider, banco de dados e progress.
2. **gui/** - Contém a aplicação PySimpleGUI para interface desktop.

## Como usar

1. **Instale as dependências**:

  ```bash
  pip install -r requirements.txt
  ````

2.	Execute a GUI (que iniciará o Flask em background):

```
python gui/main_gui.py
```

  3.	Na janela PySimpleGUI:
•	Clique em “Iniciar Scraping” para começar a coleta em background.
•	Clique em “Ver Progresso” para acompanhar pages_crawled, items_scraped, etc.
•	Use “Busca” e “Categoria”, e ajuste “Página” / “Tamanho de Página”.
Então clique em “Buscar Convênios” para ver resultados paginados.
4.	A API Flask estará em http://127.0.0.1:5001, com endpoints:
•	POST /scrape: Inicia scraping (se não estiver rodando).
•	GET /progress: Retorna status.
•	GET /convenios?search=...&cat=...&page=1&page_size=10: Busca paginada.

Observações
•	Em produção, recomenda-se rodar o Flask em um processo dedicado (Gunicorn/UWSGI, etc.) e o spider em outro (Scrapy standalone ou scrapydo via scripts).
•	Este exemplo é didático e agrupa as lógicas para mostrar como integrar tudo.
•	Ajuste os seletores CSS no spider caso o layout do site mude.
•	Ajuste a sintaxe FTS para buscas mais avançadas (coringas, etc.).

---

## Execução

1. **Instalar dependências**:
  ```bash
  pip install -r requirements.txt
  ```

  	3.	Interagir conforme explicado no README.

Pronto! Você tem um exemplo separado em arquivos para produção, com:
	•	Busca paginada (page, page_size).
	•	Filtro por categoria (cat).
	•	Busca textual (search), usando FTS5 no SQLite.
	•	Controle para não iniciar mais de um scraping ao mesmo tempo.
	•	GUI em PySimpleGUI que consome os endpoints do Flask.