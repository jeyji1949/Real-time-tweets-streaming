#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
<<<<<<< HEAD
📊 ANALYZER - VERSION AMÉLIORÉE AVEC CASSANDRA

AMÉLIORATIONS :
✅ Commit manuel (pas de perte de données)
✅ Traitement par batch (10 tweets à la fois)
=======
📊 ANALYZER - VERSION AMÉLIORÉE

AMÉLIORATIONS :
✅ Commit manuel (pas de perte de données)
✅ Traitement par batch (1 tweet → commit immédiat pour DLQ)
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
✅ Monitoring en temps réel
✅ Dead Letter Queue (DLQ)
✅ Validation du schéma
✅ Gestion robuste des erreurs
✅ Confidence correctement calculée (0-1)
<<<<<<< HEAD
✅ Écriture simultanée ES + Cassandra
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2

UTILISATION :
    python analyzer_improved.py
"""

import json
import os
import re
import time
import logging
from collections import Counter
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
from elasticsearch import Elasticsearch
from textblob import TextBlob
from jsonschema import validate, ValidationError
from elasticsearch import helpers

<<<<<<< HEAD
# ✅ NOUVEAU : Import Cassandra
import sys
sys.path.append('/app')
from cassandra_writer_improved import CassandraWriterImproved

=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
# ==================================================
# LOGGING
# ==================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================================================
# CONFIG
# ==================================================
KAFKA_TOPIC = "tweets_raw"
KAFKA_BROKER = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
<<<<<<< HEAD
CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "cassandra").split(',')
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
INDEX_NAME = "tweets_index_improved"
DLQ_TOPIC = "tweets_failed"

# Batch processing
<<<<<<< HEAD
BATCH_SIZE = 10     # ✅ Traiter 10 tweets à la fois (plus performant)
=======
BATCH_SIZE = 1      # chaque tweet échoué est envoyé immédiatement
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
BATCH_TIMEOUT = 5   # secondes

STOPWORDS = {"the","a","an","and","or","to","of","in","on","for","with","is","are","was","were","i","you","it"}

# ==================================================
# SCHÉMA DE VALIDATION
# ==================================================
TWEET_SCHEMA = {
    "type": "object",
    "required": ["tweet_id", "text", "user"],
    "properties": {
        "tweet_id": {"type": "string", "minLength": 1},
        "text": {"type": "string", "minLength": 1},
        "user": {"type": "string", "minLength": 1}
    }
}

# ==================================================
# METRICS
# ==================================================
class AnalyzerMetrics:
    def __init__(self):
        self.tweets_processed = 0
        self.tweets_failed = 0
        self.batches_processed = 0
        self.validation_errors = 0
<<<<<<< HEAD
        self.es_indexed = 0           # ✅ NOUVEAU
        self.cassandra_inserted = 0   # ✅ NOUVEAU
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
        self.start_time = time.time()
        self.processing_times = []
        self.last_print_time = time.time()
    
    def record_batch_processed(self, batch_size, processing_time):
        self.tweets_processed += batch_size
        self.batches_processed += 1
        self.processing_times.append(processing_time)
    
<<<<<<< HEAD
    def record_es_indexed(self, count):
        self.es_indexed += count
    
    def record_cassandra_inserted(self, count):
        self.cassandra_inserted += count
    
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
    def record_failure(self):
        self.tweets_failed += 1
    
    def record_validation_error(self):
        self.validation_errors += 1
    
    def print_stats(self, force=False):
        now = time.time()
        if force or (now - self.last_print_time) >= 10:
            elapsed = now - self.start_time
            rate = self.tweets_processed / elapsed if elapsed > 0 else 0
            avg_processing = sum(self.processing_times)/len(self.processing_times) if self.processing_times else 0
            
            print("\n" + "="*80, flush=True)
            print("📊 STATISTIQUES ANALYZER", flush=True)
            print("="*80, flush=True)
            print(f"✅ Tweets traités:       {self.tweets_processed}", flush=True)
            print(f"❌ Tweets échoués:       {self.tweets_failed}", flush=True)
            print(f"⚠️  Erreurs validation:  {self.validation_errors}", flush=True)
            print(f"📦 Batches traités:      {self.batches_processed}", flush=True)
            print(f"⚡ Débit:                {rate:.2f} tweets/s", flush=True)
<<<<<<< HEAD
            print(f"📊 ES indexés:           {self.es_indexed}", flush=True)
            print(f"🗄️  Cassandra insérés:   {self.cassandra_inserted}", flush=True)
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
            print(f"⏱️  Temps moyen/batch:   {avg_processing*1000:.2f}ms", flush=True)
            print(f"⏳ Temps écoulé:         {elapsed/60:.1f} minutes", flush=True)
            print("="*80 + "\n", flush=True)
            self.last_print_time = now

metrics = AnalyzerMetrics()

# ==================================================
# KAFKA CONSUMER
# ==================================================
def create_consumer():
    while True:
        try:
            logger.info("⏳ Waiting for Kafka...")
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                enable_auto_commit=False,
                max_poll_records=100,
                fetch_min_bytes=1024,
                fetch_max_wait_ms=500,
                auto_offset_reset="earliest",
                group_id="analyzer-group-v2",
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info("✅ Kafka connected")
            return consumer
        except NoBrokersAvailable:
            time.sleep(5)

consumer = create_consumer()

# ==================================================
# ELASTICSEARCH
# ==================================================
def create_es():
    while True:
        try:
            logger.info("⏳ Waiting for Elasticsearch...")
            es = Elasticsearch(ES_HOST)
            if es.ping():
                logger.info("✅ Elasticsearch connected")
                return es
        except Exception:
            pass
        time.sleep(5)

es = create_es()

# ==================================================
<<<<<<< HEAD
# CASSANDRA (✅ NOUVEAU)
# ==================================================
def create_cassandra():
    while True:
        try:
            logger.info("⏳ Waiting for Cassandra...")
            cassandra = CassandraWriterImproved(hosts=CASSANDRA_HOSTS)
            logger.info("✅ Cassandra connected")
            return cassandra
        except Exception as e:
            logger.warning(f"⚠️ Cassandra not ready: {e}")
            time.sleep(5)

cassandra_writer = create_cassandra()

# ==================================================
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
# DLQ PRODUCER
# ==================================================
def create_dlq_producer():
    try:
        dlq_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
        logger.info("✅ DLQ Producer créé")
        return dlq_producer
    except Exception as e:
        logger.warning(f"⚠️ DLQ Producer non disponible: {e}")
        return None

dlq_producer = create_dlq_producer()

def send_to_dlq(tweet, error, message_info):
    if dlq_producer is None:
        logger.warning("⚠️ DLQ non disponible")
        return
    error_message = {
        'original_tweet': tweet,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'failed_at': datetime.now().isoformat(),
        'topic': message_info.get('topic', 'unknown'),
        'partition': message_info.get('partition', 0),
        'offset': message_info.get('offset', 0)
    }
    try:
        dlq_producer.send(DLQ_TOPIC, value=error_message)
        dlq_producer.flush()
        logger.info(f"📤 Tweet envoyé vers DLQ: {tweet.get('tweet_id', 'N/A')}")
    except Exception as e:
        logger.error(f"❌ Erreur DLQ: {e}")

# ==================================================
# UTILITAIRES
# ==================================================
def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)

def word_frequency(text):
    words = [w for w in re.findall(r"\b\w+\b", text.lower()) if w not in STOPWORDS]
    return dict(Counter(words))

TOPICS = {
    "AI": ["ai","machinelearning","ml","neural","tensorflow","pytorch"],
    "Web": ["web","javascript","frontend","backend","react","vue","angular"],
    "Data": ["data","bigdata","datascience","analytics","pipeline"],
    "Cloud": ["cloud","devops","docker","kubernetes","aws","azure"],
    "Security": ["security","cybersecurity","infosec","encryption"]
}

def detect_topic(text):
    t = text.lower()
    topic_scores = {}
    for topic, keywords in TOPICS.items():
        matches = sum(1 for kw in keywords if kw in t)
        if matches > 0:
            topic_scores[topic] = matches
    return max(topic_scores, key=topic_scores.get) if topic_scores else "General Tech"

def analyze_text(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.05:
        sentiment = "positive"
    elif polarity < -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    confidence = abs(polarity)
    return sentiment, confidence

def is_valid_tweet(tweet):
    try:
        validate(instance=tweet, schema=TWEET_SCHEMA)
        return True, None
    except ValidationError as e:
        error_msg = f"Champ '{e.path[0] if e.path else 'unknown'}': {e.message}"
        return False, error_msg

def enrich_tweet(tweet):
    try:
        text = tweet.get("text", "")
        hashtags = extract_hashtags(text)
        sentiment, confidence = analyze_text(text)
        topic = detect_topic(text)
        word_freq = word_frequency(text)
<<<<<<< HEAD
        
        # Calculer le score (-1, 0, 1)
        if sentiment == "positive":
            score = 1
        elif sentiment == "negative":
            score = -1
        else:
            score = 0
        
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
        tweet.update({
            "hashtags": hashtags,
            "word_freq": word_freq,
            "sentiment": sentiment,
            "confidence": confidence,
<<<<<<< HEAD
            "score": score,  # ✅ NOUVEAU : ajout du score
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
            "topic": topic,
            "analysis_method": "textblob",
            "indexed_at": datetime.now().isoformat()
        })
        return tweet
    except Exception as e:
        logger.error(f"❌ Erreur enrichissement: {e}")
        raise

def process_batch(messages_buffer):
    tweets_enriched = []
    failed_items = []
    for item in messages_buffer:
        tweet = item['tweet']
        metadata = item['metadata']
        try:
            valid, error = is_valid_tweet(tweet)
            if not valid:
                metrics.record_validation_error()
                send_to_dlq(tweet, ValueError(error), metadata)
                continue
            enriched = enrich_tweet(tweet)
            tweets_enriched.append(enriched)
        except Exception as e:
            metrics.record_failure()
            failed_items.append((tweet, e, metadata))
    return tweets_enriched, failed_items

def bulk_index_to_es(tweets):
<<<<<<< HEAD
    """Indexer dans Elasticsearch"""
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
    if not tweets:
        return
    try:
        actions = [
            {
                "_index": INDEX_NAME,
                "_id": tweet["tweet_id"],
                "_source": tweet
            }
            for tweet in tweets
        ]
        helpers.bulk(es, actions)
<<<<<<< HEAD
        metrics.record_es_indexed(len(tweets))
        logger.info(f"✅ {len(tweets)} tweets indexés dans ES")
    except Exception as e:
        logger.error(f"❌ Erreur bulk index ES: {e}")
        raise

def bulk_insert_to_cassandra(tweets):
    """✅ NOUVEAU : Insérer dans Cassandra"""
    if not tweets:
        return
    try:
        inserted = cassandra_writer.insert_batch(tweets)
        metrics.record_cassandra_inserted(inserted)
        logger.info(f"✅ {inserted} tweets insérés dans Cassandra")
    except Exception as e:
        logger.error(f"❌ Erreur bulk insert Cassandra: {e}")
        raise

=======
        logger.info(f"✅ {len(tweets)} tweets indexés dans ES")
    except Exception as e:
        logger.error(f"❌ Erreur bulk index: {e}")
        for tweet in tweets:
            send_to_dlq(tweet, e, {'topic': KAFKA_TOPIC, 'partition': 0, 'offset': 0})
        raise
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
# ==================================================
# MAIN LOOP
# ==================================================
messages_buffer = []

<<<<<<< HEAD
print("🚀 ANALYZER IMPROVED SERVICE READY (WITH CASSANDRA)")
=======
print("🚀 ANALYZER IMPROVED SERVICE READY")
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
try:
    for msg in consumer:
        tweet = msg.value
        tweet_id = tweet.get("tweet_id")
        if not tweet_id:
            continue
        messages_buffer.append({
            'tweet': tweet,
            'metadata': {'topic': msg.topic, 'partition': msg.partition, 'offset': msg.offset}
        })
<<<<<<< HEAD
        
        # ✅ Traiter quand le batch est plein
        if len(messages_buffer) >= BATCH_SIZE:
            start_time = time.time()
            try:
                # 1. Enrichir les tweets
                tweets_enriched, failed_items = process_batch(messages_buffer)
                
                if tweets_enriched:
                    # 2. Indexer dans Elasticsearch
                    bulk_index_to_es(tweets_enriched)
                    
                    # 3. ✅ NOUVEAU : Insérer dans Cassandra
                    bulk_insert_to_cassandra(tweets_enriched)
                
                # 4. Gérer les échecs
                for tweet, error, metadata in failed_items:
                    send_to_dlq(tweet, error, metadata)
                
                # 5. Mesurer et commit
                processing_time = time.time() - start_time
                metrics.record_batch_processed(len(messages_buffer), processing_time)
                consumer.commit()
                
            except Exception as e:
                logger.error(f"❌ Erreur traitement batch: {e}")
                for item in messages_buffer:
                    send_to_dlq(item['tweet'], e, item['metadata'])
                consumer.commit()
            
            messages_buffer = []
        
        metrics.print_stats()

except KeyboardInterrupt:
    logger.info("⛔ Arrêt demandé")
=======
        if len(messages_buffer) >= BATCH_SIZE:
            start_time = time.time()
            try:
                tweets_enriched, failed_items = process_batch(messages_buffer)
                if tweets_enriched:
                    bulk_index_to_es(tweets_enriched)
                for tweet, error, metadata in failed_items:
                    send_to_dlq(tweet, error, metadata)
                processing_time = time.time() - start_time
                metrics.record_batch_processed(len(messages_buffer), processing_time)
                consumer.commit()
            except Exception as e:
                for item in messages_buffer:
                    send_to_dlq(item['tweet'], e, item['metadata'])
                consumer.commit()
            messages_buffer = []
        metrics.print_stats()
except KeyboardInterrupt:
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
    if messages_buffer:
        tweets_enriched, failed_items = process_batch(messages_buffer)
        if tweets_enriched:
            bulk_index_to_es(tweets_enriched)
<<<<<<< HEAD
            bulk_insert_to_cassandra(tweets_enriched)
        consumer.commit()
    metrics.print_stats(force=True)

=======
        consumer.commit()
    metrics.print_stats(force=True)
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
finally:
    if consumer:
        consumer.close()
    if dlq_producer:
        dlq_producer.close()
<<<<<<< HEAD
    if cassandra_writer:
        cassandra_writer.close()
    logger.info("✅ Shutdown complet")
=======
>>>>>>> d24483c920d622ab35c2734d98299328a02b02a2
