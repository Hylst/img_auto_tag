import os
import sys
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
from src.config import initialize_apis, check_credentials
from src.image_processor import ImageProcessor

# Configuration du logger enrichi
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)
logger = logging.getLogger("image_tagger")

def validate_inputs(args):
    """Valide les entrées du programme et affiche des informations utiles"""
    if not os.path.exists(args.input_path):
        logger.error(f"❌ Chemin d'entrée non trouvé: {args.input_path}")
        return False
    
    if not os.path.exists(args.credentials):
        logger.error(f"❌ Fichier d'identifiants non trouvé: {args.credentials}")
        return False
    
    # Information sur le chemin d'entrée
    input_path = Path(args.input_path)
    if input_path.is_dir():
        image_count = len([f for f in input_path.glob('**/*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])
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
    """Affiche une bannière de bienvenue pour le programme"""
    banner = Panel(
        "[bold magenta]Image Metadata Auto-Tagger[/bold magenta] [yellow]🖼️🤖[/yellow]\n"
        "[cyan]Outil d'analyse d'images avec Google Vision + Gemini AI[/cyan]\n"
        "[green]Par Geoffroy Streit (Hylst)[/green]",
        expand=False,
        border_style="blue"
    )
    console.print(banner)

def show_summary(results, start_time):
    """Affiche un résumé des opérations effectuées"""
    if not results:
        logger.warning("⚠️ Aucun résultat à afficher")
        return
    
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    table = Table(title="Résumé du traitement")
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="green")
    
    table.add_row("Images traitées", str(len(results)))
    table.add_row("Succès", f"{len(successful)} ({len(successful)/max(1, len(results))*100:.1f}%)")
    table.add_row("Échecs", f"{len(failed)} ({len(failed)/max(1, len(results))*100:.1f}%)")
    table.add_row("Temps d'exécution", f"{time.time() - start_time:.2f} secondes")
    
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

def setup_logging(verbose_level):
    """Configure le niveau de journalisation en fonction du niveau de verbosité"""
    levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
        3: logging.DEBUG  # Niveau très détaillé (mais toujours DEBUG)
    }
    logging.getLogger().setLevel(levels.get(verbose_level, logging.INFO))
    
    if verbose_level >= 3:
        # Activer la journalisation des bibliothèques tierces
        logging.getLogger("PIL").setLevel(logging.INFO)
        logging.getLogger("google").setLevel(logging.INFO)
    else:
        # Réduire le bruit des bibliothèques tierces
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

    args = parser.parse_args()
    
    # Configuration de la journalisation en fonction de la verbosité
    setup_logging(args.verbose)
    
    # Validation des entrées
    if not validate_inputs(args):
        sys.exit(1)
    
    try:
        # Initialisation des APIs
        logger.info("🔄 Initialisation des APIs Google...")
        vision_client, gemini_model = initialize_apis(args.credentials, args.project)
        
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
            directory_results = processor.process_directory(str(input_path), args.output)
            
            # Les résultats détaillés sont déjà sauvegardés dans le fichier de sortie
            with open(args.output, "r", encoding="utf-8") as f:
                results = json.load(f)
        else:
            # Traitement d'une seule image
            logger.info("🔄 Traitement d'une image unique...")
            result = processor.process_single_image(str(input_path))
            results = [result]
            
            # Sauvegarde du résultat
            with open(args.output, "w", encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Résultat enregistré dans [bold]{args.output}[/bold]")
        
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