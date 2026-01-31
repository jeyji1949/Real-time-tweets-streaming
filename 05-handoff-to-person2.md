# Guide de Passation - Personne 1 → Personne 2

## 🎯 Ce qui est prêt pour toi

### ✅ Infrastructure Kafka
- Docker Compose avec tous les services
- Kafka opérationnel sur `localhost:9092`
- Topic `tweets_raw` créé automatiquement
- Elasticsearch disponible sur `localhost:9200`

### ✅ Code fonctionnel
- **Simulateur de tweets** : Génère des tweets réalistes
- **Consumer Kafka** : Lit les tweets du topic
- Format JSON standardisé (voir `docs/schema.json`)

---

## ⚠️ IMPORTANT : Quel fichier utiliser ?

### ❌ NE PAS UTILISER : `twitter_stream_producer.py`

Ce fichier utilise l'**API Twitter réelle** (Tweepy) qui nécessite :
- Un Bearer Token valide (compte Twitter Developer)
- Plan payant ($100+/mois)
- Configuration complexe

**Ce fichier ne fonctionnera PAS pour toi !**

---

### ✅ UTILISER : `twitter_simulator.py`

Ce fichier est un **simulateur local** qui :
- ✅ Fonctionne sans API Twitter
- ✅ Génère des tweets réalistes
- ✅ Envoie vers Kafka automatiquement
- ✅ Gratuit et illimité

**C'est CE fichier que tu dois utiliser !**

---

## 🚀 Démarrage rapide (30 secondes)

### Étape 1 : Clone le repo

```bash
cd ~/Documents
git clone <URL_DU_REPO>
cd Twitter-Project
```

### Étape 2 : Démarre Docker

```bash
docker-compose up -d
sleep 90  # Attendre que Kafka démarre
```

### Étape 3 : Vérifie que tout tourne

```bash
docker-compose ps
# Tous les services doivent être "Up"
```

### Étape 4 : Installe Python venv

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎬 Lancer le pipeline COMPLET

### Terminal 1 : Producer (SIMULATEUR)

```bash
cd ~/Documents/Twitter-Project
source venv/bin/activate
cd producer
python twitter_simulator.py  # ← CE FICHIER !
```

**Tu verras :**
```
================================================================================
🤖 TWITTER SIMULATOR → KAFKA PRODUCER
================================================================================
📤 Kafka: localhost:9092
📮 Topic: tweets_raw
================================================================================

✅ Tweet #1
   👤 User: @python_dev
   📝 Text: Just finished a ML project! #Python #AI
   #️⃣  Hashtags: #Python, #AI
   🔄 RT: 42 | ❤️  Likes: 156
--------------------------------------------------------------------------------
```

### Terminal 2 : Ton Analyzer

```bash
cd ~/Documents/Twitter-Project
source venv/bin/activate
cd analysis
python analyzer.py  # Ton code d'analyse
```

**Il devrait recevoir les tweets et les analyser ! 🎉**

---

## 📊 Format des tweets reçus

Chaque tweet dans Kafka a ce format (voir `docs/schema.json`) :

```json
{
  "tweet_id": "1000000",
  "text": "Just finished a machine learning project! #Python #AI",
  "created_at": "2026-01-26T23:30:00.000Z",
  "user": "python_dev",
  "lang": "en",
  "hashtags": ["Python", "AI"],
  "retweet_count": 42,
  "like_count": 156
}
```

**Tu dois ajouter :**
```json
{
  ...,
  "sentiment": "positive",      // ← OpenAI
  "topic": "Machine Learning",  // ← OpenAI
  "confidence": 0.95            // ← OpenAI
}
```

---

## 🧪 Tester que Kafka reçoit des tweets

### Option 1 : Consumer test (Python)

```bash
source venv/bin/activate
cd consumer
python consumer.py
```

**Si tu vois des tweets s'afficher → Kafka fonctionne ! ✅**

### Option 2 : Console Kafka

```bash
docker exec -it kafka \
  kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic tweets_raw \
  --from-beginning
```

**Tu dois voir des messages JSON.**

---

## 🔧 Connexion à Kafka depuis ton code

### Consumer Python basique

```python
from kafka import KafkaConsumer
import json

# Configuration
consumer = KafkaConsumer(
    'tweets_raw',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='analyzer-group'  # Ton group ID
)

print("📥 En attente des tweets...")

# Lire les tweets
for message in consumer:
    tweet = message.value
    
    # Ton code d'analyse ici
    print(f"Tweet reçu : {tweet['text']}")
    
    # 1. Analyser avec OpenAI
    sentiment = analyze_with_openai(tweet['text'])
    
    # 2. Enrichir le tweet
    tweet['sentiment'] = sentiment
    
    # 3. Indexer dans Elasticsearch
    index_to_elasticsearch(tweet)
```

---

## 🐛 Problèmes courants

### Problème 1 : "No module named 'kafka'"

**Cause** : venv pas activé

**Solution** :
```bash
source venv/bin/activate
```

### Problème 2 : "NoBrokersAvailable"

**Cause** : Kafka pas encore prêt

**Solution** :
```bash
# Attendre 90 secondes après docker-compose up
sleep 90

# Vérifier
docker logs kafka | grep "started"
```

### Problème 3 : "Aucun tweet reçu"

**Cause** : Le simulateur n'est pas lancé

**Solution** :
```bash
# Terminal séparé
cd producer
python twitter_simulator.py  # ← Pas twitter_stream_producer.py !
```

### Problème 4 : Topic vide

**Vérifier** :
```bash
# Lister les topics
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092

# Si tweets_raw absent, créer
docker exec -it kafka \
  kafka-topics --create --topic tweets_raw \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

---

## 📋 Checklist de démarrage

```
☐ Repo cloné
☐ docker-compose up -d lancé
☐ Attendu 90 secondes
☐ docker-compose ps → tous "Up"
☐ venv créé et activé
☐ requirements.txt installé
☐ Terminal 1 : python twitter_simulator.py (simulateur)
☐ Terminal 2 : ton analyzer.py
☐ Les tweets arrivent dans ton analyzer
```

---

## 🎯 Ce que tu dois faire

1. **Recevoir les tweets** depuis Kafka (`tweets_raw`)
2. **Analyser chaque tweet** avec OpenAI :
   - Sentiment (positive/negative/neutral)
   - Topic principal
   - Score de confiance
3. **Indexer dans Elasticsearch** :
   - Index : `tweets_analyzed`
   - Mapping avec les nouveaux champs
4. **Préparer pour Personne 3** :
   - Kibana doit voir l'index `tweets_analyzed`

---

## 📞 Besoin d'aide ?

**Problèmes avec le simulateur ?**
- Vérifie que Docker tourne : `docker-compose ps`
- Vérifie les logs Kafka : `docker logs kafka`
- Lis le troubleshooting : `docs/03-troubleshooting.md`

**Problèmes avec ton analyzer ?**
- Teste d'abord avec `consumer/consumer.py`
- Vérifie Elasticsearch : `curl http://localhost:9200`

---

## 🔗 Ressources

- **Setup complet** : [docs/01-setup-guide.md](01-setup-guide.md)
- **Format JSON** : [docs/schema.json](schema.json)
- **Architecture** : [docs/04-architecture.md](04-architecture.md)
- **Troubleshooting** : [docs/03-troubleshooting.md](03-troubleshooting.md)

---

## ✅ Résumé

| Fichier | À utiliser ? | Pourquoi |
|---------|--------------|----------|
| `twitter_simulator.py` | ✅ OUI | Fonctionne sans API Twitter |
| `twitter_stream_producer.py` | ❌ NON | Nécessite API Twitter payante |

**Utilise le SIMULATEUR et tout fonctionnera ! 🚀**