# Convention de nommage des fichiers PDF

## Modèle

```txt
[TYPE]_[DOMAIN]_[YEAR]_[SHORT-TITLE]_[AUTHOR-OR-SOURCE].pdf
```

Exemple :

```txt
REVIEW_COMPUTE_2024_movie-recommender-systems_ariyanto.pdf
```

## Objectifs

1. triable (chronologique)
2. lisible rapidement (par type et domaine)
3. unique (évite les collisions)
4. exploitable par scripts

## Règles globales

1. Pas d'espaces
- `_` sépare les champs
- `-` est réservé au SHORT-TITLE

2. Pas d'accents ni caractères spéciaux

3. TYPE
- exactement un TYPE standard
- toujours en MAJUSCULES

4. DOMAIN
- exactement un domaine primaire
- toujours en MAJUSCULES
- les sous-domaines vont en tags, pas dans le nom de fichier

5. YEAR
- toujours 4 chiffres
- utiliser `0000` si inconnu
- pour les preprints, préférer l'année de publication si disponible

6. SHORT-TITLE
- en minuscules
- séparé par tirets
- mots vides supprimés
- 3 a 6 mots-clés conseillés
- abréviations autorisées seulement si standard (`nlp`, `ai`)

7. AUTHOR-OR-SOURCE
- nom de famille en minuscules
- si plusieurs auteurs : premier auteur seulement
- si inconnu : utiliser une source stable (journal, organisme)

8. Doublons
- suffixer avec `_v2`, `_v3`, etc.

9. Longueur
- garder le nom de fichier en dessous de 100 caractères

10. Stabilité
- la structure ne doit pas changer une fois adoptée
- les listes TYPE et DOMAIN peuvent évoluer

## Contraintes de classification

Chaque fichier doit avoir :

- 1 TYPE
- 1 DOMAIN primaire (dans le nom)
- 0 a 3 domaines secondaires (en tags)
- au moins 1 tag conceptuel

## Règles réellement appliquées par le pipeline

Le code dans library_pipeline/cli.py applique aussi les contraintes suivantes :

- format final : `TYPE_DOMAIN_YEAR_SHORT-TITLE_AUTHOR.pdf`
- validation regex : `^[A-Z]+_[A-Z]+_\d{4}_[a-z0-9\-]+_[a-z]+(?:_v\d+)?\.pdf$`
- si longueur > 100 : trim du SHORT-TITLE
- si collision dans le dossier `02_processed` : `_v2` a `_v99`

## Références liées

- docs/TYPES.md
- docs/DOMAINS.md
- docs/INFERENCE-RULES.md
