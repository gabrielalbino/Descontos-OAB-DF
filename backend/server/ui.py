# server/ui.py

import justpy as jp
import requests
import asyncio

# URL da API Flask
API_URL = "http://127.0.0.1:5001"

# Página principal com tabela e botão de scraping
def convenios_table():
    wp = jp.QuasarPage(tailwind=True)

    # Cabeçalho
    jp.Div(text="Convênios (Scrapy + Flask + JustPy)", classes="text-2xl m-2", a=wp)

    # Barra de filtros
    filter_div = jp.Div(classes="flex space-x-2 items-center", a=wp)
    search_label = jp.Span(text="Busca:", classes="font-bold", a=filter_div)
    search_input = jp.Input(value="", placeholder="Texto para buscar", classes="q-input q-mb-sm", a=filter_div)
    cat_label = jp.Span(text="Categoria:", classes="font-bold", a=filter_div)
    cat_input = jp.Input(value="", placeholder="Categoria (ex: Tributário)", classes="q-input", a=filter_div)

    page_label = jp.Span(text="Página:", classes="font-bold", a=filter_div)
    page_input = jp.Input(value="1", classes="q-input w-16", a=filter_div)

    # Botões para filtros
    update_btn = jp.Button(text="Buscar", classes="q-btn q-btn-outline", a=filter_div)

    # Botão para iniciar o scraping
    scrape_btn = jp.Button(text="Iniciar Scraping", classes="q-btn q-btn-primary", a=filter_div)

    # Seção de progresso
    progress_div = jp.Div(classes="q-my-md", a=wp)
    progress_label = jp.Div(text="Progresso: ", classes="text-lg", a=progress_div)
    progress_bar = jp.QLinearProgress(value=0, max=100, color="blue", size="20px", a=progress_div)

    # Tabela Quasar
    table = jp.QTable(a=wp,
                      title="Tabela de Convênios",
                      wrap_cells=True,
                      pagination={"rowsPerPage": 5},
                      classes="q-ma-md",
                      row_key="id")

    # Definição das colunas da tabela
    table.cols = [
        {"name": "id", "label": "ID", "field": "id", "sortable": True},
        {"name": "title", "label": "Título", "field": "title", "sortable": True},
        {"name": "date", "label": "Data", "field": "date", "sortable": True},
        {"name": "cats", "label": "Categorias", "field": "cats", "sortable": False},
        {"name": "content", "label": "Conteúdo", "field": "content", "sortable": False}
    ]

    # Função para buscar dados na API e atualizar a tabela
    async def update_table(self, msg):
        params = {
            "search": search_input.value.strip(),
            "cat": cat_input.value.strip(),
            "page": page_input.value.strip(),
            "page_size": 50
        }
        try:
            r = requests.get(f"{API_URL}/convenios", params=params)
            data = r.json()
            table_data = data["data"]
            table.data = table_data
        except Exception as e:
            table.data = []
            print("Erro ao buscar convênios:", e)

    update_btn.on("click", update_table)

    # Função para iniciar o scraping
    async def start_scraping(self, msg):
        try:
            r = requests.post(f"{API_URL}/scrape")
            result = r.json()
            if result.get("ok"):
                progress_label.text = "Progresso: Iniciando scraping..."
                progress_bar.value = 0
                await monitor_progress()
            else:
                progress_label.text = f"Erro: {result.get('message')}"
        except Exception as e:
            progress_label.text = f"Erro ao iniciar scraping: {e}"

    scrape_btn.on("click", start_scraping)

    # Função para monitorar o progresso em tempo quase real
    async def monitor_progress():
        while True:
            try:
                r = requests.get(f"{API_URL}/progress")
                data = r.json()
                total_items = max(data.get("pages_crawled", 1), 1)  # Evitar divisão por zero
                progress_bar.value = (data.get("items_scraped", 0) / total_items) * 100
                progress_label.text = (f"Progresso: {data.get('items_scraped', 0)} itens coletados "
                                       f"de {data.get('pages_crawled', 0)} páginas.")
                if data.get("finished"):
                    progress_label.text += " Scraping concluído!"
                    break
                await asyncio.sleep(2)  # Atualiza a cada 2 segundos
            except Exception as e:
                progress_label.text = f"Erro ao monitorar progresso: {e}"
                break

    return wp