#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import time
from collections import Counter

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from elasticsearch import Elasticsearch
from textblob import TextBlob

# ==================================================
# CONFIG
# ==================================================

KAFKA_TOPIC = "tweets_raw"
KAFKA_BROKER = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
INDEX_NAME = "tweets_index"

STOPWORDS = {
    "the","a","an","and","or","to","of","in","on",
    "for","with","is","are","was","were","i","you","it"
}

print("🔥 ANALYZER BOOTING...", flush=True)

# ==================================================
# WAIT FOR KAFKA
# ==================================================

def create_consumer():
    while True:
        try:
            print("⏳ Waiting for Kafka...", flush=True)
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                enable_auto_commit=True
            )
            print("✅ Kafka connected", flush=True)
            return consumer
        except NoBrokersAvailable:
            time.sleep(5)

# ==================================================
# WAIT FOR ELASTICSEARCH
# ==================================================

def create_es():
    while True:
        try:
            print("⏳ Waiting for Elasticsearch...", flush=True)
            es = Elasticsearch(ES_HOST)
            if es.ping():
                print("✅ Elasticsearch connected", flush=True)
                return es
        except Exception:
            pass
        time.sleep(5)

consumer = create_consumer()
es = create_es()

# ==================================================
# UTILS
# ==================================================

def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)

def word_frequency(text):
    words = re.findall(r"\b\w+\b", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    return dict(Counter(words))

# ==================================================
# TOPIC DETECTION (RULE BASED)
# ==================================================

TOPICS = {
    "AI": ["ai","machinelearning","ml","neural"],
    "Web": ["web","javascript","frontend","backend"],
    "Data": ["data","bigdata","datascience"],
    "Cloud": ["cloud","devops","docker","kubernetes"],
    "Security": ["security","cybersecurity","infosec"]
}

def detect_topic(text):
    t = text.lower()
    for topic, keywords in TOPICS.items():
        for kw in keywords:
            if kw in t:
                return topic
    return "General Tech"

# ==================================================
# SENTIMENT ANALYSIS (TEXTBLOB)
# ==================================================

def analyze_text(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # [-1, 1]

    if polarity > 0.05:
        sentiment = "positive"
    elif polarity < -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    confidence = round(abs(polarity), 2)  # ✅ entre 0 et 1

    return sentiment, confidence

# ==================================================
# MAIN LOOP
# ==================================================

print("🚀 Analyzer service started", flush=True)
print("👂 Waiting for Kafka messages...", flush=True)

for msg in consumer:
    tweet = msg.value
    text = tweet.get("text", "")
    tweet_id = tweet.get("tweet_id")

    if not tweet_id:
        print("⚠️ Tweet ignoré (pas de tweet_id)", flush=True)
        continue

    hashtags = extract_hashtags(text)
    sentiment, confidence = analyze_text(text)
    topic = detect_topic(text)

    tweet.update({
        "hashtags": hashtags,
        "word_freq": word_frequency(text),
        "sentiment": sentiment,
        "confidence": confidence,          # ✅ CHAMP ATTENDU
        "topic": topic,
        "analysis_method": "textblob"
    })

    # ✅ tweet_id utilisé comme _id → pas de doublons
    es.index(
        index=INDEX_NAME,
        id=tweet_id,
        document=tweet
    )

    print("────────────────────────────────────────────", flush=True)
    print("📥 TWEET INDEXED", flush=True)
    print(f"🆔 ID: {tweet_id}", flush=True)
    print(f"📝 {text}", flush=True)
    print(f"💬 Sentiment: {sentiment} | 🎯 Confidence: {confidence}", flush=True)
    print(f"📌 Topic: {topic}", flush=True)
    print("────────────────────────────────────────────", flush=True)

