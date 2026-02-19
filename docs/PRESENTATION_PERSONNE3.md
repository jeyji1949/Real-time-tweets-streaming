# 📊 Twitter Real-Time Analysis Pipeline
## Personne 3 : Visualisation & Stockage

---

# 📋 SOMMAIRE

1. Architecture du Projet
2. Technologies Utilisées
3. Cassandra - Stockage
4. Kibana - Visualisation
5. Réalisations
6. Démonstration
7. Conclusion

---

# 1️⃣ ARCHITECTURE DU PROJET

## Pipeline Complet

---------------------------------------

## Flux de Données

| Étape | Composant | Action |
|-------|-----------|--------|
| 1 | Producer | Génère des tweets simulés |
| 2 | Kafka | File d'attente des messages |
| 3 | Analyzer | Analyse sentiment + topic |
| 4 | Elasticsearch | Indexation pour recherche |
| 5 | Cassandra | Archivage permanent |
| 6 | Kibana | Dashboards interactifs |

---

# 2️⃣ TECHNOLOGIES UTILISÉES

## Apache Cassandra

### Qu'est-ce que Cassandra ?

- Base de données **NoSQL distribuée**
- Conçue par Facebook, maintenue par Apache
- Optimisée pour les **écritures massives**
- **Scalabilité horizontale** illimitée

### Caractéristiques

| Caractéristique | Description |
|-----------------|-------------|
| Type | NoSQL (colonnes) |
| Langage | CQL (Cassandra Query Language) |
| Port | 9042 |
| Réplication | Configurable |
| Performance | Millions d'écritures/seconde |

### Pourquoi Cassandra ?

| Avantage | Description |
|----------|-------------|
| ✅ Haute disponibilité | Pas de point unique de défaillance |
| ✅ Scalabilité | Ajout de nœuds sans downtime |
| ✅ Performance | Écritures ultra-rapides |
| ✅ Archivage | Stockage long terme |

### Cassandra vs Elasticsearch

| Critère | Elasticsearch | Cassandra |
|---------|---------------|-----------|
| Usage | Recherche temps réel | Archivage permanent |
| Rétention | 7 jours (défaut) | Illimitée |
| Requêtes | Agrégations complexes | Requêtes simples |
| Coût stockage | Élevé | Faible |

---

## Kibana

### Qu'est-ce que Kibana ?

- Interface de **visualisation** pour Elasticsearch
- Développé par Elastic
- Dashboards **interactifs** et **temps réel**
- Aucun code requis

### Caractéristiques

| Caractéristique | Description |
|-----------------|-------------|
| Type | Outil de visualisation |
| Port | 5601 |
| Source | Elasticsearch |
| Mise à jour | Temps réel |

### Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 📊 Discover | Explorer les données brutes |
| 📈 Visualize | Créer des graphiques |
| 🎛️ Dashboard | Combiner les visualisations |
| ⏰ Auto-refresh | Mise à jour automatique |
| 📤 Export | Sauvegarder les configurations |

### Types de Visualisations

- **Pie Chart** : Distribution (sentiments)
- **Bar Chart** : Comparaison (topics)
- **Line Chart** : Évolution temporelle
- **Tag Cloud** : Fréquence (hashtags)
- **Table** : Données tabulaires (top users)
- **Metric** : Valeur unique (total tweets)

---

# 3️⃣ CASSANDRA - STOCKAGE

## Schéma de Données

### Keyspace

```sql
CREATE KEYSPACE twitter_analytics
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};