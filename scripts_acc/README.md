# Scripts Accessoires - Gestionnaire de Métadonnées

Ce répertoire contient des scripts utilitaires pour la gestion des métadonnées d'images, complémentaires au système principal d'auto-tagging.

## 📁 Contenu du répertoire

### Scripts principaux

- **`paginate_metadata.py`** - Paginateur de métadonnées pour galeries web
- **`metadata_manager.py`** - Gestionnaire principal de métadonnées
- **`demo_metadata_manager.py`** - Script de démonstration
- **`test_metadata_manager.py`** - Tests automatisés
- **`extract_meta_utf8.py`** - Extracteur de métadonnées (existant)
- **`clear_and_write_metadata.py`** - Nettoyeur de métadonnées (existant)

## 📄 paginate_metadata.py

### Fonctionnalités

1. **Pagination automatique** : Division d'un fichier `metadata.json` en pages de 30 images maximum
2. **Création de dossiers** : Génération automatique de sous-dossiers numérotés (1, 2, 3, ...)
3. **Copie d'images** : Transfert automatique des fichiers images dans les dossiers correspondants
4. **Préparation web** : Structure prête à l'emploi pour galeries web paginées

### Utilisation

```bash
# Exécuter dans le répertoire contenant metadata.json et les images
cd /chemin/vers/vos/images
python ../scripts_acc/paginate_metadata.py
```

### Fonctionnement

1. **Scan** : Recherche automatique de `metadata.json` dans le répertoire courant
2. **Analyse** : Calcul du nombre de pages nécessaires (30 images max par page)
3. **Création** : Génération des dossiers numérotés
4. **Division** : Répartition des métadonnées en fichiers JSON paginés
5. **Copie** : Transfert des images correspondantes dans chaque dossier

### Structure générée

```
répertoire_source/
├── metadata.json (original)
├── image1.jpg
├── image2.jpg
├── ...
├── 1/
│   ├── metadata.json (images 1-30)
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── 2/
│   ├── metadata.json (images 31-60)
│   ├── image31.jpg
│   └── ...
└── 3/
    ├── metadata.json (images 61-90)
    └── ...
```

### Gestion d'erreurs

- **Fichier manquant** : Vérification de l'existence de `metadata.json`
- **Images manquantes** : Rapport des fichiers non trouvés
- **Permissions** : Gestion des erreurs de copie de fichiers
- **JSON invalide** : Validation du format des métadonnées

### Rapport d'exécution

```
📄 Pagination de metadata.json
📊 Nombre total d'images : 85
📁 Nombre de pages créées : 3
✅ Page 1 : 30 images copiées
✅ Page 2 : 30 images copiées
✅ Page 3 : 25 images copiées
🎉 Pagination terminée avec succès !
```

## 🔧 metadata_manager.py

### Fonctionnalités

1. **Extraction de métadonnées** : Scan d'un répertoire d'images et création d'un fichier JSON
2. **Application de métadonnées** : Lecture d'un fichier JSON et écriture des métadonnées dans les images correspondantes

### Formats supportés

- **Images** : JPG, JPEG, PNG
- **Métadonnées** : XMP, IPTC
- **Sortie** : JSON structuré compatible avec le format de `main.py`

### Utilisation en ligne de commande

```bash
# Extraction de métadonnées
python scripts_acc/metadata_manager.py extract ./images metadata.json
python scripts_acc/metadata_manager.py extract ./images metadata.json --verbose

# Application de métadonnées
python scripts_acc/metadata_manager.py apply metadata.json ./images
python scripts_acc/metadata_manager.py apply metadata.json ./images --verbose

# Aide
python scripts_acc/metadata_manager.py --help
```

### Structure JSON

Le format JSON généré/attendu suit cette structure :

```json
[
  {
    "Fichier": "nom-image.jpg",
    "Taille": "756 kB",
    "Type": "image/jpeg",
    "Largeur": 2048,
    "Hauteur": 1536,
    "Categorie": "Photographie animalière",
    "Categorie secondaire": "Paysage",
    "Createur": "Geoffroy Streit / Hylst",
    "Description": "Description détaillée de l'image...",
    "Mots cles": ["mot1", "mot2", "mot3"],
    "Titre": "Titre de l'image",
    "Caracteristiques": ["mot1", "mot2", "mot3"],
    "Perception": "Perception artistique...",
    "Conte": "Histoire ou conte associé..."
  }
]
```

### Gestion d'erreurs robuste

Le script inclut une gestion d'erreurs avancée :

- **EXIF corrompus** : Contournement automatique avec PIL
- **Métadonnées inaccessibles** : Fallback vers méthodes alternatives
- **Images problématiques** : Nettoyage et reconstruction
- **Logging détaillé** : Mode verbeux pour le diagnostic

## 🎯 demo_metadata_manager.py

### Fonctionnalités

- Démonstration interactive des capacités du gestionnaire
- Extraction d'exemples depuis le répertoire `imgs/`
- Modification et application de métadonnées de test
- Vérification des résultats

### Utilisation

```bash
python scripts_acc/demo_metadata_manager.py
```

Le script guide l'utilisateur à travers :
1. Extraction de métadonnées existantes
2. Création de métadonnées de démonstration
3. Application avec confirmation utilisateur
4. Vérification des modifications

## 🧪 test_metadata_manager.py

### Tests inclus

1. **Test d'extraction** : Vérification de la lecture des métadonnées
2. **Test d'application** : Vérification de l'écriture des métadonnées
3. **Test round-trip** : Extraction → Modification → Application → Vérification

### Utilisation

```bash
python scripts_acc/test_metadata_manager.py
```

### Résultats attendus

- ✅ Extraction : Lecture réussie des métadonnées existantes
- ✅ Application : Écriture réussie de nouvelles métadonnées
- ⚠️ Round-trip : Peut échouer sur images avec métadonnées verrouillées

## 🔄 Cas d'usage typiques

### 1. Préparation de galerie web paginée

```bash
# Après avoir généré metadata.json avec main.py
cd ./mes_images_analysees
python ../scripts_acc/paginate_metadata.py
# Résultat : dossiers 1/, 2/, 3/... prêts pour galerie web
```

### 2. Sauvegarde des métadonnées

```bash
# Extraire toutes les métadonnées avant modification
python scripts_acc/metadata_manager.py extract ./mes_images sauvegarde_metadata.json
```

### 3. Migration de métadonnées

```bash
# Extraire depuis un répertoire source
python scripts_acc/metadata_manager.py extract ./source metadata_source.json

# Appliquer vers un répertoire cible
python scripts_acc/metadata_manager.py apply metadata_source.json ./destination
```

### 4. Édition en lot

1. Extraire les métadonnées existantes
2. Éditer le fichier JSON avec un éditeur de texte
3. Appliquer les modifications

```bash
python scripts_acc/metadata_manager.py extract ./images metadata.json
# Éditer metadata.json
python scripts_acc/metadata_manager.py apply metadata.json ./images
```

### 5. Synchronisation avec le système principal

```bash
# Utiliser le format compatible avec main.py
python scripts_acc/metadata_manager.py extract ./imgs exports/metadata_backup.json
```

## ⚠️ Précautions

1. **Sauvegarde** : Toujours sauvegarder vos images avant d'appliquer des métadonnées
2. **Test** : Tester sur quelques images avant un traitement en lot
3. **Vérification** : Utiliser le mode `--verbose` pour surveiller le processus
4. **Compatibilité** : Vérifier que les noms de fichiers correspondent exactement

## 🔗 Intégration

Ces scripts sont conçus pour être complémentaires au système principal :

- **Format compatible** avec les exports de `main.py`
- **Même gestion d'erreurs** que `image_processor.py`
- **Logging cohérent** avec le reste du système
- **Structure modulaire** pour faciliter la maintenance

## 📝 Développement

Pour étendre les fonctionnalités :

1. **Nouveaux formats** : Ajouter des extensions dans `supported_extensions`
2. **Nouvelles métadonnées** : Modifier les dictionnaires de mapping XMP/IPTC
3. **Nouveaux fallbacks** : Ajouter des méthodes dans la classe `MetadataManager`
4. **Tests** : Ajouter des cas de test dans `test_metadata_manager.py`

---

*Auteur : Geoffroy Streit / Hylst*  
*Date : 2024*