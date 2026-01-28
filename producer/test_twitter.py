#!/usr/bin/env python3
from kafka import KafkaProducer
import json
import time
from datetime import datetime

print("=" * 80)
print("🧪 TEST SIMPLE PRODUCER")
print("=" * 80)

BROKER = 'localhost:9092'
TOPIC = 'tweets_raw'

print(f"\n📡 Broker: {BROKER}")
print(f"📮 Topic: {TOPIC}")
print("\n🔄 Création du producer...\n")

try:
    producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=1,
       # max_block_ms=60000
    )
    print("✅ Producer créé avec succès !\n")
    
    # Envoyer 3 messages de test
    for i in range(1, 4):
        tweet = {
            "tweet_id": str(1000 + i),
            "text": f"Message de test numero {i}",
            "created_at": datetime.now().isoformat(),
            "user": "test_user",
            "lang": "fr",
            "hashtags": ["test"]
        }
        
        print(f"📤 Envoi du message {i}...")
        future = producer.send(TOPIC, value=tweet)
        
        # Attendre confirmation
        record = future.get(timeout=10)
        print(f"   ✅ Confirmé - Partition: {record.partition}, Offset: {record.offset}")
        
        time.sleep(1)
    
    producer.flush()
    producer.close()
    print("\n✅ Test réussi ! Tous les messages envoyés.\n")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}\n")
    print(f"Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()