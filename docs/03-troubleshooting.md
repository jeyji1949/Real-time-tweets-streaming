# Guide de Dépannage - Problèmes Rencontrés et Solutions

Ce document répertorie **tous les problèmes rencontrés** pendant le développement et leurs solutions.

---

## 🔴 Problème 1 : Installation des packages Python bloquée

### Symptôme

```bash
pip3 install tweepy kafka-python python-dotenv

❌ error: externally-managed-environment
```

### Cause

Ubuntu 22.04+ bloque l'installation globale de packages Python pour protéger le système.

### Solution appliquée

✅ **Créer un environnement virtuel (venv)**

```bash
python3 -m venv venv
source venv/bin/activate
pip install tweepy kafka-python python-dotenv
```

### Pourquoi cette solution

- ✅ Isole les dépendances du projet
- ✅ Évite les conflits entre projets
- ✅ Facilite le partage avec l'équipe (requirements.txt)
- ✅ Garde le système propre

### Alternatives rejetées

❌ `pip3 install --user` : Packages mélangés entre tous les projets  
❌ `pip3 install --break-system-packages` : Risque de casser Ubuntu

---

## 🔴 Problème 2 : API Twitter - Erreur 402 "CreditsDepleted"

### Symptôme

```bash
Stream encountered HTTP error: 402
{"title":"CreditsDepleted","detail":"Your enrolled account does not have any credits"}
```

### Cause

L'API Twitter gratuite a des limites strictes :
- ❌ **Pas de streaming en temps réel** (Filtered Stream réservé aux plans payants)
- ✅ Seulement 1,500 tweets/mois en lecture

### Solution appliquée

✅ **Créer un simulateur de tweets réaliste**

Fichier : `producer/twitter_simulator.py`

**Avantages** :
- ✅ Gratuit et illimité
- ✅ Données contrôlées et cohérentes
- ✅ Parfait pour tester le pipeline
- ✅ Génère des tweets réalistes avec hashtags, métriques

### Code du simulateur

Génère des tweets toutes les 1-3 secondes avec :
- Texte réaliste
- Hashtags pertinents
- Métriques (retweets, likes)
- Format JSON standardisé

### Alternatives rejetées

❌ **Payer l'API Twitter** : $100-5000/mois (trop cher pour étudiant)  
❌ **Dataset statique** : Pas de temps réel, données obsolètes

---

## 🔴 Problème 3 : Consumer se ferme immédiatement

### Symptôme

```bash
python consumer.py

👂 En écoute des tweets...
✅ Consumer fermé proprement
# Se ferme après 1 seconde
```

### Cause

Timeout trop court dans la configuration :

```python
consumer_timeout_ms=1000  # 1 seconde
```

Si aucun message en 1 seconde → le consumer se ferme.

### Solution appliquée

✅ **Supprimer le timeout**

```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    # SUPPRIMÉ : consumer_timeout_ms=1000
    auto_offset_reset='earliest',
    enable_auto_commit=True
)
```

Maintenant le consumer attend **indéfiniment** jusqu'à Ctrl+C.

---

## 🔴 Problème 4 : ModuleNotFoundError: No module named 'kafka'

### Symptôme

```bash
python consumer.py

❌ ModuleNotFoundError: No module named 'kafka'
```

### Cause

Le **venv n'était pas activé** avant de lancer le script.

Prompt incorrect :
```bash
➜  consumer git:(kafka) ✗    # ← Pas de (venv)
```

### Solution appliquée

✅ **Toujours activer le venv**

```bash
source venv/bin/activate
```

Prompt correct :
```bash
(venv) ➜  consumer git:(kafka) ✗    # ← (venv) présent
```

### Prévention

Créer des scripts de lancement :

```bash
# run_consumer.sh
#!/bin/bash
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
source venv/bin/activate
cd consumer
python consumer.py
```

---

## 🔴 Problème 5 : KafkaTimeoutError - Failed to update metadata

### Symptôme

```bash
python twitter_simulator.py

✅ Connexion Kafka réussie
❌ Erreur: KafkaTimeoutError: Failed to update metadata after 60.0 secs.
```

### Cause

**Problème de configuration réseau** dans `docker-compose.yml`.

Configuration incorrecte :
```yaml
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
```

Le producer Python (hors Docker) ne peut pas résoudre le hostname `kafka`.

### Solution appliquée

✅ **Configurer deux listeners** : un interne (Docker) et un externe (localhost)

```yaml
kafka:
  environment:
    KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
    KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
    KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
```

### Explication

- **PLAINTEXT://kafka:29092** : Pour les conteneurs Docker (communication interne)
- **PLAINTEXT_HOST://localhost:9092** : Pour les applications sur la machine hôte (Python)

### Vérification

```bash
# Après modification
docker-compose down -v
docker-compose up -d
sleep 90

# Tester
python producer/test_simple_producer.py
# ✅ Devrait fonctionner
```

---

## 🔴 Problème 6 : NoBrokersAvailable lors de la connexion

### Symptôme

```bash
kafka.errors.NoBrokersAvailable: NoBrokersAvailable
```

### Cause

Kafka n'était **pas encore prêt** après `docker-compose up -d`.

### Solution appliquée

✅ **Attendre 90 secondes** après le démarrage

```bash
docker-compose up -d
sleep 90  # Attendre que Kafka démarre complètement
```

✅ **Vérifier que Kafka est prêt**

```bash
docker logs kafka 2>&1 | grep "started"

# Résultat attendu :
# [KafkaServer id=1] started (kafka.server.KafkaServer)
```

### Amélioration du code

Ajouter un **retry logic** dans le consumer :

```python
for attempt in range(1, 11):
    try:
        consumer = KafkaConsumer(...)
        print("✅ Connexion réussie")
        break
    except NoBrokersAvailable:
        if attempt < 10:
            print(f"⚠️  Tentative {attempt}/10...")
            time.sleep(3)
```

---

## 🔴 Problème 7 : Topic n'existe pas

### Symptôme

Les messages ne passent pas, ou erreur metadata.

### Cause

Le topic `tweets_raw` n'avait pas été créé.

### Solution 1 : Création manuelle

```bash
docker exec -it kafka \
  kafka-topics --create --topic tweets_raw \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

### Solution 2 : Auto-création (appliquée)

✅ **Activer la création automatique** dans `docker-compose.yml`

```yaml
kafka:
  environment:
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
```

Le topic se crée automatiquement au premier message ! 🎉

---

## 🔴 Problème 8 : Topic 'tweets_raw' already exists

### Symptôme

```bash
Error while executing topic command : Topic 'tweets_raw' already exists.
```

### Cause

Tentative de recréer un topic existant.

### Solution

✅ **C'est normal ! Ignorer l'erreur.**

Le topic existe déjà et fonctionne.

**OU** si vous voulez repartir de zéro :

```bash
# Supprimer
docker exec -it kafka \
  kafka-topics --delete --topic tweets_raw \
  --bootstrap-server localhost:9092

# Recréer
docker exec -it kafka \
  kafka-topics --create --topic tweets_raw \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

---

## 🔴 Problème 9 : Docker containers en status "Exited"

### Symptôme

```bash
docker-compose ps

kafka        Exited (1)
```

### Cause

Erreur de configuration ou ressources insuffisantes.

### Solution appliquée

✅ **Nettoyer et redémarrer**

```bash
docker-compose down -v  # Supprimer volumes
docker system prune -f  # Nettoyer Docker
docker-compose up -d
sleep 90
```

✅ **Vérifier les logs**

```bash
docker logs kafka
docker logs zookeeper
```

### Prévention

- Allouer au moins 4GB de RAM à Docker
- Vérifier que les ports ne sont pas utilisés : 9092, 9200, 5601, 9042

---

## 📊 Commandes de diagnostic

### Vérifier l'état des services

```bash
docker-compose ps
docker logs kafka --tail 50
docker logs zookeeper --tail 50
```

### Vérifier Kafka

```bash
# Kafka a démarré ?
docker logs kafka 2>&1 | grep "started"

# Topics disponibles
docker exec -it kafka \
  kafka-topics --list --bootstrap-server localhost:9092

# Détails d'un topic
docker exec -it kafka \
  kafka-topics --describe --topic tweets_raw \
  --bootstrap-server localhost:9092

# Lire les messages
docker exec -it kafka \
  kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic tweets_raw \
  --from-beginning \
  --max-messages 5
```

### Vérifier Python

```bash
# venv activé ?
which python  # Doit contenir "venv"

# Packages installés ?
pip list | grep kafka
pip list | grep tweepy

# Variables d'environnement chargées ?
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('KAFKA_BROKER'))"
```

---

## 🎯 Checklist de dépannage rapide

Si quelque chose ne marche pas :

```
☐ Docker tourne ? (docker ps)
☐ Services UP ? (docker-compose ps)
☐ Kafka démarré ? (docker logs kafka | grep started)
☐ venv activé ? ((venv) dans le prompt)
☐ Attendu 90s après docker-compose up ?
☐ Topic existe ? (kafka-topics --list)
☐ .env configuré ? (cat .env)
☐ Bonne version docker-compose.yml ? (avec ADVERTISED_LISTENERS)
```

---

## 🆘 Redémarrage complet (dernier recours)

Si rien ne fonctionne :

```bash
# 1. Tout arrêter et nettoyer
cd ~/Documents/BIAM/BIGDATA/Twitter-Project
docker-compose down -v
docker system prune -af --volumes

# 2. Vérifier docker-compose.yml
cat docker-compose.yml | grep ADVERTISED_LISTENERS
# Doit contenir : PLAINTEXT_HOST://localhost:9092

# 3. Redémarrer
docker-compose up -d

# 4. ATTENDRE 90 SECONDES
sleep 90

# 5. Vérifier
docker-compose ps
docker logs kafka | grep started

# 6. Tester
source venv/bin/activate
cd producer
python test_simple_producer.py
```

---

## ✅ Résumé des solutions appliquées

| Problème | Solution | Fichier modifié |
|----------|----------|-----------------|
| pip install bloqué | venv | - |
| API Twitter payante | Simulateur | `producer/twitter_simulator.py` |
| Consumer se ferme | Supprimer timeout | `consumer/consumer.py` |
| Module not found | Activer venv | - |
| Metadata timeout | Fix ADVERTISED_LISTENERS | `docker-compose.yml` |
| Broker unavailable | Attendre 90s + retry | `consumer/consumer.py` |
| Topic inexistant | Auto-create | `docker-compose.yml` |

---

## 📚 Ressources utiles

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [kafka-python Docs](https://kafka-python.readthedocs.io/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Tweepy Docs](https://docs.tweepy.org/) (référence)

---

**Tous ces problèmes ont été résolus. Le pipeline fonctionne maintenant parfaitement ! ✅**
