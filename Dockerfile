# Imagem só com as ferramentas Python de indexação (ingest.py e build_web_data.py).
# O código não é copiado: o docker compose monta a pasta do projeto dentro do container.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "--version"]
