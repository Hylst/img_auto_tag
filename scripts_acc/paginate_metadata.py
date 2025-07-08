#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paginate Metadata - Script pour diviser un fichier metadata.json en pages

Ce script scanne le répertoire courant à la recherche d'un fichier metadata.json
et le divise en sous-dossiers numérotés contenant chacun maximum 30 images
avec leur fichier metadata.json correspondant.

Utilisation:
    python paginate_metadata.py

Auteur: Geoffroy Streit / Hylst
Date: 2024
"""

import json
import os
import shutil
import math
from pathlib import Path
from typing import List, Dict, Any

class MetadataPaginator:
    """Gestionnaire pour la pagination des métadonnées d'images"""
    
    def __init__(self, images_per_page: int = 30):
        """
        Initialise le paginateur de métadonnées
        
        Args:
            images_per_page: Nombre maximum d'images par page (défaut: 30)
        """
        self.images_per_page = images_per_page
        self.current_dir = Path.cwd()
        self.metadata_file = self.current_dir / "metadata.json"
    
    def find_metadata_file(self) -> bool:
        """
        Vérifie la présence du fichier metadata.json dans le répertoire courant
        
        Returns:
            True si le fichier existe, False sinon
        """
        if not self.metadata_file.exists():
            print(f"❌ Fichier metadata.json non trouvé dans {self.current_dir}")
            return False
        
        print(f"✅ Fichier metadata.json trouvé: {self.metadata_file}")
        return True
    
    def load_metadata(self) -> List[Dict[str, Any]]:
        """
        Charge le contenu du fichier metadata.json
        
        Returns:
            Liste des métadonnées d'images ou liste vide en cas d'erreur
        """
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
            
            if not isinstance(metadata_list, list):
                print("❌ Le fichier metadata.json doit contenir une liste")
                return []
            
            print(f"📊 {len(metadata_list)} images trouvées dans metadata.json")
            return metadata_list
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de format JSON: {e}")
            return []
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return []
    
    def calculate_pages(self, total_images: int) -> int:
        """
        Calcule le nombre de pages nécessaires
        
        Args:
            total_images: Nombre total d'images
            
        Returns:
            Nombre de pages (arrondi au supérieur)
        """
        pages = math.ceil(total_images / self.images_per_page)
        print(f"📄 {pages} pages nécessaires pour {total_images} images ({self.images_per_page} par page)")
        return pages
    
    def create_page_directories(self, num_pages: int) -> List[Path]:
        """
        Crée les répertoires numérotés pour chaque page
        
        Args:
            num_pages: Nombre de pages à créer
            
        Returns:
            Liste des chemins des répertoires créés
        """
        page_dirs = []
        
        for page_num in range(1, num_pages + 1):
            page_dir = self.current_dir / str(page_num)
            
            # Créer le répertoire s'il n'existe pas
            if page_dir.exists():
                print(f"⚠️ Le répertoire {page_num} existe déjà, il sera vidé")
                # Vider le répertoire existant
                for item in page_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            else:
                page_dir.mkdir()
                print(f"📁 Répertoire créé: {page_num}")
            
            page_dirs.append(page_dir)
        
        return page_dirs
    
    def split_metadata_by_pages(self, metadata_list: List[Dict[str, Any]], num_pages: int) -> List[List[Dict[str, Any]]]:
        """
        Divise la liste de métadonnées en pages
        
        Args:
            metadata_list: Liste complète des métadonnées
            num_pages: Nombre de pages
            
        Returns:
            Liste de listes, chaque sous-liste contenant les métadonnées d'une page
        """
        pages_metadata = []
        
        for page_num in range(num_pages):
            start_idx = page_num * self.images_per_page
            end_idx = min(start_idx + self.images_per_page, len(metadata_list))
            
            page_metadata = metadata_list[start_idx:end_idx]
            pages_metadata.append(page_metadata)
            
            print(f"📄 Page {page_num + 1}: {len(page_metadata)} images (indices {start_idx}-{end_idx-1})")
        
        return pages_metadata
    
    def save_page_metadata(self, page_dir: Path, page_metadata: List[Dict[str, Any]], page_num: int) -> bool:
        """
        Sauvegarde les métadonnées d'une page dans son répertoire
        
        Args:
            page_dir: Répertoire de la page
            page_metadata: Métadonnées de la page
            page_num: Numéro de la page
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            metadata_file = page_dir / "metadata.json"
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(page_metadata, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Métadonnées sauvegardées: {metadata_file} ({len(page_metadata)} images)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde page {page_num}: {e}")
            return False
    
    def copy_images_to_page(self, page_dir: Path, page_metadata: List[Dict[str, Any]], page_num: int) -> int:
        """
        Copie les fichiers images correspondants dans le répertoire de la page
        
        Args:
            page_dir: Répertoire de la page
            page_metadata: Métadonnées de la page
            page_num: Numéro de la page
            
        Returns:
            Nombre de fichiers copiés avec succès
        """
        copied_count = 0
        missing_files = []
        
        for metadata in page_metadata:
            filename = metadata.get('Fichier', '')
            if not filename:
                print(f"⚠️ Page {page_num}: Nom de fichier manquant dans les métadonnées")
                continue
            
            source_file = self.current_dir / filename
            dest_file = page_dir / filename
            
            if source_file.exists():
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    print(f"❌ Erreur copie {filename}: {e}")
            else:
                missing_files.append(filename)
        
        if missing_files:
            print(f"⚠️ Page {page_num}: {len(missing_files)} fichiers manquants:")
            for missing in missing_files[:5]:  # Afficher seulement les 5 premiers
                print(f"   - {missing}")
            if len(missing_files) > 5:
                print(f"   ... et {len(missing_files) - 5} autres")
        
        print(f"📋 Page {page_num}: {copied_count}/{len(page_metadata)} fichiers copiés")
        return copied_count
    
    def paginate(self) -> bool:
        """
        Exécute le processus complet de pagination
        
        Returns:
            True si la pagination a réussi, False sinon
        """
        print("🚀 Début de la pagination des métadonnées")
        print("=" * 50)
        
        # 1. Vérifier la présence du fichier metadata.json
        if not self.find_metadata_file():
            return False
        
        # 2. Charger les métadonnées
        metadata_list = self.load_metadata()
        if not metadata_list:
            return False
        
        # 3. Calculer le nombre de pages
        num_pages = self.calculate_pages(len(metadata_list))
        if num_pages == 0:
            print("❌ Aucune page à créer")
            return False
        
        # 4. Créer les répertoires de pages
        page_dirs = self.create_page_directories(num_pages)
        
        # 5. Diviser les métadonnées par pages
        pages_metadata = self.split_metadata_by_pages(metadata_list, num_pages)
        
        # 6. Traiter chaque page
        total_copied = 0
        success_count = 0
        
        for page_num, (page_dir, page_metadata) in enumerate(zip(page_dirs, pages_metadata), 1):
            print(f"\n📄 Traitement de la page {page_num}...")
            
            # Sauvegarder les métadonnées de la page
            if self.save_page_metadata(page_dir, page_metadata, page_num):
                # Copier les fichiers images
                copied = self.copy_images_to_page(page_dir, page_metadata, page_num)
                total_copied += copied
                success_count += 1
            else:
                print(f"❌ Échec du traitement de la page {page_num}")
        
        # 7. Résumé final
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DE LA PAGINATION")
        print(f"✅ Pages créées avec succès: {success_count}/{num_pages}")
        print(f"📁 Répertoires créés: {', '.join([str(i) for i in range(1, num_pages + 1)])}")
        print(f"📋 Total d'images copiées: {total_copied}/{len(metadata_list)}")
        print(f"📄 Images par page: {self.images_per_page} (maximum)")
        
        if success_count == num_pages:
            print("🎉 Pagination terminée avec succès!")
            return True
        else:
            print("⚠️ Pagination terminée avec des erreurs")
            return False

def main():
    """
    Fonction principale du script
    """
    print("📚 Paginateur de Métadonnées d'Images")
    print("Divise un fichier metadata.json en pages de 30 images maximum")
    print()
    
    # Créer et exécuter le paginateur
    paginator = MetadataPaginator(images_per_page=30)
    success = paginator.paginate()
    
    if success:
        print("\n✅ Script terminé avec succès")
        return 0
    else:
        print("\n❌ Script terminé avec des erreurs")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())