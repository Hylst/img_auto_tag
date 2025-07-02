#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration du metadata_manager.py

Ce script montre comment utiliser le gestionnaire de métadonnées
avec des exemples pratiques.

Auteur: Geoffroy Streit / Hylst
Date: 2024
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour importer metadata_manager
sys.path.insert(0, str(Path(__file__).parent))

from metadata_manager import MetadataManager

def demo_extract():
    """Démonstration de l'extraction de métadonnées"""
    print("🔍 Démonstration: Extraction de métadonnées")
    print("-" * 50)
    
    # Utiliser le répertoire imgs existant
    imgs_dir = Path(__file__).parent.parent / "imgs"
    output_file = Path(__file__).parent / "extracted_metadata_demo.json"
    
    if not imgs_dir.exists():
        print(f"❌ Répertoire d'images non trouvé: {imgs_dir}")
        return False
    
    # Créer le gestionnaire et extraire
    manager = MetadataManager(verbose=True)
    success = manager.extract_metadata_from_directory(str(imgs_dir), str(output_file))
    
    if success:
        print(f"\n✅ Métadonnées extraites dans: {output_file}")
        
        # Afficher un aperçu du contenu
        with open(output_file, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)
        
        print(f"\n📊 Résumé: {len(metadata_list)} images traitées")
        
        if metadata_list:
            example = metadata_list[0]
            print(f"\n📄 Exemple d'extraction:")
            print(f"  Fichier: {example.get('Fichier', 'N/A')}")
            print(f"  Titre: {example.get('Titre', 'N/A')}")
            print(f"  Taille: {example.get('Taille', 'N/A')}")
            print(f"  Dimensions: {example.get('Largeur', 'N/A')}x{example.get('Hauteur', 'N/A')}")
            print(f"  Mots-clés: {len(example.get('Mots cles', []))} mots-clés")
            
            keywords = example.get('Mots cles', [])
            if keywords:
                print(f"    Exemples: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
        
        return True
    else:
        print("❌ Échec de l'extraction")
        return False

def demo_apply():
    """Démonstration de l'application de métadonnées"""
    print("\n\n📝 Démonstration: Application de métadonnées")
    print("-" * 50)
    
    # Vérifier si le fichier d'extraction existe
    metadata_file = Path(__file__).parent / "extracted_metadata_demo.json"
    
    if not metadata_file.exists():
        print(f"❌ Fichier de métadonnées non trouvé: {metadata_file}")
        print("   Exécutez d'abord la démonstration d'extraction.")
        return False
    
    # Créer des métadonnées de test modifiées
    with open(metadata_file, 'r', encoding='utf-8') as f:
        original_metadata = json.load(f)
    
    if not original_metadata:
        print("❌ Aucune métadonnée trouvée dans le fichier")
        return False
    
    # Modifier les métadonnées pour la démonstration
    demo_metadata = original_metadata[:3]  # Prendre seulement 3 images
    
    for i, metadata in enumerate(demo_metadata):
        metadata['Titre'] = f"[DEMO] {metadata.get('Titre', 'Sans titre')} - Modifié"
        metadata['Description'] = f"Description modifiée par la démonstration. {metadata.get('Description', '')}"
        metadata['Mots cles'] = ["demo", "test", "metadata"] + metadata.get('Mots cles', [])[:5]
        metadata['Caracteristiques'] = metadata['Mots cles'].copy()
        metadata['Createur'] = "Demo Creator / Test"
        metadata['Perception'] = "Perception artistique ajoutée par la démonstration."
        metadata['Conte'] = "Histoire créée pour la démonstration du gestionnaire de métadonnées."
    
    # Sauvegarder les métadonnées modifiées
    demo_file = Path(__file__).parent / "demo_metadata.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_metadata, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Métadonnées de démonstration créées: {demo_file}")
    print(f"📊 {len(demo_metadata)} images seront modifiées")
    
    # Afficher les modifications qui seront appliquées
    print("\n🔧 Modifications qui seront appliquées:")
    for metadata in demo_metadata:
        print(f"  • {metadata['Fichier']}:")
        print(f"    Titre: {metadata['Titre']}")
        print(f"    Mots-clés: {', '.join(metadata['Mots cles'][:3])}...")
    
    # Demander confirmation
    response = input("\n❓ Voulez-vous appliquer ces métadonnées aux images ? (o/N): ")
    
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("⏹️ Application annulée par l'utilisateur")
        return True
    
    # Appliquer les métadonnées
    imgs_dir = Path(__file__).parent.parent / "imgs"
    manager = MetadataManager(verbose=True)
    success = manager.apply_metadata_from_json(str(demo_file), str(imgs_dir))
    
    if success:
        print("\n✅ Métadonnées appliquées avec succès!")
        print("\n🔍 Vérification des modifications:")
        
        # Vérifier quelques images
        for metadata in demo_metadata[:2]:  # Vérifier 2 images
            filename = metadata['Fichier']
            image_path = imgs_dir / filename
            
            if image_path.exists():
                try:
                    import pyexiv2
                    with pyexiv2.Image(str(image_path)) as img:
                        xmp_data = img.read_xmp()
                        title = xmp_data.get('Xmp.dc.title', {})
                        
                        if isinstance(title, dict) and 'lang="x-default"' in title:
                            actual_title = title['lang="x-default"']
                        elif isinstance(title, str):
                            actual_title = title
                        else:
                            actual_title = "Titre non trouvé"
                        
                        print(f"  ✅ {filename}: {actual_title}")
                        
                except Exception as e:
                    print(f"  ⚠️ {filename}: Erreur de vérification - {str(e)}")
            else:
                print(f"  ❌ {filename}: Fichier non trouvé")
        
        return True
    else:
        print("❌ Échec de l'application des métadonnées")
        return False

def demo_usage():
    """Affiche les exemples d'utilisation en ligne de commande"""
    print("\n\n📚 Utilisation en ligne de commande")
    print("-" * 50)
    
    print("Le script metadata_manager.py peut être utilisé directement:")
    print()
    print("🔍 Extraction de métadonnées:")
    print("  python scripts_acc/metadata_manager.py extract ./imgs metadata.json")
    print("  python scripts_acc/metadata_manager.py extract ./imgs metadata.json --verbose")
    print()
    print("📝 Application de métadonnées:")
    print("  python scripts_acc/metadata_manager.py apply metadata.json ./imgs")
    print("  python scripts_acc/metadata_manager.py apply metadata.json ./imgs --verbose")
    print()
    print("📄 Aide:")
    print("  python scripts_acc/metadata_manager.py --help")
    print()
    print("💡 Conseils:")
    print("  • Utilisez --verbose pour voir les détails du traitement")
    print("  • Sauvegardez vos images avant d'appliquer des métadonnées")
    print("  • Le format JSON doit correspondre à la structure générée par l'extraction")

def main():
    """Fonction principale de démonstration"""
    print("🎯 Démonstration du Gestionnaire de Métadonnées")
    print("=" * 60)
    
    print("\nCe script démontre les capacités du metadata_manager.py:")
    print("1. Extraction de métadonnées d'images vers JSON")
    print("2. Application de métadonnées JSON vers images")
    print("3. Utilisation en ligne de commande")
    
    # Démonstration d'extraction
    extract_success = demo_extract()
    
    if extract_success:
        # Démonstration d'application
        demo_apply()
    
    # Afficher les exemples d'utilisation
    demo_usage()
    
    print("\n" + "=" * 60)
    print("🎉 Démonstration terminée!")
    print("\nFichiers créés:")
    
    files_created = [
        "extracted_metadata_demo.json",
        "demo_metadata.json"
    ]
    
    for filename in files_created:
        filepath = Path(__file__).parent / filename
        if filepath.exists():
            print(f"  ✅ {filename} ({filepath.stat().st_size} bytes)")
        else:
            print(f"  ❌ {filename} (non créé)")

if __name__ == "__main__":
    main()