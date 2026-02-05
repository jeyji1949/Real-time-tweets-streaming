
🔁 0. Après redémarrage du PC (nettoyage sécurité)
docker compose down --remove-orphans
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null
docker network prune -f
docker volume prune -f
👉 S’il n’y a pas de containers, les erreurs sont normales.

📁 1. Se placer dans le projet
cd ~/Real-time-tweets-streaming
Vérifie la structure :
ls
Tu dois voir au minimum :
docker-compose.yml
Dockerfile
analyzer.py
requirements.txt
producer/

🐳 2. Lancer toute l’architecture Docker
docker compose up -d --build
✔️ Services attendus :
    • zookeeper
    • kafka
    • elasticsearch
    • kibana
    • analyzer

🔎 3. Vérifier que tout tourne
docker ps
Tu dois voir :
kafka
elasticsearch
real-time-tweets-streaming-kibana-1
analyzer

📜 4. Vérifier les logs de l’analyzer (IMPORTANT)
docker logs -f analyzer
Tu dois voir :
🔥 ANALYZER BOOTING...
✅ Kafka connected
✅ Elasticsearch connected
 Analyzer service started
 Waiting for Kafka messages...
➡️ Ne ferme pas ce terminal (Ctrl+C plus tard)

🐍 5. Lancer le simulateur Twitter (producer)
5.1 Créer un virtualenv (UNE FOIS)
cd producer
python3 -m venv venv
source venv/bin/activate
5.2 Installer les dépendances
pip install kafka-python python-dotenv
5.3 Lancer le simulateur
python twitter_simulator.py
✔️ Tu dois voir des tweets envoyés à Kafka.

🔄 6. Vérifier que l’analyzer indexe bien
Retourne dans le terminal des logs :
📥 TWEET INDEXED
 ...
 Sentiment: positive | Confidence: 0.5
 Topic: AI | 🧠 Method: textblob
➡️ Si tu vois ça : TOUT EST OK

🗄️ 7. Vérifier Elasticsearch (brut)
7.1 Vérifier l’index
curl http://localhost:9200/_cat/indices?v
Tu dois voir :
tweets_index
7.2 Voir un document lisible
curl -s "http://localhost:9200/tweets_index/_search?size=1" | python3 -m json.tool
✔️ Champs attendus :
{
  "tweet_id": "...",
  "text": "...",
  "hashtags": ["AI", "BigData"],
  "sentiment": "positive",
  "confidence": 0.8,
  "topic": "AI",
  "analysis_method": "textblob",
  "word_freq": {...}
}

📊 8. Kibana – PARTIE 5 (Checklist Personne 2)
8.1 Ouvrir Kibana
👉 Navigateur :
http://localhost:5601

8.2 Créer l’index pattern
    1. Stack Management
    2. Index Patterns
    3. Create index pattern
    4. Nom :
tweets_index
    5. Time field :
created_at
    6. Create

8.3 Visualisations à créer (OBLIGATOIRES)
📌 1. Hashtags les plus utilisés
    • Lens
    • Horizontal bar
    • Field : hashtags.keyword
    • Top 10

💬 2. Statistiques des sentiments
    • Pie chart
    • Field : sentiment.keyword

🧠 3. Topics dominants
    • Bar chart
    • Field : topic.keyword

⭐ 4. Meilleurs tweets
    • Data Table
    • Sort : score DESC
    • Filter : sentiment = positive

💀 5. Pires tweets
    • Data Table
    • Filter : sentiment = negative

8.4 Dashboard final
    • Create Dashboard
    • Ajouter toutes les visualisations
    • Nom :
Tweet Analysis – Personne 2


