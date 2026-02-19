"""
Synchronisation Elasticsearch → Cassandra
"""

from elasticsearch import Elasticsearch
from cassandra.cluster import Cluster
from datetime import datetime

def sync_es_to_cassandra():
    print("🔄 Démarrage de la synchronisation ES → Cassandra...")
    
    # Connexion Elasticsearch
    try:
        es = Elasticsearch(["http://localhost:9200"])
        count = es.count(index="tweets_index")['count']
        print(f"✅ Elasticsearch connecté - {count} tweets trouvés")
    except Exception as e:
        print(f"❌ Erreur Elasticsearch: {e}")
        return
    
    # Connexion Cassandra
    try:
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect('twitter_analytics')
        print("✅ Cassandra connecté")
    except Exception as e:
        print(f"❌ Erreur Cassandra: {e}")
        return
    
    # Récupérer les tweets
    result = es.search(index="tweets_index", body={"query": {"match_all": {}}, "size": 1000})
    hits = result['hits']['hits']
    
    total_inserted = 0
    errors = 0
    
    print(f"📥 Traitement de {len(hits)} tweets...")
    
    for hit in hits:
        tweet = hit['_source']
        
        try:
            created_at_str = tweet.get('created_at', '')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            else:
                created_at = datetime.now()
            
            session.execute("""
                INSERT INTO tweets (tweet_id, text, user, lang, created_at, indexed_at,
                    sentiment, score, topic, hashtags, retweet_count, like_count, analysis_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('user', ''),
                tweet.get('lang', 'en'),
                created_at,
                datetime.now(),
                tweet.get('sentiment', 'neutral'),
                int(tweet.get('score', 0)),
                tweet.get('topic', 'General'),
                tweet.get('hashtags', []),
                int(tweet.get('retweet_count', 0)),
                int(tweet.get('like_count', 0)),
                tweet.get('analysis_method', 'textblob')
            ))
            
            session.execute("""
                INSERT INTO tweets_by_topic (topic, created_at, tweet_id, text, user, sentiment)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                tweet.get('topic', 'General'),
                created_at,
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('user', ''),
                tweet.get('sentiment', 'neutral')
            ))
            
            session.execute("""
                INSERT INTO tweets_by_sentiment (sentiment, created_at, tweet_id, text, user, topic)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                tweet.get('sentiment', 'neutral'),
                created_at,
                str(tweet.get('tweet_id', '')),
                tweet.get('text', ''),
                tweet.get('user', ''),
                tweet.get('topic', 'General')
            ))
            
            total_inserted += 1
            
            if total_inserted % 50 == 0:
                print(f"   📊 {total_inserted} tweets insérés...")
                
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"   ⚠️ Erreur: {e}")
    
    print(f"\n✅ Synchronisation terminée!")
    print(f"   📊 Tweets insérés: {total_inserted}")
    print(f"   ⚠️ Erreurs: {errors}")
    
    result = session.execute("SELECT COUNT(*) FROM tweets")
    print(f"   📊 Total dans Cassandra: {result.one()[0]}")
    
    cluster.shutdown()

if __name__ == "__main__":
    sync_es_to_cassandra()