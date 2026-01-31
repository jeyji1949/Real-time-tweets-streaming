# 🐦 Twitter Real-Time Analysis Pipeline

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Kafka](https://img.shields.io/badge/Kafka-3.6-red.svg)](https://kafka.apache.org)
[![Docker](https://img.shields.io/badge/Docker-required-blue.svg)](https://docker.com)

Système d'analyse de tweets en temps réel utilisant Kafka, OpenAI, Elasticsearch, Cassandra et Kibana.

## ⚠️ NOTE IMPORTANTE : Simulateur Local (Pas d'API Twitter)

**Ce projet utilise un SIMULATEUR LOCAL de tweets**, pas l'API Twitter réelle.

- ✅ **Aucun compte Twitter Developer nécessaire**
- ✅ **Aucun Bearer Token requis**
- ✅ **Fonctionne 100% localement**
- ✅ **Gratuit et illimité**

Le simulateur génère des tweets synthétiques réalistes pour tester le pipeline.

---

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
[Simulateur Local]  ← Génère des tweets synthétiques
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

**Schéma détaillé :** Voir [docs/04-architecture.md](docs/04-architecture.md)
**Schéma détaillé :** Voir [docs/04-architecture.md](docs/architecture.md)

---

## 👥 Équipe & Responsabilités

| Membre | OS | Composants | Dossiers |
|--------|----|-----------|-----------------------|
| **Personne 1** | Linux | Kafka + Simulateur | `producer/`, `consumer/`, `data/` |
| **Personne 2** | Linux | OpenAI + Elasticsearch | `analysis/` |
| **Personne 3** | Windows | Cassandra + Kibana | `storage/`, `dashboards/` |

---

## 🚀 Installation & Setup

### Prérequis

- **Python 3.8+**
- **Docker & Docker Compose**
- **Clé API OpenAI** (pour Personne 2 uniquement)

**⚠️ Aucun compte Twitter Developer nécessaire** - Ce projet utilise un simulateur local.

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

# 4. Configurer les variables d'environnement (uniquement Kafka)
# Le fichier .env existe déjà avec la config Kafka
cat .env  # Vérifier la configuration

# 5. Lancer Docker (Kafka, Elasticsearch, Kibana, Cassandra)
docker-compose up -d

# 6. Attendre 90 secondes que Kafka démarre
sleep 90

# 7. Vérifier que tous les services sont UP
docker-compose ps
```

---

## 🎮 Utilisation

### Terminal 1 : Lancer le Producer (Simulateur)

```bash
source venv/bin/activate
cd producer/
python twitter_simulator.py  # ← Simulateur local (pas d'API Twitter)
```

**Vous verrez :**
```
🤖 TWITTER SIMULATOR → KAFKA PRODUCER
================================================================================
📤 Kafka: localhost:9092
📮 Topic: tweets_raw
💡 Simulation de tweets réalistes en temps réel
================================================================================

✅ Tweet #1
   👤 User: @python_dev
   📝 Text: Just finished a machine learning project! #Python #AI
   #️⃣  Hashtags: #Python, #AI
   🔄 RT: 42 | ❤️  Likes: 156
```

---

### Terminal 2 : Lancer le Consumer

```bash
source venv/bin/activate
cd consumer/
python consumer.py
```

**Vous verrez les tweets arriver en temps réel !**

---

### Terminal 3 : Analyse OpenAI (Personne 2)

```bash
source venv/bin/activate
cd analysis/
python analyzer.py
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
├── producer/          # Simulateur de tweets → Kafka
│   ├── twitter_simulator.py      # ← SIMULATEUR (pas d'API Twitter)
│   ├── test_simple_producer.py
│   └── README.md
├── consumer/          # Kafka → Processing
│   ├── consumer.py
│   └── README.md
├── analysis/          # OpenAI + Elasticsearch (Personne 2)
│   └── README.md
├── storage/           # Cassandra setup (Personne 3)
│   └── README.md
├── dashboards/        # Kibana dashboards (Personne 3)
│   └── README.md
├── data/              # Datasets & samples
├── docs/              # Documentation technique
│   ├── 01-setup-guide.md
│   ├── 02-demo.md
│   ├── 03-troubleshooting.md
│   ├── 04-architecture.md
│   ├── 05-handoff-to-person2.md
│   └── schema.json
├── docker-compose.yml
├── requirements.txt
├── .env               # Configuration (Kafka uniquement)
└── README.md
```

---

## 🔧 Configuration

### Variables d'environnement (.env)

**Le fichier `.env` contient UNIQUEMENT la configuration Kafka :**

```bash
# ==================================
# KAFKA CONFIGURATION
# ==================================
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=tweets_raw

# ==================================
# NOTE IMPORTANTE
# ==================================
# Ce projet utilise un SIMULATEUR local
# Aucune clé Twitter API n'est nécessaire
# Le simulateur génère des tweets synthétiques
# ==================================
```

**Pour Personne 2** : Ajouter votre clé OpenAI dans `.env` :
```bash
OPENAI_API_KEY=sk-...
```

**⚠️ Ne jamais commit le fichier `.env` !**

---

## 📚 Documentation complète

| Document | Description |
|----------|-------------|
| [01-setup-guide.md](docs/01-setup-guide.md) | Installation pas à pas |
| [02-demo.md](docs/02-demo.md) | Guide de présentation |
| [03-troubleshooting.md](docs/03-troubleshooting.md) | Résolution de problèmes |
| [04-architecture.md](docs/04-architecture.md) | Architecture du système |
| [05-handoff-to-person2.md](docs/05-handoff-to-person2.md) | Guide pour Personne 2 |
| [schema.json](docs/schema.json) | Format JSON des tweets |

---

## ✅ État d'avancement

### ✅ Personne 1 - Pipeline Kafka (TERMINÉ)

#### Infrastructure
- [x] Docker Compose configuré (Kafka, Zookeeper, ES, Kibana, Cassandra)
- [x] Kafka opérationnel sur localhost:9092
- [x] Topic `tweets_raw` créé automatiquement
- [x] Configuration réseau corrigée

#### Code
- [x] Simulateur de tweets (`producer/twitter_simulator.py`)
- [x] Consumer Kafka (`consumer/consumer.py`)
- [x] Tests de validation
- [x] Scripts de démarrage

#### Documentation
- [x] 5 guides complets dans `/docs`
- [x] Schéma JSON standardisé
- [x] README dans chaque dossier

#### Pipeline
```
✅ Simulateur → Kafka (tweets_raw) → Consumer
     (1-3s)       (<100ms)            (real-time)
```

**Débit** : 20-60 tweets/minute  
**Latence** : < 100ms

---

### ⏳ Personne 2 - Analyse (EN COURS)

#### À faire
- [ ] Lire la documentation : `docs/05-handoff-to-person2.md`
- [ ] Se connecter à Kafka topic `tweets_raw`
- [ ] Analyser avec OpenAI (sentiment, topic, confidence)
- [ ] Indexer dans Elasticsearch
- [ ] Créer le mapping Elasticsearch

#### Format des données

**Entrée** (depuis Kafka) :
```json
{
  "tweet_id": "1000000",
  "text": "Just finished a ML project! #Python #AI",
  "user": "python_dev",
  "lang": "en",
  "hashtags": ["Python", "AI"],
  "retweet_count": 42,
  "like_count": 156
}
```

**Sortie** (vers Elasticsearch) :
```json
{
  ..., // Données ci-dessus
  "sentiment": "positive",      // ← À ajouter
  "topic": "Machine Learning",  // ← À ajouter
  "confidence": 0.95            // ← À ajouter
}
```

---

### ⏳ Personne 3 - Visualisation (EN ATTENTE)

- [ ] Attendre que Personne 2 indexe dans Elasticsearch
- [ ] Créer les dashboards Kibana
- [ ] Configurer Cassandra (optionnel)

---

## 🎬 Démonstration rapide

### Lancer le pipeline complet

**Terminal 1 - Consumer :**
```bash
source venv/bin/activate
cd consumer && python consumer.py
```

**Terminal 2 - Producer (Simulateur) :**
```bash
source venv/bin/activate
cd producer && python twitter_simulator.py
```

**Résultat :** Les tweets générés par le simulateur apparaissent instantanément dans le consumer ! 🎉

---

## 🧪 Tests

### Test 1 : Vérifier que Docker tourne
```bash
docker-compose ps
# Tous les services doivent être "Up"
```

### Test 2 : Vérifier que Kafka est prêt
```bash
docker logs kafka | grep "started"
# Doit afficher : [KafkaServer id=1] started
```

### Test 3 : Tester le simulateur
```bash
cd producer
python test_simple_producer.py
# Doit envoyer 3 messages de test avec succès
```

### Test 4 : Vérifier le topic Kafka
```bash
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092
# Doit afficher : tweets_raw
```

---

## 🐛 Dépannage

### Kafka ne démarre pas

```bash
docker-compose down -v
docker-compose up -d
sleep 90
docker logs kafka | grep "started"
```

### Le simulateur ne se connecte pas

**Erreur :** `NoBrokersAvailable`

**Solution :**
1. Vérifier que Docker tourne : `docker-compose ps`
2. Attendre 90 secondes après `docker-compose up -d`
3. Vérifier Kafka : `docker logs kafka | grep started`

### Pas de tweets dans le consumer

**Vérifier :**
1. Le simulateur est lancé : `python twitter_simulator.py`
2. Le topic existe : `docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092`

**Plus de détails :** Voir [docs/03-troubleshooting.md](docs/03-troubleshooting.md)

---

## 🤝 Pour Personne 2 (OpenAI + Elasticsearch)

### ✅ Ce qui est prêt pour toi

- Kafka opérationnel sur `localhost:9092`
- Topic `tweets_raw` avec ~20-60 tweets/minute
- Format JSON standardisé (voir `docs/schema.json`)
- Docker Compose avec Elasticsearch sur `localhost:9200`

### 📚 Documentation à lire

1. **Guide principal** : [docs/05-handoff-to-person2.md](docs/05-handoff-to-person2.md)
2. **Format des tweets** : [docs/schema.json](docs/schema.json)
3. **Architecture** : [docs/04-architecture.md](docs/04-architecture.md)

### 🚀 Pour démarrer

```bash
# 1. Pull le repo
git pull origin kafka

# 2. Lancer le simulateur
cd producer
python twitter_simulator.py  # ← Génère des tweets

# 3. Dans ton code, te connecter à Kafka
from kafka import KafkaConsumer
consumer = KafkaConsumer(
    'tweets_raw',
    bootstrap_servers='localhost:9092',
    group_id='analyzer-group'
)
```

### 📊 Ce que tu dois faire

1. Lire les tweets depuis Kafka (`tweets_raw`)
2. Analyser avec OpenAI → sentiment, topic, confidence
3. Indexer dans Elasticsearch (`tweets_analyzed`)
4. Préparer le mapping pour Kibana

---

## 💡 Pourquoi un simulateur au lieu de l'API Twitter ?

L'API Twitter gratuite a des limitations strictes depuis 2023 :
- ❌ Pas de streaming en temps réel (Filtered Stream)
- ❌ Limité à 1,500 tweets/mois
- ❌ Nécessite un plan payant ($100+/mois)

**Notre simulateur** :
- ✅ Génère des tweets réalistes avec hashtags, métriques
- ✅ Fonctionne 100% localement
- ✅ Gratuit et illimité
- ✅ Parfait pour tester le pipeline

**Pour passer à la vraie API :** Il suffirait de remplacer `twitter_simulator.py` par un vrai connecteur Tweepy (avec un compte payant).

---

## 📝 TODO & Améliorations

- [ ] Ajouter des tests unitaires complets
- [ ] Implémenter le retry logic pour OpenAI
- [ ] Créer des dashboards Kibana avancés
- [ ] Ajouter monitoring avec Prometheus
- [ ] Documentation API complète

---

## 👨‍💻 Contributeurs

- **Personne 1** - Pipeline Kafka & Simulateur de tweets
- **Personne 2** - Analyse OpenAI & Indexation Elasticsearch
- **Personne 3** - Visualisation Kibana & Stockage Cassandra

---

## 📄 Licence

Ce projet est à usage éducatif dans le cadre du cours de Big Data.

---

## 🆘 Support

Pour toute question :
- Consulter la documentation dans `/docs`
- Ouvrir une issue sur GitHub
- Contacter l'équipe

---

## 🔗 Liens utiles

- [Documentation Kafka](https://kafka.apache.org/documentation/)
- [kafka-python](https://kafka-python.readthedocs.io/)
- [Elasticsearch Guide](https://www.elastic.co/guide/)
- [Docker Compose](https://docs.docker.com/compose/)