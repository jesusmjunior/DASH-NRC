FROM python:3.10-slim

# Otimização
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copiar código
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor porta do Streamlit
EXPOSE 8080

# Iniciar servidor Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
