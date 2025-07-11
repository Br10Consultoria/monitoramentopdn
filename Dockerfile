FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    iputils-ping \
    traceroute \
    dnsutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/
COPY config/ ./config/

# Criar diretórios necessários
RUN mkdir -p /app/data /app/reports

# Definir usuário não-root
RUN useradd -m -u 1000 monitor && chown -R monitor:monitor /app
USER monitor

# Comando padrão
CMD ["python", "app/main.py"]
