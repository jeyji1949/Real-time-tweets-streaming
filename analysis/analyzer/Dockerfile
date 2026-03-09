# Utiliser Python slim comme base
FROM python:3.10-slim

# Installer des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script amélioré
COPY analyzer_improved.py .

# Lancer le script au démarrage du conteneur
CMD ["python", "analyzer_improved.py"]
