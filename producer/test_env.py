from dotenv import load_dotenv
import os

load_dotenv()

bearer = os.getenv('TWITTER_BEARER_TOKEN')

if bearer:
    print("✅ Bearer Token chargé !")
    print(f"   Longueur: {len(bearer)} caractères")
    print(f"   Début: {bearer[:20]}...")
else:
    print("❌ Bearer Token NON trouvé dans .env")
    print("➡️  Vérifiez votre fichier .env")
