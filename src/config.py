import os
import json
import logging
import time
from google.oauth2 import service_account
from google.cloud import vision_v1
import google.generativeai as genai
from google.auth.exceptions import DefaultCredentialsError, GoogleAuthError
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()

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

def select_gemini_model() -> str:
    """
    Interactive model selection for Gemini - because choosing an AI model 
    should be as fun as picking your favorite ice cream flavor! 🍦
    
    Returns:
        str: The selected model name (hopefully one that actually exists)
    """
    # Updated model names - no more '-preview' suffix because Google decided 
    # to graduate these models from preview to "real deal" status! 🎓
    models = {
        "1": "gemini-2.5-flash",        # The speed demon ⚡
        "2": "gemini-2.5-pro",          # The brain box 🧠  
        "3": "gemini-1.5-pro-latest"     # The reliable old-timer 👴
    }
    
    # Create a beautiful table for model selection - because ugly UIs are so 2020
    table = Table(title="🤖 Sélection du modèle Gemini", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Modèle", style="green", width=25)
    table.add_column("Description", style="yellow")
    
    # Updated descriptions with the correct model names (no more 404 errors, yay!)
    table.add_row("1", "gemini-2.5-flash", "⚡ Rapide et efficace (Recommandé)")
    table.add_row("2", "gemini-2.5-pro", "🧠 Plus puissant et précis")
    table.add_row("3", "gemini-1.5-pro-latest", "🔄 Version stable (fin de vie prévue)")
    
    console.print()
    console.print(table)
    console.print()
    
    while True:
        choice = Prompt.ask(
            "[bold cyan]Choisissez votre modèle Gemini[/bold cyan]",
            choices=["1", "2", "3"],
            default="1"
        )
        
        selected_model = models[choice]
        console.print(f"✅ Modèle sélectionné: [bold green]{selected_model}[/bold green]")
        console.print()
        return selected_model

def initialize_apis(credentials_path: str, project_id: str, gemini_model_name: str = None, retry_limit: int = 3):
    """
    Initialise les APIs Google avec les identifiants et effectue des tests de validation.
    
    This function is like a digital handshake with Google's servers - sometimes it works
    on the first try, sometimes you need to try again (and again... and again). 🤝
    
    Args:
        credentials_path: Chemin vers le fichier JSON d'identifiants (your golden ticket 🎫)
        project_id: ID du projet Google Cloud (your digital passport 🛂)
        gemini_model_name: The AI model to use (defaults to the trusty old gemini-1.5-flash)
        retry_limit: Nombre maximal de tentatives (because persistence pays off! 💪)
        
    Returns:
        Tuple (vision_client, gemini_model): Your shiny new AI assistants ready to work! ✨
        
    Raises:
        Various Google-flavored exceptions when things go sideways 🎢
    """
    retry_count = 0
    credentials = None
    
    # First, let's load those precious credentials - they're like the keys to the kingdom! 👑
    while retry_count < retry_limit:
        try:
            logger.info("🔑 Chargement des identifiants...")
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            break  # Success! No need to keep knocking on Google's door 🚪
        except Exception as e:
            retry_count += 1
            if retry_count >= retry_limit:
                logger.error(f"❌ Échec du chargement des identifiants après {retry_limit} tentatives")
                raise  # Time to give up and let the human deal with it 🤷‍♂️
            logger.warning(f"⚠️ Tentative {retry_count}/{retry_limit} de chargement des identifiants a échoué: {str(e)}")
            time.sleep(1)  # Take a breather before trying again 😴
    
    # Now let's wake up the Vision API - it's like teaching a computer to see! 👁️
    retry_count = 0
    vision_client = None
    
    while retry_count < retry_limit:
        try:
            logger.info("🔄 Initialisation de Vision API...")
            vision_client = vision_v1.ImageAnnotatorClient(credentials=credentials)
            
            # Quick sanity check - making sure Vision API didn't forget how to see 🤓
            test_request = vision_v1.Feature(type_=vision_v1.Feature.Type.LABEL_DETECTION)
            logger.info("✓ Vision API initialisée")
            break  # Vision API is awake and ready to analyze some pixels! 📸
        except (DefaultCredentialsError, GoogleAuthError) as e:
            logger.error(f"❌ Erreur d'authentification Vision API: {str(e)}")
            raise  # Authentication failed - time to check those credentials again 🔍
        except Exception as e:
            retry_count += 1
            if retry_count >= retry_limit:
                logger.error(f"❌ Échec de l'initialisation de Vision API après {retry_limit} tentatives")
                raise  # Vision API is being stubborn today 😤
            logger.warning(f"⚠️ Tentative {retry_count}/{retry_limit} d'initialisation de Vision API a échoué: {str(e)}")
            time.sleep(2)  # Give it a moment to collect itself 🧘‍♂️
    
    # Time to summon the mighty Gemini! 🧞‍♂️ (No lamp rubbing required)
    retry_count = 0
    gemini_model = None
    
    while retry_count < retry_limit:
        try:
            logger.info("🔄 Initialisation de Gemini...")
            
            # Clean slate approach - remove any conflicting API keys lurking in the environment 🧹
            import os
            api_key_backup = os.environ.pop('GEMINI_API_KEY', None)
            
            # Configure Gemini with service account credentials (the proper way!) 🎩
            genai.configure(credentials=credentials)
            
            # Create the Gemini model - hopefully with a name that actually exists this time! 🤞
            model_name = gemini_model_name or 'gemini-1.5-flash'  # Fallback to the trusty old reliable
            gemini_model = genai.GenerativeModel(model_name)
            logger.info(f"✓ Gemini initialisé avec le modèle: {model_name}")
            break  # Success! Our AI overlord is ready to serve 🤖
        except (DefaultCredentialsError, GoogleAuthError) as e:
            logger.error(f"❌ Erreur d'authentification Gemini: {str(e)}")
            raise  # Authentication drama - check those credentials! 🎭
        except Exception as e:
            retry_count += 1
            if retry_count >= retry_limit:
                logger.error(f"❌ Échec de l'initialisation de Gemini après {retry_limit} tentatives")
                raise  # Gemini is having a bad day, apparently 😔
            logger.warning(f"⚠️ Tentative {retry_count}/{retry_limit} d'initialisation de Gemini a échoué: {str(e)}")
            time.sleep(2)  # Patience, young padawan 🧘‍♀️
    
    logger.info("✅ Initialisation des APIs réussie")
    # Ta-da! 🎉 Both APIs are now ready to make your images talk and your text smart!
    return vision_client, gemini_model