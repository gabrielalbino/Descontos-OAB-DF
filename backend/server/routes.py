from flask import Blueprint, jsonify, request
from threading import Lock
import os
import json
import logging
import subprocess
import threading
from server.database import search_convenios, count_convenios, insert_convenio, get_all_convenios, clear_convenios, get_unique_cats,find_convenio_by_id, get_convenios_by_cat
import uuid


routes_bp = Blueprint("routes", __name__)

spider_lock = Lock()
spider_running = False
socketio = None  # Inicialização será feita em app.py

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
    search_text = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    sort_by = request.args.get("sort_by", "title").strip()  # Campo padrão: título
    order = request.args.get("order", "asc").strip()  # Ordem padrão: ascendente
    category = request.args.get("category", "").strip()

    convenios = search_convenios(
        search_text=search_text if search_text else None,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        cat=category if category else None
    )

    total_items = count_convenios(search_text=search_text if search_text else None, cat=category if category else None)
    total_pages = (total_items // page_size) + (1 if total_items % page_size else 0)

    # Sugestões para autocompletar
    if search_text:
        suggestions = [
            {"id": row["id"], "title": row["title"]}
            for row in search_convenios(search_text=search_text, page=1, page_size=5)
        ]
    else:
        suggestions = []

    return jsonify({
        "data": [dict(row) for row in convenios],
        "suggestions": suggestions,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    })


@routes_bp.route("/allconvenios", methods=["GET"])
def get_all_convenios_route():
    convenios = get_all_convenios()
    return jsonify(convenios)

def process_convenios():
    """Processa os convênios do arquivo JSON e insere no banco de dados"""
    # gera um map de nomes para atribuir um uuid unico para cada convenio
    convenio_map = {}
    
    try:
        json_path = os.path.join(os.getcwd(), "myspider_project", "output", "convenios.json")

        if not os.path.exists(json_path):
            logging.error("[Flask] Arquivo JSON não encontrado")
            return {"ok": False, "message": "Arquivo JSON não encontrado"}

        with open(json_path, "r", encoding="utf-8") as f:
            convenios = json.load(f)
        clear_convenios()  # Limpa a tabela de convênios
        for convenio in convenios:
            uuid_convenio = str(uuid.uuid4())
            # Verifica se o convenio já foi inserido
            if convenio["title"] in convenio_map:
                # pega o uuid do convenio
                uuid_convenio = convenio_map[convenio["title"]]
            else:
                # adiciona o convenio ao map
                convenio_map[convenio["title"]] = uuid_convenio
            
            insert_convenio(
                title=convenio.get("title", "Sem título"),
                date=convenio.get("date", ""),
                cats=convenio.get("cats", ""),
                content=convenio.get("content", ""),
                discounts=convenio.get("discounts", ""),
                id=uuid_convenio
            )

        logging.info("[Flask] Dados processados e inseridos no banco de dados com sucesso.")
        os.remove(json_path)  # Opcional: Remover o arquivo após o processamento

        return {"ok": True, "message": "Dados processados com sucesso"}
    except Exception as e:
        logging.error(f"[Flask] Erro ao processar convênios: {str(e)}")
        return {"ok": False, "message": f"Erro: {str(e)}"}
    
@routes_bp.route("/get_categories", methods=["GET"])
def get_categories():
    try:
        cats = get_unique_cats()
        return jsonify(cats)
    except Exception as e:
        logging.error(f"[Flask] Erro ao buscar categorias: {str(e)}")
        return jsonify([])
    
@routes_bp.route("/convenio/<id>", methods=["GET"])
def get_convenio_by_id(id):
    convenio = find_convenio_by_id(id)
    if not convenio:
        return jsonify({"ok": False, "message": "Convênio não encontrado"}), 404
    return jsonify(convenio)

@routes_bp.route("/convenios_by_cat/<cat>", methods=["GET"])
def get_convenios_by_cat_route(cat):
    logging.info(f"[Flask] Buscando convênios da categoria {cat}")
    convenios = get_convenios_by_cat(cat)
    return jsonify(convenios)
