#!/usr/bin/env python3
"""
🤖 SIMULATEUR LOCAL DE TWEETS (Pas d'API Twitter)

Ce fichier génère des tweets synthétiques localement.
⚠️  AUCUNE connexion à l'API Twitter
⚠️  AUCUN Bearer Token nécessaire
⚠️  AUCUN compte Twitter Developer requis

Le simulateur crée des tweets réalistes avec :
- Textes variés et cohérents
- Hashtags pertinents
- Métriques (retweets, likes)
- Format JSON standardisé

Les tweets sont envoyés directement vers Kafka.
"""

from kafka import KafkaProducer
import json
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'tweets_raw')

# Données de simulation réalistes
USERS = [
    "data_scientist", "python_dev", "ai_researcher", "tech_enthusiast",
    "ml_engineer", "code_lover", "dev_community", "tech_guru",
    "startup_founder", "innovation_lab"
]

HASHTAGS_SETS = [
    ["Python", "Programming", "Code"],
    ["AI", "MachineLearning", "DeepLearning"],
    ["DataScience", "BigData", "Analytics"],
    ["Technology", "Innovation", "Tech"],
    ["Cloud", "DevOps", "AWS"],
    ["WebDev", "JavaScript", "React"],
    ["Blockchain", "Crypto", "Web3"],
    ["Cybersecurity", "InfoSec", "Security"]
]

TWEET_TEMPLATES = [
    "Just finished building a {topic} project! Learned so much about {skill}. #{tag1} #{tag2}",
    "Amazing tutorial on {topic}! This changed how I think about {skill}. #{tag1} #{tag2}",
    "Can't believe how powerful {topic} is for {skill}. Mind blown! 🤯 #{tag1} #{tag2}",
    "Struggling with {topic} today but making progress on {skill}... #{tag1} #{tag2}",
    "New breakthrough in {topic}! This will revolutionize {skill}. #{tag1} #{tag2}",
    "5 years of {skill} and I'm still learning new things about {topic}. #{tag1} #{tag2}",
    "Hot take: {topic} is overrated. Focus on {skill} fundamentals first. #{tag1} #{tag2}",
    "Finally understand {topic}! Key is to master {skill} basics. #{tag1} #{tag2}",
    "Looking for recommendations on {topic} tools for {skill}. What do you use? #{tag1} #{tag2}",
    "Just deployed my first {topic} application! {skill} makes it so easy. #{tag1} #{tag2}",
]

TOPICS = [
    "machine learning", "neural networks", "data pipelines", 
    "API development", "microservices", "cloud architecture",
    "Python decorators", "async programming", "containerization",
    "CI/CD", "GraphQL", "serverless functions"
]

SKILLS = [
    "distributed systems", "algorithm optimization", "system design",
    "data modeling", "API design", "code refactoring",
    "performance tuning", "debugging", "testing strategies"
]

# Créer le producer Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
        compression_type='gzip',
        max_block_ms=60000,  
        request_timeout_ms=60000,  
        api_version_auto_timeout_ms=20000 
    )
    print("✅ Connexion Kafka réussie")
except Exception as e:
    print(f"❌ Erreur connexion Kafka: {e}")
    exit(1)

print("=" * 80)
print("🤖 TWITTER SIMULATOR → KAFKA PRODUCER")
print("=" * 80)
print(f"📤 Kafka: {KAFKA_BROKER}")
print(f"📮 Topic: {KAFKA_TOPIC}")
print("💡 Simulation de tweets réalistes en temps réel")
print("=" * 80)
print("\n🚀 Démarrage de la simulation...")
print("⏸️  Ctrl+C pour arrêter\n")
print("-" * 80)

tweet_id = 1000000
tweet_count = 0

try:
    while True:
        # Générer un tweet réaliste
        user = random.choice(USERS)
        hashtag_set = random.choice(HASHTAGS_SETS)
        topic = random.choice(TOPICS)
        skill = random.choice(SKILLS)
        template = random.choice(TWEET_TEMPLATES)
        
        # Créer le texte du tweet
        text = template.format(
            topic=topic,
            skill=skill,
            tag1=hashtag_set[0],
            tag2=hashtag_set[1] if len(hashtag_set) > 1 else hashtag_set[0]
        )
        
        # Générer des métriques réalistes
        retweet_count = random.randint(0, 100)
        like_count = random.randint(0, 500)
        
        # Créer l'objet tweet
        tweet_data = {
            "tweet_id": str(tweet_id),
            "text": text,
            "created_at": datetime.now().isoformat(),
            "user": user,
            "lang": "en",
            "hashtags": hashtag_set[:2],  # 2 hashtags max
            "retweet_count": retweet_count,
            "like_count": like_count
        }
        
        # Envoyer vers Kafka
        producer.send(KAFKA_TOPIC, value=tweet_data)
        
        tweet_count += 1
        tweet_id += 1
        
        # Affichage
        print(f"✅ Tweet #{tweet_count}")
        print(f"   👤 User: @{user}")
        print(f"   📝 Text: {text[:80]}...")
        print(f"   #️⃣  Hashtags: {', '.join(['#' + h for h in hashtag_set[:2]])}")
        print(f"   🔄 RT: {retweet_count} | ❤️  Likes: {like_count}")
        print("-" * 80)
        
        # Vitesse de simulation (entre 0.5 et 3 secondes)
        delay = random.uniform(0.5, 3)
        time.sleep(delay)
        
except KeyboardInterrupt:
    print(f"\n⛔ Arrêt de la simulation")
    print(f"📊 Total de tweets générés: {tweet_count}")
    producer.flush()
    producer.close()
    print("✅ Producer fermé proprement")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    producer.close()