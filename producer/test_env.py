#!/usr/bin/env python3
"""
Test de configuration - Vérification des variables Kafka
"""

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

print("🔍 Vérification de la configuration")
print("=" * 50)

# Kafka
kafka_broker = os.getenv('KAFKA_BROKER')
kafka_topic = os.getenv('KAFKA_TOPIC')

if kafka_broker:
    print(f"✅ KAFKA_BROKER: {kafka_broker}")
else:
    print("❌ KAFKA_BROKER non défini")

if kafka_topic:
    print(f"✅ KAFKA_TOPIC: {kafka_topic}")
else:
    print("❌ KAFKA_TOPIC non défini")

print("=" * 50)
print("\n💡 Ce projet utilise un SIMULATEUR local")
print("   Aucune clé Twitter API n'est nécessaire\n")