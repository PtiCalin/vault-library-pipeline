# Types de documents (TYPE)

Ce document décrit les valeurs TYPE utilisées dans la convention de nommage :

TYPE_DOMAIN_YEAR_short-title-slug_authorlastname.pdf

Le TYPE représente la nature du document (article, rapport, cours, etc.).

## Règles d'inférence

- La détection est basée sur des mots-clés définis dans library_pipeline/config.yaml, section type_keywords.
- Le texte classifié combine le titre, le nom de fichier, et si possible le texte de la première page.
- La normalisation est en minuscules, sans ponctuation, avec espaces simplifiés.
- Le meilleur TYPE est choisi par score de correspondance.
- En cas d'égalité, le TYPE avec le plus de mots-clés trouvés est retenu.
- Si aucun mot-clé ne matche, la valeur de repli est PAPER.

## Contrat d'usage

- Chaque PDF doit avoir exactement 1 TYPE.
- Le TYPE est encodé dans le nom de fichier.
- Les variantes fines doivent rester dans les tags (pas dans le token TYPE).
- Le TYPE doit être en UPPER_ALPHA (majuscules, sans point).

## Taxonomie canonique

### 1) Academic

- PAPER : article de recherche original.
- REVIEW : revue structurée de littérature.
- SURVEY : panorama large d'un domaine.
- META : méta-analyse de plusieurs études.
- THESIS : mémoire académique (MSc).
- DISSERTATION : thèse doctorale (PhD).
- PREPRINT : article non peer-reviewed (ex. arXiv).

### 2) Conference / publication formats

- PROCEEDING : article publié dans des proceedings.
- ABSTRACT : abstract de conférence uniquement.
- POSTER : poster de recherche.
- TALK : présentation, slide deck, keynote.

### 3) Books and long-form

- BOOK : livre académique ou technique complet.
- CHAPTER : chapitre de livre.
- MONOGRAPH : ouvrage spécialisé.

### 4) Technical / industry / grey literature

- REPORT : rapport institutionnel ou industriel.
- WHITEPAPER : document de position technique.
- STANDARD : standard formel (ISO, RFC, W3C, etc.).
- SPEC : spécification technique (API, protocole, système).
- DOC : documentation officielle.

### 5) Educational / explanatory

- TUTORIAL : guide technique pas à pas.
- GUIDE : document explicatif structuré.
- COURSE : support de cours, série de leçons.
- NOTE : note structurée personnelle ou informelle.

### 6) Data / code / artifacts

- DATASET : dataset ou description de dataset.
- BENCHMARK : benchmark ou dataset d'évaluation.
- CODE : implémentation ou référence de dépôt.
- MODEL : architecture de modèle ou modèle préentraîné.

### 7) Media / communication

- ARTICLE : article de publication générale ou magazine.
- BLOG : billet de blog.
- NEWS : contenu d'actualité.
- INTERVIEW : entretien ou discussion.

### 8) Legal / policy

- POLICY : document de gouvernance/politique.
- LAW : texte juridique.
- REGULATION : document réglementaire.

## Bonnes pratiques

- Garder les catégories stables dans le temps : le TYPE est une interface de classement.
- Ajouter des mots-clés dans config.yaml plutôt que changer les noms de TYPE existants.
- Utiliser des TYPE en UPPER_ALPHA (majuscules, sans point).
- Éviter d'ajouter un nouveau TYPE si un TYPE existant couvre déjà le besoin.
- En cas d'ambiguïté forte, garder PAPER et affiner via tags plutôt que sur-spécialiser le token.
