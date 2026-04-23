# Règles d'inférence TYPE et DOMAIN

Ce document formalise la logique de classification utilisée par le pipeline v2+ avec scoring pondéré et fuzzy matching.

## Entrée de classification (sources)

Le pipeline analyse plusieurs sources textuelles avec des poids différents :

1. **titre** (poids 3.0) — poids maximal, très fiable
2. **nom de fichier** (poids 2.0) — souvent informatif
3. **première page** (poids 1.5) — contexte utile mais peut être bruité
4. **abstract** (poids 1.2) — poids faible, peut être absent

Chaque source est normalisée (minuscules, accents supprimés, ponctuation neutralisée).

## Sources de règles

- TYPE : `type_keywords` dans `library_pipeline/config.yaml`
- DOMAIN : `domain_keywords` dans `library_pipeline/config.yaml`

Les mots-clés supportent deux syntaxes :

**Syntaxe simple (legacy) :**
```yaml
REVIEW: ["systematic review", "literature review"]
```

**Syntaxe enrichie :**
```yaml
COMPUTE:
  - { term: "machine learning", aliases: ["ml"], weight: 1.4, concepts: ["ml"] }
  - { term: "deep learning", concepts: ["deep-learning"] }
  - "algorithm"
```

Les entrées enrichies permettent :
- `term` : terme principal
- `aliases` : variantes (ex. "ml", "ML machine learning")
- `weight` : multiplicateur de score (défaut 1.0)
- `concepts` : tags conceptuels pour la note (ex. "machine-learning")

## Algorithme de score (pondéré + fuzzy)

### Étape 1 : Matching exact

Pour chaque entrée de mot-clé (terme + aliases) :

1. Normaliser le terme
2. Chercher dans chaque source texte
3. Si trouvé (mot exact) : `score = longueur_du_terme * poids_terme * poids_source`
4. Bonus pour match exact : `+0.25 * poids_terme`

### Étape 2 : Matching fuzzy (tolérance aux typos)

Si pas de match exact et fuzzy est activé dans `config.yaml` :

1. Calculer similarité avec `SequenceMatcher` (Python stdlib)
2. Si similarité >= seuil (`threshold: 0.88` par défaut) :
   - `score = longueur * similarité * boost (0.7) * poids_terme * poids_source`
3. Si multi-mot ET similarité >= `partial_threshold (0.92)` : utiliser ce score

Exemples de typos récupérés :
- "systmatic review" → "systematic review" (~0.95 match)
- "machne learning" → "machine learning" (~0.91 match)

### Étape 3 : Sélection du gagnant

Pour chaque label (TYPE ou DOMAIN) :

1. Accumuler le score total de tous les mots-clés qui matchent
2. Compter les mots-clés matchés
3. Classer par (score DESC, match_count DESC)

Fallbacks si aucun match :
- TYPE fallback : `PAPER`
- DOMAIN fallback : `META`

## Domaines secondaires et concepts

### Domaines secondaires

Une fois le domaine primaire sélectionné :

1. Examiner les 2e, 3e, 4e domaines classés
2. Pour chacun : si `score >= primary_score * min_relative_score (0.35)`, l'ajouter
3. Limiter à `max_count: 3` domaines secondaires

Exemple :
- Primary: `COMPUTE` (score 15.0)
- Candidate 2: `FORMAL` (score 6.0) → 6.0 >= 15.0 * 0.35 ✓ inclus
- Candidate 3: `NATURE` (score 3.0) → 3.0 >= 15.0 * 0.35 ✗ exclu

### Concepts

Les concepts sont extraits des mots-clés matchés :

1. Chercher le champ `concepts` de chaque entrée matchée
2. Normaliser et dédupliquer
3. Filtrer les stopwords de domaine (ex. "analysis", "approach", "method")
4. Si aucun concept trouvé : extraire les 2 premiers tokens du titre (hors stopwords)
5. Garantir au moins 1 concept (fallback: "general")

## Périmètre de sortie

Chaque fichier obtient dans le JSON `03_metadata/` :

- `type` : exactement 1 TYPE
- `primary_domain` : exactement 1 DOMAIN primaire
- `secondary_domains` : 0–3 domaines secondaires
- `concept_tags` : 1+ tags conceptuels
- `tags` : fusion dedupliquée de tous les tags (domaines + type + concepts)
- `classification_scores` : top 5 candidats avec leurs scores (pour calibration)

Le nom de fichier ne change pas :
```
TYPE_DOMAIN_YEAR_short-title_author.pdf
```

## Configuration (ajustement de la précision)

Dans `library_pipeline/config.yaml`, section `classification` :

```yaml
classification:
  field_weights:          # Ajuster l'influence de chaque source
    title: 3.0
    filename: 2.0
    first_page: 1.5
    abstract: 1.2
  fuzzy:
    enabled: true         # Tolérance aux typos
    threshold: 0.88       # Seuil pour termes simples
    partial_threshold: 0.92  # Seuil pour multi-mots
    fuzzy_boost: 0.7      # Réduction de score pour fuzzy vs exact
  secondary_domains:
    max_count: 3          # Max de domaines secondaires
    min_relative_score: 0.35  # Seuil relatif au primary
  concept_tags:
    min_count: 1
    fallback: "general"
```

### Stratégies de tuning

**Pour améliorer la précision TYPE :**
- Ajouter plus de `aliases` dans les entrées de `type_keywords`
- Augmenter `weight` pour les types qui sont confondus
- Ajouter des concepts explicites

**Pour améliorer la précision DOMAIN :**
- Enrichir les domaines avec des entrées { term, aliases, weight, concepts }
- Augmenter `weight` pour les domaines clés (ex. "machine learning": 1.4)
- Réduire `min_relative_score` pour être plus inclusif sur les secondaires

**Pour déboguer :**
- Utiliser `python cli.py --dry-run --explain chemin/au/pdf.pdf`
- Voir les scores de chaque candidat TYPE/DOMAIN
- Ajuster les poids et relancer

## Fallbacks et robustesse

- Si aucun mot-clé ne matche : TYPE=`PAPER`, DOMAIN=`META`
- Si titre est vide ou identifiant : utiliser le nom de fichier
- Si PDF ne peut être lu : utiliser le nom de fichier seul
- Si année inconnue : utiliser `0000`
- Si auteur inconnu : utiliser `unknown`

## Conseils d'évolution

- Avant de modifier les seuils, tester avec `--dry-run --explain` sur 5–10 PDFs
- Préférer ajouter des `aliases` plutôt que réduire les seuils (moins de faux positifs)
- Garder les concepts explicites et lisibles (hyphénés, minuscules)
- Conserver les fallbacks en dernier dans config.yaml pour éviter les règles trop générales
- Revalider avec `python cli.py --validate` après changement de config
