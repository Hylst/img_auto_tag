import os
# The usual suspects - our trusty imports! 📦
import sys
import os
import json
import logging
import argparse
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from src.config import initialize_apis, check_credentials, select_gemini_model
from src.image_processor import ImageProcessor

# Setting up our fancy logger - because plain text is so last century! ✨
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Keep it simple, stupid! 🤓
    handlers=[RichHandler(rich_tracebacks=True, console=console)]  # Rich makes everything better! 💎
)
logger = logging.getLogger("image_tagger")  # Our chatty companion 🗣️

def validate_inputs(args):
    """
    The bouncer of our application - checking IDs at the door! 🕴️
    
    Makes sure everything is in order before we start the party.
    No ticket, no entry! 🎫
    """
    # Does this path actually exist, or are we chasing ghosts? 👻
    if not os.path.exists(args.input_path):
        logger.error(f"❌ Chemin d'entrée non trouvé: {args.input_path}")
        return False
    
    # Credentials check - show me your papers! 📋
    if not os.path.exists(args.credentials):
        logger.error(f"❌ Fichier d'identifiants non trouvé: {args.credentials}")
        return False
    
    # Information sur le chemin d'entrée
    input_path = Path(args.input_path)
    if input_path.is_dir():
        if args.recursive:
            logger.info(f"📂 Dossier (mode récursif): [bold]{input_path}[/bold]")
            if args.verbose >= 2:
                logger.info("ℹ️ Le décompte des images sera effectué pendant le traitement")
        else:
            image_count = len([f for f in input_path.glob('*.*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
            logger.info(f"📂 Dossier: [bold]{input_path}[/bold]")
            logger.info(f"🖼️ Images trouvées: [bold]{image_count}[/bold]")
    else:
        logger.info(f"🖼️ Image à traiter: [bold]{input_path.name}[/bold]")
    
    # Validation des identifiants
    try:
        project_id = check_credentials(args.credentials)
        if not project_id and not args.project:
            logger.error("❌ ID de projet non trouvé dans les identifiants et non spécifié en argument")
            return False
        
        # Utiliser l'ID du projet spécifié ou extrait des identifiants
        args.project = args.project or project_id
        logger.info(f"🔑 Google Cloud Project: [bold]{args.project}[/bold]")
    except Exception as e:
        logger.error(f"❌ Erreur de validation des identifiants: {str(e)}")
        return False
    
    # Afficher les paramètres de sortie
    output_path = Path(args.output)
    logger.info(f"💾 Sortie JSON: [bold]{output_path}[/bold]")
    logger.info(f"🌍 Langue: [bold]{args.lang.upper()}[/bold]")
    
    return True

def show_banner():
    """
    Roll out the red carpet! 🎭
    
    Because every great application deserves a dramatic entrance.
    It's showtime, folks! 🎪
    """
    banner = Panel(
        "[bold magenta]Image Metadata Auto-Tagger[/bold magenta] [yellow]🖼️🤖[/yellow]\n"
        "[cyan]Outil d'analyse d'images avec Google Vision + Gemini AI[/cyan]\n"
        "[green]Par Geoffroy Streit (Hylst)[/green]",
        expand=False,
        border_style="blue"  # Blue like the sky of possibilities! 🌌
    )
    console.print(banner)

def show_summary(results, start_time):
    """
    The grand finale! 🎊
    
    Time to tally up our victories and learn from our defeats.
    Every good story needs an ending! 📖
    """
    if not results:
        logger.warning("⚠️ Aucun résultat à afficher")  # Empty handed? That's unusual! 🤷‍♂️
        return
    
    # Sorting the wheat from the chaff 🌾
    successful = [r for r in results if "error" not in r]  # The champions! 🏆
    failed = [r for r in results if "error" in r]          # The learning opportunities 📚
    
    table = Table(title="Résumé du traitement")
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="green")
    
    # The numbers don't lie! 📊
    table.add_row("Images traitées", str(len(results)))
    table.add_row("Succès", f"{len(successful)} ({len(successful)/max(1, len(results))*100:.1f}%)")
    table.add_row("Échecs", f"{len(failed)} ({len(failed)/max(1, len(results))*100:.1f}%)")
    table.add_row("Temps d'exécution", f"{time.time() - start_time:.2f} secondes")
    
    # Calculate average time if we have successful results 🕐
    if len(successful) > 0:
        avg_time = sum(r.get("processing_time", 0) for r in successful) / len(successful)
        table.add_row("Temps moyen/image", f"{avg_time:.2f} secondes")
    
    console.print(Panel(table, expand=False))
    
    # Afficher les 3 premiers échecs s'il y en a
    if failed:
        console.print("[bold red]Détails des échecs:[/bold red]")
        for i, f in enumerate(failed[:3], 1):
            console.print(f"  {i}. [red]{f.get('original_file', 'Unknown')}: {f.get('error', 'Erreur inconnue')}[/red]")
        if len(failed) > 3:
            console.print(f"  ... et {len(failed) - 3} autres échecs (voir le fichier journal pour les détails)")

def generate_metadata_json(results, input_path):
    """
    Génère un fichier metadata.json dans le répertoire des images avec le format spécifié
    
    Args:
        results: Liste des résultats de traitement
        input_path: Chemin du répertoire d'entrée
    """
    try:
        input_dir = Path(input_path)
        if input_dir.is_file():
            input_dir = input_dir.parent
        
        metadata_file = input_dir / "metadata.json"
        
        # Traiter chaque résultat pour créer le format metadata.json
        metadata_entries = []
        
        for result in results:
            if "error" in result:
                continue  # Ignorer les résultats avec erreurs
            
            # Calculer la taille du fichier
            file_path = Path(result.get("path", ""))
            file_size = "0 kB"
            if file_path.exists():
                size_bytes = file_path.stat().st_size
                if size_bytes < 1024:
                    file_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    file_size = f"{size_bytes // 1024} kB"
                else:
                    file_size = f"{size_bytes // (1024 * 1024)} MB"
            
            # Déterminer le type MIME
            file_ext = file_path.suffix.lower() if file_path else ""
            mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"
            
            # Construire l'entrée metadata
            metadata_entry = {
                "Fichier": result.get("new_file", result.get("original_file", "")),
                "Taille": file_size,
                "Type": mime_type,
                "Largeur": result.get("original_dimensions", [0, 0])[0],
                "Hauteur": result.get("original_dimensions", [0, 0])[1],
                "Categorie": result.get("main_genre", ""),
                "Categorie secondaire": result.get("secondary_genre", ""),
                "Createur": "Geoffroy Streit / Hylst",  # Valeur par défaut comme dans l'exemple
                "Description": result.get("description", ""),
                "Mots cles": result.get("keywords", []),
                "Titre": result.get("title", ""),
                "Caracteristiques": result.get("keywords", []),
                "Perception": result.get("story", ""),
                "Conte": result.get("comment", "")
            }
            
            metadata_entries.append(metadata_entry)
        
        # Sauvegarder le fichier metadata.json
        if metadata_entries:
            with open(metadata_file, "w", encoding="utf-8") as f:
                if len(metadata_entries) == 1:
                    # Un seul fichier, sauvegarder directement l'objet
                    json.dump(metadata_entries[0], f, indent=2, ensure_ascii=False)
                else:
                    # Plusieurs fichiers, sauvegarder comme tableau
                    json.dump(metadata_entries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Fichier metadata.json généré: [bold]{metadata_file}[/bold]")
            return str(metadata_file)
        else:
            logger.warning("⚠️ Aucune métadonnée valide à sauvegarder")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération du metadata.json: {str(e)}")
        return None

def setup_logging(verbose_level):
    """
    The volume control for our chatty application! 🔊
    
    From whisper-quiet to full-blown karaoke mode.
    Choose your noise level wisely! 🎤
    """
    # The verbosity scale: from monk-like silence to chatty parrot 🦜
    levels = {
        0: logging.WARNING,   # Shhh! Only emergencies! 🤫
        1: logging.INFO,      # Normal conversation level 💬
        2: logging.DEBUG,     # Getting chatty now! 🗣️
        3: logging.DEBUG      # Full disclosure mode! 📢
    }
    logging.getLogger().setLevel(levels.get(verbose_level, logging.INFO))
    
    if verbose_level >= 3:
        # Let the third-party libraries join the conversation! 🎉
        logging.getLogger("PIL").setLevel(logging.INFO)
        logging.getLogger("google").setLevel(logging.INFO)
    else:
        # Keep the third-party chatter to a minimum 🤐
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("google").setLevel(logging.WARNING)
    
    logger.info(f"🛠️ Niveau de verbosité: {verbose_level}")

def main():
    """Fonction principale avec interface utilisateur améliorée"""
    show_banner()
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Outil d'analyse d'images et de génération de métadonnées avec Google AI")
    parser.add_argument("input_path", help="Fichier image unique ou répertoire contenant des images")
    parser.add_argument("--credentials", required=True, help="Fichier JSON de compte de service GCP")
    parser.add_argument("--output", default=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", help="Fichier de sortie JSON")
    parser.add_argument("--project", help="ID de projet GCP (détecté automatiquement si non spécifié)")
    parser.add_argument("--lang", default="fr", choices=["fr", "en"], help="Langue de sortie")
    parser.add_argument("--workers", type=int, default=4, help="Nombre de travailleurs parallèles (1 = séquentiel)")
    parser.add_argument("-v", "--verbose", action="count", default=1, help="Niveau de verbosité (v, vv, vvv)")
    parser.add_argument("--no-rename", action="store_true", help="Ne pas renommer les fichiers")
    parser.add_argument("--retry", type=int, default=3, help="Nombre de tentatives pour les appels API")
    parser.add_argument("--backup", action="store_true", help="Créer des sauvegardes des fichiers originaux")
    parser.add_argument("--recursive", "-r", action="store_true", help="Rechercher récursivement les images dans les sous-répertoires")

    args = parser.parse_args()
    
    # Configuration de la journalisation en fonction de la verbosité
    setup_logging(args.verbose)
    
    # S'assurer que le répertoire d'exports existe
    output_path = Path(args.output)
    output_dir = output_path.parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Création du répertoire de sortie: {output_dir}")
        except Exception as e:
            logger.error(f"❌ Impossible de créer le répertoire de sortie: {str(e)}")
            sys.exit(1)
    
    # Validation des entrées
    if not validate_inputs(args):
        sys.exit(1)
    
    try:
        # Sélection interactive du modèle Gemini
        logger.info("🤖 Sélection du modèle Gemini...")
        selected_model = select_gemini_model()
        
        # Initialisation des APIs
        logger.info("🔄 Initialisation des APIs Google...")
        vision_client, gemini_model = initialize_apis(args.credentials, args.project, selected_model)
        input_path = Path(args.input_path)  # Définir input_path ici    
        # Ajuster le nombre de workers au nombre de fichiers
        if input_path.is_dir():
            # On ne compte pas les fichiers à l'avance pour la récursivité pour des raisons de performance
            if args.recursive:
                logger.info(f"🧵 Mode récursif activé avec {args.workers} workers")
            else:
                image_count = len([f for f in input_path.glob('*.*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
                args.workers = min(args.workers, max(1, image_count))
                if args.verbose >= 1:
                    logger.info(f"🧵 Nombre de workers ajusté: [bold]{args.workers}[/bold]")

        # Création du processeur d'images
        processor = ImageProcessor(
            vision_client, 
            gemini_model, 
            lang=args.lang,
            verbose=args.verbose,
            max_workers=args.workers
        )
        
        # Configuration des options supplémentaires
        processor.retry_count = args.retry
        processor.rename_files = not args.no_rename
        processor.create_backups = args.backup
        
        # Traitement
        results = []
        input_path = Path(args.input_path)
        
        if input_path.is_dir():
            # Traitement d'un répertoire
            logger.info("🔄 Début du traitement par lots...")
            directory_results = processor.process_directory(str(input_path), args.output, recursive=args.recursive)
            
            # Les résultats détaillés sont déjà sauvegardés dans le fichier de sortie
            if os.path.exists(args.output):
                with open(args.output, "r", encoding="utf-8") as f:
                    results = json.load(f)
            else:
                logger.warning("⚠️ Fichier de résultats non trouvé, affichage du résumé limité")
                results = []
        else:
            # Traitement d'une seule image
            logger.info("🔄 Traitement d'une image unique...")
            result = processor.process_single_image(str(input_path))
            results = [result]
            
            # Sauvegarde du résultat
            with open(args.output, "w", encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Résultat enregistré dans [bold]{args.output}[/bold]")
        
        # Générer le fichier metadata.json dans le répertoire des images
        if results:
            metadata_file = generate_metadata_json(results, args.input_path)
            if metadata_file and args.verbose >= 1:
                logger.info(f"📋 Métadonnées supplémentaires sauvegardées: [bold]{Path(metadata_file).name}[/bold]")
        
        # Afficher le résumé
        show_summary(results, start_time)
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Opération interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Erreur critique: {str(e)}")
        if args.verbose >= 2:
            import traceback
            logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")
        sys.exit(1)
    
    logger.info("✅ Traitement terminé.")

if __name__ == "__main__":
    main()