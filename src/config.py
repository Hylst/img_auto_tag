import os
import json
import logging
import time
from google.oauth2 import service_account
from google.cloud import vision_v1
import google.generativeai as genai
from google.auth.exceptions import DefaultCredentialsError, GoogleAuthError

logger = logging.getLogger(__name__)

def check_credentials(credentials_path: str) -> str:
    """
    Vérifie la validité du fichier d'identifiants et extrait l'ID du projet
    
    Args:
        credentials_path: Chemin vers le fichier JSON d'identifiants
        
    Returns:
        ID du projet extrait des identifiants ou chaîne vide en cas d'échec
    """
    try:
        with open(credentials_path, 'r') as f:
            credentials_data = json.load(f)
        
        required_fields = ['client_email', 'private_key', 'project_id']
        missing_fields = [field for field in required_fields if field not in credentials_data]
        
        if missing_fields:
            logger.error(f"❌ Champs manquants dans le fichier d'identifiants: {', '.join(missing_fields)}")
            return ""
        
        # Vérifier le format de l'email et de la clé
        if not credentials_data['client_email'].endswith('.gserviceaccount.com'):
            logger.warning("⚠️ Format d'email de compte de service suspect")
        
        if not credentials_data['private_key'].startswith('-----BEGIN PRIVATE KEY-----'):
            logger.error("❌ Format de clé privée invalide")
            return ""
            
        return credentials_data.get('project_id', '')
        
    except json.JSONDecodeError:
        logger.error("❌ Le fichier d'identifiants n'est pas un JSON valide")
        return ""
    except FileNotFoundError:
        logger.error(f"❌ Fichier d'identifiants non trouvé: {credentials_path}")
        return ""
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des identifiants: {str(e)}")
        return ""

def initialize_apis(credentials_path: str, project_id: str, retry_limit: int = 3):
    """
    Initialise les APIs Google avec les identifiants et effectue des tests de validation
    
    Args:
        credentials_path: Chemin vers le fichier JSON d'identifiants
        project_id: ID du projet Google Cloud
        retry_limit: Nombre maximal de tentatives en cas d'échec
        
    Returns:
        Tuple (vision_client, gemini_model)
    """
    retry_count = 0
    credentials = None
    
    while retry_count < retry_limit:
        try:
            # Charger les identifiants
            logger.info("🔑 Chargement des identifiants...")
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            break
        except Exception as e:
            retry_count += 1
            if retry_count >= retry_limit:
                logger.error(f"❌ Échec du chargement des identifiants après {retry_limit} tentatives")
                raise
            logger.warning(f"⚠️ Tentative {retry_count}/{retry_limit} de chargement des identifiants a échoué: {str(e)}")
            time.sleep(1)
    
    # Initialisation de Vision API
    retry_count = 0
    vision_client = None
    
    while retry_count < retry_limit:
        try:
            # Configuration pour Vision API
            logger.info("🔄 Initialisation de Vision API...")
            vision_client = vision_v1.ImageAnnotatorClient(credentials=credentials)
            
            # Test rapide de Vision API
            test_request = vision_v1.Feature(type_=vision_v1.Feature.Type.LABEL_DETECTION)
            logger.info("✓ Vision API initialisée")
            break
        except (DefaultCredentialsError, GoogleAuthError) as e:
            logger.error(f"❌ Erreur d'authentification Vision API: {str(e)}")
            raise
        except Exception as e:
            retry_count += 1
            if retry_count >= retry_limit:
                logger.error(f"❌ Échec de l'initialisation de Vision API après {retry_limit} tentatives")
                raise
            logger.warning(f"⚠️ Tentative {retry_count}/{retry_limit} d'initialisation de Vision API a échoué: {str(e)}")
            time.sleep(2)
    
    # Initialisation de Gemini
    retry_count = 0
    gemini_model = None
    
    while retry_count < retry_limit:
        try:
            # Configuration pour Gemini - utiliser uniquement les credentials du service account
            logger.info("🔄 Initialisation de Gemini...")
            
            # Vérifier si une API key est définie dans l'environnement et la supprimer temporairement
            import os
            api_key_backup = os.environ.pop('GEMINI_API_KEY', None)
            
            # Configurer Gemini avec les credentials du service account uniquement
            genai.configure(credentials=credentials)
            
            # Création du modèle Gemini
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✓ Gemini initialisé avec les credentials du service account")
            break
        except (DefaultCredentialsError, GoogleAuthError) as e:
            logger.error(f"❌ Erreur d'authentification Gemini: {str(e)}")
            raise
        except Exception as e:
            retry_count += 1
            if retry_count >= retry_limit:
                logger.error(f"❌ Échec de l'initialisation de Gemini après {retry_limit} tentatives")
                raise
            logger.warning(f"⚠️ Tentative {retry_count}/{retry_limit} d'initialisation de Gemini a échoué: {str(e)}")
            time.sleep(2)
    
    logger.info("✅ Initialisation des APIs réussie")
    return vision_client, gemini_model