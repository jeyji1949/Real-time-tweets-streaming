#!/usr/bin/env python3
"""
Test OpenAI MINIMAL - version API moderne
Coût: ~$0.00005
"""

import os
from openai import OpenAI

# 🔍 DEBUG
print("DEBUG OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY non trouvé")
    print("➡️ Vérifie que tu as bien fait : source .env")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

print("=" * 80)
print("🧪 TEST OPENAI MINIMAL (API MODERNE)")
print("=" * 80)

tweet = "I love Python! It's amazing for data science. #Python"
print(f"📝 Tweet: {tweet}\n")

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Reply ONLY with valid JSON like: "
                    "{\"sentiment\":\"positive|neutral|negative\",\"topic\":\"one word\"}"
                )
            },
            {
                "role": "user",
                "content": tweet
            }
        ],
        max_tokens=25,
        temperature=0
    )

    content = response.choices[0].message.content

    print("✅ SUCCÈS !")
    print("📊 Réponse OpenAI :")
    print(content)

    tokens = response.usage.total_tokens
    cost = (tokens / 1_000_000) * 0.15  # gpt-4o-mini

    print("\n📈 Stats:")
    print(f"Tokens: {tokens}")
    print(f"Coût estimé: ${cost:.6f}")

except Exception as e:
    print("❌ ERREUR OpenAI")
    print(e)

