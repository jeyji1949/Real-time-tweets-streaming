#!/usr/bin/env python3
"""
Test Cassandra Writer Improved
Vérifie que toutes les fonctionnalités V2.0 fonctionnent correctement
"""

import sys
import time
from datetime import datetime
from analysis.analyzer.cassandra_writer_improved import CassandraWriterImproved

def test_connection():
    """Test 1 : Connexion à Cassandra"""
    print("\n" + "="*70)
    print("🧪 TEST 1 : Connexion à Cassandra")
    print("="*70)
    
    try:
        writer = CassandraWriterImproved(hosts=['127.0.0.1'])
        print("✅ Connexion réussie")
        return writer
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        sys.exit(1)

def test_single_insert(writer):
    """Test 2 : Insert simple"""
    print("\n" + "="*70)
    print("🧪 TEST 2 : Insert d'un tweet")
    print("="*70)
    
    tweet = {
        "tweet_id": "TEST_001",
        "text": "Test tweet for Cassandra V2.0",
        "user": "test_user",
        "lang": "en",
        "created_at": datetime.now().isoformat(),
        "indexed_at": datetime.now().isoformat(),
        "sentiment": "positive",
        "confidence": 0.85,  # ✅ NOUVEAU champ V2.0
        "score": 1,
        "topic": "Testing",
        "hashtags": ["test", "v2"],
        "retweet_count": 10,
        "like_count": 25,
        "analysis_method": "textblob"
    }
    
    try:
        writer.insert_tweet(tweet)
        print(f"✅ Tweet {tweet['tweet_id']} inséré")
    except Exception as e:
        print(f"❌ Erreur d'insertion : {e}")

def test_batch_insert(writer):
    """Test 3 : Batch insert"""
    print("\n" + "="*70)
    print("🧪 TEST 3 : Batch insert (10 tweets)")
    print("="*70)
    
    tweets = []
    for i in range(10):
        tweet = {
            "tweet_id": f"TEST_{i:03d}",
            "text": f"Batch test tweet #{i}",
            "user": f"user_{i % 3}",  # 3 users différents
            "lang": "en",
            "created_at": datetime.now().isoformat(),
            "indexed_at": datetime.now().isoformat(),
            "sentiment": ["positive", "neutral", "negative"][i % 3],
            "confidence": 0.70 + (i * 0.02),  # Confidence variable
            "score": [1, 0, -1][i % 3],
            "topic": ["AI", "Cloud", "Data"][i % 3],
            "hashtags": [["ai", "ml"], ["cloud", "devops"], ["data", "analytics"]][i % 3],
            "retweet_count": i * 5,
            "like_count": i * 10,
            "analysis_method": "textblob"
        }
        tweets.append(tweet)
    
    try:
        start = time.time()
        inserted = writer.insert_batch(tweets)
        elapsed = time.time() - start
        print(f"✅ {inserted} tweets insérés en {elapsed:.2f}s")
        print(f"⚡ Débit : {inserted/elapsed:.1f} tweets/s")
    except Exception as e:
        print(f"❌ Erreur batch insert : {e}")

def test_queries(writer):
    """Test 4 : Requêtes de lecture"""
    print("\n" + "="*70)
    print("🧪 TEST 4 : Requêtes de lecture")
    print("="*70)
    
    # Total count
    try:
        total = writer.get_tweet_count()
        print(f"📊 Total tweets : {total}")
    except Exception as e:
        print(f"❌ Erreur count : {e}")
    
    # By topic
    try:
        ai_tweets = writer.get_tweets_by_topic("AI", limit=3)
        print(f"🤖 Tweets AI : {len(ai_tweets)}")
        if ai_tweets:
            print(f"   Exemple : {ai_tweets[0]['text'][:50]}...")
    except Exception as e:
        print(f"❌ Erreur query by topic : {e}")
    
    # By sentiment
    try:
        positive_tweets = writer.get_tweets_by_sentiment("positive", limit=3)
        print(f"😊 Tweets positifs : {len(positive_tweets)}")
    except Exception as e:
        print(f"❌ Erreur query by sentiment : {e}")
    
    # By user
    try:
        user_tweets = writer.get_tweets_by_user("user_0", limit=3)
        print(f"👤 Tweets user_0 : {len(user_tweets)}")
    except Exception as e:
        print(f"❌ Erreur query by user : {e}")

def test_stats(writer):
    """Test 5 : Statistiques"""
    print("\n" + "="*70)
    print("🧪 TEST 5 : Statistiques globales")
    print("="*70)
    
    try:
        stats = writer.get_stats()
        print(f"📊 Stats globales :")
        print(f"   Total tweets : {stats.get('total_tweets', 0)}")
        print(f"   Sentiments : {stats.get('sentiment_distribution', {})}")
        print(f"   Topics : {stats.get('topic_distribution', {})}")
    except Exception as e:
        print(f"❌ Erreur stats : {e}")

def test_monitoring_stats(writer):
    """Test 6 : Stats de monitoring"""
    print("\n" + "="*70)
    print("🧪 TEST 6 : Stats de monitoring (performance)")
    print("="*70)
    
    try:
        writer.print_stats()
    except Exception as e:
        print(f"❌ Erreur monitoring stats : {e}")

def test_confidence_field(writer):
    """Test 7 : Vérifier que le champ confidence existe"""
    print("\n" + "="*70)
    print("🧪 TEST 7 : Vérification champ 'confidence' (V2.0)")
    print("="*70)
    
    try:
        # Récupérer un tweet
        tweets = writer.get_tweets_by_topic("AI", limit=1)
        if tweets and len(tweets) > 0:
            tweet = tweets[0]
            if 'confidence' in tweet:
                print(f"✅ Champ 'confidence' trouvé : {tweet['confidence']}")
                if 0.0 <= tweet['confidence'] <= 1.0:
                    print(f"✅ Valeur valide (entre 0 et 1)")
                else:
                    print(f"⚠️  Valeur hors bornes : {tweet['confidence']}")
            else:
                print(f"❌ Champ 'confidence' manquant !")
                print(f"   Champs présents : {list(tweet.keys())}")
        else:
            print(f"⚠️  Aucun tweet trouvé pour tester")
    except Exception as e:
        print(f"❌ Erreur test confidence : {e}")

def cleanup(writer):
    """Cleanup : Supprimer les tweets de test"""
    print("\n" + "="*70)
    print("🧹 CLEANUP : Suppression des tweets de test")
    print("="*70)
    
    # Note: Cassandra n'a pas de DELETE facile sans clé primaire
    # Pour nettoyer, il faudrait utiliser TRUNCATE ou DELETE avec tweet_id
    print("⚠️  Cleanup manuel requis si nécessaire")
    print("   Commande : DELETE FROM tweets WHERE tweet_id IN ('TEST_001', 'TEST_000', ...);")

def main():
    """Lancer tous les tests"""
    print("\n" + "="*70)
    print("🧪 TESTS CASSANDRA WRITER IMPROVED - VERSION 2.0")
    print("="*70)
    
    # Test 1 : Connexion
    writer = test_connection()
    
    # Test 2 : Insert simple
    test_single_insert(writer)
    
    # Test 3 : Batch insert
    test_batch_insert(writer)
    
    # Test 4 : Requêtes
    test_queries(writer)
    
    # Test 5 : Stats
    test_stats(writer)
    
    # Test 6 : Monitoring
    test_monitoring_stats(writer)
    
    # Test 7 : Champ confidence (V2.0)
    test_confidence_field(writer)
    
    # Cleanup
    # cleanup(writer)
    
    # Fermer la connexion
    writer.close()
    
    print("\n" + "="*70)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("="*70)
    print("\n💡 Pour nettoyer les données de test :")
    print("   docker exec -it cassandra cqlsh")
    print("   USE twitter_analytics;")
    print("   DELETE FROM tweets WHERE tweet_id LIKE 'TEST_%';")
    print("   DELETE FROM tweets_by_topic WHERE topic='Testing';")
    print("   DELETE FROM tweets_by_user WHERE user LIKE 'user_%' OR user='test_user';")
    print("   DELETE FROM tweets_by_sentiment WHERE sentiment IN ('positive', 'neutral', 'negative');")
    print()

if __name__ == "__main__":
    main()