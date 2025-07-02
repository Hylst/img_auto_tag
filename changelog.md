## [En cours] - 2024-XX-XX

### Ajouté
- **Script metadata_manager.py** : Gestionnaire autonome de métadonnées d'images
  - Extraction de métadonnées d'images (JPG, JPEG, PNG) vers fichier JSON
  - Application de métadonnées depuis fichier JSON vers images correspondantes
  - Support des métadonnées XMP et IPTC
  - Gestion robuste des erreurs avec méthodes de fallback
  - Interface en ligne de commande avec mode verbeux
  - Script de démonstration (demo_metadata_manager.py)
  - Script de test automatisé (test_metadata_manager.py)
- **Guide d'amélioration CODE_QUALITY_IMPROVEMENTS.md** : Recommandations détaillées
  - Suggestions d'architecture et refactoring
  - Stratégies de tests et validation
  - Optimisations de performance
  - Bonnes pratiques de sécurité
  - Roadmap de développement futur

- Refactorisation majeure et amélioration de `extract_meta_utf8.py`:
  - Ajout de documentation complète (docstrings et commentaires détaillés)
  - Architecture modulaire avec fonctions séparées (`get_image_files`, `extract_metadata`, `clear_metadata_batch`, `write_author_metadata`, `display_menu`, `main`)
  - Menu interactif pour une meilleure expérience utilisateur
  - Gestion d'erreurs améliorée avec messages informatifs
  - Fonction de nettoyage en lot des métadonnées spécifiées (Creator, By-line, Artist, XP Author, XP Subject, Software)
  - Fonction d'écriture en lot des informations d'auteur ('Geoffroy Streit / Hylst' dans Artist et XP Author)
  - Support complet UTF-8 pour les accents français
  - Interface utilisateur améliorée avec émojis et formatage

- Nouvelles fonctionnalités avancées de visualisation des métadonnées dans `extract_meta_utf8.py`:
  - `view_all_metadata()`: Affichage complet de toutes les métadonnées disponibles pour un fichier sélectionné
  - `view_useful_metadata()`: Affichage structuré des métadonnées les plus utiles (informations de base, techniques, dates, descriptives, mots-clés, instructions)
  - `compare_metadata()`: Comparaison côte à côte des métadonnées entre deux fichiers image
  - `search_metadata()`: Recherche de termes spécifiques dans toutes les métadonnées des fichiers
  - Menu étendu avec 8 options pour une navigation complète
  - Support parfait des accents français dans tous les affichages
  - Formatage amélioré avec sections organisées et émojis descriptifs

### Modifié
- **Amélioration de la gestion des erreurs EXIF** dans image_processor.py
  - Gestion robuste des répertoires EXIF corrompus (Sony1, Canon avec trop d'entrées)
  - Méthode de fallback avec nettoyage PIL pour contourner les EXIF problématiques
  - Stratégie d'écriture en cascade avec plusieurs niveaux de fallback
  - Logging amélioré pour le diagnostic des problèmes de métadonnées

### Corrigé
- **Erreurs de métadonnées** : "Directory Sony1/Canon with XXXX entries considered invalid"
- **Écriture de métadonnées** : Les métadonnées sont maintenant écrites même sur les images avec EXIF corrompus
- **Robustesse** : Le traitement continue même en cas d'erreur de lecture des métadonnées existantes
- **Comptage doublé dans metadata_manager.py** : Correction du bug qui comptait chaque image deux fois (extensions minuscules + majuscules)

## [2024-12-19] - Correction des métadonnées manquantes et amélioration du débogage

### Corrections
- **extract_meta_utf8.py**: Correction du problème de métadonnées manquantes lors de l'extraction
  - Ajout d'une fonction de débogage `debug_metadata_fields()` pour identifier les noms exacts des champs ExifTool
  - **CORRECTION CRITIQUE**: Commande ExifTool corrigée pour extraire les bons champs:
    - Suppression des préfixes incorrects (`-XMP:Category` → `-Category`)
    - Utilisation des noms de champs simples sans groupes
    - Ajout de `-Caption-Abstract` pour le champ "Conte"
  - **CORRECTION CRITIQUE**: Mapping corrigé des champs de métadonnées:
    - `"Createur"`: `Creator` → `Artist` (maintenant extrait correctement)
    - `"Caracteristiques"`: `HierarchicalSubject` → `Keywords` (maintenant extrait correctement)
    - `"Conte"`: `SpecialInstructions` → `Caption-Abstract` (maintenant extrait correctement)
  - Mise à jour du menu principal pour inclure l'option de débogage (option 8)
  - Correction de la numérotation du menu (1-9 au lieu de 1-8)
  - Amélioration des commentaires pour refléter les sources IPTC/XMP correctes

### Corrections précédentes
- **extract_meta_utf8.py (imgs)**: Correction du `TypeError: 'bool' object is not iterable` en corrigeant la compréhension de liste pour le filtrage des fichiers
  - Ligne 39: Changement de `files = [f for f in os in os.listdir('.') if os.path.splitext(f)[1].lower() in extensions]` 
  - Vers: `files = [f for f in os.listdir('.') if os.path.splitext(f)[1].lower() in extensions]`

### Corrigé

### À faire
- Tests unitaires pour les nouvelles fonctionnalités
- Documentation utilisateur détaillée
- Optimisation des performances pour les gros volumes de fichiers
- Ajout d'options d'export pour les comparaisons et recherches
- Interface graphique optionnelle pour les fonctionnalités avancées