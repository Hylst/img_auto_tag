# Image Metadata Auto-Tagger 🖼️🤖

Un outil Python puissant pour l'analyse automatique d'images et la génération de métadonnées enrichies (IPTC/XMP) utilisant Google Vision API et Gemini AI.

*Développé par Geoffroy Streit (Hylst)*

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#-fonctionnalités)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Guide des identifiants Google Cloud](#-guide-des-identifiants-google-cloud)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Exemples de sortie](#-exemples-de-sortie)
- [Résolution des problèmes courants](#-résolution-des-problèmes-courants)
- [Changelog](#-changelog)
- [Contribution](#-contribution)
- [Licence](#-licence)

## Aperçu

Image Metadata Auto-Tagger est un outil qui utilise l'intelligence artificielle pour analyser des images et générer automatiquement des métadonnées riches et contextuelles. Il combine la puissance de Google Vision API pour la détection d'objets et d'éléments visuels avec Gemini AI pour l'interprétation créative et la génération de contenu textuel.

Ces métadonnées sont ensuite intégrées directement dans les fichiers d'images selon les standards IPTC/XMP, rendant ces informations disponibles dans la plupart des logiciels de gestion d'images, y compris Adobe Lightroom et autres outils professionnels.

## ✨ Fonctionnalités

- **Analyse par lots** de répertoires d'images (JPG/PNG)  
  *Traitez des centaines d'images en une seule opération*

- **Génération intelligente** via IA :
  - 📌 **Titres optimisés SEO** - Titres concis et descriptifs  
  - 📝 **Descriptions contextuelles** - Descriptions détaillées du contenu de l'image  
  - 🎨 **Interprétations artistiques** - Commentaires poétiques ou philosophiques sur l'image  
  - 🔑 **Mots-clés thématiques** - Ensemble de mots-clés pertinents pour le référencement

- **Écriture des métadonnées** :
  - ✅ Normes IPTC/XMP compatibles avec les logiciels professionnels  
  - 🌍 Support multilingue (français et anglais)  
  - 🖼️ Compatibilité Adobe/Lightroom et autres outils de gestion d'images

- **Automatisations** :
  - 🔄 Renommage intelligent des fichiers basé sur le titre généré  
  - 📊 Statistiques détaillées de traitement  
  - 💾 Export JSON structuré pour utilisation ultérieure  
  - 🔍 Traitement parallèle pour des performances optimales

## 🔧 Prérequis

- Python 3.8 ou supérieur
- Compte Google Cloud Platform avec:
  - Vision API activée
  - Gemini API activée
  - Un fichier d'identifiants de compte de service

## 🚀 Installation

1. **Clonez le dépôt**:
   ```bash
   git clone https://github.com/votre-username/image-metadata-auto-tagger.git
   cd image-metadata-auto-tagger
   ```

2. **Créez un environnement virtuel**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sous Windows: venv\Scripts\activate
   ```

3. **Installez les dépendances**:
   ```bash
   pip install -r requirements.txt
   ```

Les dépendances principales incluent:
- google-cloud-vision
- google-generativeai
- Pillow
- pyexiv2
- rich
- tqdm

## ⚙️ Configuration

1. **Configurer Google Cloud Platform**:
   - Créez un projet GCP si ce n'est pas déjà fait
   - Activez Vision API et Gemini API
   - Créez un compte de service et téléchargez le fichier JSON d'identifiants
   - Placez le fichier d'identifiants dans un dossier sécurisé (par exemple, `./config/`)

2. **Structure de dossiers recommandée**:
   ```
   image-metadata-auto-tagger/
   ├── config/
   │   └── service-account.json
   ├── imgs/
   │   └── (vos images à traiter)
   ├── exports/
   │   └── (résultats JSON générés)
   ├── src/
   │   ├── __init__.py
   │   ├── config.py
   │   └── image_processor.py
   ├── main.py
   ├── requirements.txt
   └── README.md
   ```

## 📷 Utilisation

### Traitement d'un dossier d'images

```bash
python -m src.main ./imgs --credentials config/service-account.json --output exports/resultats.json --lang fr
```

### Traitement d'une seule image

```bash
python -m src.main ./imgs/image.jpg --credentials config/service-account.json --output exports/resultats.json --lang fr
```

### Options disponibles

```
Arguments obligatoires:
  input_path            Fichier image unique ou répertoire contenant des images
  --credentials PATH    Fichier JSON de compte de service GCP

Arguments optionnels:
  --output PATH         Fichier de sortie JSON (par défaut: results_YYYYMMDD_HHMMSS.json)
  --project ID          ID de projet GCP (détecté automatiquement si non spécifié)
  --lang {fr,en}        Langue de sortie (par défaut: fr)
  --workers N           Nombre de travailleurs parallèles (1 = séquentiel, par défaut: 4)
  -v, --verbose         Niveau de verbosité (v, vv, vvv)
  --no-rename           Ne pas renommer les fichiers
  --retry N             Nombre de tentatives pour les appels API (par défaut: 3)
  --backup              Créer des sauvegardes des fichiers originaux
```

## 📁 Structure du projet

- **main.py** : Point d'entrée principal, gestion des arguments et coordination
- **config.py** : Configuration et initialisation des APIs Google
- **image_processor.py** : Classe principale pour le traitement des images

### Détails des composants

#### Main.py
- Interface en ligne de commande avec argparse
- Affichage d'informations avec rich
- Validation des entrées et configuration
- Gestion des erreurs et affichage du résumé

#### Config.py
- Validation des identifiants Google Cloud
- Initialisation sécurisée des APIs (Vision et Gemini)
- Gestion des tentatives et erreurs de connexion

#### Image_processor.py
- Traitement des images individuelles et par lots
- Analyse avec Vision API
- Génération de métadonnées avec Gemini
- Écriture des métadonnées IPTC/XMP
- Gestion du traitement parallèle

## 📊 Exemples de sortie

### Sortie console

```
╭─────────────────────────────────────────────────────────╮
│ Image Metadata Auto-Tagger 🖼️🤖                          │
│ Outil d'analyse d'images avec Google Vision + Gemini AI │
│ Par Geoffroy Streit (Hylst)                             │
╰─────────────────────────────────────────────────────────╯
[04/15/25 23:37:53] INFO     🛠️ Niveau de verbosité: 1
                    INFO     📂 Dossier: [bold]imgs[/bold]
                    INFO     🖼️ Images trouvées: [bold]2[/bold]
                    ...
Traitement de 2 images... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:09 0:00:00
╭────────────────────────────────────╮
│        Résumé du traitement        │
│ ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓ │
│ ┃ Métrique          ┃ Valeur     ┃ │
│ ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩ │
│ │ Images traitées   │ 2/2        │ │
│ │ Réussites         │ 2 (100.0%) │ │
│ │ Échecs            │ 0 (0.0%)   │ │
│ │ Temps total       │ 9.52s      │ │
│ │ Temps moyen/image │ 4.76s      │ │
│ └───────────────────┴────────────┘ │
╰────────────────────────────────────╯
```

### Format de sortie JSON

```json
[
  {
    "original_file": "image.jpg",
    "new_file": "Happy White Wolf Pup.jpg",
    "path": "imgs/Happy White Wolf Pup.jpg",
    "original_dimensions": [1200, 800],
    "title": "Happy White Wolf Pup",
    "description": "Une illustration stylisée d'un louveteau blanc...",
    "comment": "Cette image évoque l'innocence et la joie...",
    "main_genre": "Illustration",
    "secondary_genre": "Animation",
    "keywords": ["wolf", "pup", "cute", "cartoon", "coloring book"],
    "metadata_written": true,
    "processing_time": 4.76
  },
  {
    "original_file": "service.png",
    "new_file": "Hindu Temple Light Show.png",
    "path": "imgs/Hindu Temple Light Show.png",
    "original_dimensions": [2400, 1600],
    "title": "Hindu Temple Light Show",
    "description": "Une photographie nocturne impressionnante...",
    "comment": "Les lumières dansantes symbolisent la communion...",
    "main_genre": "Photography",
    "secondary_genre": "Night",
    "keywords": ["Hindu Temple", "Light Show", "Night Photography", "Festival", "India"],
    "metadata_written": true,
    "processing_time": 5.25
  }
]
```

## 🔍 Résolution des problèmes courants

### Erreurs de renommage de fichiers

Si vous voyez des erreurs comme `Le fichier spécifié est introuvable` lors du renommage:

```
ERROR: ❌ Échec renommage : [WinError 2] Le fichier spécifié est introuvable:
'imgs\\service.png' -> 'imgs\\Hindu Temple Light Show_1.png'
```

**Solutions possibles**:
- Réduisez le nombre de workers (--workers 1) pour éviter les accès concurrents
- Utilisez l'option --no-rename pour désactiver le renommage automatique
- Vérifiez que vos fichiers ne sont pas utilisés par d'autres applications

### Comptage incorrect des images

Si le programme rapporte plus d'images que ce qui est réellement présent:

**Solutions possibles**:
- Vérifiez les fichiers cachés ou les sous-répertoires
- Utilisez l'option -vvv pour un débogage détaillé
- Réduisez le nombre de workers (--workers 1)

### Erreurs d'API Google

Si vous rencontrez des erreurs liées aux APIs Google:

**Solutions possibles**:
- Vérifiez que les APIs sont activées dans votre projet GCP
- Assurez-vous que votre compte de service a les permissions nécessaires
- Vérifiez votre connexion internet
- Augmentez le nombre de tentatives avec --retry 5

## 🔑 Guide des identifiants Google Cloud

Pour obtenir des identifiants Google Cloud et résoudre les problèmes de configuration, consultez le guide détaillé :

📖 **[GOOGLE_CREDENTIALS_GUIDE.md](GOOGLE_CREDENTIALS_GUIDE.md)**

Ce guide couvre :
- ✅ Création d'un projet Google Cloud
- ✅ Activation des APIs nécessaires
- ✅ Création d'un compte de service
- ✅ Téléchargement des identifiants JSON
- ✅ Résolution des erreurs courantes
- ✅ Différences entre API Key et Service Account

### Erreurs récemment corrigées

**❌ "client_options.api_key and credentials are mutually exclusive"**
- **Cause** : Conflit entre l'utilisation simultanée d'une API key et d'un service account
- **✅ Solution** : L'application utilise maintenant exclusivement les service accounts
- **Status** : Corrigé dans la version actuelle

**❌ "You exceeded your current quota"**
- **Cause** : Quotas API dépassés
- **✅ Solution** : Consultez le guide pour configurer des quotas appropriés

## 📝 Changelog

### Version actuelle (2025-01-19)

**🔧 Corrections importantes :**
- Résolution du conflit entre API key et service account credentials
- Amélioration de la gestion des erreurs d'authentification Gemini
- Suppression automatique des variables d'environnement conflictuelles
- Configuration exclusive des service accounts pour plus de sécurité

**📚 Documentation :**
- Ajout du guide complet pour les identifiants Google Cloud
- Instructions détaillées pour résoudre les erreurs de quota
- Clarification des différences entre API Key et Service Account

**🛠️ Améliorations techniques :**
- Meilleure isolation des configurations d'authentification
- Logs plus informatifs pour le débogage
- Gestion robuste des tentatives de connexion

Pour l'historique complet, consultez [changelog.md](changelog.md)

## 🤝 Contribution

Les contributions sont bienvenues! Si vous souhaitez améliorer cet outil:

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

Veuillez mentionner l'auteur original et demander l'autorisation pour toute modification significative.

## 📜 Licence

Libre partage et utilisation mais mention et demande si fork / modification requise.
Ce projet est sous licence Creative Commons Attribution-NonCommercial 4.0 International.

## 📧 Contact

Geoffroy Streit (Hylst) - [Votre Email ou Site Web]

---

*Ce projet utilise les APIs Google Cloud Platform, qui peuvent entraîner des coûts d'utilisation. Veuillez consulter la tarification de Google pour plus d'informations.*