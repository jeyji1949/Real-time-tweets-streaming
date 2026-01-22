	import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

if not BEARER_TOKEN:
    print("❌ Bearer Token manquant !")
    exit(1)

try:
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    
    # Test simple : chercher des tweets récents
    response = client.search_recent_tweets(
        query="python",
        max_results=10
    )
    
    if response.data:
        print(f"✅ Connexion Twitter réussie !")
        print(f"   {len(response.data)} tweets trouvés")
        print(f"\n📝 Exemple de tweet:")
        print(f"   {response.data[0].text[:100]}...")
    else:
        print("⚠️  Connexion OK mais aucun tweet trouvé")
        
except tweepy.errors.Unauthorized:
    print("❌ Erreur d'authentification !")
    print("➡️  Vérifiez votre Bearer Token")
except Exception as e:
    print(f"❌ Erreur: {e}")
