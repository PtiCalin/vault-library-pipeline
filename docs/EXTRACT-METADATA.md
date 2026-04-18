# Extraction des métadonnées

Ce document décrit comment le pipeline extrait et enrichit les métadonnées d'un PDF.

## Vue d'ensemble

Le traitement est piloté par `extract_document_metadata` dans library_pipeline/cli.py.

Sources utilisées :

1. métadonnées internes PDF (source de base)
2. GROBID (optionnel)
3. CrossRef via DOI (optionnel)
4. Semantic Scholar via DOI (optionnel)

## Champs extraits

- `title`
- `author` (token normalisé pour le nom de fichier)
- `authors` (liste complète si disponible)
- `year`
- `doi`
- `abstract`
- `first_page_text` (utilisé pour l'inférence)
- `metadata_sources` (traçabilité des sources)

## Détails de fallback

### Titre

- valeur initiale : stem du nom de fichier
- remplacé par le titre PDF si disponible
- peut être amélioré par enrichissement externe si jugé meilleur

### Auteur

- extrait depuis la métadonnée PDF auteur
- liste parsée avec séparateurs `;` et ` and `
- token auteur final : dernier mot alphabétique du premier auteur
- fallback : `unknown`

### Année

- extraction via regex `(?:19|20)\d{2}`
- priorité : `creationdate`, puis `moddate`
- fallback : `0000`

### DOI

- détection regex dans titre + front matter
- regex : `10\.\d{4,9}/[-._;()/:a-z0-9]+`
- normalisé en minuscules

## Enrichissement optionnel

Contrôlé par `metadata_enrichment` dans library_pipeline/config.yaml.

Comportement :

- si `enabled: true`, tentative GROBID
- si DOI disponible ensuite, tentative CrossRef puis Semantic Scholar
- en cas d'échec réseau/API : warning et continuation sans crash

## Stratégie de fusion

La fusion est non destructive :

- un champ existant est conservé sauf cas explicitement préférentiel
- `title` peut être remplacé si candidat plus informatif
- `authors` rempli seulement si vide
- `author` rempli si `unknown`
- `year` remplacé si courant `0000` et candidat valide
- `doi` et `abstract` remplis si absents

## Sortie persistée

Les métadonnées finales sont écrites dans `03_metadata` en JSON, un fichier par PDF traité.
