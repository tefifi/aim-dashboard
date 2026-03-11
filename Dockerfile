# ── AIM Dashboard — Dockerfile ──────────────────────────────────────────────
# Imagen base: Python 3.11 slim para menor tamaño
FROM python:3.11-slim

# Metadatos
LABEL maintainer="tu-equipo@empresa.cl"
LABEL description="AIM Dashboard — Perfil de ciberseguridad para PyMEs"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema (necesarias para torch y lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo el requirements primero (aprovecha cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
# --no-cache-dir reduce el tamaño de imagen
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copiar el código del proyecto
COPY . .

# Descargar recursos NLTK necesarios durante el build
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Puerto que expone la app
EXPOSE 8050

# Comando de inicio con Gunicorn
# - 2 workers (ajustar según CPU disponibles: 2 * num_cpus + 1)
# - timeout 300s porque el análisis NLP puede tardar varios minutos
# - El objeto WSGI de Dash se llama "server" dentro de app.py
CMD ["gunicorn", \
     "--workers", "2", \
     "--timeout", "300", \
     "--bind", "0.0.0.0:8050", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:server"]
