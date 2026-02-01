from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import json
from datetime import datetime

# Cassandra connection
cluster = Cluster(["127.0.0.1"])
session = cluster.connect("realtime")

# Kafka consumer
consumer = KafkaConsumer(
    "tweets",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Listening for tweets...")

for msg in consumer:
    tweet = msg.value

    tweet_id = str(tweet.get("id"))
    text = tweet.get("text")
    sentiment = tweet.get("sentiment", "neutral")
    hashtags = tweet.get("hashtags", [])
    created_at = datetime.utcnow()

    session.execute(
        """
        INSERT INTO tweets (tweet_id, text, created_at, sentiment, hashtags)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (tweet_id, text, created_at, sentiment, hashtags)
    )

    print("Inserted:", tweet_id)
