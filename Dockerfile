FROM python:3.10-slim

# Otimização do ambiente
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copia todos os arquivos para dentro do container
COPY . .

# Instala as dependências listadas
RUN pip install --no-cache-dir -r requirements.txt

# Exposição da porta padrão do Streamlit (usada pelo Cloud Run)
EXPOSE 8080

# Comando de execução do app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
