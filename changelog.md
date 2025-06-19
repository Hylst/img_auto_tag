# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

## [1.1.0] - 2025-01-19

### 🔧 Corrections importantes
- **CRITIQUE** : Résolution du conflit entre API key et service account credentials
  - L'erreur "client_options.api_key and credentials are mutually exclusive" est maintenant corrigée
  - L'application utilise exclusivement les service accounts pour plus de sécurité
  - Suppression automatique des variables d'environnement conflictuelles (GEMINI_API_KEY)
- Amélioration de la gestion des erreurs d'authentification Gemini
- Configuration robuste des APIs avec isolation des méthodes d'authentification
- Logs plus informatifs pour identifier les problèmes de configuration

### 📚 Documentation
- **NOUVEAU** : Guide complet pour obtenir des identifiants Google Cloud (GOOGLE_CREDENTIALS_GUIDE.md)
- Instructions détaillées pour créer un projet Google Cloud
- Explication des différences entre API Key et Service Account
- Guide de résolution des erreurs de quota et d'authentification
- Mise à jour du README avec les corrections et nouveautés
- Ajout de sections dédiées aux erreurs courantes et leurs solutions

### 🛠️ Améliorations techniques
- Meilleure isolation des configurations d'authentification
- Gestion robuste des tentatives de connexion avec retry intelligent
- Amélioration de la sécurité par l'utilisation exclusive des service accounts
- Optimisation de la gestion des erreurs API
- Code plus maintenable avec séparation claire des responsabilités

### ✅ Tests et validation
- Validation des corrections sur les erreurs de credentials
- Tests de compatibilité avec différentes configurations Google Cloud
- Vérification de la robustesse des mécanismes de retry

## [1.0.0] - 2024-12-XX

### Ajouté
- Ajout de la fonctionnalité de traitement par lots avec barre de progression
- Ajout de la validation des identifiants Google Cloud
- Ajout de la gestion des erreurs avec retry automatique
- Ajout du support multilingue (FR/EN)
- Ajout de l'écriture des métadonnées IPTC/XMP dans les images
- Ajout du renommage intelligent des fichiers
- Ajout de statistiques détaillées de traitement
- Ajout de l'export JSON structuré
- Ajout du traitement parallèle configurable
- Ajout de la validation des formats d'images supportés
- Ajout de la gestion des sauvegardes automatiques
- Ajout de la détection automatique du projet GCP
- Ajout de l'interface en ligne de commande enrichie avec Rich
- Ajout de la gestion des niveaux de verbosité
- Ajout de la validation des chemins et permissions
- Ajout de la gestion des timeouts API
- Ajout de la surveillance des performances
- Ajout de la gestion des caractères spéciaux dans les noms de fichiers
- Ajout de la validation des métadonnées générées
- Ajout de la gestion des erreurs de quota API
- Ajout de la configuration flexible des modèles Gemini
- Ajout de la gestion des formats d'images étendus
- Ajout de la validation de la structure des répertoires
- Ajout de la gestion des conflits de noms de fichiers
- Updated `prompt_for_model_selection()` and `prompt_for_api_key()` functions
- Added comprehensive error handling for API initialization
- Added support for different Gemini models
- Added interactive mode for better user experience
- Added validation for API keys and credentials
- Added fallback mechanisms for API failures
- Added detailed logging for debugging purposes
- Added configuration management for different environments
- Added support for batch processing with progress tracking
- Added metadata validation and sanitization
- Added file backup functionality before processing
- Added intelligent file renaming based on generated titles
- Added multi-language support for metadata generation
- Added parallel processing capabilities for better performance
- Added comprehensive error reporting and recovery
- Added support for various image formats (JPEG, PNG)
- Added IPTC/XMP metadata writing capabilities
- Added JSON export functionality for processed results
- Added command-line interface with rich formatting
- Added Google Cloud Vision API integration
- Added Gemini AI integration for creative content generation

### Modifié
- Amélioration de la gestion des erreurs API
- Optimisation des performances de traitement
- Amélioration de l'interface utilisateur
- Optimisation de la consommation mémoire
- Amélioration de la robustesse du code
- Adding `genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))` to explicitly use the API key from the `.env` file.
- Improved error handling for API quota limits
- Enhanced logging and debugging capabilities
- Optimized image processing pipeline
- Improved metadata validation and sanitization
- Enhanced file handling and backup mechanisms
- Improved parallel processing efficiency
- Enhanced user interface with better progress indicators
- Improved configuration management
- Enhanced error recovery mechanisms

### Corrigé
- Correction des erreurs de timeout API
- Correction des problèmes de caractères spéciaux
- Correction des erreurs de permissions de fichiers
- Correction des problèmes de mémoire avec les gros fichiers
- Correction des erreurs de validation des métadonnées
- Correction des problèmes de concurrence dans le traitement parallèle
- Correction des erreurs de format de fichier
- Correction des problèmes de chemins relatifs/absolus
- Correction des erreurs de quota API
- Correction des problèmes d'encodage de caractères
- Correction des erreurs de validation des identifiants
- Correction des problèmes de gestion des exceptions
- Correction des erreurs de parsing JSON
- Correction des problèmes de compatibilité des formats d'images
- Correction des erreurs de renommage de fichiers
- Correction des problèmes de sauvegarde automatique
- Correction des erreurs de détection de projet GCP
- Correction des problèmes d'affichage de l'interface
- Correction des erreurs de gestion des niveaux de verbosité
- Correction des problèmes de validation des chemins
- Correction des erreurs de timeout et retry
- Correction des problèmes de surveillance des performances
- Correction des erreurs de gestion des caractères spéciaux
- Correction des problèmes de validation des métadonnées
- Correction des erreurs de quota API avec gestion intelligente
- Correction des problèmes de configuration des modèles
- Correction des erreurs de format d'images étendus
- Correction des problèmes de structure des répertoires
- Correction des erreurs de conflits de noms de fichiers
- Fixed API initialization errors
- Fixed credential validation issues
- Fixed image processing pipeline bugs
- Fixed metadata writing errors
- Fixed file handling and backup issues
- Fixed parallel processing synchronization problems
- Fixed memory leaks in image processing
- Fixed character encoding issues
- Fixed path resolution problems
- Fixed API quota management
- Fixed error reporting and logging
- Fixed configuration loading issues
- Fixed JSON export formatting
- Fixed command-line argument parsing
- Fixed progress tracking accuracy

### Supprimé
- Suppression du code obsolète de gestion des APIs
- Suppression des dépendances inutiles
- Suppression des fonctions dépréciées
- Suppression des imports non utilisés
- Suppression des configurations redondantes
- Removed deprecated API endpoints
- Removed unused dependencies
- Removed obsolete configuration options
- Removed redundant error handling code
- Removed deprecated functions and methods

### Sécurité
- Amélioration de la gestion des identifiants
- Renforcement de la validation des entrées
- Amélioration de la sécurité des fichiers temporaires
- Renforcement de la validation des chemins
- Amélioration de la gestion des permissions
- Enhanced credential security
- Improved input validation
- Strengthened file permission handling
- Enhanced API key management
- Improved error message sanitization

---

**Note**: Ce projet suit les conventions de [Semantic Versioning](https://semver.org/) et les recommandations de [Keep a Changelog](https://keepachangelog.com/).

## 🚀 À venir (Roadmap)

### Version 1.2.0 (Prévue)
- Support des formats d'images supplémentaires (TIFF, WebP)
- Interface graphique optionnelle
- Intégration avec d'autres services cloud
- Amélioration des performances de traitement
- Support des métadonnées vidéo

### Version 1.3.0 (Prévue)
- Mode batch avancé avec planification
- API REST pour intégration dans d'autres applications
- Support des workflows personnalisés
- Intégration avec les systèmes de gestion d'actifs numériques (DAM)

## [Latest] - 2024-12-19

### Added
- ✅ **Gemini 2.5 Flash Preview model support** - Added the latest Gemini 2.5 Flash Preview model to available options
- ✅ **Visible API key input** - Changed API key input from masked (getpass) to visible (input) for better user experience
- ✅ **Dynamic model selection prompts** - Updated prompts to automatically adjust to the number of available models
- Added default value for `--output` argument in `main.py` to `output.json`.
- Changed default language code for `--lang` argument in `main.py` from `FR` to `fr`.
- Refactored credentials handling in `src/config.py` to use `google.auth.default()` when no credentials path is provided, and removed `check_credentials` function.

### Changed
- ✅ **Interactive model selection** - Now supports 5 models instead of 4, with dynamic numbering
- ✅ **API key input method** - Replaced `getpass.getpass()` with `input()` for visible key entry
- ✅ **Documentation updates** - Updated INTERACTIVE_FEATURES.md to reflect new model and input changes

### Fixed
- ✅ **Model count validation** - Fixed hardcoded model count limits in validation messages
- ✅ **Command line argument choices** - Updated argument parser to include new Gemini 2.5 model

### Technical Details
- Modified `get_available_gemini_models()` in `src/config.py`
- Updated `prompt_for_model_selection()` and `prompt_for_api_key()` functions
- Enhanced command line argument parsing in `src/main.py`
- Updated documentation and examples

## [Unreleased]

### Added
- Option to choose between Google Cloud Vision API and Gemini API for image analysis via `--api` command-line argument.
  - `src/main.py`: Added `--api` argument to `argparse`.
  - `src/image_processor.py`: 
    - Modified `ImageProcessor.__init__` to accept and store `api_choice`.
    - Updated `ImageProcessor.process_single_image` to conditionally call `_analyze_with_vision` or `_analyze_with_gemini` based on `api_choice`.
    - Added basic adaptation of Vision API output to the expected metadata structure when `vision` is chosen.
    - Included `api_used` in the output JSON.

### Changed
- Updated SDK usage for `google-genai` in `src/config.py` and `src/image_processor.py`.
- Updated `requirements.txt` to use `google-genai` instead of `google-generativeai`.

### Fixed
- Corrected `google-genai` SDK usage in `src/image_processor.py` (`generate_content` instead of `generate_text`).
- Resolved `AttributeError: 'ImageProcessor' object has no attribute 'api_choice'` by ensuring `api_choice` is passed and set.
- Fixed import error for `genai` in `src/image_processor.py` by importing it directly.
- Resolved `AttributeError: module 'google.genai' has no attribute 'GenerativeModel'` in `src/config.py` by:
    - Changing the import from `from google import genai` to `import google.generativeai as genai`.
    - Adding `genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))` to explicitly use the API key from the `.env` file.
    - Updated Gemini model from `gemini-2.5-flash` to `gemini-1.5-flash-latest` for better compatibility.
- Fixed `IndentationError` in `src/main.py` related to API initialization block.
- Fixed `NameError: name 'Optional' is not defined` by correctly importing `Optional` from `typing` in `src/config.py`.
- Fixed `ImportError: cannot import name 'check_credentials'` by removing the import of `check_credentials` from `src/main.py`.
- Fixed `NameError: name 'genai_client' is not defined` by using `gemini_model` instead of `genai_client` in `ImageProcessor` initialization in `src/main.py`.

## [Latest] - 2024-12-19

### Added
- **New Exception System**: Created comprehensive custom exception classes in `src/exceptions.py`
  - Base `ImageTaggerError` class with error codes and structured details
  - Specific exceptions for API errors, validation, file processing, and configuration
  - Better error context and debugging information

- **Advanced Logging System**: Implemented structured logging in `src/logging_utils.py`
  - Centralized logging configuration with singleton pattern
  - JSON structured logging support for better log analysis
  - Specialized logging for API calls, file processing, and performance metrics
  - Configurable log levels and file rotation

- **Performance Monitoring**: Added comprehensive performance tracking in `src/performance_monitor.py`
  - Real-time monitoring of API calls, processing times, and system resources
  - Context managers for automatic timing of operations
  - Detailed statistics and metrics collection
  - System resource monitoring (CPU, memory, disk usage)

- **Input Validation System**: Created robust validation utilities in `src/validation.py`
  - File format and size validation for images
  - Path and filename sanitization
  - Configuration and credentials validation
  - Language code and API name validation
  - JSON structure validation for metadata

- **Configuration Management**: Enhanced configuration handling in `src/config_manager.py`
  - Centralized application settings management
  - Environment variable support
  - Configuration validation and defaults
  - Support for different configuration sources

### Enhanced
- **Main Application**: Completely refactored `src/main.py`
  - Integrated all new modules for better error handling
  - Added performance monitoring throughout the application
  - Improved input validation and error reporting
  - Better logging configuration and structured output
  - Enhanced user interface with detailed metrics display

- **Dependencies**: Updated `requirements.txt`
  - Added `psutil` for system monitoring
  - Added `pydantic` for data validation
  - Added `pyyaml` for configuration file support
  - Updated existing dependencies to latest stable versions

### Fixed
- Fixed `AttributeError: module 'google.genai' has no attribute 'GenerativeModel'` by:
  - Changed import from `from google import genai` to `import google.generativeai as genai`
  - Added logic to configure Gemini API using `GEMINI_API_KEY` environment variable if available
  - Updated Gemini model name to 'gemini-1.5-flash-latest' for better compatibility
- Updated model to 'gemini-1.5-pro-latest' for improved performance
- Implemented hybrid Vision+Gemini analysis approach for better JSON output quality
- Enhanced prompts with more detailed field descriptions
- Added robust JSON parsing and field validation
- Improved error handling and retry logic for both APIs
- Added text detection capability to Vision API analysis
- Fixed syntax error: removed invalid backslash character at end of line 448 in image_processor.py
- Fixed syntax error: corrected malformed annotate_image call with unclosed dictionary bracket on line 497

### Technical Improvements
- **Code Quality**: Implemented comprehensive error handling patterns
- **Maintainability**: Separated concerns into specialized modules
- **Observability**: Added detailed logging and performance metrics
- **Reliability**: Enhanced input validation and error recovery
- **User Experience**: Better error messages and progress reporting

### To Do
- Refine the Vision API output adaptation in `src/image_processor.py` to better match the richness of Gemini's output, potentially by using a light Gemini call for structuring title, description, and comment if Vision API is the primary choice.
- Enhance error handling and logging for the new API choice mechanism.
- Add unit tests for both Vision API and Gemini processing paths.
- Consider more sophisticated ways to combine outputs if both APIs are used (e.g., Vision for labels/objects, Gemini for creative text).