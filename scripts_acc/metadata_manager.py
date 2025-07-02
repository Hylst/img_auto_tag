#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata Manager - Script pour gérer les métadonnées d'images

Ce script permet de :
1. Extraire les métadonnées d'images (JPG, JPEG, PNG) vers un fichier JSON
2. Appliquer les métadonnées d'un fichier JSON aux images correspondantes

Auteur: Geoffroy Streit / Hylst
Date: 2024
"""

import json
import pathlib
import argparse
import sys
import os
from typing import Dict, List, Optional, Any
from PIL import Image as PILImage
from PIL.ExifTags import TAGS
import pyexiv2
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MetadataManager:
    """Gestionnaire pour l'extraction et l'application de métadonnées d'images"""
    
    def __init__(self, verbose: bool = False):
        """Initialise le gestionnaire de métadonnées
        
        Args:
            verbose: Active le mode verbeux pour plus de logs
        """
        self.verbose = verbose
        self.supported_extensions = {'.jpg', '.jpeg', '.png'}
        
        if verbose:
            logger.setLevel(logging.DEBUG)
    
    def extract_metadata_from_directory(self, directory_path: str, output_file: str = None) -> bool:
        """Extrait les métadonnées de toutes les images d'un répertoire vers un fichier JSON
        
        Args:
            directory_path: Chemin du répertoire contenant les images
            output_file: Chemin du fichier JSON de sortie (par défaut: metadata.json dans le répertoire des images)
            
        Returns:
            True si l'extraction s'est bien passée, False sinon
        """
        try:
            directory = pathlib.Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                logger.error(f"❌ Le répertoire {directory_path} n'existe pas ou n'est pas un dossier")
                return False
            
            # Définir le fichier de sortie par défaut dans le répertoire des images
            if output_file is None:
                output_file = directory / "metadata.json"
            
            # Rechercher toutes les images supportées (éviter les doublons)
            image_files = set()
            for ext in self.supported_extensions:
                image_files.update(directory.glob(f"*{ext}"))
                image_files.update(directory.glob(f"*{ext.upper()}"))
            
            # Convertir en liste pour le traitement
            image_files = list(image_files)
            
            if not image_files:
                logger.warning(f"⚠️ Aucune image trouvée dans {directory_path}")
                return False
            
            logger.info(f"📁 Traitement de {len(image_files)} images dans {directory_path}")
            
            # Extraire les métadonnées de chaque image
            metadata_collection = []
            for image_file in image_files:
                metadata = self._extract_single_image_metadata(image_file)
                if metadata:
                    metadata_collection.append(metadata)
            
            # Sauvegarder le JSON
            output_path = pathlib.Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_collection, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Métadonnées extraites et sauvegardées dans {output_file}")
            logger.info(f"📊 {len(metadata_collection)} images traitées avec succès")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des métadonnées: {str(e)}")
            return False
    
    def _extract_single_image_metadata(self, image_path: pathlib.Path) -> Optional[Dict[str, Any]]:
        """Extrait les métadonnées d'une seule image
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Dictionnaire contenant les métadonnées ou None en cas d'erreur
        """
        try:
            if self.verbose:
                logger.debug(f"🔍 Extraction métadonnées: {image_path.name}")
            
            # Informations de base avec PIL
            with PILImage.open(image_path) as img:
                width, height = img.size
                file_size = image_path.stat().st_size
                
                # Formatage de la taille
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.0f} kB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Métadonnées de base
            metadata = {
                "Fichier": image_path.name,
                "Taille": size_str,
                "Type": f"image/{image_path.suffix[1:].lower()}",
                "Largeur": width,
                "Hauteur": height,
                "Categorie": "",
                "Categorie secondaire": "",
                "Createur": "Geoffroy Streit / Hylst",
                "Description": "",
                "Mots cles": [],
                "Titre": "",
                "Caracteristiques": [],
                "Perception": "",
                "Conte": ""
            }
            
            # Tentative d'extraction des métadonnées XMP/IPTC avec pyexiv2
            try:
                with pyexiv2.Image(str(image_path)) as img:
                    # Lecture XMP
                    try:
                        xmp_data = img.read_xmp()
                        if xmp_data:
                            # Titre
                            if 'Xmp.dc.title' in xmp_data:
                                title_data = xmp_data['Xmp.dc.title']
                                if isinstance(title_data, dict) and 'lang="x-default"' in title_data:
                                    metadata["Titre"] = title_data['lang="x-default"']
                                elif isinstance(title_data, str):
                                    metadata["Titre"] = title_data
                            
                            # Description
                            if 'Xmp.dc.description' in xmp_data:
                                desc_data = xmp_data['Xmp.dc.description']
                                if isinstance(desc_data, dict) and 'lang="x-default"' in desc_data:
                                    metadata["Description"] = desc_data['lang="x-default"']
                                elif isinstance(desc_data, str):
                                    metadata["Description"] = desc_data
                            
                            # Mots-clés
                            if 'Xmp.dc.subject' in xmp_data:
                                keywords = xmp_data['Xmp.dc.subject']
                                if isinstance(keywords, list):
                                    metadata["Mots cles"] = keywords
                                    metadata["Caracteristiques"] = keywords.copy()
                            
                            # Créateur
                            if 'Xmp.dc.creator' in xmp_data:
                                creator_data = xmp_data['Xmp.dc.creator']
                                if isinstance(creator_data, list) and creator_data:
                                    metadata["Createur"] = creator_data[0]
                                elif isinstance(creator_data, str):
                                    metadata["Createur"] = creator_data
                            
                            # Perception (story)
                            if 'Xmp.photoshop.Instructions' in xmp_data:
                                metadata["Perception"] = xmp_data['Xmp.photoshop.Instructions']
                            
                            # Conte (comment)
                            if 'Xmp.dc.rights' in xmp_data:
                                metadata["Conte"] = xmp_data['Xmp.dc.rights']
                    
                    except Exception as xmp_error:
                        if self.verbose:
                            logger.debug(f"⚠️ Erreur lecture XMP pour {image_path.name}: {str(xmp_error)}")
                    
                    # Lecture IPTC
                    try:
                        iptc_data = img.read_iptc()
                        if iptc_data:
                            # Catégorie
                            if 'Iptc.Application2.Category' in iptc_data:
                                metadata["Categorie"] = iptc_data['Iptc.Application2.Category']
                            
                            # Catégorie secondaire
                            if 'Iptc.Application2.SuppCategory' in iptc_data:
                                metadata["Categorie secondaire"] = iptc_data['Iptc.Application2.SuppCategory']
                            
                            # Mots-clés IPTC (complément)
                            if 'Iptc.Application2.Keywords' in iptc_data:
                                iptc_keywords = iptc_data['Iptc.Application2.Keywords']
                                if isinstance(iptc_keywords, list):
                                    # Fusionner avec les mots-clés XMP
                                    all_keywords = list(set(metadata["Mots cles"] + iptc_keywords))
                                    metadata["Mots cles"] = all_keywords
                                    metadata["Caracteristiques"] = all_keywords.copy()
                    
                    except Exception as iptc_error:
                        if self.verbose:
                            logger.debug(f"⚠️ Erreur lecture IPTC pour {image_path.name}: {str(iptc_error)}")
            
            except Exception as pyexiv2_error:
                if self.verbose:
                    logger.debug(f"⚠️ Erreur pyexiv2 pour {image_path.name}: {str(pyexiv2_error)}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction métadonnées {image_path.name}: {str(e)}")
            return None
    
    def apply_metadata_from_json(self, json_file: str, target_directory: str) -> bool:
        """Applique les métadonnées d'un fichier JSON aux images correspondantes
        
        Args:
            json_file: Chemin vers le fichier JSON contenant les métadonnées
            target_directory: Répertoire contenant les images cibles
            
        Returns:
            True si l'application s'est bien passée, False sinon
        """
        try:
            # Vérifier l'existence du fichier JSON
            json_path = pathlib.Path(json_file)
            if not json_path.exists():
                logger.error(f"❌ Le fichier JSON {json_file} n'existe pas")
                return False
            
            # Vérifier l'existence du répertoire cible
            target_dir = pathlib.Path(target_directory)
            if not target_dir.exists() or not target_dir.is_dir():
                logger.error(f"❌ Le répertoire cible {target_directory} n'existe pas")
                return False
            
            # Charger les métadonnées JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
            
            if not isinstance(metadata_list, list):
                logger.error(f"❌ Le fichier JSON doit contenir une liste de métadonnées")
                return False
            
            logger.info(f"📁 Application des métadonnées à {len(metadata_list)} images")
            
            success_count = 0
            error_count = 0
            
            # Appliquer les métadonnées à chaque image
            for metadata in metadata_list:
                if not isinstance(metadata, dict) or 'Fichier' not in metadata:
                    logger.warning(f"⚠️ Métadonnées invalides ignorées: {metadata}")
                    continue
                
                filename = metadata['Fichier']
                image_path = target_dir / filename
                
                if not image_path.exists():
                    logger.warning(f"⚠️ Image non trouvée: {filename}")
                    error_count += 1
                    continue
                
                if self._apply_single_image_metadata(image_path, metadata):
                    success_count += 1
                else:
                    error_count += 1
            
            logger.info(f"✅ Application terminée: {success_count} succès, {error_count} erreurs")
            return error_count == 0
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'application des métadonnées: {str(e)}")
            return False
    
    def _apply_single_image_metadata(self, image_path: pathlib.Path, metadata: Dict[str, Any]) -> bool:
        """Applique les métadonnées à une seule image
        
        Args:
            image_path: Chemin vers l'image
            metadata: Dictionnaire contenant les métadonnées à appliquer
            
        Returns:
            True si l'application s'est bien passée, False sinon
        """
        try:
            if self.verbose:
                logger.debug(f"🔧 Application métadonnées: {image_path.name}")
            
            # Description complète (pour compatibilité avec l'ancien format)
            description_parts = []
            if metadata.get('Description'):
                description_parts.append(metadata['Description'])
            if metadata.get('Perception'):
                description_parts.append(metadata['Perception'])
            if metadata.get('Conte'):
                description_parts.append(metadata['Conte'])
            
            full_description = '\n\n'.join(description_parts) if description_parts else ''
            
            # Préparer les métadonnées XMP
            xmp_data = {}
            
            # Titre
            if metadata.get('Titre'):
                xmp_data['Xmp.dc.title'] = metadata['Titre']
            
            # Description complète
            if full_description:
                xmp_data['Xmp.dc.description'] = full_description
            
            # Mots-clés
            keywords = metadata.get('Mots cles', [])
            if keywords and isinstance(keywords, list):
                xmp_data['Xmp.dc.subject'] = keywords
            
            # Createur
            if metadata.get('Createur'):
                xmp_data['Xmp.dc.creator'] = [metadata['Createur']]
            
            # Préparer les métadonnées IPTC
            iptc_data = {}
            
            # Catégorie
            if metadata.get('Categorie'):
                iptc_data['Iptc.Application2.Category'] = metadata['Categorie']
            
            # Catégorie secondaire
            if metadata.get('Categorie secondaire'):
                iptc_data['Iptc.Application2.SuppCategory'] = metadata['Categorie secondaire']
            
            # Mots-clés IPTC
            if keywords:
                iptc_data['Iptc.Application2.Keywords'] = keywords
            
            # Application avec gestion d'erreur robuste
            return self._write_metadata_robust(image_path, xmp_data, iptc_data)
            
        except Exception as e:
            logger.error(f"❌ Erreur application métadonnées {image_path.name}: {str(e)}")
            return False
    
    def _write_metadata_robust(self, image_path: pathlib.Path, xmp_data: Dict, iptc_data: Dict) -> bool:
        """Écrit les métadonnées avec gestion d'erreur robuste (similaire à image_processor.py)
        
        Args:
            image_path: Chemin vers l'image
            xmp_data: Données XMP à écrire
            iptc_data: Données IPTC à écrire
            
        Returns:
            True si l'écriture s'est bien passée, False sinon
        """
        try:
            # Stratégie 1: Écriture normale avec pyexiv2
            try:
                with pyexiv2.Image(str(image_path)) as img:
                    if xmp_data:
                        img.modify_xmp(xmp_data)
                    if iptc_data:
                        img.modify_iptc(iptc_data)
                
                if self.verbose:
                    logger.debug(f"✅ Métadonnées écrites (méthode normale): {image_path.name}")
                return True
                
            except Exception as e:
                if self.verbose:
                    logger.debug(f"⚠️ Échec méthode normale pour {image_path.name}: {str(e)}")
                
                # Stratégie 2: Fallback avec nettoyage PIL
                return self._write_metadata_fallback(image_path, xmp_data, iptc_data)
        
        except Exception as e:
            logger.error(f"❌ Erreur complète écriture métadonnées {image_path.name}: {str(e)}")
            return False
    
    def _write_metadata_fallback(self, image_path: pathlib.Path, xmp_data: Dict, iptc_data: Dict) -> bool:
        """Méthode de fallback pour l'écriture des métadonnées
        
        Args:
            image_path: Chemin vers l'image
            xmp_data: Données XMP à écrire
            iptc_data: Données IPTC à écrire
            
        Returns:
            True si l'écriture s'est bien passée, False sinon
        """
        try:
            if image_path.suffix.lower() == '.png':
                return self._write_png_metadata_only(image_path, xmp_data)
            else:
                return self._write_jpg_metadata_simple(image_path, xmp_data, iptc_data)
        
        except Exception as e:
            logger.error(f"❌ Erreur fallback {image_path.name}: {str(e)}")
            return False
    
    def _write_png_metadata_only(self, image_path: pathlib.Path, xmp_data: Dict) -> bool:
        """Écriture métadonnées PNG avec PIL
        
        Args:
            image_path: Chemin vers l'image PNG
            xmp_data: Données XMP à écrire
            
        Returns:
            True si l'écriture s'est bien passée, False sinon
        """
        try:
            from PIL.PngImagePlugin import PngInfo
            
            with PILImage.open(image_path) as img:
                metadata = PngInfo()
                
                # Ajouter les métadonnées comme texte PNG
                if 'Xmp.dc.title' in xmp_data:
                    metadata.add_text("Title", str(xmp_data['Xmp.dc.title']))
                
                if 'Xmp.dc.description' in xmp_data:
                    metadata.add_text("Description", str(xmp_data['Xmp.dc.description']))
                
                if 'Xmp.dc.subject' in xmp_data:
                    keywords = xmp_data['Xmp.dc.subject']
                    if isinstance(keywords, list):
                        metadata.add_text("Keywords", ", ".join(keywords))
                
                if 'Xmp.dc.creator' in xmp_data:
                    creator = xmp_data['Xmp.dc.creator']
                    if isinstance(creator, list) and creator:
                        metadata.add_text("Author", creator[0])
                    elif isinstance(creator, str):
                        metadata.add_text("Author", creator)
                
                # Sauvegarder avec métadonnées
                img.save(image_path, pnginfo=metadata)
            
            if self.verbose:
                logger.debug(f"✅ Métadonnées PNG écrites: {image_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur PNG fallback {image_path.name}: {str(e)}")
            return False
    
    def _write_jpg_metadata_simple(self, image_path: pathlib.Path, xmp_data: Dict, iptc_data: Dict) -> bool:
        """Écriture métadonnées JPG avec approche alternative
        
        Args:
            image_path: Chemin vers l'image JPG
            xmp_data: Données XMP à écrire
            iptc_data: Données IPTC à écrire
            
        Returns:
            True si l'écriture s'est bien passée, False sinon
        """
        try:
            import tempfile
            import shutil
            
            if self.verbose:
                logger.debug(f"🔧 Utilisation de PIL pour contourner les EXIF corrompus")
            
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
                    if xmp_data:
                        clean_img.modify_xmp(xmp_data)
                    if iptc_data:
                        clean_img.modify_iptc(iptc_data)
                
                # Remplacer l'image originale par la version nettoyée avec métadonnées
                shutil.move(temp_path, str(image_path))
                
                if self.verbose:
                    logger.debug(f"✅ Image nettoyée et métadonnées ajoutées: {image_path.name}")
                
                return True
                
            except Exception as xmp_error:
                # Si même l'image nettoyée échoue, au moins on a une image sans EXIF corrompus
                shutil.move(temp_path, str(image_path))
                if self.verbose:
                    logger.debug(f"⚠️ Image nettoyée mais métadonnées non ajoutées: {str(xmp_error)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur JPG fallback PIL {image_path.name}: {str(e)}")
            return False

def main():
    """Fonction principale du script"""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de métadonnées d'images - Extraction et application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Extraire les métadonnées d'un dossier vers JSON
  python metadata_manager.py extract ./images metadata.json
  
  # Appliquer les métadonnées JSON aux images
  python metadata_manager.py apply metadata.json ./images
  
  # Mode verbeux
  python metadata_manager.py extract ./images metadata.json --verbose
        """
    )
    
    parser.add_argument(
        'action',
        choices=['extract', 'apply'],
        help='Action à effectuer: extract (extraire vers JSON) ou apply (appliquer depuis JSON)'
    )
    
    parser.add_argument(
        'source',
        help='Répertoire source (pour extract) ou fichier JSON (pour apply)'
    )
    
    parser.add_argument(
        'target',
        help='Fichier JSON de sortie (pour extract) ou répertoire cible (pour apply)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Active le mode verbeux'
    )
    
    args = parser.parse_args()
    
    # Créer le gestionnaire de métadonnées
    manager = MetadataManager(verbose=args.verbose)
    
    # Exécuter l'action demandée
    if args.action == 'extract':
        logger.info(f"🔍 Extraction des métadonnées de {args.source} vers {args.target}")
        success = manager.extract_metadata_from_directory(args.source, args.target)
    else:  # apply
        logger.info(f"📝 Application des métadonnées de {args.source} vers {args.target}")
        success = manager.apply_metadata_from_json(args.source, args.target)
    
    if success:
        logger.info("✅ Opération terminée avec succès")
        sys.exit(0)
    else:
        logger.error("❌ Opération échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()