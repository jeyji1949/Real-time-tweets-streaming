from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
session = cluster.connect("realtime")

def save_tweet(tweet):
    query = """
    INSERT INTO tweets (tweet_id, text, created_at, sentiment, hashtags)
    VALUES (%s, %s, %s, %s, %s)
    """

    session.execute(query, (
        tweet["id"],
        tweet["text"],
        tweet["created_at"],
        tweet["sentiment"],
        tweet["hashtags"]
    ))

    print("Tweet saved in Cassandra")
