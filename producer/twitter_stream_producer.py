#!/usr/bin/env python3
"""
Twitter Real-Time Stream Producer
Collecte les tweets en temps réel et les envoie vers Kafka
"""

import tweepy
from kafka import KafkaProducer
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Twitter
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Configuration Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'tweets_raw')

# Vérifier le Bearer Token
if not BEARER_TOKEN:
    print("❌ ERREUR: TWITTER_BEARER_TOKEN non trouvé dans .env")
    print("➡️  Créez un fichier .env avec votre Bearer Token")
    sys.exit(1)

# Créer le producer Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
        compression_type='gzip'
    )
    print("✅ Connexion Kafka réussie")
except Exception as e:
    print(f"❌ Erreur connexion Kafka: {e}")
    sys.exit(1)


class TwitterStreamListener(tweepy.StreamingClient):
    """Classe pour streamer les tweets"""
    
    def __init__(self, bearer_token):
        super().__init__(bearer_token, wait_on_rate_limit=True)
        self.tweet_count = 0
    
    def on_tweet(self, tweet):
        """Appelé quand un nouveau tweet arrive"""
        try:
            # Extraire les hashtags
            hashtags = []
            if hasattr(tweet, 'entities') and tweet.entities:
                if 'hashtags' in tweet.entities:
                    hashtags = [tag['tag'] for tag in tweet.entities['hashtags']]
            
            # Créer l'objet tweet
            tweet_data = {
                "tweet_id": str(tweet.id),
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat() if hasattr(tweet, 'created_at') else datetime.now().isoformat(),
                "user": str(tweet.author_id) if hasattr(tweet, 'author_id') else "unknown",
                "lang": tweet.lang if hasattr(tweet, 'lang') else "unknown",
                "hashtags": hashtags,
            }
            
            # Ajouter les métriques
            if hasattr(tweet, 'public_metrics'):
                tweet_data['retweet_count'] = tweet.public_metrics.get('retweet_count', 0)
                tweet_data['like_count'] = tweet.public_metrics.get('like_count', 0)
            
            # Envoyer vers Kafka
            producer.send(KAFKA_TOPIC, value=tweet_data)
            
            self.tweet_count += 1
            
            # Affichage
            print(f"✅ Tweet #{self.tweet_count}")
            print(f"   👤 User: {tweet_data['user']}")
            print(f"   📝 Text: {tweet_data['text'][:80]}...")
            if hashtags:
                print(f"   #️⃣  Hashtags: {', '.join(['#' + h for h in hashtags])}")
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def on_errors(self, errors):
        print(f"⚠️  Erreur stream: {errors}")
        return True


def setup_rules(stream):
    """Configure les règles de filtrage"""
    
    print("\n🔧 Configuration des règles...")
    
    # Supprimer anciennes règles
    try:
        existing_rules = stream.get_rules()
        if existing_rules.data:
            rule_ids = [rule.id for rule in existing_rules.data]
            stream.delete_rules(rule_ids)
            print(f"🗑️  {len(rule_ids)} anciennes règles supprimées")
    except:
        print("⚠️  Pas d'anciennes règles")
    
    # Nouvelles règles (MODIFIEZ ICI vos mots-clés)
    rules = [
        tweepy.StreamRule("python OR programming lang:en"),
        tweepy.StreamRule("AI OR MachineLearning lang:en"),
        tweepy.StreamRule("technology OR tech lang:en"),
    ]
    
    stream.add_rules(rules)
    print(f"✅ {len(rules)} règles ajoutées")
    print("\n🔍 Mots-clés surveillés :")
    for i, rule in enumerate(rules, 1):
        print(f"   {i}. {rule.value}")


def main():
    """Fonction principale"""
    print("=" * 80)
    print("🐦 TWITTER STREAM → KAFKA PRODUCER")
    print("=" * 80)
    print(f"📤 Kafka: {KAFKA_BROKER}")
    print(f"📮 Topic: {KAFKA_TOPIC}")
    print("=" * 80)
    
    stream = TwitterStreamListener(BEARER_TOKEN)
    setup_rules(stream)
    
    print("\n🚀 Démarrage du stream...")
    print("⏸️  Ctrl+C pour arrêter\n")
    
    try:
        stream.filter(
            tweet_fields=['created_at', 'lang', 'author_id', 'public_metrics', 'entities'],
            threaded=True
        )
    except KeyboardInterrupt:
        print(f"\n⛔ Arrêt. Total: {stream.tweet_count} tweets")
        producer.flush()
        producer.close()
        print("✅ Fermé proprement")


if __name__ == "__main__":
    main()
