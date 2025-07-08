import io
import json
import logging
import re
import time
import pathlib
import shutil
import unicodedata
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai
from xml.sax.saxutils import escape
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from google.cloud import vision_v1
import pyexiv2
from tqdm import tqdm
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Configuration du logger enrichi - because plain text logs are so last century! 📜
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]  # Rich logs = happy developers 😊
)
logger = logging.getLogger("image_processor")  # Our trusty sidekick for debugging adventures 🕵️‍♂️

class ProcessingStats:
    """
    Classe pour suivre les statistiques de traitement - like a fitness tracker, 
    but for AI image processing! 📊
    
    Keeps track of wins, losses, and how long we've been staring at progress bars.
    """
    def __init__(self):
        self.total_images = 0      # The mountain we need to climb 🏔️
        self.processed = 0         # How far we've come 🚶‍♂️
        self.successful = 0        # Victory count! 🏆
        self.failed = 0           # The ones that got away 🐟
        self.start_time = time.time()  # When this epic journey began ⏰
        self.processing_times = []     # Speed records for the hall of fame 🏃‍♂️
        
    def add_result(self, success: bool, processing_time: float):
        """Add a result to our collection - like Pokemon cards, but for image processing! 🎴"""
        self.processed += 1
        if success:
            self.successful += 1  # Another one bites the dust! 🎵
        else:
            self.failed += 1      # F in the chat 😔
        self.processing_times.append(processing_time)
    
    def average_time(self) -> float:
        """Calculate average processing time - because we love our metrics! 📈"""
        if not self.processing_times:
            return 0  # No data yet, we're still warming up! 🔥
        return sum(self.processing_times) / len(self.processing_times)
    
    def elapsed_time(self) -> float:
        """How long have we been at this? Time flies when you're having fun! ⏰"""
        return time.time() - self.start_time
    
    def estimated_remaining(self) -> float:
        """Crystal ball prediction of remaining time - accuracy not guaranteed! 🔮"""
        if self.processed == 0 or self.total_images == 0:
            return 0  # Can't predict the future without data! 🤷‍♂️
        avg_time = self.average_time()
        return avg_time * (self.total_images - self.processed)
    
    def display_summary(self):
        """Show off our achievements - like a report card, but prettier! 📊"""
        table = Table(title="Résumé du traitement")
        table.add_column("Métrique", style="cyan")
        table.add_column("Valeur", style="green")
        
        # The good, the bad, and the processed 🎬
        table.add_row("Images traitées", f"{self.processed}/{self.total_images}")
        table.add_row("Réussites", f"{self.successful} ({self.successful/max(1, self.processed)*100:.1f}%)")
        table.add_row("Échecs", f"{self.failed} ({self.failed/max(1, self.processed)*100:.1f}%)")
        table.add_row("Temps total", f"{self.elapsed_time():.2f}s")
        table.add_row("Temps moyen/image", f"{self.average_time():.2f}s")
        
        console.print(Panel(table, expand=False))


class ImageProcessor:
    """
    The main event! This class turns boring images into poetic masterpieces. 🎨
    
    It's like having a digital art critic that never gets tired, never needs coffee,
    and always has something interesting to say about your photos! ☕
    """
    def __init__(self, vision_client, gemini_model, lang="fr", verbose=1, max_workers=4):
        """Initialize our image processing wizard - assembly required! 🧙‍♂️"""
        self.vision_client = vision_client    # The eyes of the operation 👁️
        self.gemini_model = gemini_model      # The brain of the operation 🧠
        self.lang = lang.lower().strip()     # Parlez-vous français? 🇫🇷
        self.verbose = verbose                # How chatty should we be? 🗣️
        self.max_workers = max_workers        # Our digital workforce 👷‍♂️
        self.stats = ProcessingStats()       # Our personal scorekeeper 📊
        self._init_prompts()                  # Loading our conversation starters 💬
        self.retry_count = 3                 # Because third time's the charm! 🍀
        self.retry_delay = 2                 # Patience, young grasshopper ⏳
        
        logger.info(f"🌍 Mode langue : [bold]{self.lang.upper()}[/bold]")
        logger.info(f"🧵 Traitement parallèle : [bold]{self.max_workers}[/bold] workers")

    def _init_prompts(self):
        """Initialize prompts with separated content keywords and technical characteristics"""
        self.prompts = {
            "fr": {
                "main": """Analyse cette image et retourne un JSON avec :
                {
                    "title": "Titre (3-7 mots)",
                    "description": "Description détaillée",
                    "comment": "Interprétation poétique/philosophique (3-5 phrases)",
                    "story": "Histoire lyrique et artistique qui fait rêver (4-6 phrases narratives)",
                    "main_genre": "Genre principal",
                    "secondary_genre": "Sous-genre", 
                    "content_keywords": ["sujet1", "objet2", "émotion3"],
                    "technical_characteristics": ["technique1", "style2", "format3"]
                }
                
Pour content_keywords: identifie ce qui est représenté (sujets, objets, émotions, concepts, ambiances).
Pour technical_characteristics: identifie les aspects techniques et stylistiques (technique artistique, style, format, couleurs dominantes).""",
                "comment_instruction": "Rédige une interprétation poétique en 3-5 phrases"
            },
            "en": {
                "main": """Analyze this image and return JSON with:
                {
                    "title": "Title (3-7 words)",
                    "description": "Detailed description",
                    "comment": "Poetic interpretation (3-5 sentences)",
                    "story": "Lyrical and artistic story that inspires dreams (4-6 narrative sentences)",
                    "main_genre": "Main genre",
                    "secondary_genre": "Sub-genre",
                    "content_keywords": ["subject1", "object2", "emotion3"],
                    "technical_characteristics": ["technique1", "style2", "format3"]
                }
                
For content_keywords: identify what is represented (subjects, objects, emotions, concepts, moods).
For technical_characteristics: identify technical and stylistic aspects (artistic technique, style, format, dominant colors).""",
                "comment_instruction": "Write a poetic interpretation in 3-5 sentences"
            }
        }
        
    def _sanitize_filename(self, title: str) -> str:
        """
        Transform chaotic titles into well-behaved filenames! 🧹
        
        Like a digital Marie Kondo, this function sparks joy by turning
        "Château de Versailles - Vue d'ensemble!!!" into "Chateau-De-Versailles-Vue-D-Ensemble"
        Because filesystems deserve respect too! 💾
        """
        import re
        
        # Normalize unicode characters - making peace with accents 🕊️
        normalized = unicodedata.normalize('NFKD', title)
        
        # Convert to ASCII, removing accents - sorry François! 🇫🇷➡️🇺🇸
        ascii_str = normalized.encode('ASCII', 'ignore').decode('ASCII')
        
        # Convert to lowercase for proper slug format - no shouting allowed! 🤫
        ascii_str = ascii_str.lower()
        
        # Replace spaces and special characters with hyphens - the great unifier! ➖
        slug = re.sub(r'[^a-z0-9]+', '-', ascii_str)
        
        # Remove leading/trailing hyphens and multiple consecutive hyphens - no stuttering! 🚫
        slug = re.sub(r'^-+|-+$', '', slug)
        slug = re.sub(r'-+', '-', slug)
        
        # Capitalize first letter of each word for better readability - proper etiquette! 🎩
        slug = '-'.join(word.capitalize() for word in slug.split('-') if word)
        
        # Limit length to 50 characters - because brevity is the soul of wit! ✂️
        return slug[:50].rstrip('-')

    def resize_image(self, image_path: str) -> Tuple[bytes, Tuple[int, int]]:
        """
        Resize images like a digital tailor - one size fits all APIs! 👔
        
        Takes your massive 4K photos and gently convinces them to play nice
        with our AI friends who prefer their images bite-sized. 🍰
        """
        try:
            with Image.open(image_path) as img:
                original_size = img.size
                if self.verbose >= 2:
                    logger.info(f"📐 Dimensions originales : {original_size[0]}x{original_size[1]}")
                
                # Some images are special snowflakes with fancy color modes ❄️
                if img.mode in ['P', 'RGBA']:
                    if self.verbose >= 2:
                        logger.info(f"🎨 Conversion du mode {img.mode} vers RGB")
                    img = img.convert('RGB')
                
                # Vérifier si redimensionnement nécessaire
                if max(original_size) > 1024:
                    img.thumbnail((1024, 1024))
                    if self.verbose >= 2:
                        logger.info(f"📉 Image redimensionnée à {img.size[0]}x{img.size[1]}")
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                return buffer.getvalue(), original_size
        except Exception as e:
            logger.warning(f"⚠️ Redimensionnement échoué : {str(e)}")
            with open(image_path, "rb") as f:
                return f.read(), (0, 0)  # Dimensions inconnues

    def process_directory(self, directory_path: str, output_file: str, recursive=False) -> Dict:
        """Traite un répertoire d'images avec barre de progression"""
        start_time = time.time()
        path = pathlib.Path(directory_path)
        
        # Collecte des fichiers images avec support récursif
        image_files = []
        extensions = {'.jpg', '.jpeg', '.png'}
        
        # Fonction pour parcourir le répertoire
        if recursive:
            pattern = '**/*.*'  # Récursif
            if self.verbose >= 2:
                logger.info(f"🔍 Recherche récursive d'images dans les sous-répertoires")
        else:
            pattern = '*.*'  # Non récursif (fichiers à la racine seulement)
        
        for file_path in path.glob(pattern):
            if file_path.suffix.lower() in extensions:
                image_files.append(file_path)
        
        self.stats.total_images = len(image_files)
        logger.info(f"📂 Dossier : {directory_path}")
        logger.info(f"🖼️ Images trouvées : {self.stats.total_images}")
        
        if not image_files:
            logger.warning("⚠️ Aucune image trouvée dans le répertoire")
            return {"error": "Aucune image trouvée"}
        
        # Traitement parallèle avec barre de progression
        results = []
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Traitement de {self.stats.total_images} images...", total=self.stats.total_images)
            
            # Créer un pool de threads
            if self.max_workers > 1:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_image = {executor.submit(self.process_single_image, str(img)): img for img in image_files}
                    
                    for future in as_completed(future_to_image):
                        result = future.result()
                        results.append(result)
                        success = "error" not in result
                        self.stats.add_result(success, result.get("processing_time", 0))
                        
                        # Mise à jour de la progression
                        progress.update(task, advance=1)
                        
                        # Afficher les résultats intermédiaires
                        if self.verbose >= 1:
                            status = "✅" if success else "❌"
                            logger.info(f"{status} {result.get('original_file', 'Unknown')} → {result.get('new_file', 'N/A')}")
            else:
                # Traitement séquentiel
                for img in image_files:
                    result = self.process_single_image(str(img))
                    results.append(result)
                    success = "error" not in result
                    self.stats.add_result(success, result.get("processing_time", 0))
                    progress.update(task, advance=1)
                    
                    if self.verbose >= 1:
                        status = "✅" if success else "❌"
                        logger.info(f"{status} {result.get('original_file', 'Unknown')} → {result.get('new_file', 'N/A')}")
        
        # Écriture des résultats
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Afficher le résumé
        self.stats.display_summary()
        logger.info(f"💾 Résultats enregistrés dans [bold]{output_file}[/bold]")
        
        return {
            "total_files": self.stats.total_images,
            "successful": self.stats.successful,
            "failed": self.stats.failed,
            "total_time": time.time() - start_time,
            "output_file": output_file
        }

    def process_single_image(self, image_path: str) -> Dict:
        """Traite une seule image avec des informations détaillées"""
        start_time = time.time()
        original_path = pathlib.Path(image_path)
        
        if self.verbose >= 2:
            logger.info(f"🔄 Traitement de {original_path.name}...")
        
        try:
            # Vérification de l'existence du fichier
            if not original_path.exists():
                raise FileNotFoundError(f"Fichier non trouvé: {image_path}")
            
            # Vérification du type de fichier
            if original_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                raise ValueError(f"Format non supporté: {original_path.suffix}")
            
            # Redimensionnement et préparation de l'image
            image_bytes, original_dimensions = self.resize_image(str(original_path))
            
            mime_type = "image/jpeg"
            if original_path.suffix.lower() == '.png':
                mime_type = "image/png"
            
            # Analyse avec Vision API
            if self.verbose >= 2:
                logger.info("🔍 Analyse via Google Vision API...")
            vision_data = self._analyze_with_vision(image_bytes)
            
            # Analyse avec Gemini
            if self.verbose >= 2:
                logger.info("🤖 Génération de métadonnées via Gemini...")
            gemini_data = self._analyze_with_gemini(image_bytes, mime_type, vision_data)
            
            # Renommage du fichier
            if self.verbose >= 2:
                logger.info("📝 Renommage du fichier...")
            new_path = self._rename_file(original_path, gemini_data.get('title', ''))
            
            # Écriture des métadonnées
            if self.verbose >= 2:
                logger.info("📋 Écriture des métadonnées...")
            metadata_status = self._write_metadata(new_path, gemini_data)
            
            processing_time = time.time() - start_time
            
            # Résumé des métadonnées générées
            if self.verbose >= 1:
                if "error" not in gemini_data:
                    keywords_str = ", ".join(gemini_data.get('keywords', [])[:5])
                    if len(gemini_data.get('keywords', [])) > 5:
                        keywords_str += "..."
                    
                    logger.info(f"📊 Métadonnées générées : ")
                    logger.info(f"  📌 Titre: {gemini_data.get('title', 'N/A')}")
                    logger.info(f"  🏷️ Genre: {gemini_data.get('main_genre', 'N/A')}")
                    logger.info(f"  🔑 Mots-clés: {keywords_str}")
            
            return {
                "original_file": original_path.name,
                "new_file": pathlib.Path(new_path).name,
                "path": str(new_path),
                "original_dimensions": original_dimensions,
                **gemini_data,
                "metadata_written": metadata_status,
                "processing_time": processing_time
            }
        except Exception as e:
            error_message = str(e)
            logger.error(f"❌ Échec du traitement : {error_message}")
            return {
                "original_file": original_path.name if original_path else "Unknown",
                "error": error_message,
                "processing_time": time.time() - start_time
            }

    def _analyze_with_vision(self, image_bytes: bytes) -> Dict:
        """Analyse avec Vision API avec tentatives en cas d'échec"""
        for attempt in range(self.retry_count):
            try:
                image = vision_v1.Image(content=image_bytes)
                context = vision_v1.ImageContext(
                    language_hints=["fr" if self.lang == "fr" else "en"]
                )
                
                features = [
                    {"type_": vision_v1.Feature.Type.LABEL_DETECTION},
                    {"type_": vision_v1.Feature.Type.WEB_DETECTION},
                    {"type_": vision_v1.Feature.Type.IMAGE_PROPERTIES},
                    {"type_": vision_v1.Feature.Type.OBJECT_LOCALIZATION},
                    {"type_": vision_v1.Feature.Type.LANDMARK_DETECTION}
                ]
                
                if self.verbose >= 3:
                    logger.debug(f"Vision API: Tentative {attempt+1}/{self.retry_count}")
                
                response = self.vision_client.annotate_image({
                    "image": image,
                    "image_context": context,
                    "features": features
                })
                
                # Extraction des données avec plus d'informations
                result = {
                    "labels": [{"description": label.description, "score": label.score} 
                              for label in response.label_annotations],
                    "web_entities": [{"description": entity.description, "score": entity.score} 
                                    for entity in response.web_detection.web_entities],
                    "colors": [{"rgb": f"rgb({int(color.color.red)},{int(color.color.green)},{int(color.color.blue)})", 
                               "score": color.score} 
                              for color in response.image_properties_annotation.dominant_colors.colors[:5]],
                    "objects": [{"name": obj.name, "confidence": obj.score} 
                               for obj in response.localized_object_annotations],
                    "landmarks": [{"name": landmark.description, "confidence": landmark.score} 
                                 for landmark in response.landmark_annotations]
                }
                
                if self.verbose >= 3:
                    detected_items = sum(len(v) for v in result.values())
                    logger.debug(f"Vision API: {detected_items} éléments détectés")
                
                return result
                
            except Exception as e:
                if attempt < self.retry_count - 1:
                    logger.warning(f"⚠️ Vision API: échec tentative {attempt+1}: {str(e)}. Nouvelle tentative...")
                    time.sleep(self.retry_delay * (attempt + 1))  # Backoff exponentiel
                else:
                    logger.error(f"❌ Vision API: échec après {self.retry_count} tentatives: {str(e)}")
                    return {
                        "labels": [],
                        "web_entities": [],
                        "colors": [],
                        "objects": [],
                        "landmarks": []
                    }

    def _analyze_with_gemini(self, image_bytes: bytes, mime_type: str, vision_data: Dict) -> Dict:
        """Appel Gemini API avec contexte linguistique strict et gestion des erreurs améliorée"""
        for attempt in range(self.retry_count):
            try:
                # Instruction système explicite
                system_instruction = {
                    "fr": "Rédige toutes tes réponses en français. ",
                    "en": "Respond in English only. "
                }[self.lang]
                
                # Enrichir le prompt avec les données de Vision
                vision_context = ""
                if vision_data:
                    # Ajouter des informations de contexte à partir de Vision API
                    labels = [label.get("description") for label in vision_data.get("labels", [])][:10]
                    objects = [obj.get("name") for obj in vision_data.get("objects", [])][:5]
                    landmarks = [lm.get("name") for lm in vision_data.get("landmarks", [])][:3]
                    
                    if self.lang == "fr":
                        vision_context = f"Voici des éléments détectés dans l'image: {', '.join(labels)}. "
                        if objects:
                            vision_context += f"Objets identifiés: {', '.join(objects)}. "
                        if landmarks:
                            vision_context += f"Lieux potentiels: {', '.join(landmarks)}. "
                    else:
                        vision_context = f"Elements detected in the image: {', '.join(labels)}. "
                        if objects:
                            vision_context += f"Objects identified: {', '.join(objects)}. "
                        if landmarks:
                            vision_context += f"Potential landmarks: {', '.join(landmarks)}. "

                full_prompt = f"{system_instruction}\n{vision_context}\n{self.prompts[self.lang]['main']}"
                
                if self.verbose >= 3:
                    logger.debug(f"Gemini: Tentative {attempt+1}/{self.retry_count}")
                
                response = self.gemini_model.generate_content(
                    contents=[
                        {"mime_type": mime_type, "data": image_bytes},
                        full_prompt
                    ],
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        temperature=0.7,
                        top_p=0.95
                    )
                )
                
                data = self._parse_gemini_response(response.text)
                
                if self.verbose >= 3:
                    logger.debug(f"Gemini: Réponse reçue, taille {len(response.text)} caractères")
                
                # Complétion des champs manquants
                if not data:
                    raise ValueError("Échec du parsing JSON de la réponse Gemini")
                
                # Fallback de génération du commentaire si nécessaire
                if not data.get("comment"):
                    if self.verbose >= 2:
                        logger.info("🔍 Génération d'un commentaire complémentaire...")
                    
                    comment_prompt = f"{system_instruction}\n{self.prompts[self.lang]['comment_instruction']}"
                    comment_response = self.gemini_model.generate_content([
                        {"mime_type": mime_type, "data": image_bytes},
                        comment_prompt
                    ])
                    data["comment"] = comment_response.text
                
                # Validation et enrichissement des données
                self._validate_metadata(data)
                return data
                
            except Exception as e:
                if attempt < self.retry_count - 1:
                    logger.warning(f"⚠️ Gemini: échec tentative {attempt+1}: {str(e)}. Nouvelle tentative...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"❌ Gemini: échec après {self.retry_count} tentatives: {str(e)}")
                    # Valeurs par défaut minimales
                    return {
                        "title": "Image sans titre",
                        "description": "Pas de description disponible",
                        "comment": "",
                        "story": "",
                        "main_genre": "Non classé",
                        "secondary_genre": "",
                        "content_keywords": ["image"],
                        "technical_characteristics": ["numérique"],
                        "error_gemini": str(e)
                    }

    def _validate_metadata(self, data: Dict) -> None:
        """Validate and complete metadata fields with new separated keywords structure"""
        if not data.get("title"):
            data["title"] = "Image sans titre"
        
        if not data.get("description"):
            data["description"] = "Pas de description disponible"
            
        if not data.get("main_genre"):
            data["main_genre"] = "Non classé"
        
        # Handle content keywords (what is represented)
        if not data.get("content_keywords") or not isinstance(data.get("content_keywords"), list):
            data["content_keywords"] = ["image"]
        elif isinstance(data.get("content_keywords"), str):
            data["content_keywords"] = [k.strip() for k in data["content_keywords"].split(",")]
        
        # Handle technical characteristics (how it's made)
        if not data.get("technical_characteristics") or not isinstance(data.get("technical_characteristics"), list):
            data["technical_characteristics"] = ["numérique"]
        elif isinstance(data.get("technical_characteristics"), str):
            data["technical_characteristics"] = [k.strip() for k in data["technical_characteristics"].split(",")]
        
        # Maintain backward compatibility: create combined keywords for legacy systems
        combined_keywords = []
        combined_keywords.extend(data.get("content_keywords", []))
        combined_keywords.extend(data.get("technical_characteristics", []))
        data["keywords"] = list(dict.fromkeys([k for k in combined_keywords if k]))  # Remove duplicates

    @staticmethod
    def _parse_gemini_response(text: str) -> Dict:
        """Extrait le JSON de la réponse Gemini de manière plus robuste"""
        try:
            # Première tentative: extraction par regex
            json_match = re.search(r'({[\s\S]*?})(?:\s*$|\n\n)', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # Deuxième tentative: recherche de bloc de code JSON
            code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.DOTALL)
            if code_block_match:
                try:
                    return json.loads(code_block_match.group(1))
                except:
                    pass
            
            # Dernière tentative: nettoyer le texte et essayer de parser l'ensemble
            cleaned_text = re.sub(r'```json|```', '', text).strip()
            return json.loads(cleaned_text)
        except Exception as e:
            logger.error(f"Échec de l'analyse JSON : {str(e)}")
            logger.debug(f"Texte brut reçu : {text[:200]}...")
            return {}

    def _rename_file(self, original_path: pathlib.Path, title: str) -> pathlib.Path:
        """Renomme le fichier de manière sécurisée avec vérification préalable"""
        try:
            # Vérifier si le fichier existe encore
            if not original_path.exists():
                logger.warning(f"⚠️ Fichier introuvable pour renommage: {original_path}")
                return original_path
                
            sanitized = self._sanitize_filename(title)
            if not sanitized:
                sanitized = f"image_{int(time.time())}"
                
            ext = original_path.suffix.lower()
            new_name = f"{sanitized}{ext}"
            new_path = original_path.with_name(new_name)
            
            # Éviter les collisions de noms
            counter = 1
            while new_path.exists() and new_path != original_path:
                new_name = f"{sanitized}_{counter}{ext}"
                new_path = original_path.with_name(new_name)
                counter += 1
                
            if new_path == original_path:
                if self.verbose >= 2:
                    logger.info(f"🔄 Nom de fichier inchangé: {original_path.name}")
                return original_path
                
            # Créer une copie de sauvegarde si demandé
            if hasattr(self, 'create_backups') and self.create_backups:
                temp_backup = original_path.with_name(f".bak_{original_path.name}")
                shutil.copy2(original_path, temp_backup)
                if self.verbose >= 2:
                    logger.debug(f"💾 Copie de sauvegarde créée: {temp_backup.name}")
                
            # Renommer le fichier avec vérification supplémentaire
            try:
                original_path.rename(new_path)
                if self.verbose >= 2:
                    logger.info(f"📝 Fichier renommé: {original_path.name} → {new_path.name}")
                return new_path
            except FileNotFoundError:
                logger.warning(f"⚠️ Le fichier a peut-être déjà été renommé: {original_path}")
                # Vérifier si la destination existe déjà
                if new_path.exists():
                    return new_path
                return original_path
                
        except Exception as e:
            logger.error(f"❌ Échec renommage : {str(e)}")
            return original_path

    def _write_metadata(self, image_path: pathlib.Path, metadata: dict) -> bool:
            """Écrit les métadonnées avec plus d'informations sur le processus"""
            try:
                # Vérification préalable des métadonnées existantes (optionnelle)
                # Cette étape peut échouer sur certaines images avec des EXIF corrompus
                try:
                    with pyexiv2.Image(str(image_path)) as img:
                        if self.verbose >= 3:
                            try:
                                existing_xmp = img.read_xmp()
                                existing_iptc = img.read_iptc() if image_path.suffix.lower() in ('.jpg', '.jpeg') else {}
                                logger.debug(f"📋 Métadonnées existantes : {len(existing_xmp)} XMP, {len(existing_iptc)} IPTC")
                            except Exception as read_error:
                                logger.debug(f"⚠️ Impossible de lire les métadonnées existantes: {str(read_error)}")
                                logger.debug("ℹ️ Cela peut être dû à des répertoires EXIF corrompus ou trop volumineux")
                except Exception as e:
                    if self.verbose >= 2:
                        logger.info(f"ℹ️ Erreur lors de l'ouverture pour lecture des métadonnées: {str(e)}")
                        logger.info("ℹ️ Tentative d'écriture des nouvelles métadonnées malgré tout...")
                
                # Préparation des mots-clés (combinaison des nouveaux champs)
                keywords = []
                if metadata.get('main_genre'):
                    keywords.append(metadata['main_genre'])
                if metadata.get('secondary_genre'):
                    keywords.append(metadata['secondary_genre'])
                if metadata.get('content_keywords') and isinstance(metadata.get('content_keywords'), list):
                    keywords.extend(metadata.get('content_keywords', []))
                if metadata.get('technical_characteristics') and isinstance(metadata.get('technical_characteristics'), list):
                    keywords.extend(metadata.get('technical_characteristics', []))
                
                # Dédoublonnage des mots-clés
                keywords = list(dict.fromkeys([k for k in keywords if k]))
                
                # Créer une description combinée
                full_description = f"{metadata.get('description', '')}\n\n{metadata.get('comment', '')}".strip()

                if self.verbose >= 3:
                    logger.debug(f"🔑 Mots-clés préparés : {keywords}")
                    logger.debug(f"📝 Description: {len(full_description)} caractères")

                # Tentative d'écriture des métadonnées avec gestion robuste des erreurs
                metadata_written = False
                
                # Stratégie 1: Écriture normale avec pyexiv2
                try:
                    # Tentative d'ouverture de l'image avec pyexiv2
                    with pyexiv2.Image(str(image_path)) as img:
                        # XMP (plus universel et robuste)
                        xmp_data = {
                            'Xmp.dc.title': metadata.get('title', ''),
                            'Xmp.dc.description': full_description,
                            'Xmp.dc.subject': keywords,
                            'Xmp.Iptc4xmpCore.Category': metadata.get('main_genre', ''),
                            'Xmp.Iptc4xmpCore.SupplementalCategories': [metadata.get('secondary_genre', '')],
                            'Xmp.photoshop.Instructions': metadata.get('story', '')
                        }
                        
                        if self.verbose >= 3:
                            logger.debug(f"📝 Écriture XMP : {len(xmp_data)} champs")
                        
                        img.modify_xmp(xmp_data)
                        metadata_written = True
                        
                        # IPTC pour JPG (optionnel, peut échouer sur certaines images)
                        if image_path.suffix.lower() in ('.jpg', '.jpeg'):
                            try:
                                iptc_data = {
                                    'Iptc.Envelope.CharacterSet': '\x1b%G',
                                    'Iptc.Application2.ObjectName': metadata.get('title', ''),
                                    'Iptc.Application2.Headline': metadata.get('title', ''),
                                    'Iptc.Application2.Caption': full_description,
                                    'Iptc.Application2.Keywords': keywords,
                                    'Iptc.Application2.Category': metadata.get('main_genre', ''),
                                    'Iptc.Application2.SuppCategory': metadata.get('secondary_genre', '')
                                }
                                
                                if self.verbose >= 3:
                                    logger.debug(f"📝 Écriture IPTC : {len(iptc_data)} champs")
                                
                                img.modify_iptc(iptc_data)
                            except Exception as iptc_error:
                                if self.verbose >= 2:
                                    logger.warning(f"⚠️ Échec écriture IPTC (XMP conservé): {str(iptc_error)}")
                                
                except Exception as write_error:
                    if self.verbose >= 2:
                        logger.warning(f"⚠️ Échec écriture pyexiv2: {str(write_error)}")
                        logger.info("🔄 Tentative avec méthode alternative...")
                    
                    # Stratégie 2: Fallback pour les images problématiques
                    if not metadata_written:
                        try:
                            self._write_metadata_fallback(image_path, metadata, full_description, keywords)
                            metadata_written = True
                            if self.verbose >= 2:
                                logger.info("✅ Métadonnées écrites avec méthode alternative")
                        except Exception as fallback_error:
                            if self.verbose >= 1:
                                logger.error(f"❌ Échec complet écriture métadonnées: {str(fallback_error)}")

                # Traitement spécial PNG
                if image_path.suffix.lower() == '.png':
                    if self.verbose >= 2:
                        logger.info("📊 Traitement spécial PNG pour les métadonnées")
                        
                    with Image.open(image_path) as img:
                        png_info = PngInfo()
                        xmp_packet = f"""<?xpacket begin='\ufeff' id='W5M0MpCehiHzreSzNTczkc9d'?>
                        <x:xmpmeta xmlns:x="adobe:ns:meta/">
                            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                                <rdf:Description rdf:about=""
                                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                                    xmlns:iptc="http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/">
                                    
                                    <dc:title>{escape(metadata.get('title',''))}</dc:title>
                                    <dc:description>{escape(full_description)}</dc:description>
                                    <dc:subject>
                                        <rdf:Bag>
                                            {"".join(f'<rdf:li>{escape(k)}</rdf:li>' for k in keywords)}
                                        </rdf:Bag>
                                    </dc:subject>
                                    <iptc:Category>{escape(metadata.get('main_genre',''))}</iptc:Category>
                                    <iptc:SupplementalCategories>
                                        <rdf:Bag>
                                            <rdf:li>{escape(metadata.get('secondary_genre',''))}</rdf:li>
                                        </rdf:Bag>
                                    </iptc:SupplementalCategories>
                                </rdf:Description>
                            </rdf:RDF>
                        </x:xmpmeta>
                        <?xpacket end='w'?>"""
                        png_info.add_text('XML:com.adobe.xmp', xmp_packet)
                        
                        if self.verbose >= 3:
                            logger.debug(f"💾 Sauvegarde PNG avec XMP intégré ({len(xmp_packet)} octets)")
                        
                        img.save(image_path, pnginfo=png_info, optimize=True)

                if self.verbose >= 2 and metadata_written:
                    logger.info("✅ Métadonnées écrites avec succès")
                    
                return metadata_written
            except Exception as e:
                logger.error(f"❌ Erreur d'écriture des métadonnées : {str(e)}")
                if self.verbose >= 3:
                    import traceback
                    logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")
                return False
    
    def _write_metadata_fallback(self, image_path: pathlib.Path, metadata: dict, full_description: str, keywords: list) -> bool:
        """Méthode de fallback pour écrire les métadonnées sur les images problématiques"""
        try:
            if self.verbose >= 2:
                logger.info(f"🔧 Utilisation de la méthode fallback pour {image_path.name}")
            
            # Pour les PNG, utiliser uniquement la méthode PIL
            if image_path.suffix.lower() == '.png':
                return self._write_png_metadata_only(image_path, metadata, full_description, keywords)
            
            # Pour les JPG, essayer une approche plus simple avec pyexiv2
            elif image_path.suffix.lower() in ('.jpg', '.jpeg'):
                return self._write_jpg_metadata_simple(image_path, metadata, full_description, keywords)
            
            else:
                if self.verbose >= 2:
                    logger.warning(f"⚠️ Format non supporté pour fallback: {image_path.suffix}")
                return False
                
        except Exception as e:
            if self.verbose >= 2:
                logger.error(f"❌ Échec méthode fallback: {str(e)}")
            return False
    
    def _write_png_metadata_only(self, image_path: pathlib.Path, metadata: dict, full_description: str, keywords: list) -> bool:
        """Écriture métadonnées PNG uniquement avec PIL"""
        try:
            with Image.open(image_path) as img:
                png_info = PngInfo()
                
                # Métadonnées de base
                png_info.add_text('Title', metadata.get('title', ''))
                png_info.add_text('Description', full_description)
                png_info.add_text('Keywords', ', '.join(keywords))
                png_info.add_text('Genre', metadata.get('main_genre', ''))
                
                # XMP simplifié
                xmp_packet = f"""<?xpacket begin='\ufeff' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about=""
            xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:title>{escape(metadata.get('title',''))}</dc:title>
            <dc:description>{escape(full_description)}</dc:description>
        </rdf:Description>
    </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'?>"""
                png_info.add_text('XML:com.adobe.xmp', xmp_packet)
                
                img.save(image_path, pnginfo=png_info, optimize=True)
                return True
        except Exception as e:
            if self.verbose >= 2:
                logger.error(f"❌ Échec PNG fallback: {str(e)}")
            return False
    
    def _write_jpg_metadata_simple(self, image_path: pathlib.Path, metadata: dict, full_description: str, keywords: list) -> bool:
        """Écriture métadonnées JPG avec approche alternative sans pyexiv2"""
        try:
            # Utiliser PIL pour créer une nouvelle image avec métadonnées intégrées
            # Cette méthode évite complètement les EXIF corrompus
            from PIL import Image as PILImage
            from PIL.ExifTags import TAGS
            import tempfile
            import shutil
            
            if self.verbose >= 2:
                logger.info(f"🔧 Utilisation de PIL pour contourner les EXIF corrompus")
            
            # Ouvrir l'image avec PIL (ignore les EXIF corrompus)
            with PILImage.open(image_path) as img:
                # Convertir en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Sauvegarder l'image sans les EXIF corrompus
                img.save(temp_path, 'JPEG', quality=95, optimize=True)
            
            # Maintenant essayer d'ajouter les métadonnées XMP avec pyexiv2 sur l'image "propre"
            try:
                with pyexiv2.Image(temp_path) as clean_img:
                    minimal_xmp = {
                        'Xmp.dc.title': metadata.get('title', ''),
                        'Xmp.dc.description': full_description
                    }
                    
                    if keywords:
                        minimal_xmp['Xmp.dc.subject'] = keywords[:10]
                    
                    clean_img.modify_xmp(minimal_xmp)
                
                # Remplacer l'image originale par la version nettoyée avec métadonnées
                shutil.move(temp_path, str(image_path))
                
                if self.verbose >= 2:
                    logger.info(f"✅ Image nettoyée et métadonnées ajoutées: {image_path.name}")
                
                return True
                
            except Exception as xmp_error:
                # Si même l'image nettoyée échoue, au moins on a une image sans EXIF corrompus
                shutil.move(temp_path, str(image_path))
                if self.verbose >= 2:
                    logger.warning(f"⚠️ Image nettoyée mais métadonnées non ajoutées: {str(xmp_error)}")
                return False
                
        except Exception as e:
            if self.verbose >= 2:
                logger.error(f"❌ Échec JPG fallback PIL: {str(e)}")
            return False