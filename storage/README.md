# Stockage Permanent – Cassandra
*(Personne 3 – Windows)*

## Objectif

Fournir un stockage persistant et scalable pour les tweets analysés, en complément d'Elasticsearch.  
Cassandra est particulièrement adaptée pour :
- Écritures massives et rapides
- Requêtes par clé primaire (tweet_id)
- Stockage historique longue durée
- Haute disponibilité (si cluster plus tard)

**Note** : Cette partie est **optionnelle** pour la démo de base, mais elle ajoute beaucoup de valeur professionnelle au projet.

## Prérequis

- Docker Compose lancé (`docker-compose up -d`)
- Container Cassandra UP :  
  ```powershell
  docker-compose ps | findstr cassandra