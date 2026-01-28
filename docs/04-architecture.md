# Architecture du Système - Twitter Real-Time Analysis

## 🏗️ Vue d'ensemble

Pipeline de streaming temps réel pour l'analyse de tweets utilisant Apache Kafka comme système de messagerie central.

---

## 📊 Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      TWITTER ANALYSIS PIPELINE                   │
└─────────────────────────────────────────────────────────────────┘

                           ┌──────────────┐
                           │   PERSONNE 1 │
                           │    (Kafka)   │
                           └──────┬───────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐         ┌──────────────┐         ┌──────────────┐
│   Simulator   │────────▶│    Kafka     │────────▶│   Consumer   │
│  (Producer)   │  JSON   │  tweets_raw  │  JSON   │   (Reader)   │
└───────────────┘         └──────────────┘         └──────┬───────┘
                                                          │
                          ┌──────────────┐                │
                          │   PERSONNE 2 │                │
                          │ (OpenAI + ES)│                │
                          └──────┬───────┘                │
                                 │                        │
                                 ▼                        ▼
                          ┌──────────────┐         ┌─────────────┐
                          │  OpenAI API  │◀────────│  Analysis   │
                          │  (Sentiment  │         │   Module    │
                          │   + Topics)  │         └─────────────┘
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │Elasticsearch │
                          │   (Index)    │
                          └──────┬───────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
         ┌──────────┐    ┌──────────┐    ┌──────────┐
         │  PERSONNE 3   │          │    │          │
         │  (Viz/Store)  │          │    │          │
         └──────┬───┘    │          │    │          │
                │        │          │    │          │
                ▼        ▼          ▼    ▼          ▼
         ┌──────────┐ ┌──────────┐ ┌──────────┐
         │  Kibana  │ │Cassandra │ │ Storage  │
         │(Dashboards)│(Permanent)│          │
         └──────────┘ └──────────┘ └──────────┘
```

---

## 🔄 Flux de données détaillé

### Étape 1 : Génération (Personne 1)

**Composant** : `producer/twitter_simulator.py`

**Fonction** :
- Génère des tweets réalistes toutes les 1-3 secondes
- Simule des données Twitter authentiques

**Données générées** :
```json
{
  "tweet_id": "1000000",
  "text": "Just finished a ML project! #Python #AI",
  "created_at": "2026-01-26T23:30:00",
  "user": "python_dev",
  "lang": "en",
  "hashtags": ["Python", "AI"],
  "retweet_count": 42,
  "like_count": 156
}
```

---

### Étape 2 : Production vers Kafka (Personne 1)

**Composant** : Kafka Producer dans le simulateur

**Configuration** :
```python
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
```

**Action** :
```python
producer.send('tweets_raw', value=tweet_data)
```

**Topic Kafka** : `tweets_raw`
- 1 partition
- Replication factor: 1
- Retention: 7 jours (168 heures)

---

### Étape 3 : Stockage dans Kafka

**Broker Kafka** :
- Persiste les messages sur disque
- Garantit la durabilité des données
- Permet le replay des messages

**Avantages** :
- ✅ Buffer entre producer et consumer
- ✅ Plusieurs consumers possibles
- ✅ Résilience aux pannes
- ✅ Scalabilité horizontale

---

### Étape 4 : Consommation (Personne 1)

**Composant** : `consumer/consumer.py`

**Configuration** :
```python
consumer = KafkaConsumer(
    'tweets_raw',
    bootstrap_servers='localhost:9092',
    group_id='tweet-consumer-group',
    auto_offset_reset='earliest'
)
```

**Fonction** :
- Lit les tweets depuis Kafka
- Affiche en temps réel
- Transmet à l'étape suivante

---

### Étape 5 : Analyse (Personne 2) ⏳

**Composants** :
- Module d'analyse OpenAI
- Indexation Elasticsearch

**Fonctions prévues** :
1. Analyser le sentiment (positif/négatif/neutre)
2. Extraire les topics principaux
3. Indexer dans Elasticsearch

**Format enrichi** :
```json
{
  "tweet_id": "1000000",
  "text": "Just finished a ML project!",
  "sentiment": "positive",      // ← Ajouté par OpenAI
  "topic": "Machine Learning",  // ← Ajouté par OpenAI
  "confidence": 0.95,
  ...
}
```

---

### Étape 6 : Visualisation (Personne 3) ⏳

**Composants** :
- Kibana pour dashboards
- Cassandra pour stockage permanent

**Dashboards prévus** :
- Distribution des sentiments
- Top hashtags
- Timeline des tweets
- Carte des mots-clés

---

## 🐳 Infrastructure Docker

### Services déployés

| Service | Image | Port | Fonction |
|---------|-------|------|----------|
| Zookeeper | `confluentinc/cp-zookeeper:7.4.0` | 2181 | Coordination Kafka |
| Kafka | `confluentinc/cp-kafka:7.4.0` | 9092 | Message broker |
| Elasticsearch | `elastic/elasticsearch:8.11.0` | 9200 | Indexation |
| Kibana | `elastic/kibana:8.11.0` | 5601 | Visualisation |
| Cassandra | `cassandra:4.1` | 9042 | Base NoSQL |

### Configuration réseau

**Kafka Listeners** :
```yaml
KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
```

**Explication** :
- `kafka:29092` : Communication interne Docker
- `localhost:9092` : Communication depuis la machine hôte

---

## 🔧 Technologies utilisées

### Backend

| Tech | Version | Usage |
|------|---------|-------|
| Python | 3.12 | Langage principal |
| kafka-python | 2.0.2 | Client Kafka |
| Docker | 20.10+ | Conteneurisation |
| Docker Compose | 2.0+ | Orchestration |

### Kafka Ecosystem

| Composant | Rôle |
|-----------|------|
| Zookeeper | Gestion de la configuration Kafka |
| Broker | Stockage et distribution des messages |
| Topics | Canaux de communication |
| Partitions | Parallélisation du traitement |

### Data Stack (à venir)

| Tech | Version | Usage (Personne 2/3) |
|------|---------|----------------------|
| OpenAI API | GPT-4 | Analyse NLP |
| Elasticsearch | 8.11.0 | Indexation fulltext |
| Kibana | 8.11.0 | Dashboards |
| Cassandra | 4.1 | Stockage NoSQL |

---

## 📊 Métriques et performances

### Capacités actuelles

- **Throughput** : ~1 tweet/1-3 secondes (configurable)
- **Latence** : < 100ms entre producer et consumer
- **Durabilité** : Messages persistés 7 jours
- **Scalabilité** : 1 partition (extensible à N partitions)

### Limites actuelles

- 1 broker Kafka (pas de haute disponibilité)
- 1 partition (pas de parallélisation)
- Pas de réplication (factor = 1)

### Améliorations possibles

Pour production :
- 3+ brokers Kafka (haute disponibilité)
- Réplication factor = 3
- Multiples partitions (parallélisation)
- Monitoring (Prometheus + Grafana)

---

## 🔐 Sécurité

### Actuel (Développement)

- ❌ Pas d'authentification Kafka
- ❌ Pas de chiffrement
- ❌ Pas de contrôle d'accès

**⚠️ Configuration de développement uniquement !**

### Pour Production

Ajouter :
- ✅ SASL authentication
- ✅ SSL/TLS encryption
- ✅ ACL (Access Control Lists)
- ✅ Secrets management (Vault)

---

## 🔄 États du système

### État 1 : Démarrage

```
Docker Compose up → Zookeeper démarre (5s)
                  → Kafka démarre (30s)
                  → ES/Kibana/Cassandra démarrent (30s)
                  → Topic auto-créé au 1er message
```

### État 2 : Fonctionnement normal

```
Simulator → Kafka → Consumer
  (1-3s)     (<100ms)   (temps réel)
```

### État 3 : Arrêt

```
Ctrl+C → Producer s'arrête
       → Consumer s'arrête
       → Messages restent dans Kafka (7 jours)
```

---

## 📁 Structure du projet

```
Twitter-Project/
├── docker-compose.yml      # Infrastructure
├── .env                    # Configuration
├── requirements.txt        # Dépendances Python
│
├── producer/               # Personne 1
│   ├── twitter_simulator.py
│   ├── test_simple_producer.py
│   └── README.md
│
├── consumer/               # Personne 1
│   ├── consumer.py
│   └── README.md
│
├── analysis/               # Personne 2 (à faire)
│   └── README.md
│
├── storage/                # Personne 3 (à faire)
│   └── README.md
│
├── dashboards/             # Personne 3 (à faire)
│   └── README.md
│
└── docs/                   # Documentation
    ├── 01-setup-guide.md
    ├── 02-demo.md
    ├── 03-troubleshooting.md
    ├── 04-architecture.md
    └── schema.json
```

---

## 🎯 État d'avancement

### ✅ Complété (Personne 1)

- [x] Infrastructure Docker
- [x] Topic Kafka `tweets_raw`
- [x] Simulateur de tweets
- [x] Producer Kafka
- [x] Consumer Kafka
- [x] Tests et validation
- [x] Documentation

### ⏳ En attente (Personne 2)

- [ ] Intégration OpenAI
- [ ] Analyse des sentiments
- [ ] Extraction de topics
- [ ] Indexation Elasticsearch

### ⏳ En attente (Personne 3)

- [ ] Dashboards Kibana
- [ ] Stockage Cassandra
- [ ] Visualisations finales

---

## 🔗 Interfaces de communication

### Entre Personne 1 et Personne 2

**Topic Kafka** : `tweets_raw`  
**Format** : JSON (voir `schema.json`)  
**Fréquence** : ~1 tweet/1-3 secondes

### Entre Personne 2 et Personne 3

**Elasticsearch** : `http://localhost:9200`  
**Index** : `tweets_analyzed`  
**Format** : JSON enrichi avec sentiment et topic

---

## 📚 Références

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [kafka-python](https://kafka-python.readthedocs.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

---

**Architecture mise à jour** : 26 janvier 2026  
**Version** : 1.0  
**Auteur** : EL KHRAIBI Jihane (Pipeline Kafka)
