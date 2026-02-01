# 📥 Consumer Kafka - Réception des Tweets

## 🎯 Description

Le consumer Kafka lit les tweets en temps réel depuis le topic `tweets_raw` et les affiche dans la console.

**Rôle dans le pipeline** :
```
[Simulateur] → [Kafka: tweets_raw] → [Consumer] → [Affichage/Traitement]
                                          ↑
                                       VOUS ÊTES ICI
```

---

## 📁 Fichiers

| Fichier | Description | Usage |
|---------|-------------|-------|
| `consumer.py` | Consumer principal | `python consumer.py` |
| `README.md` | Ce fichier | Documentation |

---

## 🚀 Utilisation

### Démarrage du consumer

```bash
# 1. Activer le venv
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate

# 2. Aller dans consumer
cd consumer

# 3. Lancer le consumer
python consumer.py
```

### Résultat attendu

```
================================================================================
📥 KAFKA CONSUMER - Réception des tweets
================================================================================
📡 Kafka Broker: localhost:9092
📮 Topic: tweets_raw
================================================================================

🔄 Tentative de connexion à Kafka (1/10)...
✅ Connexion à Kafka réussie !

⏸️  Ctrl+C pour arrêter
================================================================================

👂 En écoute des tweets...

📩 Tweet #1 reçu
   ID: 1000000
   👤 User: python_dev
   📝 Text: Just finished a machine learning project! #Python #AI
   🌍 Lang: en
   #️⃣  Hashtags: #Python, #AI
   🔄 Retweets: 42
   ❤️  Likes: 156
--------------------------------------------------------------------------------
📩 Tweet #2 reçu
   ID: 1000001
   👤 User: ai_researcher
   📝 Text: Amazing tutorial on neural networks! #MachineLearning
   🌍 Lang: en
   #️⃣  Hashtags: #MachineLearning
   🔄 Retweets: 67
   ❤️  Likes: 342
--------------------------------------------------------------------------------
```

**Le consumer reste ouvert et affiche chaque tweet au fur et à mesure qu'il arrive.**

---

## 🔧 Comment ça marche ?

### 1. Configuration

```python
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'tweets_raw')
```

Le consumer lit la configuration depuis `../.env` :
- **Broker** : Adresse du serveur Kafka
- **Topic** : Nom du topic à lire

---

### 2. Création du consumer

```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,                    # Topic à écouter
    bootstrap_servers=KAFKA_BROKER, # Adresse Kafka
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),  # Décode JSON
    auto_offset_reset='earliest',   # Lire depuis le début
    enable_auto_commit=True,        # Sauvegarder la position
    group_id='tweet-consumer-group' # Groupe de consumers
)
```

**Explications** :

| Paramètre | Explication |
|-----------|-------------|
| `bootstrap_servers` | Où se trouve Kafka (localhost:9092) |
| `value_deserializer` | Convertit les bytes en JSON Python |
| `auto_offset_reset='earliest'` | Si premier lancement, lire depuis le début |
| `enable_auto_commit=True` | Kafka sauvegarde automatiquement où on en est |
| `group_id` | Identifiant du groupe de consumers |

---

### 3. Boucle de lecture

```python
for message in consumer:
    tweet = message.value  # Extraire le JSON du message
    
    # Afficher les informations
    print(f"📩 Tweet #{tweet_count} reçu")
    print(f"   ID: {tweet['tweet_id']}")
    print(f"   👤 User: {tweet['user']}")
    print(f"   📝 Text: {tweet['text'][:100]}...")
    # etc.
```

**La boucle tourne indéfiniment** jusqu'à `Ctrl+C`.

---

### 4. Retry logic (connexion automatique)

Si Kafka n'est pas encore prêt, le consumer essaie 10 fois :

```python
for attempt in range(1, max_retries + 1):
    try:
        consumer = KafkaConsumer(...)
        print("✅ Connexion réussie")
        break
    except NoBrokersAvailable:
        print(f"⚠️  Tentative {attempt}/10...")
        time.sleep(3)
```

**Avantage** : Pas besoin de relancer manuellement si Kafka démarre lentement.

---

## 📊 Format des données reçues

Chaque message reçu est un **objet JSON** :

```json
{
  "tweet_id": "1000000",
  "text": "Just finished a machine learning project! #Python #AI",
  "created_at": "2026-01-27T10:30:00.000Z",
  "user": "python_dev",
  "lang": "en",
  "hashtags": ["Python", "AI"],
  "retweet_count": 42,
  "like_count": 156
}
```

**Voir le schéma complet** : [../docs/schema.json](../docs/schema.json)

---

## 🎯 À quoi sert le consumer ?

### Rôle dans le projet

Le consumer a **3 fonctions principales** :

1. **Vérifier que le pipeline fonctionne**
   - Si les tweets s'affichent → Le producer et Kafka fonctionnent ✅

2. **Débugger le flux de données**
   - Voir les tweets bruts avant traitement
   - Vérifier le format JSON

3. **Base pour Personne 2**
   - Ce code montre comment se connecter à Kafka
   - Personne 2 peut s'en inspirer pour son analyzer

---

## 🔧 Configuration avancée

### Changer le group ID

Si vous voulez plusieurs consumers indépendants :

```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    group_id='mon-consumer-unique'  # ← Changer ici
)
```

**Avec le même group_id** : Les consumers se partagent les messages (load balancing)  
**Avec des group_id différents** : Chaque consumer reçoit TOUS les messages

---

### Lire depuis le dernier message

```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    auto_offset_reset='latest'  # ← Lire seulement les nouveaux
)
```

**'earliest'** : Lire tous les messages depuis le début (par défaut)  
**'latest'** : Lire seulement les nouveaux messages

---

### Ajouter un timeout

```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    consumer_timeout_ms=10000  # Arrête après 10s sans message
)
```

**⚠️ Attention** : Avec un timeout, le consumer s'arrête s'il ne reçoit rien !

---

## 🧪 Tests

### Test 1 : Vérifier que Kafka tourne

```bash
docker-compose ps | grep kafka
# Doit afficher : Up
```

### Test 2 : Vérifier que le topic existe

```bash
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092
# Doit afficher : tweets_raw
```

### Test 3 : Lire manuellement le topic

```bash
docker exec -it kafka \
  kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic tweets_raw \
  --from-beginning \
  --max-messages 5
```

**Si vous voyez des messages JSON** → Le topic contient des données ✅

---

## 🐛 Dépannage

### Problème 1 : "ModuleNotFoundError: No module named 'kafka'"

**Cause** : venv pas activé

**Solution** :
```bash
source ../venv/bin/activate
```

**Vérifier** :
```bash
which python
# Doit contenir "venv"
```

---

### Problème 2 : "NoBrokersAvailable"

**Cause** : Kafka pas encore prêt ou pas démarré

**Solution** :
```bash
# Vérifier Docker
docker-compose ps

# Si pas UP
docker-compose up -d
sleep 90

# Vérifier Kafka
docker logs kafka | grep "started"
```

---

### Problème 3 : Le consumer se connecte mais ne reçoit rien

**Causes possibles** :

1. **Le producer n'est pas lancé**
   ```bash
   # Terminal 2
   cd producer
   python twitter_simulator.py
   ```

2. **Le topic est vide**
   ```bash
   # Vérifier
   docker exec -it kafka \
     kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic tweets_raw \
     --from-beginning \
     --max-messages 1
   ```

3. **Offset déjà au bout**
   ```bash
   # Réinitialiser le consumer group
   docker exec -it kafka \
     kafka-consumer-groups \
     --bootstrap-server localhost:9092 \
     --group tweet-consumer-group \
     --reset-offsets \
     --to-earliest \
     --topic tweets_raw \
     --execute
   ```

---

### Problème 4 : Le consumer se ferme immédiatement

**Cause** : Un timeout est configuré dans le code

**Solution** : Vérifier qu'il n'y a PAS cette ligne dans `consumer.py` :
```python
consumer_timeout_ms=1000  # ← À SUPPRIMER
```

---

## 🔄 Workflow typique

### Démarrage du pipeline complet

**Terminal 1 - Consumer :**
```bash
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd consumer
python consumer.py
```

**Terminal 2 - Producer :**
```bash
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd producer
python twitter_simulator.py
```

**Résultat** : Les tweets du producer apparaissent dans le consumer en temps réel ! 🎉

---

## 📚 Pour aller plus loin

### Modifier l'affichage

Vous pouvez personnaliser comment les tweets sont affichés.

**Exemple - Affichage minimal :**
```python
for message in consumer:
    tweet = message.value
    print(f"[{tweet['user']}] {tweet['text']}")
```

**Exemple - Sauvegarder dans un fichier :**
```python
with open('tweets.log', 'a') as f:
    for message in consumer:
        tweet = message.value
        f.write(json.dumps(tweet) + '\n')
        print(f"✅ Tweet {tweet['tweet_id']} sauvegardé")
```

**Exemple - Filtrer par langue :**
```python
for message in consumer:
    tweet = message.value
    if tweet['lang'] == 'en':  # Seulement anglais
        print(f"📩 Tweet: {tweet['text']}")
```

---

### Créer un consumer personnalisé

Pour **Personne 2**, voici un exemple de consumer qui prépare pour OpenAI :

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'tweets_raw',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='analyzer-group'  # Groupe différent
)

print("📊 Analyzer Consumer - En attente des tweets...")

for message in consumer:
    tweet = message.value
    
    # 1. Analyser avec OpenAI (à implémenter)
    # sentiment = analyze_sentiment(tweet['text'])
    
    # 2. Enrichir le tweet
    # tweet['sentiment'] = sentiment
    
    # 3. Indexer dans Elasticsearch (à implémenter)
    # index_to_elasticsearch(tweet)
    
    print(f"✅ Tweet {tweet['tweet_id']} traité")
```

---

## 🎓 Concepts Kafka importants

### Offset

**Définition** : La position du consumer dans le topic (quel message il lit)

**Exemple** :
```
Topic tweets_raw:
  Offset 0: Tweet #1
  Offset 1: Tweet #2
  Offset 2: Tweet #3  ← Consumer est ici
  Offset 3: Tweet #4
```

Si le consumer s'arrête et redémarre, il reprend à l'offset 2.

---

### Consumer Group

**Définition** : Groupe de consumers qui partagent la lecture d'un topic

**Exemple 1 - Même groupe** :
```
Consumer A (group: 'team1') → Lit 50% des messages
Consumer B (group: 'team1') → Lit 50% des messages
```

**Exemple 2 - Groupes différents** :
```
Consumer A (group: 'team1') → Lit 100% des messages
Consumer B (group: 'team2') → Lit 100% des messages (indépendant)
```

---

### Auto-commit

**Définition** : Kafka sauvegarde automatiquement l'offset

**Avantage** : Si le consumer crash, il reprend où il en était  
**Inconvénient** : Peut perdre des messages si crash avant traitement

---

## 🔗 Ressources

- **Documentation Kafka** : [kafka.apache.org](https://kafka.apache.org/documentation/)
- **kafka-python** : [kafka-python.readthedocs.io](https://kafka-python.readthedocs.io/)
- **Schéma JSON** : [../docs/schema.json](../docs/schema.json)
- **Architecture** : [../docs/04-architecture.md](../docs/04-architecture.md)

---

## 📞 Support

**Problèmes avec le consumer ?**
- Consulter [../docs/03-troubleshooting.md](../docs/03-troubleshooting.md)
- Vérifier que Docker tourne : `docker-compose ps`
- Vérifier les logs Kafka : `docker logs kafka`

**Pour Personne 2** : Voir [../docs/05-handoff-to-person2.md](../docs/05-handoff-to-person2.md)

---

## ✅ Checklist

```
☐ Docker Compose lancé (docker-compose up -d)
☐ Kafka démarré (docker logs kafka | grep "started")
☐ venv activé (source ../venv/bin/activate)
☐ Topic existe (kafka-topics --list)
☐ Producer lancé (python ../producer/twitter_simulator.py)
☐ Consumer lancé (python consumer.py)
☐ Les tweets s'affichent en temps réel
```

---

**Le consumer est la porte d'entrée vers l'analyse des données ! 🚪📊**