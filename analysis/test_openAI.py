#!/usr/bin/env python3
"""
Test OpenAI MINIMAL - Pour vérifier que ça marche sans gaspiller
Coût: ~$0.0001 (0.01 centime)
Compatible avec openai>=1.0.0
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv(dotenv_path='../.env')

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY non trouvé dans .env")
    print("Ajoutez votre clé dans le fichier .env :")
    print("OPENAI_API_KEY=sk-...")
    exit(1)

# Créer le client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

print("=" * 80)
print("🧪 TEST OPENAI MINIMAL")
print("=" * 80)
print(f"🔑 Clé API: {OPENAI_API_KEY[:20]}...")
print()

# Test avec un seul tweet (coût: ~$0.0001)
test_tweet = "I love Python! It's amazing for data science. #Python"

print(f"📝 Tweet de test: {test_tweet}")
print()
print("🔄 Appel OpenAI en cours...")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Modèle le moins cher
        messages=[
            {
                "role": "system",
                "content": "Reply with JSON: {\"sentiment\": \"positive/negative/neutral\", \"topic\": \"topic name\"}"
            },
            {
                "role": "user",
                "content": f"Analyze: {test_tweet}"
            }
        ],
        max_tokens=30,  # Minimum nécessaire
        temperature=0
    )
    
    # Résultat
    print("✅ SUCCÈS ! OpenAI fonctionne !\n")
    
    # Afficher la réponse
    content = response.choices[0].message.content
    print(f"📊 Réponse OpenAI:")
    print(f"   {content}")
    print()
    
    # Statistiques d'utilisation
    tokens_used = response.usage.total_tokens
    cost = (tokens_used / 1000) * 0.0015  # Prix GPT-3.5
    
    print("📈 Statistiques:")
    print(f"   Tokens utilisés: {tokens_used}")
    print(f"   Coût estimé: ${cost:.6f} (~{cost * 100:.4f} centimes)")
    print()
    
    # Vérifier les crédits restants
    print("💰 Pour voir vos crédits restants:")
    print("   → https://platform.openai.com/account/usage")
    print()
    
    print("=" * 80)
    print("✅ TEST RÉUSSI - Vous pouvez utiliser OpenAI !")
    print("=" * 80)
    
except Exception as e:
    error_message = str(e)
    
    if "authentication" in error_message.lower():
        print("❌ ERREUR: Clé API invalide")
        print("Vérifiez votre clé sur: https://platform.openai.com/api-keys")
    
    elif "rate_limit" in error_message.lower():
        print("❌ ERREUR: Limite de taux atteinte")
        print("Attendez quelques secondes et réessayez")
    
    elif "quota" in error_message.lower() or "insufficient" in error_message.lower():
        print("❌ ERREUR: Crédits épuisés")
        print("Ajoutez des crédits sur: https://platform.openai.com/account/billing")
    
    else:
        print(f"❌ ERREUR: {e}")
        print(f"Type: {type(e).__name__}")
