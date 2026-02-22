# Real-time Tweets Streaming

Ce projet met en place un pipeline de traitement en temps réel de tweets avec Kafka, Elasticsearch, Kibana et un service `analyzer_improved.py` pour analyser et indexer les tweets.

## Guide pratique pour suivre et tester le pipeline

### 1️⃣ Consulter les logs en temps réel

Pour voir ce que fait le service `analyzer_improved` :

```bash
docker logs -f analyzer_improved
```

- `-f` = “follow” → affiche les nouveaux logs en temps réel.
- Tu verras quand un tweet est traité, indexé dans Elasticsearch ou envoyé dans le DLQ.

---

### 2️⃣ Vérifier les topics Kafka

#### a) Consommer le topic principal (`tweets_raw`)

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic tweets_raw \
  --from-beginning
```

- Affiche les tweets bruts qui arrivent dans Kafka.
- Supprime `--from-beginning` pour ne voir que les nouveaux messages.

#### b) Consommer le DLQ (`tweets_failed`)

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic tweets_failed \
  --from-beginning
```

- Montre les tweets qui n’ont pas pu être indexés (ex. problème de connexion Elasticsearch).

---

### 3️⃣ Tester l’indexation dans Elasticsearch

Voir tous les indices existants :

```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

Afficher les 5 derniers documents :

```bash
curl -X GET "http://localhost:9200/tweets/_search?size=5&sort=indexed_at:desc"
```

- Change `size=5` pour plus de documents.

---

### 4️⃣ Consulter via Kibana

- Ouvre ton navigateur : [http://localhost:5601](http://localhost:5601)
- Crée un **Index Pattern** sur ton index `tweets`
- Explorer les documents, visualiser les statistiques, appliquer des filtres.

---

### 5️⃣ Vérifier l’état des services Docker

```bash
docker compose ps
```

- Permet de voir si **Kafka, Elasticsearch, Kibana, analyzer_improved** sont bien "Up" et healthy.

---

💡 **Astuce** : Si tu ajoutes de nouveaux tweets dans Kafka, ils seront automatiquement traités et indexés par `analyzer_improved`.

---

### 6️⃣ Exemple de test rapide

Tu peux injecter un tweet de test dans Kafka :

```bash
docker exec -i kafka kafka-console-producer \
  --bootstrap-server kafka:29092 \
  --topic tweets_raw <<EOF
{"tweet_id": "12345", "text": "Test tweet for analyzer_improved", "created_at": "2026-02-21T10:00:00", "user": "test_user", "lang": "en", "hashtags": ["Test"], "retweet_count": 0, "like_count": 0}
EOF
```

- Vérifie ensuite les logs de `analyzer_improved` et Elasticsearch pour voir si le tweet est bien indexé.
---

## 🧱 Architecture globale

- **Kafka** : ingestion et transport des tweets
- **Python consumers** : analyse des tweets + gestion des erreurs
- **Elasticsearch** : indexation et recherche
- **Docker & Docker Compose** : orchestration

Topics Kafka :
- `tweets_raw` → tweets entrants
- `tweets_failed` → tweets échoués (erreurs d’analyse ou d’indexation)

Index Elasticsearch :
- `tweets_index_improved`

---

## 🚀 Lancer le projet

```bash
docker compose up
```

Pour quitter les logs sans arrêter les services :
- Appuyer sur `d` (detach)

---

## 🔹 Phase 2 : Vérification de la consommation & des tweets échoués

### 1️⃣ Vérifier que les topics existent

```bash
docker exec -it kafka kafka-topics   --bootstrap-server localhost:29092   --list
```

Tu dois voir :
- `tweets_raw`
- `tweets_failed`

---

### 2️⃣ Vérifier les tweets échoués (format lisible)

```bash
docker exec -it kafka kafka-console-consumer   --bootstrap-server localhost:29092   --topic tweets_failed   --from-beginning   --max-messages 10   | jq '{tweet_id: .original_tweet.tweet_id, text: .original_tweet.text, error_type, error_message, failed_at}'
```

À vérifier :
- présence de `tweet_id`
- type d’erreur (`error_type`)
- message d’erreur (`error_message`)

---

### 3️⃣ Vérifier le groupe de consommateurs Kafka

```bash
docker exec -it kafka kafka-consumer-groups   --bootstrap-server localhost:29092   --describe   --group analyzer-group-v2
```

Résultat attendu :
- `CURRENT-OFFSET = LOG-END-OFFSET`
- `LAG = 0`

➡️ Cela confirme que **tous les tweets ont été consommés**.

---

## 🔹 Phase 3 : Vérification de l’indexation Elasticsearch

### 1️⃣ Vérifier que l’index existe

```bash
curl -X GET "http://localhost:9200/tweets_index_improved?pretty"
```

---

### 2️⃣ Vérifier le mapping

```bash
curl -X GET "http://localhost:9200/tweets_index_improved/_mapping?pretty"
```

Champs attendus :
- `tweet_id`
- `text`
- `hashtags`
- `sentiment`
- `topic`
- `analysis_method`
- `confidence`
- `created_at`

Vérifie que les types correspondent au fichier `mapping_improved.json`.

---

### 3️⃣ Vérifier le nombre total de tweets indexés

```bash
curl -X GET "http://localhost:9200/tweets_index_improved/_search?pretty&q=*:*&size=0"
```

La valeur :
```json
hits.total.value
```
doit correspondre au nombre de tweets générés.

---

### 4️⃣ Vérifier des tweets précis par ID

```bash
curl -s -X GET "http://localhost:9200/tweets_index_improved/_search?pretty" -H 'Content-Type: application/json' -d '{
  "query": {
    "terms": {
      "tweet_id": ["1000191", "1000193", "1000220"]
    }
  }
}' | jq ".hits.hits[]._source | {tweet_id, text}"
```

➡️ Vérifie que :
- les tweets sont bien présents
- le texte correspond

---

### 5️⃣ Vérifier la cohérence des champs indexés

```bash
curl -s -X GET "http://localhost:9200/tweets_index_improved/_search?pretty&q=*:*&size=5" | jq ".hits.hits[]._source | {tweet_id, text, sentiment, topic, analysis_method}"
```

➡️ Chaque document doit contenir **tous les champs du mapping**.

---

## 🧪 Debug rapide (si ça ne marche pas)

- Aucun tweet dans Elasticsearch ?
  - Vérifier que les consumers Python tournent
  - Vérifier `tweets_failed`
- Tweets échoués nombreux ?
  - Vérifier les logs du consumer
  - Vérifier les champs envoyés à Elasticsearch

---

## 📌 Bonnes pratiques

- Utiliser `jq` pour des sorties lisibles
- Vérifier régulièrement `LAG = 0`
- Tester Elasticsearch avec des requêtes simples avant des requêtes complexes

---

## ✅ Validation du projet

✔ Les topics Kafka existent  
✔ Les tweets sont consommés sans lag  
✔ Les erreurs sont stockées dans `tweets_failed`  
✔ Les tweets sont indexés dans `tweets_index_improved`  
✔ Le mapping est respecté  

---
