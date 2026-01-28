# 🐳 Docker – Organisation du projet

---

## ❓ Qui crée le docker-compose ?

👉 **UNE SEULE PERSONNE** (toi – Personne 1)

Pourquoi ?
- Un seul fichier = cohérence
- Pas de conflits
- Même environnement pour tous

---

## 🧱 docker-compose.yml contient :

- Kafka
- Zookeeper
- Elasticsearch
- Kibana
- Cassandra

👉 Versions définies dans le fichier (pas sur les machines)

---

## 💻 Installation locale (TOUT LE MONDE)

Chaque membre installe :

- Docker
- Docker Compose

OS différent ? Aucun problème :
- Linux ✅
- Windows ✅
- Docker isole tout

---

## ▶️ Lancer le projet

```bash
docker compose up -d
docker compose down