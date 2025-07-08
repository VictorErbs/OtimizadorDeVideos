# Usa imagem ffmpeg com suporte a AMD, NVIDIA, Intel e CPU
FROM jrottenberg/ffmpeg:7.0-ubuntu2204

# Instala Python, pip e venv
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Cria virtualenv
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Instala dependências Python no virtualenv
COPY requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt && pip install flask

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos necessários para o diretório de trabalho
COPY webserver.py otimizador.py ./
COPY web/ ./web/

EXPOSE 5000

# Garante que o Flask será executado
ENTRYPOINT []
CMD ["python", "webserver.py"]