from flask import Blueprint, jsonify, request
from threading import Lock
import os
import json
import logging
import subprocess
import threading
import uuid
from meilisearch import Client


routes_bp = Blueprint("routes", __name__)

spider_lock = Lock()
spider_running = False
socketio = None  # Inicialização será feita em app.py

# Configura o cliente Meilisearch
MEILISEARCH_URL = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
MEILISEARCH_API_KEY = os.getenv("MEILISEARCH_API_KEY", "masterKey")
client = Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
INDEX_NAME = "convenios"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def init_socketio(sockio_instance):
    global socketio
    socketio = sockio_instance

@routes_bp.route("/scrape", methods=["POST"])
def scrape_data():
    global spider_running
    with spider_lock:
        if spider_running:
            return jsonify({"ok": False, "message": "Scraping já em andamento"}), 400
        spider_running = True

    def run_scrapy():
        def process_convenios():
            def configure_meilisearch_index():
                """Configura o índice Meilisearch."""
                try:
                    # Configurar o índice
                    index = client.index(INDEX_NAME)
                    
                    # Definir atributos de ordenação
                    index.update_sortable_attributes(["date", "title", "cats"])
                    
                    # Definir atributos de filtragem
                    index.update_filterable_attributes(["cats"])
                    
                    print(f"Atributos de ordenação configurados com sucesso para o índice '{INDEX_NAME}'.")

                except Exception as e:
                    print(f"Erro ao configurar o índice Meilisearch: {e}")
            """Processa os convênios do arquivo JSON e indexa no Meilisearch."""
            try:
                # Caminho para o arquivo JSON
                json_path = os.path.join(os.getcwd(), "myspider_project", "output", "convenios.json")
            
                if not os.path.exists(json_path):
                    logging.error("[Flask] Arquivo JSON não encontrado")
                    return {"ok": False, "message": "Arquivo JSON não encontrado"}

                # Lê os convênios do arquivo JSON
                with open(json_path, "r", encoding="utf-8") as f:
                    convenios = json.load(f)

                # Garante que o índice existe
                try:
                    client.create_index(INDEX_NAME, {"primaryKey": "id"})
                except Exception:
                    logging.info(f"[Flask] Índice '{INDEX_NAME}' já existe")
                    
                client.index(INDEX_NAME).delete_all_documents()
                
                # Adiciona um UUID único para cada convênio e indexa no Meilisearch
                for convenio in convenios:
                    convenio["id"] = str(uuid.uuid4())

                client.index(INDEX_NAME).add_documents(convenios)
                configure_meilisearch_index()
                
                logging.info("[Flask] Documentos processados e indexados com sucesso no Meilisearch.")

                os.remove(json_path)  # Opcional: Remove o arquivo após o processamento
                return {"ok": True, "message": "Dados processados e indexados com sucesso"}
            except Exception as e:
                logging.error(f"[Flask] Erro ao processar convênios: {str(e)}")
                return {"ok": False, "message": f"Erro: {str(e)}"}
            
        try:
            json_path = os.path.join(os.getcwd(), "myspider_project", "output", "convenios.json")
            if os.path.exists(json_path):
                os.remove(json_path)

            scrapy_project_dir = os.path.join(os.getcwd(), "myspider_project")

            logging.info("[Flask] Executando Scrapy...")
            process = subprocess.Popen(
                ["scrapy", "crawl", "convenio_spider"],
                cwd=scrapy_project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                if socketio:
                    socketio.emit('scrapy_progress', {'message': line.strip()})
                logging.info(line.strip())

            process.wait()
            if process.returncode != 0:
                if socketio:
                    socketio.emit('scrapy_error', {'message': "Erro ao executar Scrapy"})
                logging.error("[Flask] Erro ao executar Scrapy.")
            else:
                process_convenios()
                if socketio:
                    socketio.emit('scrapy_done', {'message': "Scraping concluído com sucesso"})

        except Exception as e:
            if socketio:
                socketio.emit('scrapy_error', {'message': str(e)})
            logging.error(f"[Flask] Erro: {str(e)}")
        finally:
            global spider_running
            spider_running = False

    thread = threading.Thread(target=run_scrapy)
    thread.start()

    return jsonify({"ok": True, "message": "Scraping iniciado"}), 200
@routes_bp.route("/convenios", methods=["GET"])
def get_convenios():
    index = client.index(INDEX_NAME)

    # Parâmetros da requisição
    search_text = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    sort_by = request.args.get("sort_by", "title").strip()  # Campo padrão: título
    order = request.args.get("order", "asc").strip()  # Ordem padrão: ascendente
    category = request.args.get("category", "").strip()

    # Configuração do filtro e ordenação
    filters = []
    if category:
        filters.append(f"cats = '{category}'")

    sort = [f"{sort_by}:{order}"] if sort_by else None

    # Busca principal
    try:
        search_result = index.search(
            search_text,
            {
                "limit": page_size,
                "offset": (page - 1) * page_size,
                "filter": " AND ".join(filters) if filters else None,
                "sort": sort,
                "attributesToHighlight": ["title", "content", "discounts"],  # Adicione os campos que deseja destacar
                "highlightPreTag": "<em>",  # Tag usada para abrir o destaque
                "highlightPostTag": "</em>",  # Tag usada para fechar o destaque
            },
        )

        total_items = search_result.get("estimatedTotalHits", 0)
        total_pages = (total_items // page_size) + (1 if total_items % page_size else 0)

        # Sugestões para autocompletar
        suggestions = []
        if search_text:
            suggestion_result = index.search(
                search_text,
                {
                    "limit": 5,
                    "attributesToRetrieve": ["id", "title"],
                },
            )
            suggestions = [
                {"id": item["id"], "title": item["title"]}
                for item in suggestion_result.get("hits", [])
            ]

        # Retorno final com os highlights
        return jsonify({
            "data": [
                {
                    **item,
                    "title_highlight": item["_formatted"].get("title", item.get("title")),
                    "content_highlight": item["_formatted"].get("content", item.get("content")),
                    "discounts_highlight": item["_formatted"].get("discounts", item.get("discounts")),
                }
                for item in search_result.get("hits", [])
            ],
            "suggestions": suggestions,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        })

    except Exception as e:
        logging.error(f"[Flask] Erro ao buscar convênios: {str(e)}")
        return jsonify({"ok": False, "data": [], "message": f"Erro ao buscar convênios: {str(e)}"}), 500
    
@routes_bp.route("/get_categories", methods=["GET"])
def get_categories():
    try:
        index = client.index(INDEX_NAME)
        # Recupera todas as categorias existentes
        search_result = index.search("", {"attributesToRetrieve": ["cats"], "limit": 1000})
        categories = set()
        for hit in search_result.get("hits", []):
            if "cats" in hit and hit["cats"]:
                categories.update([cat.strip() for cat in hit["cats"].split(",")])

        return jsonify(sorted(categories))

    except Exception as e:
        logging.error(f"[Flask] Erro ao buscar categorias: {str(e)}")
        return jsonify([])
    

@routes_bp.route("/convenio/<id>", methods=["GET"])
def get_convenio_by_id(id):
    try:
        index = client.index(INDEX_NAME)

        # Busca o documento pelo ID
        convenio = index.get_document(id)
        
        # Converte o objeto para um dicionário se necessário
        convenio_dict = dict(convenio) if not isinstance(convenio, dict) else convenio
        
        return jsonify(convenio_dict)

    except Exception as e:
        logging.error(f"[Flask] Erro ao buscar convênio por ID '{id}': {str(e)}")
        return jsonify({"ok": False, "message": "Convênio não encontrado"}), 404