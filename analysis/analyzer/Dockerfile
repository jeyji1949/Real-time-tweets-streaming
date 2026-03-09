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

<<<<<<< HEAD
# Copier le script analyzer.py
COPY analyzer_improved.py .
COPY cassandra_writer_improved.py .

# Commande par défaut
CMD ["python", "analyzer_improved.py"]
=======
# Copier le script amélioré
COPY analyzer_improved.py .
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2

# Lancer le script au démarrage du conteneur
CMD ["python", "analyzer_improved.py"]
