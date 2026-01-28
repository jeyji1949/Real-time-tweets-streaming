# Guide de Démonstration - Pipeline Kafka en Temps Réel

## 🎬 Objectif de la démo

Démontrer le fonctionnement du pipeline de streaming temps réel :
- Génération de tweets simulés
- Transit par Kafka
- Consommation et affichage en temps réel

**Durée** : 5-10 minutes

---

## 🎯 Checklist pré-démo

```
☐ Docker Desktop/Engine démarré
☐ Tous les services Docker UP (docker-compose ps)
☐ venv Python créé et fonctionnel
☐ 2 terminaux prêts (ou splits dans VS Code)
☐ Connexion internet stable (pas obligatoire, tout est local)
```

---

## 📋 Script de démonstration

### Partie 1 : Présentation de l'infrastructure (2 minutes)

**Montrer le fichier docker-compose.yml** :
```bash
cat docker-compose.yml
```

**Expliquer** :
- 5 services Docker : Zookeeper, Kafka, Elasticsearch, Kibana, Cassandra
- Kafka sur port 9092
- Configuration réseau pour communication localhost

**Vérifier les services** :
```bash
docker-compose ps
```

**Résultat à montrer** :
```
NAME          STATUS    PORTS
zookeeper     Up        2181
kafka         Up        9092
elasticsearch Up        9200
kibana        Up        5601
cassandra     Up        9042
```

---

### Partie 2 : Présentation du code (2 minutes)

#### A. Le Producer (Simulateur)

**Ouvrir** `producer/twitter_simulator.py` :
```bash
# Montrer les sections clés :
# - Ligne 15 : Données de simulation (users, hashtags, topics)
# - Ligne 60 : Création du producer Kafka
# - Ligne 90 : Génération des tweets
# - Ligne 115 : Envoi vers Kafka
```

**Expliquer** :
- Génère des tweets réalistes avec hashtags, métriques
- Envoie vers Kafka topic `tweets_raw`
- Vitesse : 1 tweet toutes les 1-3 secondes

#### B. Le Consumer

**Ouvrir** `consumer/consumer.py` :
```bash
# Montrer les sections clés :
# - Ligne 20 : Connexion à Kafka
# - Ligne 35 : Configuration du consumer
# - Ligne 60 : Boucle de lecture des messages
```

**Expliquer** :
- Lit depuis Kafka topic `tweets_raw`
- Affiche les tweets en temps réel
- Group ID : `tweet-consumer-group`

---

### Partie 3 : Démonstration live (3-5 minutes)

#### Terminal 1 : Lancer le Consumer

```bash
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd consumer
python consumer.py
```

**Montrer** :
```
================================================================================
📥 KAFKA CONSUMER - Réception des tweets
================================================================================
📡 Kafka Broker: localhost:9092
📮 Topic: tweets_raw
================================================================================

🔄 Tentative de connexion à Kafka (1/10)...
✅ Connexion à Kafka réussie !

👂 En écoute des tweets...
```

**Expliquer** :
- Le consumer se connecte à Kafka
- Il attend maintenant les messages
- Aucun tweet pour l'instant (topic vide ou offset à la fin)

---

#### Terminal 2 : Lancer le Producer

```bash
# Nouveau terminal
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd producer
python twitter_simulator.py
```

**Montrer** :
```
================================================================================
🤖 TWITTER SIMULATOR → KAFKA PRODUCER
================================================================================
📤 Kafka: localhost:9092
📮 Topic: tweets_raw
================================================================================

🚀 Démarrage de la simulation...

✅ Tweet #1
   👤 User: @python_dev
   📝 Text: Just finished a machine learning project! #Python #AI
   #️⃣  Hashtags: #Python, #AI
   🔄 RT: 42 | ❤️  Likes: 156
--------------------------------------------------------------------------------
```

**Dans le Terminal 1, les tweets apparaissent instantanément !** 🎉

```
📩 Tweet #1 reçu
   ID: 1000000
   👤 User: python_dev
   📝 Text: Just finished a machine learning project! #Python #AI
   🌍 Lang: en
   #️⃣  Hashtags: #Python, #AI
   🔄 Retweets: 42
   ❤️  Likes: 156
--------------------------------------------------------------------------------
```

**Laisser tourner 30-60 secondes** pour montrer plusieurs tweets.

---

### Partie 4 : Vérification technique (2 minutes)

#### Vérifier le topic Kafka

```bash
# Terminal 3 (ou arrêter le producer avec Ctrl+C)
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092
```

**Résultat** :
```
tweets_raw
```

#### Vérifier le contenu du topic

```bash
docker exec -it kafka \
  kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic tweets_raw \
  --from-beginning \
  --max-messages 3
```

**Montrer les messages bruts en JSON**.

#### Voir les détails du topic

```bash
docker exec -it kafka \
  kafka-topics --describe --topic tweets_raw \
  --bootstrap-server localhost:9092
```

**Résultat** :
```
Topic: tweets_raw
PartitionCount: 1
ReplicationFactor: 1
Leader: 1
```

**Expliquer** :
- 1 partition (suffisant pour le projet)
- Pas de réplication (1 seul broker)
- Leader : broker ID 1

---

## 🎯 Points clés à mentionner

### Architecture

```
[Simulateur] → [Kafka Producer] → [Topic: tweets_raw] → [Kafka Consumer] → [Affichage]
```

### Avantages de Kafka

1. **Découplage** : Producer et Consumer indépendants
2. **Scalabilité** : Peut gérer des millions de messages/seconde
3. **Durabilité** : Messages persistés sur disque
4. **Temps réel** : Latence < 100ms

### Évolution du projet

**Actuellement (Personne 1)** :
- ✅ Génération de tweets
- ✅ Streaming via Kafka
- ✅ Consommation basique

**Prochaines étapes** :
- **Personne 2** : Analyse OpenAI + Indexation Elasticsearch
- **Personne 3** : Dashboards Kibana + Stockage Cassandra

---

## 🛑 Arrêt propre de la démo

```bash
# Dans chaque terminal : Ctrl+C

# Arrêter Docker (optionnel)
docker-compose down
```

---

## 📊 Métriques à présenter

Si le temps le permet, montrer :

### Statistiques Kafka

```bash
docker exec -it kafka \
  kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic tweets_raw
```

### Logs Kafka

```bash
docker logs kafka --tail 20
```

---

## 🎤 Questions attendues

**Q : Pourquoi un simulateur et pas la vraie API Twitter ?**  
R : L'API Twitter gratuite ne permet plus le streaming temps réel (limité à 1500 tweets/mois). Notre simulateur génère des données réalistes illimitées pour tester le pipeline.

**Q : Combien de tweets par seconde ?**  
R : ~1 tweet toutes les 1-3 secondes (configurable dans le code). Kafka peut gérer bien plus (millions/seconde).

**Q : Les données sont-elles persistées ?**  
R : Oui, Kafka garde les messages sur disque. Par défaut : 168 heures (7 jours).

**Q : Peut-on ajouter d'autres consumers ?**  
R : Oui ! Plusieurs consumers peuvent lire le même topic simultanément grâce aux consumer groups.

---

## 🎬 Variantes de la démo

### Version courte (3 minutes)

1. Montrer docker-compose ps
2. Lancer consumer + producer
3. Montrer les tweets en temps réel
4. Fin

### Version longue (15 minutes)

1. Présentation infrastructure complète
2. Explication du code ligne par ligne
3. Démonstration live
4. Vérifications techniques Kafka
5. Questions/Réponses

---

## 📸 Screenshots recommandés

1. `docker-compose ps` avec tous les services UP
2. Producer générant des tweets
3. Consumer recevant les tweets
4. `kafka-topics --list` montrant tweets_raw
5. Architecture diagram (à créer)

---

## ✅ Checklist post-démo

```
☐ Tous les terminaux arrêtés proprement (Ctrl+C)
☐ Docker arrêté si nécessaire (docker-compose down)
☐ Code committé sur Git
☐ Documentation à jour
☐ Prêt à passer la main à Personne 2
```
