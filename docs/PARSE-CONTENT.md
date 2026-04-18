# Parsing du contenu PDF

Ce document décrit la phase de parsing texte utilisée pour la classification.

## Objectif

Extraire un signal textuel suffisant pour améliorer l'inférence TYPE/DOMAIN sans rendre le pipeline fragile.

## Zones extraites

Le pipeline lit des zones courtes et utiles :

- première page : max 8000 caractères (`extract_first_page_text`)
- front matter (pages 1 et 2) : max 16000 caractères (`extract_front_matter_text`)

Ces limites gardent un coût stable et évitent de parser tout le document.

## Nettoyage et normalisation

Fonctions clés :

- `normalize_text` : minuscule, suppression ponctuation, espaces normalisés
- `tokenize_text` : tokenisation et retrait de bruit (`doi`, `isbn`, éditeurs, URLs)
- `clean_text` : nettoyage orienté slugification

## Détection de titres faibles

La fonction `looks_like_identifier` identifie des titres peu informatifs (ID, séquences numériques, etc.).

Si un titre semble être un identifiant :

- le stem du fichier est réinjecté dans le texte de classification
- cela réduit les cas de fallback forcé (`PAPER`, `META`)

## Impact sur la suite

Le texte parsé alimente :

- extraction DOI (titre + front matter)
- inférence TYPE/DOMAIN (titre + stem + première page)

En cas d'échec d'extraction texte (PDF complexe/scanné), le pipeline continue avec les autres signaux disponibles.
