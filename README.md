# 🐦 Twitter Real-Time Analysis Pipeline

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Kafka](https://img.shields.io/badge/Kafka-3.6-red.svg)](https://kafka.apache.org)
[![Docker](https://img.shields.io/badge/Docker-required-blue.svg)](https://docker.com)

Système d'analyse de tweets en temps réel utilisant Kafka, OpenAI, Elasticsearch, Cassandra et Kibana.

## 🎯 Objectifs du projet

Analyser des tweets en temps réel pour extraire :
- ✅ Les hashtags les plus utilisés
- ✅ Les statistiques des sentiments (positif/négatif/neutre)
- ✅ Les mots les plus fréquents
- ✅ Les meilleurs et pires tweets
- ✅ Visualisations interactives avec Kibana

---

## 🏗️ Architecture
```
[Twitter API] 
    ↓
[Kafka Producer] → [Topic: tweets_raw]
    ↓
[Kafka Consumer]
    ↓
[OpenAI API] (analyse sentiment + topics)
    ↓
[Elasticsearch] (indexation + recherche)
    ↓
[Cassandra] (stockage permanent)
    ↓
[Kibana] (visualisation + dashboards)
```

**Schéma détaillé :** Voir [docs/architecture.md](docs/architecture.md)

---

## 👥 Équipe & Responsabilités

| Membre | OS | Composants | Dossiers |
|--------|----|-----------|-----------------------|
| **Personne 1** | Linux | Kafka + Twitter Stream | `producer/`, `consumer/`, `data/` |
| **Personne 2** | Linux | OpenAI + Elasticsearch | `analysis/` |
| **Personne 3** | Windows | Cassandra + Kibana | `storage/`, `dashboards/` |

---

## 🚀 Installation & Setup

### Prérequis

- **Python 3.8+**
- **Docker & Docker Compose**
- **Compte développeur Twitter** ([developer.twitter.com](https://developer.twitter.com))
- **Clé API OpenAI** (pour Personne 2)

### Setup rapide
```bash
# 1. Cloner le repo
git clone https://github.com/votre-username/Twitter-Project.git
cd Twitter-Project

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env  # Ajouter vos clés API

# 5. Lancer Docker (Kafka, Elasticsearch, Kibana, Cassandra)
docker-compose up -d

# 6. Vérifier que tous les services sont UP
docker-compose ps
```

---

## 🎮 Utilisation

### Terminal 1 : Lancer le Producer (Twitter → Kafka)
```bash
source venv/bin/activate
cd producer/
python twitter_stream_producer.py
```

### Terminal 2 : Lancer le Consumer (Kafka → Analyse)
```bash
source venv/bin/activate
cd consumer/
python consumer.py
```

### Terminal 3 : Analyse OpenAI (Personne 2)
```bash
source venv/bin/activate
cd analysis/
python openai_analyzer.py
```

---

## 📊 Accès aux interfaces

| Service | URL | Description |
|---------|-----|-------------|
| **Kibana** | http://localhost:5601 | Dashboards & visualisations |
| **Elasticsearch** | http://localhost:9200 | API REST pour requêtes |
| **Kafka** | localhost:9092 | Broker Kafka |
| **Cassandra** | localhost:9042 | Base de données NoSQL |

---

## 📁 Structure du projet
```
Twitter-Project/
├── producer/          # Stream Twitter → Kafka
├── consumer/          # Kafka → Processing
├── analysis/          # OpenAI + Elasticsearch (Personne 2)
├── storage/           # Cassandra setup (Personne 3)
├── dashboards/        # Kibana dashboards (Personne 3)
├── data/              # Datasets & samples
├── docs/              # Documentation technique
└── tests/             # Tests unitaires
```

**Voir les README spécifiques dans chaque dossier pour plus de détails.**

---

## 🔧 Configuration

### Variables d'environnement (.env)
```bash
# Twitter API
TWITTER_BEARER_TOKEN=your_token_here
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here

# Kafka
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC_RAW=tweets_raw
KAFKA_TOPIC_ANALYZED=tweets_analyzed

# OpenAI (Personne 2)
OPENAI_API_KEY=your_openai_key_here

# Elasticsearch
ELASTICSEARCH_HOST=localhost:9200

# Cassandra
CASSANDRA_HOST=localhost:9042
```

**⚠️ Ne jamais commit le fichier `.env` ! Utilisez `.env.example` comme template.**

---

## 📚 Documentation

- [Architecture détaillée](docs/04-architecture.md)
- [Schéma JSON](docs/schema.json)
- [Guide de setup complet](docs/01-setup-guide.md)
- [Producer README](producer/README.md)
- [Consumer README](consumer/README.md)
- [Analysis README](analysis/README.md)

---

## 🧪 Tests
```bash
# Tester la connexion Twitter
python producer/test_twitter.py

# Tester Kafka
python tests/test_kafka.py

# Tester Elasticsearch
python tests/test_elasticsearch.py
```

---

## 🐛 Dépannage

### Kafka ne démarre pas
```bash
docker-compose down
docker-compose up -d
docker logs kafka
```

### Tweets n'arrivent pas
- Vérifier le Bearer Token dans `.env`
- Vérifier les règles de filtrage dans `producer/twitter_stream_producer.py`
- Consulter les logs : `docker logs kafka`

### Elasticsearch inaccessible
```bash
curl http://localhost:9200
# Si erreur, restart: docker-compose restart elasticsearch
```

---

## 📝 TODO & Améliorations

- [ ] Ajouter des tests unitaires
- [ ] Implémenter le retry logic pour OpenAI
- [ ] Créer des dashboards Kibana avancés
- [ ] Ajouter monitoring avec Prometheus
- [ ] Documentation API complète

---

## 👨‍💻 Contributeurs

- **Personne 1** - Kafka Pipeline & Twitter Integration
- **Personne 2** - OpenAI Analysis & Elasticsearch
- **Personne 3** - Cassandra & Kibana Dashboards

---
## ✅ État d'avancement - Personne 1 (Kafka Pipeline)

### Infrastructure ✅ TERMINÉ
- [x] Docker Compose configuré avec 5 services
- [x] Kafka + Zookeeper opérationnels
- [x] Topic `tweets_raw` créé automatiquement
- [x] Configuration réseau corrigée (ADVERTISED_LISTENERS)

### Code ✅ TERMINÉ
- [x] Simulateur de tweets réaliste (`producer/twitter_simulator.py`)
- [x] Consumer Kafka fonctionnel (`consumer/consumer.py`)
- [x] Tests de validation (`test_simple_producer.py`)
- [x] Scripts de démarrage automatique

### Documentation ✅ TERMINÉ
- [x] Guide d'installation complet (`docs/01-setup-guide.md`)
- [x] Guide de démonstration (`docs/02-demo.md`)
- [x] Guide de dépannage (`docs/03-troubleshooting.md`)
- [x] Architecture du système (`docs/04-architecture.md`)
- [x] Schéma JSON standardisé (`docs/schema.json`)

### Pipeline ✅ OPÉRATIONNEL
```
Simulator → Kafka (tweets_raw) → Consumer
  (1-3s)       (<100ms)            (real-time)
```

---

## 📊 Démonstration rapide

### Lancer le pipeline

**Terminal 1 - Consumer :**
```bash
source venv/bin/activate
cd consumer && python consumer.py
```

**Terminal 2 - Producer :**
```bash
source venv/bin/activate
cd producer && python twitter_simulator.py
```

### Résultat attendu

Les tweets générés par le producer apparaissent instantanément dans le consumer ! 🎉

---

## 🤝 Pour Personne 2 (OpenAI + Elasticsearch)

**Le pipeline Kafka est prêt !**

**Ce qui fonctionne :**
- ✅ Kafka sur `localhost:9092`
- ✅ Topic : `tweets_raw`
- ✅ Format : JSON (voir `docs/schema.json`)
- ✅ ~20 tweets/minute

**Pour démarrer :**
1. Lire le guide : `docs/01-setup-guide.md`
2. Voir le format : `docs/schema.json`
3. Se connecter à Kafka :
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer('tweets_raw', bootstrap_servers='localhost:9092')
```

**Prochaines étapes :**
1. Analyser chaque tweet avec OpenAI
2. Ajouter les champs : `sentiment`, `topic`, `confidence`
3. Indexer dans Elasticsearch

---

## 📚 Documentation complète

Toute la documentation se trouve dans `/docs` :
- **Setup** : [01-setup-guide.md](docs/01-setup-guide.md)
- **Démo** : [02-demo.md](docs/02-demo.md)
- **Troubleshooting** : [03-troubleshooting.md](docs/03-troubleshooting.md)
- **Architecture** : [04-architecture.md](docs/04-architecture.md)
- **Schema** : [schema.json](docs/schema.json)
```
---

## Collaboration rules
- Do NOT push to main
- Work only on your branch
- Use Pull Requests for merging

## 📄 Licence

Ce projet est à usage éducatif dans le cadre du cours de Big Data.

---

## 🆘 Support

Pour toute question :
- Ouvrir une issue sur GitHub
- Contacter l'équipe par email
- Consulter la documentation dans `/docs`
