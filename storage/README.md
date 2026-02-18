# 🗃️ CASSANDRA - Stockage des Tweets

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Installation et Configuration](#installation-et-configuration)
4. [Schéma de données](#schéma-de-données)
5. [Synchronisation ES → Cassandra](#synchronisation-es--cassandra)
6. [Requêtes et Vérifications](#requêtes-et-vérifications)
7. [Dépannage](#dépannage)

---

## Vue d'ensemble

### 🎯 Rôle de Cassandra dans le projet

[Producer] → [Kafka] → [Analyzer] → [Elasticsearch] → [Cassandra]
↓ ↓
Analyse temps Archivage
réel long terme


**Cassandra** stocke les tweets analysés pour :
- ✅ Archivage permanent (Elasticsearch garde 7 jours)
- ✅ Requêtes rapides par topic, sentiment, user
- ✅ Scalabilité horizontale

---

## Prérequis

### Services Docker requis

| Service | Port | Statut requis |
|---------|------|---------------|
| Cassandra | 9042 | Running |
| Elasticsearch | 9200 | Running (healthy) |

### Vérifier les services

```powershell
cd D:\Projets\real-time-tweets-streaming
docker compose ps