CREATE KEYSPACE IF NOT EXISTS realtime
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE realtime;

CREATE TABLE IF NOT EXISTS tweets (
    tweet_id text PRIMARY KEY,
    text text,
    created_at timestamp,
    sentiment text,
    hashtags list<text>
);
