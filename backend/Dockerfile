FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente recomendadas em contêineres Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app  

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 
# Cria a pasta output se não existir
RUN mkdir -p output

# Instala seu pacote
RUN pip install --no-cache-dir .

EXPOSE 5001

CMD ["python", "-m", "server.app"]