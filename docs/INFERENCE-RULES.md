# Règles d'inférence TYPE et DOMAIN

Ce document formalise la logique de classification utilisée par le pipeline.

## Entrée de classification

Le texte de classification est construit par `build_classification_text` avec :

1. titre du document
2. nom de fichier original (stem)
3. texte de première page si disponible

Si le titre ressemble à un identifiant non informatif, les tokens du stem sont renforcés.

## Sources de règles

- TYPE : `type_keywords` dans library_pipeline/config.yaml
- DOMAIN : `domain_keywords` dans library_pipeline/config.yaml

Les matches sont faits en mode normalisé (insensible à la casse, ponctuation neutralisée).

## Algorithme de score

Fonction : `score_label_matches`.

Pour chaque mot-clé qui matche :

- `match_count += 1`
- `score += nombre_de_mots_du_mot_clé`

Conséquence :

- une expression multi-mots (ex. `machine learning`) pèse plus qu'un terme court isolé

## Sélection du gagnant

Fonction : `infer_label`.

Ordre de décision :

1. meilleur `score`
2. en cas d'égalité, meilleur `match_count`
3. si score nul partout : fallback

Fallbacks actuels :

- TYPE fallback : `PAPER`
- DOMAIN fallback : `META`

## Périmètre de sortie

Chaque fichier obtient :

- exactement 1 TYPE
- exactement 1 DOMAIN primaire

Les sous-domaines et concepts ne sont pas encodés dans le nom du fichier. Ils sont destinés aux tags des notes.

## Conseils d'évolution

- ajuster d'abord les mots-clés dans config.yaml
- préférer des expressions spécifiques plutôt que des mots trop génériques
- tester sur un lot réel avant de figer de nouvelles règles
- conserver l'ordre logique des fallback en dernier
