# Guide d'Installation - Pipeline Kafka (Personne 1)

## 🎯 Objectif

Mettre en place un pipeline de streaming temps réel avec Apache Kafka pour collecter et distribuer des tweets simulés.

---

## 📋 Prérequis

- **OS** : Ubuntu 20.04+ (ou autre distribution Linux)
- **Docker** : 20.10+
- **Docker Compose** : 2.0+
- **Python** : 3.8+
- **Git** : Pour versionner le code

### Vérification des prérequis

```bash
# Docker
docker --version
docker-compose --version

# Python
python3 --version

# Git
git --version
```

---

## 🚀 Installation

### Étape 1 : Cloner le projet

```bash
cd ~/Documents/BIAM/BIGDATA
git clone <URL_DU_REPO>
cd Twitter-Project
```

### Étape 2 : Créer l'environnement virtuel Python

```bash
# Créer le venv
python3 -m venv venv

# Activer le venv
source venv/bin/activate

# Le prompt doit afficher (venv)
```

**⚠️ Important** : Toujours activer le venv avant de lancer les scripts Python !

### Étape 3 : Installer les dépendances Python

```bash
# Installer depuis requirements.txt
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep -E "kafka|tweepy|dotenv"
```

**Dépendances installées** :
- `kafka-python==2.0.2` : Client Kafka
- `tweepy==4.14.0` : API Twitter (non utilisé, remplacé par simulateur)
- `python-dotenv==1.0.0` : Gestion des variables d'environnement

### Étape 4 : Configurer les variables d'environnement

```bash
# Le fichier .env existe déjà à la racine
# Il contient la configuration Kafka
cat .env
```

**Contenu de `.env`** :
```bash
# Kafka Configuration
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=tweets_raw
```

### Étape 5 : Démarrer l'infrastructure Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Attendre 90 secondes que Kafka démarre complètement
sleep 90

# Vérifier que tous les services sont UP
docker-compose ps
```

**Services démarrés** :
- `zookeeper` : Coordination Kafka (port 2181)
- `kafka` : Broker Kafka (port 9092)
- `elasticsearch` : Indexation (port 9200)
- `kibana` : Visualisation (port 5601)
- `cassandra` : Base NoSQL (port 9042)

### Étape 6 : Vérifier Kafka

```bash
# Vérifier que Kafka a bien démarré
docker logs kafka 2>&1 | grep "started"

# Résultat attendu :
# [KafkaServer id=1] started (kafka.server.KafkaServer)

# Lister les topics (doit être vide au début)
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092
```

---

## 🧪 Tests

### Test 1 : Environnement virtuel

```bash
cd producer
python test_env.py
```

**Résultat attendu** :
```
✅ Bearer Token chargé !
```

### Test 2 : Producer simple

```bash
cd producer
python test_simple_producer.py
```

**Résultat attendu** :
```
✅ Producer créé avec succès !
📤 Envoi du message 1...
   ✅ Confirmé - Partition: 0, Offset: 0
```

### Test 3 : Vérifier le topic créé automatiquement

```bash
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092
```

**Résultat attendu** :
```
tweets_raw
```

---

## 🎬 Lancement du pipeline

### Terminal 1 : Consumer

```bash
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd consumer
python consumer.py
```

**Le consumer attend les tweets...**

### Terminal 2 : Producer (Simulateur)

```bash
# Ouvrir un NOUVEAU terminal
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd producer
python twitter_simulator.py
```

**Les tweets commencent à s'afficher dans les deux terminaux !** 🎉

---

## 📊 Format des données

Voir [schema.json](schema.json) pour le format détaillé des tweets.

**Exemple de tweet** :
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

---

## ⏹️ Arrêt du système

### Arrêter le pipeline

Dans chaque terminal : `Ctrl+C`

### Arrêter Docker

```bash
# Arrêter les conteneurs (garde les données)
docker-compose down

# Arrêter ET supprimer les données
docker-compose down -v
```

### Désactiver le venv

```bash
deactivate
```

---

## 🔄 Redémarrage rapide

```bash
# 1. Démarrer Docker
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
docker-compose up -d
sleep 90

# 2. Terminal 1 : Consumer
source venv/bin/activate
cd consumer && python consumer.py

# 3. Terminal 2 : Producer
source venv/bin/activate
cd producer && python twitter_simulator.py
```

---

## 📝 Notes importantes

- **Toujours activer le venv** avant de lancer les scripts Python
- **Attendre 90 secondes** après `docker-compose up -d` pour que Kafka démarre
- **Le topic se crée automatiquement** grâce à `KAFKA_AUTO_CREATE_TOPICS_ENABLE`
- **Ne jamais commit le fichier `.env`** (il est dans `.gitignore`)

---

## 🆘 Besoin d'aide ?

Consultez [03-troubleshooting.md](03-troubleshooting.md) pour les problèmes courants.
