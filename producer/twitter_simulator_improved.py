#!/usr/bin/env python3
"""
🤖 SIMULATEUR LOCAL DE TWEETS - VERSION AMÉLIORÉE

AMÉLIORATIONS par rapport à twitter_simulator.py :
✅ Gestion robuste des erreurs (acks='all', retries, callbacks)
✅ Monitoring en temps réel (débit, latence, erreurs)
✅ Validation du schéma JSON
✅ Partitionnement par utilisateur
✅ Logs détaillés

UTILISATION :
    python twitter_simulator_improved.py

DIFFÉRENCES AVEC L'ANCIEN :
- Aucune connexion Twitter (toujours simulé)
- Messages GARANTIS d'arriver (acks='all')
- Statistiques affichées toutes les 10 secondes
- Validation automatique des tweets avant envoi
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os
import time
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

# ============================================================================
# CONFIGURATION DES LOGS
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('producer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CHARGEMENT DE LA CONFIGURATION
# ============================================================================
load_dotenv()

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'tweets_raw')

# ============================================================================
# SCHÉMA DE VALIDATION (Simplifié)
# ============================================================================
TWEET_SCHEMA = {
    "type": "object",
    "required": ["tweet_id", "text", "created_at", "user", "lang", "hashtags"],
    "properties": {
        "tweet_id": {"type": "string", "minLength": 1},
        "text": {"type": "string", "minLength": 1, "maxLength": 500},
        "created_at": {"type": "string"},
        "user": {"type": "string", "minLength": 1},
        "lang": {"type": "string", "pattern": "^[a-z]{2}$"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "retweet_count": {"type": "integer", "minimum": 0},
        "like_count": {"type": "integer", "minimum": 0}
    }
}

# ============================================================================
# CLASSE POUR LE MONITORING
# ============================================================================
class KafkaMetrics:
    """Suivi des performances du producer"""
    
    def __init__(self):
        self.messages_sent = 0
        self.messages_failed = 0
        self.validation_errors = 0
        self.start_time = time.time()
        self.latencies = []
        self.last_print_time = time.time()
    
    def record_success(self, latency):
        """Enregistrer un succès"""
        self.messages_sent += 1
        self.latencies.append(latency)
    
    def record_failure(self):
        """Enregistrer un échec d'envoi"""
        self.messages_failed += 1
    
    def record_validation_error(self):
        """Enregistrer une erreur de validation"""
        self.validation_errors += 1
    
    def print_stats(self, force=False):
        """Afficher les stats toutes les 10 secondes"""
        now = time.time()
        
        if force or (now - self.last_print_time) >= 10:
            elapsed = now - self.start_time
            rate = self.messages_sent / elapsed if elapsed > 0 else 0
            
            if self.latencies:
                avg_latency = sum(self.latencies) / len(self.latencies)
                min_latency = min(self.latencies)
                max_latency = max(self.latencies)
            else:
                avg_latency = min_latency = max_latency = 0
            
            print("\n" + "=" * 80)
            print("📊 STATISTIQUES KAFKA PRODUCER")
            print("=" * 80)
            print(f"✅ Messages envoyés:     {self.messages_sent}")
            print(f"❌ Échecs d'envoi:       {self.messages_failed}")
            print(f"⚠️  Erreurs validation:  {self.validation_errors}")
            print(f"⚡ Débit:                {rate:.2f} msg/s")
            print(f"⏱️  Latence moyenne:      {avg_latency*1000:.2f}ms")
            print(f"⏱️  Latence min:          {min_latency*1000:.2f}ms")
            print(f"⏱️  Latence max:          {max_latency*1000:.2f}ms")
            print(f"⏳ Temps écoulé:         {elapsed/60:.1f} minutes")
            print("=" * 80 + "\n")
            
            self.last_print_time = now

# ============================================================================
# DONNÉES DE SIMULATION
# ============================================================================
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
     "Terrible experience with {topic}. Complete waste of time for {skill}. #{tag1} #{tag2}",
    "This {topic} is awful. Horrible for {skill}. Never using it again. #{tag1} #{tag2}",
    "Disappointed with {topic}. Doesn't work well for {skill} at all. #{tag1} #{tag2}",
    "Worst {topic} tutorial ever. Terrible explanations of {skill}. #{tag1} #{tag2}",
    "I hate {topic}. So frustrating for {skill}. Total disaster. #{tag1} #{tag2}",
    "Failed miserably with {topic} today. {skill} is impossible. #{tag1} #{tag2}",
    "{topic} is garbage for {skill}. Buggy and unstable. Avoid it. #{tag1} #{tag2}",
    "Absolutely horrible {topic} experience. {skill} is a nightmare. #{tag1} #{tag2}",
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

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def validate_tweet(tweet_data):
    """
    Valide un tweet contre le schéma
    
    Returns:
        (bool, str): (est_valide, message_erreur)
    """
    try:
        validate(instance=tweet_data, schema=TWEET_SCHEMA)
        return True, None
    except ValidationError as e:
        error_msg = f"Champ '{e.path[0] if e.path else 'unknown'}': {e.message}"
        return False, error_msg

def on_send_success(record_metadata):
    """Callback appelé quand le message arrive"""
    logger.debug(f"✅ Message envoyé - Topic: {record_metadata.topic}, "
                 f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")

def on_send_error(excp):
    """Callback appelé en cas d'erreur"""
    logger.error(f"❌ Échec de l'envoi: {excp}")

# ============================================================================
# CRÉATION DU PRODUCER KAFKA (AMÉLIORÉ)
# ============================================================================

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
        
        # ✅ AMÉLIORATION 1 : Garantie de livraison
        acks='all',  # Attendre la confirmation de tous les replicas
        
        # ✅ AMÉLIORATION 2 : Retry automatique
        retries=3,  # Réessayer 3 fois en cas d'échec
        
        # ✅ AMÉLIORATION 3 : Pas de doublons
        enable_idempotence=True,  # Éviter les doublons lors des retries
        
        # ✅ AMÉLIORATION 4 : Garantir l'ordre
        max_in_flight_requests_per_connection=1,
        
        # Compression
        compression_type='gzip',
        
        # Timeouts
        max_block_ms=60000,
        request_timeout_ms=60000,
        api_version_auto_timeout_ms=20000
    )
    logger.info("✅ Connexion Kafka réussie")
    
except Exception as e:
    logger.error(f"❌ Erreur connexion Kafka: {e}")
    exit(1)

# ============================================================================
# AFFICHAGE DE DÉMARRAGE
# ============================================================================

print("=" * 80)
print("🤖 TWITTER SIMULATOR → KAFKA PRODUCER (VERSION AMÉLIORÉE)")
print("=" * 80)
print(f"📤 Kafka: {KAFKA_BROKER}")
print(f"📮 Topic: {KAFKA_TOPIC}")
print("💡 Simulation de tweets réalistes en temps réel")
print("\n🔥 AMÉLIORATIONS ACTIVES :")
print("   ✅ acks='all' → Garantie de livraison")
print("   ✅ retries=3 → Retry automatique")
print("   ✅ Validation JSON → Tweets valides seulement")
print("   ✅ Monitoring → Stats toutes les 10s")
print("   ✅ Partitionnement par user")
print("=" * 80)
print("\n🚀 Démarrage de la simulation...")
print("⏸️  Ctrl+C pour arrêter")
print("📊 Statistiques affichées toutes les 10 secondes\n")
print("-" * 80)

# ============================================================================
# BOUCLE PRINCIPALE
# ============================================================================

tweet_id = 1000000
tweet_count = 0
metrics = KafkaMetrics()

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
            "hashtags": hashtag_set[:2],
            "retweet_count": retweet_count,
            "like_count": like_count
        }
        
        # ✅ VALIDATION du tweet
        is_valid, error = validate_tweet(tweet_data)
        
        if not is_valid:
            logger.error(f"❌ Tweet invalide ignoré: {error}")
            logger.error(f"   Données: {tweet_data}")
            metrics.record_validation_error()
            continue
        
        # ✅ ENVOI vers Kafka avec mesure du temps
        start = time.time()
        
        try:
            # Envoyer avec clé = user (pour partitionnement)
            future = producer.send(
                KAFKA_TOPIC,
                key=user.encode('utf-8'),  # ✅ Partitionnement par user
                value=tweet_data
            )
            
            # Ajouter les callbacks
            future.add_callback(on_send_success)
            future.add_errback(on_send_error)
            
            # Attendre la confirmation
            future.get(timeout=10)
            
            # Mesurer la latence
            latency = time.time() - start
            metrics.record_success(latency)
            
            tweet_count += 1
            tweet_id += 1
            
            # Affichage
            print(f"✅ Tweet #{tweet_count}")
            print(f"   👤 User: @{user}")
            print(f"   📝 Text: {text[:80]}...")
            print(f"   #️⃣  Hashtags: {', '.join(['#' + h for h in hashtag_set[:2]])}")
            print(f"   🔄 RT: {retweet_count} | ❤️  Likes: {like_count}")
            print(f"   ⏱️  Latence: {latency*1000:.2f}ms")
            print("-" * 80)
            
        except KafkaError as e:
            logger.error(f"❌ Erreur Kafka: {e}")
            metrics.record_failure()
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            metrics.record_failure()
        
        # ✅ AFFICHER les statistiques périodiquement
        metrics.print_stats()
        
        # Vitesse de simulation
        delay = random.uniform(0.5, 3)
        time.sleep(delay)

except KeyboardInterrupt:
    print(f"\n⛔ Arrêt de la simulation")
    print(f"📊 Total de tweets générés: {tweet_count}")
    
    # Afficher les stats finales
    metrics.print_stats(force=True)
    
    # Flush et fermeture
    producer.flush()
    producer.close()
    logger.info("✅ Producer fermé proprement")

except Exception as e:
    logger.error(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    producer.close()
