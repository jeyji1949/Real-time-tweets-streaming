#!/usr/bin/env python3
"""
Kafka Consumer - Lit les tweets depuis Kafka
"""

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import os
import time
import sys
from dotenv import load_dotenv

# Charger .env
load_dotenv(dotenv_path='../.env')

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'tweets_raw')

print("=" * 80)
print("📥 KAFKA CONSUMER - Réception des tweets")
print("=" * 80)
print(f"📡 Kafka Broker: {KAFKA_BROKER}")
print(f"📮 Topic: {KAFKA_TOPIC}")
print("=" * 80)

# Retry connection to Kafka
max_retries = 10
retry_delay = 3

consumer = None
for attempt in range(1, max_retries + 1):
    try:
        print(f"\n🔄 Tentative de connexion à Kafka ({attempt}/{max_retries})...")
        
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='tweet-consumer-group',
            #consumer_timeout_ms=1000,
            request_timeout_ms=30000,
            connections_max_idle_ms=540000
        )
        
        print("✅ Connexion à Kafka réussie !")
        break
        
    except NoBrokersAvailable:
        if attempt < max_retries:
            print(f"⚠️  Kafka pas encore prêt. Nouvelle tentative dans {retry_delay}s...")
            time.sleep(retry_delay)
        else:
            print("\n❌ Impossible de se connecter à Kafka après plusieurs tentatives")
            print("➡️  Vérifiez que Docker est bien démarré : docker-compose ps")
            print("➡️  Vérifiez les logs Kafka : docker logs twitter-project_kafka_1")
            sys.exit(1)

if not consumer:
    sys.exit(1)

print("\n⏸️  Ctrl+C pour arrêter")
print("=" * 80)
print()

tweet_count = 0

try:
    print("👂 En écoute des tweets...\n")
    
    for message in consumer:
        tweet = message.value
        tweet_count += 1
        
        print(f"📩 Tweet #{tweet_count} reçu")
        print(f"   ID: {tweet.get('tweet_id', 'N/A')}")
        print(f"   👤 User: {tweet.get('user', 'N/A')}")
        print(f"   📝 Text: {tweet.get('text', '')[:100]}...")
        print(f"   🌍 Lang: {tweet.get('lang', 'N/A')}")
        
        if tweet.get('hashtags'):
            hashtags = ', '.join(['#' + h for h in tweet['hashtags']])
            print(f"   #️⃣  Hashtags: {hashtags}")
        
        if 'retweet_count' in tweet:
            print(f"   🔄 Retweets: {tweet['retweet_count']}")
            print(f"   ❤️  Likes: {tweet['like_count']}")
        
        print("-" * 80)
        
except KeyboardInterrupt:
    print(f"\n⛔ Arrêt demandé. Total reçu: {tweet_count} tweets")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
finally:
    if consumer:
        consumer.close()
        print("✅ Consumer fermé proprement")
