# Imagem oficial e enxuta definida no enunciado da Etapa Final.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências primeiro, para aproveitar o cache de camadas do Docker.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY tests/ tests/

# Executa como usuário sem privilégios de root.
RUN useradd --create-home --uid 1000 analyzer
USER analyzer

CMD ["pytest", "tests/test_harness.py", "-v", "-p", "no:cacheprovider"]
