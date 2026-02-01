
### 2. `dashboards/README.md`

```markdown
# Dashboards Interactifs – Kibana
*(Personne 3 – Windows)*

## Objectif principal

Créer des visualisations et un dashboard attractif pour présenter :
- Répartition des sentiments
- Hashtags / Topics les plus populaires
- Meilleurs & pires tweets
- Statistiques globales (likes, RT, confiance moyenne)

## Accès Kibana

Ouvre ton navigateur :  
**http://localhost:5601**

## Étape 1 – Créer l’Index Pattern (obligatoire)

1. Menu → **Stack Management** → **Kibana** → **Index Patterns**
2. **Create index pattern**
3. Pattern name : `tweets_analyzed*`
4. Next step → Time field : **aucun** (pas de `@timestamp` pour l’instant)
5. Create index pattern

## Étape 2 – Visualisations recommandées (dans Visualize)

Crée au moins 5–6 visualisations :

| N° | Type de viz         | Nom du dashboard suggéré             | Configuration principale                                      | Objectif                              |
|----|---------------------|--------------------------------------|----------------------------------------------------------------|---------------------------------------|
| 1  | Pie                 | Répartition Sentiments               | Buckets → Terms → `sentiment.keyword`                          | % Positif / Négatif / Neutre          |
| 2  | Vertical Bar        | Top 10 Hashtags                      | Buckets → Terms → `hashtags.keyword` (size:10, order desc)     | Hashtags les plus utilisés            |
| 3  | Horizontal Bar      | Top 10 Topics                        | Buckets → Terms → `topic.keyword` (size:10)                    | Thèmes dominants                      |
| 4  | Data Table          | Meilleurs Tweets (Likes + RT)        | Split rows: Top values `text.keyword` + Metrics: Max like_count, Max retweet_count | Top tweets performants                |
| 5  | Metric              | Tweet le plus liké                   | Metric: Max → `like_count`                                     | Record de likes                       |
| 6  | Lens / Data Table   | Tweets Négatifs les plus likés       | Filter: `sentiment:negatif` + Sort by like_count desc          | Pires tweets (impact négatif fort)    |
| 7  | Tag Cloud (option)  | Nuage de mots                        | Terms → `text` (analyzer standard), size 30                    | Mots fréquents visuels                |

## Étape 3 – Créer le Dashboard

1. Menu → **Dashboard** → **Create dashboard**
2. Ajoute toutes les visualisations créées ci-dessus
3. Organise-les (exemple de layout) :
   - Haut : Pie Sentiments + Metric "Tweet le plus liké"
   - Milieu : Top Hashtags + Top Topics
   - Bas : Data Table "Meilleurs Tweets" + "Tweets Négatifs"
4. Ajoute un contrôle Markdown en haut :

   ```markdown
   # Twitter Real-Time Analytics
   Pipeline local : Simulateur → Kafka → OpenAI → Elasticsearch → Kibana  
   Projet – Analyse de sentiments et tendances en temps réel