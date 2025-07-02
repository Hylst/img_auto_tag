#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour metadata_manager.py

Ce script teste les fonctionnalités d'extraction et d'application de métadonnées.

Auteur: Geoffroy Streit / Hylst
Date: 2024
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Ajouter le répertoire parent au path pour importer metadata_manager
sys.path.insert(0, str(Path(__file__).parent))

from metadata_manager import MetadataManager

def test_extraction():
    """Test de l'extraction de métadonnées"""
    print("🔍 Test d'extraction de métadonnées...")
    
    # Utiliser le répertoire imgs existant
    imgs_dir = Path(__file__).parent.parent / "imgs"
    
    if not imgs_dir.exists():
        print(f"❌ Répertoire d'images non trouvé: {imgs_dir}")
        return False
    
    # Créer un fichier de sortie temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_json = temp_file.name
    
    try:
        # Créer le gestionnaire et extraire
        manager = MetadataManager(verbose=True)
        success = manager.extract_metadata_from_directory(str(imgs_dir), temp_json)
        
        if not success:
            print("❌ Échec de l'extraction")
            return False
        
        # Vérifier le contenu du fichier JSON
        with open(temp_json, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)
        
        if not isinstance(metadata_list, list) or len(metadata_list) == 0:
            print("❌ Fichier JSON vide ou invalide")
            return False
        
        print(f"✅ Extraction réussie: {len(metadata_list)} images traitées")
        
        # Afficher un exemple
        if metadata_list:
            example = metadata_list[0]
            print(f"📄 Exemple - Fichier: {example.get('Fichier', 'N/A')}")
            print(f"📄 Titre: {example.get('Titre', 'N/A')}")
            print(f"📄 Mots-clés: {len(example.get('Mots cles', []))} mots-clés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'extraction: {str(e)}")
        return False
    
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_json):
            os.unlink(temp_json)

def test_application():
    """Test de l'application de métadonnées"""
    print("\n📝 Test d'application de métadonnées...")
    
    # Créer un répertoire temporaire avec une copie d'image
    imgs_dir = Path(__file__).parent.parent / "imgs"
    
    if not imgs_dir.exists():
        print(f"❌ Répertoire d'images non trouvé: {imgs_dir}")
        return False
    
    # Trouver une image de test
    test_images = list(imgs_dir.glob("*.jpg"))[:2]  # Prendre 2 images pour le test
    
    if not test_images:
        print("❌ Aucune image JPG trouvée pour le test")
        return False
    
    # Créer un répertoire temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copier les images de test
        copied_images = []
        for img in test_images:
            dest = temp_path / img.name
            shutil.copy2(img, dest)
            copied_images.append(dest)
        
        # Créer des métadonnées de test
        test_metadata = []
        for i, img_path in enumerate(copied_images):
            metadata = {
                "Fichier": img_path.name,
                "Taille": "Test",
                "Type": "image/jpeg",
                "Largeur": 1920,
                "Hauteur": 1080,
                "Categorie": "Test Category",
                "Categorie secondaire": "Test Subcategory",
                "Createur": "Test Creator",
                "Description": f"Description de test pour l'image {i+1}",
                "Mots cles": ["test", "metadata", f"image{i+1}", "automatique"],
                "Titre": f"Titre de test {i+1}",
                "Caracteristiques": ["test", "metadata", f"image{i+1}"],
                "Perception": f"Perception artistique de test pour l'image {i+1}",
                "Conte": f"Histoire imaginaire pour l'image {i+1}"
            }
            test_metadata.append(metadata)
        
        # Sauvegarder le JSON de test
        test_json = temp_path / "test_metadata.json"
        with open(test_json, 'w', encoding='utf-8') as f:
            json.dump(test_metadata, f, ensure_ascii=False, indent=2)
        
        try:
            # Appliquer les métadonnées
            manager = MetadataManager(verbose=True)
            success = manager.apply_metadata_from_json(str(test_json), str(temp_path))
            
            if not success:
                print("❌ Échec de l'application des métadonnées")
                return False
            
            print(f"✅ Application réussie sur {len(copied_images)} images")
            
            # Vérifier que les métadonnées ont été appliquées
            verification_success = True
            for img_path in copied_images:
                try:
                    import pyexiv2
                    with pyexiv2.Image(str(img_path)) as img:
                        xmp_data = img.read_xmp()
                        if 'Xmp.dc.title' in xmp_data:
                            print(f"✅ Métadonnées vérifiées pour {img_path.name}")
                        else:
                            print(f"⚠️ Métadonnées non trouvées pour {img_path.name}")
                            verification_success = False
                except Exception as e:
                    print(f"⚠️ Erreur vérification {img_path.name}: {str(e)}")
                    verification_success = False
            
            return verification_success
            
        except Exception as e:
            print(f"❌ Erreur lors du test d'application: {str(e)}")
            return False

def test_round_trip():
    """Test complet: extraction puis application"""
    print("\n🔄 Test complet (extraction + application)...")
    
    imgs_dir = Path(__file__).parent.parent / "imgs"
    
    if not imgs_dir.exists():
        print(f"❌ Répertoire d'images non trouvé: {imgs_dir}")
        return False
    
    # Prendre une image pour le test
    test_images = list(imgs_dir.glob("*.jpg"))[:1]
    
    if not test_images:
        print("❌ Aucune image JPG trouvée pour le test")
        return False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copier l'image de test
        test_img = test_images[0]
        copied_img = temp_path / test_img.name
        shutil.copy2(test_img, copied_img)
        
        try:
            manager = MetadataManager(verbose=True)
            
            # 1. Extraire les métadonnées existantes
            extracted_json = temp_path / "extracted.json"
            success1 = manager.extract_metadata_from_directory(str(temp_path), str(extracted_json))
            
            if not success1:
                print("❌ Échec de l'extraction")
                return False
            
            # 2. Modifier légèrement les métadonnées
            with open(extracted_json, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
            
            if metadata_list:
                # Forcer un titre complètement différent
                metadata_list[0]['Titre'] = "TEST ROUND-TRIP MODIFIÉ"
                metadata_list[0]['Mots cles'] = ["test", "round-trip", "metadata"]
                metadata_list[0]['Description'] = "Description modifiée par le test round-trip"
            
            modified_json = temp_path / "modified.json"
            with open(modified_json, 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, ensure_ascii=False, indent=2)
            
            # 3. Appliquer les métadonnées modifiées
            success2 = manager.apply_metadata_from_json(str(modified_json), str(temp_path))
            
            if not success2:
                print("❌ Échec de l'application")
                return False
            
            # 4. Vérifier les modifications
            try:
                import pyexiv2
                with pyexiv2.Image(str(copied_img)) as img:
                    xmp_data = img.read_xmp()
                    title = xmp_data.get('Xmp.dc.title', {})
                    if isinstance(title, dict) and 'lang="x-default"' in title:
                        actual_title = title['lang="x-default"']
                        if "TEST ROUND-TRIP MODIFIÉ" in actual_title:
                            print("✅ Test round-trip réussi: modifications appliquées")
                            return True
                        else:
                            print(f"⚠️ Titre attendu non trouvé. Titre actuel: {actual_title}")
                    elif isinstance(title, str):
                        if "TEST ROUND-TRIP MODIFIÉ" in title:
                            print("✅ Test round-trip réussi: modifications appliquées")
                            return True
                        else:
                            print(f"⚠️ Titre attendu non trouvé. Titre actuel: {title}")
                    else:
                        print(f"⚠️ Format de titre inattendu: {title}")
            except Exception as e:
                print(f"⚠️ Erreur vérification finale: {str(e)}")
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur lors du test round-trip: {str(e)}")
            return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests du gestionnaire de métadonnées")
    print("=" * 50)
    
    tests = [
        ("Extraction", test_extraction),
        ("Application", test_application),
        ("Round-trip", test_round_trip)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    
    success_count = 0
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Score: {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("🎉 Tous les tests sont passés avec succès!")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)