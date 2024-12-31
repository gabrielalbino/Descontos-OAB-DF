from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, func
from sqlalchemy.sql import select, asc, desc
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

# Obtém a URL do banco de dados do ambiente
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/convenios")

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define a tabela 'convenios'
convenios_table = Table(
    "convenios",
    metadata,
    Column("id", String, nullable=False),
    Column("title", String, nullable=False),
    Column("date", String, nullable=True),
    Column("cats", String, nullable=True),
    Column("content", Text, nullable=True),
    Column("discounts", String, nullable=True),
)

def create_tables():
    """Cria as tabelas no banco de dados"""
    try:
        metadata.create_all(engine)
        print("Tabelas criadas com sucesso!")
    except SQLAlchemyError as e:
        print(f"Erro ao criar tabelas: {e}")

def insert_convenio(title, date, cats, content, id, discounts):
    """Insere um convênio no banco de dados"""
    print(f"Inserindo convênio: title={title}, date={date}, cats={cats}")
    try:
        with engine.begin() as conn:  # Usa transação para garantir atomicidade
            conn.execute(
                convenios_table.insert().values(title=title, date=date, cats=cats, content=content, id=id, discounts=discounts)
            )
        print(f"Convênio '{title}' inserido com sucesso!")
    except SQLAlchemyError as e:
        print(f"Erro ao inserir convênio: {e}")

def search_convenios(search_text=None, page=1, page_size=10, sort_by="title", order="asc", cat=None):
    """Busca convênios no banco de dados com paginação e ordenação"""
    try:
        with engine.connect() as conn:
            query = select(convenios_table)

            if search_text:
                query = query.where(convenios_table.c.title.ilike(f"%{search_text}%"))
                
            if cat:
                query = query.where(convenios_table.c.cats.ilike(f"%{cat}%"))

            # Ordenação dinâmica
            sort_column = getattr(convenios_table.c, sort_by, convenios_table.c.title)
            if order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            query = query.offset((page - 1) * page_size).limit(page_size)
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]
    except SQLAlchemyError as e:
        print(f"Erro ao buscar convênios: {e}")
        return []
    
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
        print(f"Erro ao contar convênios: {e}")
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
        print(f"Erro ao obter todos os convênios: {e}")
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
        print(f"Erro ao buscar convênio por ID: {e}")
        return None 
    
def clear_convenios():
    """Limpa todos os convênios do banco de dados"""
    try:
        with engine.begin() as conn:
            conn.execute(convenios_table.delete())
        print("Convênios removidos com sucesso!")
    except SQLAlchemyError as e:
        print(f"Erro ao remover convênios: {e}")
        
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
        print(f"Erro ao buscar categorias únicas: {e}")
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
        print(f"Erro ao buscar convênios por categoria: {e}")
        return []