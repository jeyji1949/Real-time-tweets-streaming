Projet : Real-Time Tweets Streaming
Partie : Personne 2 – Analyse & Indexation

1️⃣ Objectif de la partie Personne 2
La partie Personne 2 a pour objectif de :
    • Consommer les tweets depuis Kafka
    • Analyser chaque tweet (sentiment + topic)
    • Enrichir les données
    • Indexer les résultats dans Elasticsearch
    • Rendre les données exploitables dans Kibana
📌 Cette partie constitue le cœur analytique du projet.

2️⃣ Architecture globale (rôle de Personne 2)
Kafka  →  Analyzer (Python)  →  Elasticsearch  →  Kibana
Responsabilités exactes
Élément
Rôle
Kafka
Fournit les tweets en streaming
Analyzer
Analyse NLP & enrichissement
Elasticsearch
Stockage + recherche
Kibana
Visualisation

3️⃣ Mise en place de l’environnement
Technologies utilisées
    • Python 3.10
    • Kafka
    • Docker & Docker Compose
    • Elasticsearch 8.x
    • Kibana
    • TextBlob (NLP)
Choix clés
    • Dockerisation pour reproductibilité
    • NLP local (pas d’API payante)
    • Index Elasticsearch structuré

4️⃣ Étape Kafka – Consommation des tweets
Fonctionnement
    • L’analyzer écoute le topic Kafka tweets
    • Chaque message est un tweet JSON
Validation
    • Connexion Kafka vérifiée au démarrage
    • Lecture continue des messages
✔️ Kafka fonctionne comme source unique de vérité

5️⃣ Analyse NLP (cœur du travail)
Choix final : TextBlob
Pourquoi TextBlob ?
    • Gratuit
    • Léger
    • Fonctionne hors ligne
    • Suffisant pour un projet académique
Analyses effectuées
    1. Sentiment
        ◦ positive / neutral / negative
    2. confidence
        ◦ -1, 0, +1
    3. Topic
        ◦ Basé sur mots-clés (AI, Data, Web, Security, Cloud…)
Exemple de résultat
{
  "sentiment": "positive",
  "confidence": 1,
  "topic": "AI",
  "analysis_method": "textblob"
}

6️⃣ Enrichissement du tweet
Chaque tweet est enrichi avec :
    • sentiment
    • confidence
    • topic
    • méthode d’analyse
    • word frequency
    • hashtags extraits
    • timestamp
📌 Le tweet devient une donnée analytique, pas seulement textuelle.

7️⃣ Gestion des erreurs (robustesse)
Problèmes rencontrés
    • APIs payantes (OpenAI)
    • IA locale instable (Ollama)
    • Exceptions Python
    • Messages Kafka corrompus
Stratégie adoptée
    • Try/Except systématique
    • Valeurs par défaut
    • Aucun crash du service
✔️ Le streaming ne s’arrête jamais

8️⃣ Elasticsearch – Indexation
Nom de l’index
tweets_index
Mapping structuré
{
  "tweet_id": "keyword",
  "text": "text",
  "created_at": "date",
  "user": "keyword",
  "hashtags": "keyword",
  "sentiment": "keyword",
  "confidence": "integer",
  "topic": "keyword",
  "analysis_method": "keyword",
  "word_freq": "object"
}
Bonnes pratiques
    • Mapping défini AVANT indexation
    • Types compatibles avec Kibana
    • Données normalisées

9️⃣ Vérification Elasticsearch
Commandes utilisées
curl http://localhost:9200
curl http://localhost:9200/_cat/indices?v
curl http://localhost:9200/tweets_index/_search?pretty
Résultat
    • Index présent
    • Documents indexés
    • Champs visibles
✔️ Elasticsearch opérationnel

🔟 Kibana – Préparation & exploitation
Étapes clés
    1. Accès à http://localhost:5601
    2. Création d’index pattern :
       tweets_index
    3. Champ temporel :
       created_at
Visualisations possibles
    • Répartition des sentiments
    • Top topics
    • Évolution temporelle
    • Mots les plus fréquents
📊 Kibana transforme les tweets en insights

1️⃣1️⃣ Docker & orchestration
Services utilisés
    • kafka
    • zookeeper
    • analyzer
    • elasticsearch
    • kibana
Problèmes rencontrés
    • Ports occupés
    • Containers orphelins
    • Réseaux Docker persistants
Solution
docker compose down --remove-orphans
docker network prune -f
docker volume prune -f

1️⃣2️⃣ Résultat final obtenu
Ce qui fonctionne à 100 %
✅ Kafka streaming
✅ Analyzer stable
✅ NLP fonctionnel
✅ Elasticsearch indexé
✅ Kibana prêt
✅ Projet reproductible

