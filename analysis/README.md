PARTIE PERSONNE 2 — ANALYSE & INDEXATION DES TWEETS (DÉTAIL COMPLET)

🟦 PARTIE 1 — Consommation des tweets depuis Kafka
🎯 Objectif
Lire les tweets produits par le simulateur (Personne 1) depuis Kafka en temps réel.

🔧 Code (extrait analyzer.py)
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "tweets_topic",
    bootstrap_servers="kafka:29092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

⌨️ Commandes utilisées
docker compose up -d --build
docker logs -f analyzer

📊 Résultat obtenu
🔥 ANALYZER BOOTING...
✅ Kafka connected
 Waiting for Kafka messages...
👉 Kafka fonctionne et les tweets sont bien reçus

🟦 PARTIE 2 — Analyse de sentiment avec TextBlob
🎯 Objectif
Déterminer si un tweet est positif, négatif ou neutre.

🔧 Code (analyzer.py)
from textblob import TextBlob

def analyze_with_textblob(text):
    polarity = TextBlob(text).sentiment.polarity
    
    if polarity > 0.1:
        return "positive", 1
    elif polarity < -0.1:
        return "negative", -1
    else:
        return "neutral", 0

📊 Résultat obtenu
💬 Sentiment: positive | ⭐ Score: 1
💬 Sentiment: neutral  | ⭐ Score: 0
👉 Score normalisé :
    • 1 → positif
    • 0 → neutre
    • -1 → négatif

❗ Problème rencontré
Au début :
    • uniquement 0 et 1
    • jamais -1
✅ Correction
Ajout d’un seuil négatif polarity < -0.1

🟦 PARTIE 3 — Détection de topic dynamique
🎯 Objectif
Associer chaque tweet à un thème logique.

🔧 Code (topic mapping)
TOPIC_KEYWORDS = {
    "AI": ["ai", "machine", "learning", "neural"],
    "Cloud": ["cloud", "aws", "azure"],
    "Security": ["cyber", "security", "infosec"],
    "Web": ["javascript", "web", "frontend"],
    "Data": ["data", "pipeline", "bigdata"]
}

def detect_topic(text):
    text = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in text for k in keywords):
            return topic
    return "General Tech"

📊 Résultat obtenu
📌 Topic: AI
📌 Topic: Security
📌 Topic: Data
👉 Problème initial :
Tous les tweets retournaient technology
👉 Solution :
Topic dynamique par mots-clés

🟦 PARTIE 4 — Extraction des hashtags & fréquence des mots
🎯 Objectif
Permettre :
    • hashtags les plus utilisés
    • mots fréquents
    • meilleurs / pires tweets

🔧 Code (extrait)
import re
from collections import Counter

def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)

def word_frequency(text):
    words = re.findall(r"\b\w+\b", text.lower())
    return dict(Counter(words))

📊 Résultat indexé
"hashtags": ["Cybersecurity", "InfoSec"],
"word_freq": {
  "api": 1,
  "design": 1,
  "security": 1
}

🟦 PARTIE 5 — Indexation dans Elasticsearch
🎯 Objectif
Stocker les tweets enrichis pour analyse.

🔧 Mapping Elasticsearch
curl -X PUT http://localhost:9200/tweets_index \
-H "Content-Type: application/json" \
-d '{
  "mappings": {
    "properties": {
      "tweet_id": { "type": "keyword" },
      "text": { "type": "text" },
      "hashtags": { "type": "keyword" },
      "sentiment": { "type": "keyword" },
      "score": { "type": "integer" },
      "topic": { "type": "keyword" },
      "analysis_method": { "type": "keyword" }
    }
  }
}'

🔧 Code d’indexation
es.index(index="tweets_index", document=tweet_doc)

📊 Vérification
curl http://localhost:9200/tweets_index/_search?size=1&pretty
Résultat :
{
  "text": "New breakthrough in CI/CD!",
  "sentiment": "positive",
  "score": 1,
  "topic": "Security"
}

🟦 PARTIE 6 — Kibana (Visualisation)
🎯 Objectif
Analyser les données sans coder.

Étapes Kibana
    1. Accéder à
👉 http://localhost:5601
    2. Create Data View
        ◦ Index: tweets_index
        ◦ Time field: created_at
    3. Visualisations :
        ◦ Pie → sentiment
        ◦ Bar → topic
        ◦ Tag cloud → hashtags
    4. Dashboard :
Real-Time Tweets Analytics

🟦 PARTIE 7 — Dockerisation
🎯 Objectif
Pipeline automatisé et reproductible.

🔧 Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY analyzer.py .
CMD ["python", "analyzer.py"]

🔧 Commandes Docker
docker compose down
docker compose up -d --build
docker ps

🟦 PARTIE 8 — Problèmes rencontrés & solutions
❌ Problèmes
    • OpenAI API quota (429)
    • Ollama mémoire insuffisante
    • Kafka module manquant en local
    • Mapping Elasticsearch écrasé
✅ Solutions
    • Abandon OpenAI & Ollama
    • TextBlob stable & gratuit
    • Kafka uniquement via Docker
    • Mapping fixé une seule fois

## Docker Integration

The analyzer service was added to the root docker-compose.yml to integrate
the sentiment analysis pipeline with Kafka and Elasticsearch.
No existing services were modified.

🟦 PARTIE 9 — Handoff Personne 3
🎁 Livré à Personne 3
    • Index tweets_index
    • Mapping validé
    • Dashboard Kibana
    • Champs prêts pour statistiques :
        ◦ hashtags
        ◦ sentiment
        ◦ score
        ◦ topic
        ◦ word_freq

