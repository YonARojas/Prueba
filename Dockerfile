# ================================
# 1) Imagen base
# ================================
FROM python:3.12-slim

# ================================
# 2) Dependencias del sistema
# ================================
RUN apt-get update && apt-get install -y \
    unzip \
    libaio1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ================================
# 3) Instalar Oracle Instant Client
# ================================
WORKDIR /opt/oracle

# Basiclite oficial (21.13)
RUN wget https://download.oracle.com/otn_software/instantclient/instantclient-basiclite-linux.x64-21.13.0.0.0dbru.zip -O instant.zip && \
    unzip instant.zip && \
    rm instant.zip && \
    mv instantclient* instantclient

ENV LD_LIBRARY_PATH="/opt/oracle/instantclient"
ENV PATH="$PATH:/opt/oracle/instantclient"

# ================================
# 4) Directorio de la app
# ================================
WORKDIR /app

# Instalar requirements primero (usa caché)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ================================
# 5) Reconstrucción del Wallet
# ================================
ENV WALLET_DIR=/app/Wallet
RUN mkdir -p /app/Wallet

# Copiar script de wallet
COPY build.sh .
RUN chmod +x build.sh

# ================================
# 6) Copiar código completo
# ================================
COPY . .

# ================================
# 7) Ejecutar reconstrucción del Wallet
# ================================
RUN ./build.sh

# ================================
# 8) Variables Oracle
# ================================
ENV TNS_ADMIN=/app/Wallet

# ================================
# 9) Iniciar con Gunicorn
# ================================
CMD ["bash", "-c", "export TNS_ADMIN=/app/Wallet && gunicorn run:app --bind 0.0.0.0:10000 --workers 3"]
