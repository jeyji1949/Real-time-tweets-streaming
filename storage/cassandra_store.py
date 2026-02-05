from cassandra.cluster import Cluster
from datetime import datetime

cluster = Cluster(["127.0.0.1"])
session = cluster.connect("realtime")

def insert_tweet(id, text, sentiment, hashtags):
    session.execute(
        """
        INSERT INTO tweets (tweet_id, text, created_at, sentiment, hashtags)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (id, text, datetime.utcnow(), sentiment, hashtags)
    )

if __name__ == "__main__":
    insert_tweet("2", "storage test", "neutral", ["storage"])
    print("Inserted test tweet")
