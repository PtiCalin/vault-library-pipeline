# Domaines disciplinaires (DOMAIN)

Ce document décrit les valeurs DOMAIN utilisées dans la convention de nommage :

TYPE_DOMAIN_YEAR_short-title-slug_authorlastname.pdf

Le DOMAIN représente le champ disciplinaire principal du document.

## Règles d'inférence

- La détection est basée sur les mots-clés de library_pipeline/config.yaml, section domain_keywords.
- Le texte analysé combine le titre, le nom du fichier, et si disponible la première page extraite du PDF.
- Le texte est normalisé (minuscules, ponctuation retirée, espaces simplifiés).
- Le DOMAIN est choisi selon le meilleur score de correspondance.
- En cas d'égalité de score, le domaine avec le plus de mots-clés trouvés est retenu.
- Si aucun mot-clé ne matche, la valeur de repli est META.

## Modèle de classification attendu

Chaque fichier doit avoir :

- 1 PRIMARY DOMAIN (dans le nom de fichier)
- 0 a 3 SECONDARY DOMAINS (en tags)
- au moins 1 tag CONCEPT

## Taxonomie primaire et secondaire

### 1) FORMAL

Systèmes abstraits : mathématiques, logique, statistique, symbolique.

- FORMAL.MATH
- FORMAL.STATS
- FORMAL.LOGIC
- FORMAL.OPTIMIZATION

### 2) COMPUTE

Informatique et calcul : logiciels, IA, systèmes, données.

- COMPUTE.ML
- COMPUTE.AI
- COMPUTE.RECSYS
- COMPUTE.DATA
- COMPUTE.DB
- COMPUTE.SYS
- COMPUTE.SE
- COMPUTE.NET
- COMPUTE.SEC
- COMPUTE.BLOCKCHAIN
- COMPUTE.MEDIA

### 3) NATURE

Sciences physiques et biologiques : bio, médecine, physique, chimie, écologie.

- NATURE.BIO
- NATURE.MED
- NATURE.PHYSICS
- NATURE.CHEM
- NATURE.ECOLOGY

### 4) HUMAN

Esprit et comportement : psychologie, cognition, neurosciences, décision.

- HUMAN.PSYCH
- HUMAN.COGNITION
- HUMAN.NEURO
- HUMAN.BEHAVIOR

### 5) SOCIAL

Systèmes humains : économie, politique, organisations, gouvernance.

- SOCIAL.ECON
- SOCIAL.POLITICS
- SOCIAL.ORG
- SOCIAL.SYSTEMS

### 6) CULTURE

Sens et expression : art, musique, cinéma, littérature, philosophie, religion.

- CULTURE.ART
- CULTURE.MUSIC
- CULTURE.CINEMA
- CULTURE.LITERATURE
- CULTURE.PHILOSOPHY
- CULTURE.RELIGION

### 7) DESIGN

Conception et forme : UX, produit, architecture, pensée système.

- DESIGN.UX
- DESIGN.PRODUCT
- DESIGN.ARCH
- DESIGN.SYSTEMS

### 8) ENGINEERING

Systèmes appliqués : infrastructure, hardware, énergie.

- ENGINEERING.SOFTWARE
- ENGINEERING.HARDWARE
- ENGINEERING.INFRA
- ENGINEERING.ENERGY

### 9) META

Connaissance de la connaissance : méthodes, apprentissage, classification.

- META.RESEARCH
- META.LEARNING
- META.KNOWLEDGE
- META.CLASSIFICATION

## Important : DOMAIN n'est pas un tag fin

- DOMAIN doit rester compact et stable.
- Les sous-domaines (exemple : cybersécurité mobile, recsys, LLM, bioinformatique) vont dans les tags de notes, pas dans le nom de fichier.
- Le nom de fichier garde un seul token DOMAIN, en UPPER_ALPHA.
- Les sous-domaines sont des tags secondaires, pas des segments du filename.

## Exemples

- PAPER_COMPUTE_2024_mobile-malware-analysis_dupont.pdf
- REVIEW_NATURE_2021_crispr-gene-editing_martin.pdf
- REPORT_SOCIAL_2020_governance-of-ai_bernard.pdf
- GUIDE_DESIGN_2023_accessible-interfaces_leroy.pdf

## Conseils de maintenance

- Modifier d'abord les mots-clés dans config.yaml avant d'introduire un nouveau DOMAIN.
- Ajouter un nouveau DOMAIN seulement si la distinction est durable et utile sur le long terme.
- Éviter les domaines trop fins qui réduisent la cohérence du classement.
- Préserver un petit nombre de domaines primaires pour garder la lecture stable.
