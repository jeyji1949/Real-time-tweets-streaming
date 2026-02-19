-- ===========================================
-- Twitter Analytics - Cassandra Schema
-- Personne 3 - Stockage & Visualisation
-- ===========================================

-- Créer le keyspace
CREATE KEYSPACE IF NOT EXISTS twitter_analytics
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE twitter_analytics;

-- Table principale des tweets
CREATE TABLE IF NOT EXISTS tweets (
    tweet_id text PRIMARY KEY,
    text text,
    user text,
    lang text,
    created_at timestamp,
    indexed_at timestamp,
    sentiment text,
    score int,
    topic text,
    hashtags list<text>,
    retweet_count int,
    like_count int,
    analysis_method text
);

-- Table pour requêtes par topic
CREATE TABLE IF NOT EXISTS tweets_by_topic (
    topic text,
    created_at timestamp,
    tweet_id text,
    text text,
    user text,
    sentiment text,
    PRIMARY KEY ((topic), created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Table pour requêtes par user
CREATE TABLE IF NOT EXISTS tweets_by_user (
    user text,
    created_at timestamp,
    tweet_id text,
    text text,
    sentiment text,
    topic text,
    PRIMARY KEY ((user), created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Table pour requêtes par sentiment
CREATE TABLE IF NOT EXISTS tweets_by_sentiment (
    sentiment text,
    created_at timestamp,
    tweet_id text,
    text text,
    user text,
    topic text,
    PRIMARY KEY ((sentiment), created_at, tweet_id)
) WITH CLUSTERING ORDER BY (created_at DESC);