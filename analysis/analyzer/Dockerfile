# Base Python
FROM python:3.10-slim

# Variables d'environnement pour éviter les prompts lors de l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création du dossier de l'application
WORKDIR /app

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script analyzer.py
COPY analyzer.py .

# Commande par défaut
CMD ["python", "analyzer.py"]

