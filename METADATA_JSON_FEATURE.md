# Fonctionnalité metadata.json

## Description

Le programme `main.py` a été modifié pour générer automatiquement un second fichier JSON nommé `metadata.json` dans le répertoire des images traitées. Ce fichier contient les métadonnées dans un format spécifique adapté aux besoins de l'utilisateur.

## Modifications apportées

### 1. Ajout de l'import manquant
- Ajout de `import os` dans les imports de `main.py`

### 2. Nouvelle fonction `generate_metadata_json()`

Cette fonction :
- Prend en paramètres les résultats du traitement et le chemin d'entrée
- Calcule automatiquement la taille des fichiers
- Détermine le type MIME basé sur l'extension
- Mappe les champs des résultats vers le format demandé
- Sauvegarde le fichier `metadata.json` dans le répertoire des images

### 3. Intégration dans le flux principal

La fonction est appelée automatiquement après le traitement des images, juste avant l'affichage du résumé.

## Format du fichier metadata.json

Le fichier généré contient les champs suivants :

```json
{
  "Fichier": "nom-du-fichier.jpg",
  "Taille": "307 kB",
  "Type": "image/jpeg",
  "Largeur": 655,
  "Hauteur": 919,
  "Categorie": "Genre principal",
  "Categorie secondaire": "Sous-genre",
  "Createur": "Geoffroy Streit / Hylst",
  "Description": "Description détaillée de l'image",
  "Mots cles": ["mot1", "mot2", "mot3"],
  "Titre": "Titre de l'image",
  "Caracteristiques": ["mot1", "mot2", "mot3"],
  "Perception": "Histoire lyrique et artistique",
  "Conte": "Interprétation poétique/philosophique"
}
```

## Mapping des champs

| Champ metadata.json | Source dans les résultats | Notes |
|---------------------|---------------------------|-------|
| Fichier | `new_file` ou `original_file` | Nom du fichier après renommage |
| Taille | Calculé automatiquement | Taille du fichier sur disque |
| Type | Déterminé par l'extension | `image/jpeg` ou `image/png` |
| Largeur | `original_dimensions[0]` | Largeur en pixels |
| Hauteur | `original_dimensions[1]` | Hauteur en pixels |
| Categorie | `main_genre` | Genre principal |
| Categorie secondaire | `secondary_genre` | Sous-genre |
| Createur | Valeur fixe | "Geoffroy Streit / Hylst" |
| Description | `description` | Description détaillée |
| Mots cles | `keywords` | Liste des mots-clés |
| Titre | `title` | Titre de l'image |
| Caracteristiques | `keywords` | Copie des mots-clés |
| Perception | `story` | Histoire lyrique |
| Conte | `comment` | Interprétation poétique |

## Comportement

### Fichier unique
Si une seule image est traitée, le fichier `metadata.json` contient directement l'objet JSON.

### Plusieurs fichiers
Si plusieurs images sont traitées, le fichier `metadata.json` contient un tableau d'objets JSON.

### Gestion des erreurs
- Les résultats avec erreurs sont ignorés
- Si aucune métadonnée valide n'est disponible, un avertissement est affiché
- Les erreurs de génération sont capturées et loggées

## Emplacement du fichier

Le fichier `metadata.json` est toujours créé dans le répertoire contenant les images :
- Pour un fichier unique : dans le répertoire parent du fichier
- Pour un répertoire : dans le répertoire spécifié

## Exemple d'utilisation

```bash
# Traitement d'un fichier unique
python src/main.py image.jpg --credentials creds.json
# Génère : metadata.json dans le même répertoire que image.jpg

# Traitement d'un répertoire
python src/main.py images/ --credentials creds.json
# Génère : images/metadata.json
```

## Messages de log

La génération du fichier `metadata.json` produit les messages suivants :
- `📋 Fichier metadata.json généré: [chemin]` (succès)
- `⚠️ Aucune métadonnée valide à sauvegarder` (aucune donnée)
- `❌ Erreur lors de la génération du metadata.json: [erreur]` (échec)
- `📋 Métadonnées supplémentaires sauvegardées: metadata.json` (confirmation)