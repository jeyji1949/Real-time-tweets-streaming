-- ===========================================
-- Twitter Analytics - Cassandra Schema IMPROVED
-- Personne 3 - Stockage & Visualisation
-- 
-- AMÉLIORATIONS par rapport à schema.cql :
-- ✅ Champ confidence ajouté (compatible analyzer_improved)
-- ✅ Index secondaires pour requêtes avancées
-- ✅ TTL optionnel pour auto-purge
-- ✅ Commentaires détaillés
-- ===========================================

-- Créer le keyspace avec stratégie de réplication
CREATE KEYSPACE IF NOT EXISTS twitter_analytics
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
}
AND durable_writes = true;

USE twitter_analytics;

-- ===========================================
-- TABLE PRINCIPALE : tweets
-- ===========================================
-- Stocke tous les tweets avec toutes leurs métadonnées
-- Clé de partition: tweet_id (recherche par ID exact)
--
CREATE TABLE IF NOT EXISTS tweets (
    tweet_id text PRIMARY KEY,
    
    -- Contenu
    text text,
    user text,
    lang text,
    
    -- Timestamps
    created_at timestamp,     -- Date création du tweet
    indexed_at timestamp,     -- Date d'indexation dans Cassandra
    
    -- Analyse sentiment
    sentiment text,           -- positive | neutral | negative
    confidence float,         -- ✅ NOUVEAU : 0.0 à 1.0 (compatible analyzer_improved)
    score int,                -- 1 | 0 | -1
    
    -- Analyse topic
    topic text,               -- AI | Cloud | Data | Web | etc.
    
    -- Métadonnées
    hashtags list<text>,
    retweet_count int,
    like_count int,
    
    -- Méthode d'analyse
    analysis_method text      -- textblob | openai | vader
);

-- ✅ Index secondaire pour recherche par user (optionnel)
-- CREATE INDEX IF NOT EXISTS ON tweets (user);

-- ✅ Index secondaire pour recherche par sentiment (optionnel)
-- CREATE INDEX IF NOT EXISTS ON tweets (sentiment);


-- ===========================================
-- TABLE : tweets_by_topic
-- ===========================================
-- Optimisée pour requêtes: "Tous les tweets d'un topic"
-- Clé de partition: topic
-- Clé de clustering: created_at (ordre DESC)
-- Exemple: SELECT * FROM tweets_by_topic WHERE topic='AI' LIMIT 10
--
CREATE TABLE IF NOT EXISTS tweets_by_topic (
    topic text,
    created_at timestamp,
    tweet_id text,
    text text,
    user text,
    sentiment text,
    confidence float,         -- ✅ NOUVEAU
    PRIMARY KEY ((topic), created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC)
AND comment = 'Tweets ordonnés par topic et date';


-- ===========================================
-- TABLE : tweets_by_user
-- ===========================================
-- Optimisée pour requêtes: "Tous les tweets d'un user"
-- Clé de partition: user
-- Clé de clustering: created_at (ordre DESC)
-- Exemple: SELECT * FROM tweets_by_user WHERE user='python_dev' LIMIT 10
--
CREATE TABLE IF NOT EXISTS tweets_by_user (
    user text,
    created_at timestamp,
    tweet_id text,
    text text,
    sentiment text,
    topic text,
    confidence float,         -- ✅ NOUVEAU
    PRIMARY KEY ((user), created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC)
AND comment = 'Tweets ordonnés par utilisateur et date';


-- ===========================================
-- TABLE : tweets_by_sentiment
-- ===========================================
-- Optimisée pour requêtes: "Tous les tweets positifs/négatifs"
-- Clé de partition: sentiment
-- Clé de clustering: created_at (ordre DESC)
-- Exemple: SELECT * FROM tweets_by_sentiment WHERE sentiment='positive' LIMIT 10
--
CREATE TABLE IF NOT EXISTS tweets_by_sentiment (
    sentiment text,
    created_at timestamp,
    tweet_id text,
    text text,
    user text,
    topic text,
    confidence float,         -- ✅ NOUVEAU
    PRIMARY KEY ((sentiment), created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC)
AND comment = 'Tweets ordonnés par sentiment et date';


-- ===========================================
-- TABLE OPTIONNELLE : tweets_by_date
-- ===========================================
-- Optimisée pour requêtes: "Tous les tweets d'un jour"
-- Utile pour générer des rapports quotidiens
-- UNCOMMENT si besoin
--
-- CREATE TABLE IF NOT EXISTS tweets_by_date (
--     date_bucket text,         -- Format: YYYY-MM-DD
--     created_at timestamp,
--     tweet_id text,
--     text text,
--     user text,
--     sentiment text,
--     topic text,
--     confidence float,
--     PRIMARY KEY ((date_bucket), created_at, tweet_id)
-- ) WITH CLUSTERING ORDER BY (created_at DESC);


-- ===========================================
-- TABLE OPTIONNELLE : top_hashtags
-- ===========================================
-- Stocke les compteurs de hashtags (mise à jour manuelle)
-- UNCOMMENT si besoin
--
-- CREATE TABLE IF NOT EXISTS top_hashtags (
--     hashtag text PRIMARY KEY,
--     count counter
-- );


-- ===========================================
-- TABLE OPTIONNELLE : user_stats
-- ===========================================
-- Stocke les stats par utilisateur (mise à jour manuelle)
-- UNCOMMENT si besoin
--
-- CREATE TABLE IF NOT EXISTS user_stats (
--     user text PRIMARY KEY,
--     total_tweets counter,
--     positive_tweets counter,
--     negative_tweets counter,
--     total_likes counter,
--     total_retweets counter
-- );


-- ===========================================
-- VÉRIFICATION DES TABLES
-- ===========================================
-- Pour vérifier que tout est créé :
-- DESCRIBE TABLES;
-- DESCRIBE TABLE tweets;
-- DESCRIBE TABLE tweets_by_topic;
-- DESCRIBE TABLE tweets_by_user;
-- DESCRIBE TABLE tweets_by_sentiment;


-- ===========================================
-- EXEMPLES DE REQUÊTES
-- ===========================================

-- 1. Compter tous les tweets
-- SELECT COUNT(*) FROM tweets;

-- 2. Tweets récents d'un topic
-- SELECT * FROM tweets_by_topic WHERE topic='AI' LIMIT 10;

-- 3. Tweets d'un user
-- SELECT * FROM tweets_by_user WHERE user='python_dev' LIMIT 10;

-- 4. Tweets positifs
-- SELECT * FROM tweets_by_sentiment WHERE sentiment='positive' LIMIT 10;

-- 5. Tweet spécifique par ID
-- SELECT * FROM tweets WHERE tweet_id='1000042';

-- 6. Tweets avec haute confiance
-- SELECT * FROM tweets WHERE confidence > 0.8 ALLOW FILTERING;
-- (Note: ALLOW FILTERING est lent, éviter en production)


-- ===========================================
-- NOTES D'OPTIMISATION
-- ===========================================

-- 1. PARTITIONNEMENT
--    - Chaque table a une clé de partition différente
--    - topic, user, sentiment → Uniformément distribués
--    - Éviter les hot partitions

-- 2. CLUSTERING
--    - Toutes les tables triées par created_at DESC
--    - Permet de récupérer les tweets les plus récents rapidement

-- 3. RÉPLICATION
--    - SimpleStrategy avec replication_factor=1 pour dev/test
--    - En production : NetworkTopologyStrategy avec RF=3

-- 4. TTL (Time To Live) - OPTIONNEL
--    - Pour auto-purger les vieux tweets
--    - Ajouter: AND default_time_to_live = 604800 (7 jours)

-- 5. COMPRESSION
--    - Cassandra compresse automatiquement avec LZ4
--    - Réduit l'espace disque de ~70%


-- ===========================================
-- COMMANDES UTILES
-- ===========================================

-- Se connecter à Cassandra :
-- docker exec -it cassandra cqlsh

-- Lister les keyspaces :
-- DESCRIBE KEYSPACES;

-- Utiliser le keyspace :
-- USE twitter_analytics;

-- Voir toutes les tables :
-- DESCRIBE TABLES;

-- Voir le schéma d'une table :
-- DESCRIBE TABLE tweets;

-- Supprimer une table :
-- DROP TABLE tweets_by_date;

-- Supprimer tout le keyspace :
-- DROP KEYSPACE twitter_analytics;

-- Truncate (vider sans supprimer) :
-- TRUNCATE tweets;

-- ===========================================
-- FIN DU SCHÉMA
-- ===========================================
