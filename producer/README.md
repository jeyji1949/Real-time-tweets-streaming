# 📤 Twitter Stream Producer

Producer Kafka qui collecte les tweets en temps réel depuis un simulateur 
## 🎯 Responsabilité

Streamer les tweets depuis Twitter vers le topic Kafka `tweets_raw`.

---


## 🚀 Utilisation
```bash
# Activer le venv
source ../venv/bin/activate

# Lancer le producer
python twitter_stream_producer.py
```

---

## 📊 Format des données envoyées

Chaque tweet est envoyé au format JSON vers Kafka :
```json
{
  "tweet_id": "1234567890",
  "text": "Just learned Python! #python #coding",
  "created_at": "2025-01-22T10:30:00",
  "user": "987654321",
  "lang": "en",
  "hashtags": ["python", "coding"],
  "retweet_count": 5,
  "like_count": 12
}
```

Voir le schéma complet : [docs/schema.json](../docs/schema.json)

---

## 🧪 Tests
```bash
# Tester la connexion Twitter
python test_twitter.py

```

---

## 🐛 Dépannage


### Erreur 429 (Too Many Requests)
- Rate limit atteint, attendre 15 minutes
- Réduire le nombre de règles de filtrage

### Pas de tweets reçus
- Vérifier que les mots-clés sont populaires
- Essayer avec `lang:en` pour avoir plus de résultats
