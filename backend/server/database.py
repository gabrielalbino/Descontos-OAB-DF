from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, func, DDL
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.sql import text, select
from sqlalchemy.event import listen
from server.logging import logging
import time
import os

# Configuração do SQLAlchemy
# DATABASE_URL = "postgresql://postgres:password@localhost:5432/convenios"
# get DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/convenios")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define a tabela 'convenios'
convenios_table = Table(
    "convenios",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("title", String, nullable=False),
    Column("date", String, nullable=True),
    Column("cats", String, nullable=True),
    Column("content", Text, nullable=True),
    Column("discounts", String, nullable=True),
    Column("search_vector", Text, nullable=True),  # Coluna para Full-Text Search
)
def create_tables():
    """Recria as tabelas no banco de dados, índices e triggers para Full-Text Search."""
    try:
        # Cria as tabelas novamente
        metadata.create_all(engine)
        print("Tabelas recriadas com sucesso!")

        with engine.connect() as conn:
            # Habilitar extensões
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
            print("Extensões habilitadas com sucesso!")

            # Adiciona a coluna search_vector, se não existir
            conn.execute(text("""
                ALTER TABLE convenios
                ADD COLUMN IF NOT EXISTS search_vector tsvector;
            """))
            print("Coluna 'search_vector' adicionada com sucesso!")

            # Criação do índice GIN
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_convenios_search
                ON convenios
                USING GIN (to_tsvector('portuguese', unaccent(title || ' ' || content || ' ' || COALESCE(discounts, ''))));
            """))
            print("Índice GIN criado com sucesso!")

        # Para comandos de criação de função e trigger, use uma conexão em modo autocommit
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            # Criação da função para atualizar o search_vector
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_search_vector()
                RETURNS trigger AS $$
                BEGIN
                    NEW.search_vector := to_tsvector('portuguese', unaccent(
                        COALESCE(NEW.title, '') || ' ' || 
                        COALESCE(NEW.content, '') || ' ' || 
                        COALESCE(NEW.discounts, '')));
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            print("Função 'update_search_vector' criada com sucesso!")

            # Criação do trigger
            conn.execute(text("""
                CREATE TRIGGER trigger_update_search_vector
                BEFORE INSERT OR UPDATE ON convenios
                FOR EACH ROW
                EXECUTE FUNCTION update_search_vector();
            """))
            print("Trigger para atualizar o 'search_vector' criado com sucesso!")

        # Atualização dos registros existentes
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE convenios
                SET search_vector = to_tsvector('portuguese', unaccent(
                    COALESCE(title, '') || ' ' || 
                    COALESCE(content, '') || ' ' || 
                    COALESCE(discounts, '')));
            """))
            print("Registros existentes atualizados com sucesso!")

    except SQLAlchemyError as e:
        print(f"Erro ao recriar tabelas ou configurar Full-Text Search: {e}")
        
        
def search_convenios(search_text=None, page=1, page_size=10, sort_by="title", order="asc", cat=None):
    """Busca convênios no banco de dados com paginação, ordenação e destaque."""
    try:
        with engine.connect() as conn:
            # Base da consulta
            base_query = """
                SELECT 
                    id, 
                    title, 
                    content, 
                    cats,
                    discounts
            """

            # Adiciona os campos destacados apenas se search_text for válido
            if search_text and search_text.strip():
                base_query += """,
                    ts_headline('portuguese', title, websearch_to_tsquery(:search_text)) AS title_highlight,
                    ts_headline('portuguese', content, websearch_to_tsquery(:search_text)) AS content_highlight,
                    ts_headline('portuguese', discounts, websearch_to_tsquery(:search_text)) AS discounts_highlight
                """
            else:
                base_query += """
                    , title AS title_highlight,
                    content AS content_highlight,
                    discounts AS discounts_highlight
                """

            base_query += " FROM convenios"

            filters = []
            params = {
                "limit": page_size,
                "offset": (page - 1) * page_size,
            }

            # Adiciona filtros somente se search_text for válido
            if search_text and search_text.strip():
                filters.append("""
                    (search_vector @@ websearch_to_tsquery(:search_text) 
                    OR title ILIKE :ilike_text 
                    OR content ILIKE :ilike_text 
                    OR discounts ILIKE :ilike_text)
                """)
                params["search_text"] = search_text
                params["ilike_text"] = f"%{search_text}%"

            if cat:
                filters.append("cats ILIKE :cat")
                params["cat"] = f"%{cat}%"

            if filters:
                base_query += " WHERE " + " AND ".join(filters)

            base_query += f" ORDER BY {sort_by} {'DESC' if order == 'desc' else 'ASC'}"
            base_query += " LIMIT :limit OFFSET :offset"

            query = text(base_query)
            result = conn.execute(query, params)

            # Retorna o resultado
            return [dict(row._mapping) for row in result]

    except SQLAlchemyError as e:
        logging.info(f"Erro ao buscar convênios: {e}")
        return []
    
def insert_convenio(title, date, cats, content, id, discounts):
    """Insere um convênio no banco de dados"""
    logging.info(f"Inserindo convênio: title={title}, date={date}, cats={cats}")
    try:
        with engine.begin() as conn:  # Usa transação para garantir atomicidade
            conn.execute(
                convenios_table.insert().values(title=title, date=date, cats=cats, content=content, id=id, discounts=discounts)
            )
        logging.info(f"Convênio '{title}' inserido com sucesso!")
    except SQLAlchemyError as e:
        logging.info(f"Erro ao inserir convênio: {e}")

def count_convenios(search_text=None, cat=None):
    """Conta o número de convênios no banco de dados com suporte a filtros"""
    try:
        with engine.connect() as conn:
            query = select(func.count(convenios_table.c.id))  # Conte as IDs diretamente
            
            # Aplica filtro de busca
            if search_text:
                query = query.where(convenios_table.c.title.ilike(f"%{search_text}%"))
            
            # Aplica filtro de categoria
            if cat:
                query = query.where(convenios_table.c.cats.ilike(f"%{cat}%"))

            # Executa a query
            result = conn.execute(query)
            return result.scalar()  # Retorna o valor do count
    except SQLAlchemyError as e:
        logging.info(f"Erro ao contar convênios: {e}")
        return 0
    
def get_all_convenios():
    """Retorna todos os convênios"""
    try:
        with engine.connect() as conn:
            query = select(convenios_table)
            result = conn.execute(query)
            # Converte cada RowMapping em um dicionário serializável
            convenios = [dict(row._mapping) for row in result]
            return convenios
    except SQLAlchemyError as e:
        logging.info(f"Erro ao obter todos os convênios: {e}")
        return []
    

def find_convenio_by_id(id):
    """Busca um convênio pelo ID"""
    try:
        with engine.connect() as conn:
            query = select(convenios_table).where(convenios_table.c.id == id)
            result = conn.execute(query)
            convenio = result.fetchone()
            return dict(convenio._mapping) if convenio else None
    except SQLAlchemyError as e:
        logging.info(f"Erro ao buscar convênio por ID: {e}")
        return None 
    
def clear_convenios():
    """Limpa todos os convênios do banco de dados"""
    try:
        with engine.begin() as conn:
            conn.execute(convenios_table.delete())
        logging.info("Convênios removidos com sucesso!")
    except SQLAlchemyError as e:
        logging.info(f"Erro ao remover convênios: {e}")
        
def get_unique_cats():
    """Retorna uma lista de categorias únicas"""
    try:
        cats = []
        with engine.connect() as conn:
            query = select(convenios_table.c.cats)
            result = conn.execute(query)
            for row in result:
                cats.extend(row[0].split(","))
        return sorted(set(cats))
    except SQLAlchemyError as e:
        logging.info(f"Erro ao buscar categorias únicas: {e}")
        return []


def get_convenios_by_cat(cat):
    """Retorna convênios por categoria"""
    try:
        with engine.connect() as conn:
            query = select(convenios_table).where(convenios_table.c.cats.ilike(f"%{cat}%"))
            result = conn.execute(query)
            convenios = [dict(row._mapping) for row in result]
            return convenios
    except SQLAlchemyError as e:
        logging.info(f"Erro ao buscar convênios por categoria: {e}")
        return []
    
    
def update_coalesce():
    """Atualiza a coluna 'content' com valores não nulos de 'content' e 'title'"""
    try:
        with engine.connect() as conn:
              conn.execute(text("""
                UPDATE convenios
                SET search_vector = to_tsvector('portuguese', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(content, '') || ' ' || 
                    COALESCE(discounts, ''));
            """))
        logging.info("Coluna 'content' atualizada com sucesso!")
    except SQLAlchemyError as e:
        logging.info(f"Erro ao atualizar coluna 'content': {e}")