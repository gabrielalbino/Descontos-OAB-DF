# Dockerfile para o frontend (Next.js)
FROM node:18-alpine

WORKDIR /app

# Instalar dependências
COPY package.json yarn.lock ./
RUN yarn install

# Copiar o restante do código
COPY . .

# Expor porta e rodar o Next.js
EXPOSE 3000
CMD ["yarn", "dev"]