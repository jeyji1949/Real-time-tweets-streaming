# 🧠 GitHub Workflow – Travail en équipe

Ce document explique **comment travailler ensemble correctement avec GitHub** afin d'éviter les conflits et garder un projet propre.

---

## 👥 Organisation des rôles

| Personne | Branche | Responsabilité principale |
|----------|---------|--------------------------|
| 1 | `kafka` | Kafka + Twitter Simulator |
| 2 | `analysis` | OpenAI + Elasticsearch |
| 3 | `cassandra` | Cassandra + Kibana |

---

## 🚫 Règle d'or

❌ **Personne ne travaille directement sur `main`**

- `main` = branche stable finale
- Toute modification passe par une **Pull Request**

---

## 🌱 Créer sa branche (une seule fois)

```bash
git checkout main
git pull origin main
git checkout -b <nom-branche>
```

**Exemples :**

```bash
git checkout -b kafka
git checkout -b analysis
git checkout -b cassandra
```

---

## ✍️ Travailler sur sa branche

```bash
# vérifier la branche
git branch

# coder normalement
# puis :
git add .
git commit -m "Description claire du changement"
```

---

## 🚀 Push vers GitHub

```bash
git push origin <nom-branche>
```

**Exemple :**

```bash
git push origin kafka
```

---

## 🔀 Pull Request (PR)

1. Aller sur GitHub
2. Onglet **Pull Requests**
3. Cliquer sur **New Pull Request**
4. **Base :** `main`
5. **Compare :** ta branche (`kafka`, `analysis`, etc.)

👉 Le PR ne modifie **PAS encore** `main`

---

## ✅ Merge (intégration finale)

1. Le responsable (ou l'équipe) valide la PR
2. GitHub merge la branche dans `main`
3. ✔️ À ce moment-là, les changements sont dans `main`

---

## 🔄 Mettre à jour son local après un merge

⚠️ **OBLIGATOIRE pour tout le monde**

```bash
git checkout main
git pull origin main
```

Puis remettre à jour sa branche :

```bash
git checkout kafka
git merge main
```

---

## ⚠️ Conflits

En cas de conflit :

1. Corriger manuellement
2. Puis :

```bash
git add .
git commit -m "Resolve merge conflict"
```
