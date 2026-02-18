"""
Cassandra Writer - Insertion des tweets analysés
Personne 3 - Stockage & Visualisation
"""

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime
import json

class CassandraWriter:
    def __init__(self, hosts=['cassandra'], keyspace='twitter_analytics'):
        """Initialise la connexion à Cassandra"""
        self.cluster = Cluster(hosts)
        self.session = self.cluster.connect()
        
        # Créer le keyspace si nécessaire
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS twitter_analytics
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        
        self.session.set_keyspace(keyspace)
        print("✅ Connecté à Cassandra")
    
    def insert_tweet(self, tweet):
        """Insère un tweet dans toutes les tables"""
        try:
            # Parser la date
            if isinstance(tweet.get('created_at'), str):
                created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
            else:
                created_at = tweet.get('created_at', datetime.now())
            
            indexed_at = datetime.now()
            
            # Table principale
            self.session.execute("""
                INSERT INTO tweets (
                    tweet_id, text, user, lang, created_at, indexed_at,
                    sentiment, score, topic, hashtags, retweet_count, 
                    like_count, analysis_method
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('user', ''),
                tweet.get('lang', 'en'),
                created_at,
                indexed_at,
                tweet.get('sentiment', 'neutral'),
                tweet.get('score', 0),
                tweet.get('topic', 'General'),
                tweet.get('hashtags', []),
                tweet.get('retweet_count', 0),
                tweet.get('like_count', 0),
                tweet.get('analysis_method', 'textblob')
            ))
            
            # Table par topic
            self.session.execute("""
                INSERT INTO tweets_by_topic (
                    topic, created_at, tweet_id, text, user, sentiment
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                tweet.get('topic', 'General'),
                created_at,
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('user', ''),
                tweet.get('sentiment', 'neutral')
            ))
            
            # Table par user
            self.session.execute("""
                INSERT INTO tweets_by_user (
                    user, created_at, tweet_id, text, sentiment, topic
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                tweet.get('user', ''),
                created_at,
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('sentiment', 'neutral'),
                tweet.get('topic', 'General')
            ))
            
            # Table par sentiment
            self.session.execute("""
                INSERT INTO tweets_by_sentiment (
                    sentiment, created_at, tweet_id, text, user, topic
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                tweet.get('sentiment', 'neutral'),
                created_at,
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('user', ''),
                tweet.get('topic', 'General')
            ))
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur insertion: {e}")
            return False
    
    def get_tweet_count(self):
        """Compte le nombre de tweets"""
        result = self.session.execute("SELECT COUNT(*) FROM tweets")
        return result.one()[0]
    
    def get_tweets_by_topic(self, topic, limit=10):
        """Récupère les tweets par topic"""
        result = self.session.execute(
            "SELECT * FROM tweets_by_topic WHERE topic = %s LIMIT %s",
            (topic, limit)
        )
        return list(result)
    
    def get_tweets_by_sentiment(self, sentiment, limit=10):
        """Récupère les tweets par sentiment"""
        result = self.session.execute(
            "SELECT * FROM tweets_by_sentiment WHERE sentiment = %s LIMIT %s",
            (sentiment, limit)
        )
        return list(result)
    
    def close(self):
        """Ferme la connexion"""
        self.cluster.shutdown()
        print("🔌 Connexion Cassandra fermée")


# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du CassandraWriter...")
    
    writer = CassandraWriter(hosts=['127.0.0.1'])
    
    # Tweet de test
    test_tweet = {
        "tweet_id": "TEST001",
        "text": "This is a test tweet for Cassandra! #Python #BigData",
        "user": "test_user",
        "lang": "en",
        "created_at": datetime.now().isoformat(),
        "sentiment": "positive",
        "score": 1,
        "topic": "Data",
        "hashtags": ["Python", "BigData"],
        "retweet_count": 10,
        "like_count": 25,
        "analysis_method": "textblob"
    }
    
    # Insérer
    if writer.insert_tweet(test_tweet):
        print("✅ Tweet de test inséré")
    
    # Vérifier
    count = writer.get_tweet_count()
    print(f"📊 Nombre total de tweets: {count}")
    
    writer.close()