# Système de tags

Ce document définit le système de tags utilisé pour enrichir la classification au-delà du nom de fichier.

## Rôle des tags

Le nom de fichier contient seulement :

- 1 TYPE
- 1 DOMAIN primaire

Les tags permettent d'ajouter de la précision sans casser la stabilité du nommage.

## Contrat minimal

Chaque document doit avoir :

- 1 TYPE (dans le filename)
- 1 PRIMARY DOMAIN (dans le filename)
- 0 à 3 SECONDARY DOMAINS (en tags)
- au moins 1 tag CONCEPT

## Format recommandé

Tags courts, en minuscules, séparés par tirets si nécessaire.

Exemples :

- `compute.recsys`
- `compute.ml`
- `graph-neural-networks`
- `cold-start`
- `ranking`

## Catégories de tags

### 1) Domaines secondaires

Utiliser les sous-domaines pour préciser le domaine principal.

Exemples :

- `compute.recsys`, `compute.sec`, `compute.db`
- `nature.bio`, `nature.med`
- `social.econ`, `social.politics`

Limiter à 0-3 tags de sous-domaines par document.

### 2) Concepts

Décrivent les thèmes intellectuels principaux.

Exemples :

- `recommendation`
- `collaborative-filtering`
- `content-based-filtering`
- `evaluation-metrics`
- `privacy`
- `causal-inference`

Chaque document doit avoir au moins 1 tag conceptuel.

### 3) Méthodes (optionnel)

Exemples :

- `systematic-review`
- `meta-analysis`
- `benchmarking`
- `ablation-study`
- `case-study`

### 4) Données / artefacts (optionnel)

Exemples :

- `movielens`
- `lastfm`
- `amazon-reviews`
- `open-source`

### 5) Contexte applicatif (optionnel)

Exemples :

- `healthcare`
- `finance`
- `education`
- `cybersecurity`

## Bonnes pratiques

- Préférer des tags stables et réutilisables.
- Éviter les tags trop proches sémantiquement (`recsys` vs `recommender-systems`) dans la même base.
- Garder une granularité cohérente entre documents.
- Éviter les tags purement temporels (`2024-trends`) sauf besoin explicite.
- Ne pas encoder TYPE/DOMAIN primaire en tag si déjà présents dans le nom de fichier.

## Anti-patterns

- Trop de tags (bruit > signal).
- Tags vagues (`misc`, `other`, `general`).
- Tags qui dupliquent le titre mot à mot.
- Mélange de conventions (`snake_case`, `camelCase`, espaces).

## Exemple complet

Fichier :

`REVIEW_COMPUTE_2024_movie-recommender-systems_ariyanto.pdf`

Tags recommandés :

- `compute.recsys`
- `compute.ml`
- `recommendation`
- `collaborative-filtering`
- `cold-start`

## Lien avec les autres guides

- docs/FILE-NAMING.md
- docs/TYPES.md
- docs/DOMAINS.md
- docs/INFERENCE-RULES.md
