Erreurs courantes et solutions

Ce document regroupe les principales erreurs rencontrées durant le projet, avec leurs causes et solutions associées.

1. Erreur TLS Docker

Synthèse
Problème réseau lors du téléchargement des images Docker.

Solution

docker compose down
docker system prune -f
docker compose up --build

2. Attribut version obsolète (Docker Compose v2)

Synthèse
L’attribut version n’est plus nécessaire avec Docker Compose v2.

Solution
Supprimer la ligne suivante du fichier docker-compose.yml :

version: "3.8"

3. Erreur xpack Elasticsearch

Synthèse
Faute de frappe ou mauvaise configuration des options de sécurité Elasticsearch.

Solution

xpack.security.enabled: false
xpack.security.http.ssl.enabled: false

4. Port 9200 déjà utilisé

Synthèse
Conflit de port sur la machine hôte.

Solutions possibles

Identifier et tuer le processus utilisant le port :

sudo lsof -i :9200
sudo kill -9 <PID>


Modifier le port exposé :

ports:
  - "9201:9200"

5. Connection refused Elasticsearch

Synthèse
Mauvais hostname ou port depuis un conteneur Docker.

Solution

from elasticsearch import Elasticsearch

es = Elasticsearch("http://elasticsearch:9200")

6. Client Elasticsearch incompatible

Synthèse
Incompatibilité entre la version du client Python et celle du serveur Elasticsearch.

Solution

pip install elasticsearch==8.9.0

7. NoBrokersAvailable Kafka

Synthèse
Kafka n’est pas encore prêt au moment de la connexion.

Solution

import time
from kafka import KafkaConsumer

while True:
    try:
        consumer = KafkaConsumer(...)
        break
    except:
        time.sleep(5)

8. Erreur PEP 668 (pip bloqué)

Synthèse
Installation de paquets interdite dans l’environnement Python système.

Solution

python3 -m venv venv
source venv/bin/activate

9. Modules Python manquants

Synthèse
Dépendances non installées.

Solution

pip install kafka-python python-dotenv tweepy

10. Erreur OpenAI 429

Synthèse
Quota OpenAI épuisé.

Décision

Abandon de l’API OpenAI

Remplacement par TextBlob pour l’analyse de sentiment

11. Erreur Ollama
Problèmes rencontrés

Ollama non accessible

404 Client Error

Manque de mémoire

Service indisponible

Solution retenue

Suppression d’Ollama

Retour à TextBlob

12. Mapping Elasticsearch non modifiable

Synthèse
Un mapping Elasticsearch ne peut pas être modifié après la création de l’index.

Solution

curl -X DELETE http://localhost:9200/tweets_index
curl -X PUT http://localhost:9200/tweets_index -d @mapping.json

