# Guide Débutant - Image Auto Tag CLI 🚀

## Qu'est-ce que c'est ?

Une application qui analyse automatiquement vos images et génère :
- Des titres descriptifs
- Des descriptions détaillées
- Des métadonnées (genre, mots-clés, etc.)
- Renomme vos fichiers avec des noms plus parlants

## Fichiers Essentiels 📁

Pour que l'application fonctionne, vous avez besoin de :

### Fichiers Obligatoires ✅
- `src/main.py` - Point d'entrée principal
- `src/config.py` - Configuration des APIs
- `src/image_processor.py` - Moteur de traitement des images
- `requirements.txt` - Liste des dépendances Python
- Fichier de credentials Google Cloud (JSON)

### Fichiers Optionnels (mais recommandés) 📋
- `src/config_manager.py` - Gestion avancée de la configuration
- `src/exceptions.py` - Gestion des erreurs personnalisées
- `src/logging_utils.py` - Utilitaires de logging
- `src/performance_monitor.py` - Monitoring des performances
- `src/validation.py` - Validation des entrées

## Installation Rapide ⚡

### 1. Prérequis
- Python 3.8 ou plus récent
- Un compte Google Cloud avec Vision API et Gemini API activées

### 2. Installation
```bash
# Cloner ou télécharger le projet
cd "Img Auto Tag CLI OK ++"

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration Google Cloud
1. Créer un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activer les APIs :
   - Vision API
   - Gemini API (Vertex AI)
3. Créer une clé de service (fichier JSON)
4. Télécharger le fichier JSON des credentials

## Utilisation Simple 🎯

### Commande de Base
```bash
python -m src.main "chemin/vers/vos/images" --credentials "chemin/vers/credentials.json" --project "votre-project-id"
```

### Exemples Pratiques

#### Traiter une seule image
```bash
python -m src.main "C:\Photos\vacances.jpg" --credentials "credentials.json" --project "mon-projet-123"
```

#### Traiter un dossier entier
```bash
python -m src.main "C:\Photos\Vacances" --credentials "credentials.json" --project "mon-projet-123" --recursive
```

#### Mode verbeux (pour voir ce qui se passe)
```bash
python -m src.main "C:\Photos" --credentials "credentials.json" --project "mon-projet-123" -vv
```

## Options Principales 🛠️

| Option | Description | Exemple |
|--------|-------------|----------|
| `--credentials` | Fichier JSON des credentials Google | `--credentials "creds.json"` |
| `--project` | ID du projet Google Cloud | `--project "mon-projet-123"` |
| `--output` | Dossier de sortie | `--output "C:\Photos\Traitees"` |
| `--lang` | Langue (fr/en) | `--lang fr` |
| `--workers` | Nombre de threads | `--workers 2` |
| `--recursive` | Traiter les sous-dossiers | `--recursive` |
| `--no-rename` | Ne pas renommer les fichiers | `--no-rename` |
| `--backup` | Créer une sauvegarde | `--backup` |
| `-v`, `-vv`, `-vvv` | Niveau de verbosité | `-vv` |

## Que fait l'application ? 🔄

1. **Analyse** : Lit vos images avec Google Vision API
2. **Génère** : Crée des métadonnées avec Gemini AI
3. **Renomme** : Donne des noms plus descriptifs aux fichiers
4. **Sauvegarde** : Crée des fichiers `.txt` avec toutes les informations

## Résolution de Problèmes 🔧

### Erreur "Credentials not found"
- Vérifiez le chemin vers votre fichier JSON
- Assurez-vous que le fichier existe et est lisible

### Erreur "Project ID invalid"
- Vérifiez l'ID de votre projet Google Cloud
- Assurez-vous que les APIs sont activées

### Erreur "JSON parsing failed"
- L'IA a renvoyé une réponse mal formatée
- L'application va réessayer automatiquement
- Utilisez `-vv` pour voir les détails de l'erreur

### L'application est lente
- Réduisez le nombre de workers : `--workers 1`
- Traitez moins d'images à la fois
- Vérifiez votre connexion internet

## Conseils pour Débutants 💡

1. **Commencez petit** : Testez avec 1-2 images d'abord
2. **Utilisez le mode verbeux** : `-vv` pour voir ce qui se passe
3. **Faites des sauvegardes** : Utilisez `--backup` au début
4. **Organisez vos dossiers** : Créez un dossier de sortie dédié
5. **Surveillez les quotas** : Google Cloud a des limites d'utilisation

## Structure des Fichiers Générés 📄

Pour chaque image `photo.jpg`, l'application crée :
- `photo.txt` - Métadonnées complètes
- `Nouveau-Nom-Descriptif.jpg` - Image renommée (si activé)

## Support 🆘

En cas de problème :
1. Vérifiez les logs avec `-vv`
2. Consultez le fichier `changelog.md` pour les nouveautés
3. Vérifiez que vos credentials Google Cloud sont valides
4. Assurez-vous que les APIs sont activées et facturées

---

**Bon traitement d'images ! 📸✨**