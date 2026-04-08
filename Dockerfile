FROM python:3.11-slim

# Dépendances système nécessaires pour ChromaDB et PyPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY 5_app_visuelle.py .

# Création des dossiers persistants
RUN mkdir -p ./data ./ma_base

# Exposition du port Streamlit
EXPOSE 8501

# Healthcheck pour vérifier que l'app tourne
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Lancement de l'app
CMD ["streamlit", "run", "5_app_visuelle.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
