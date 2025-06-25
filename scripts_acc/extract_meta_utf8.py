"""
extract_meta_utf8.py

Ce script Python utilise l'outil ExifTool pour extraire les métadonnées EXIF, IPTC et XMP
des fichiers image dans le répertoire courant et les exporte dans un fichier JSON.
Il offre également des fonctionnalités pour nettoyer et modifier les métadonnées en lot.

Prérequis:
  - ExifTool doit être installé et accessible via le PATH de votre système.
    Téléchargez-le ici: https://exiftool.org/

Utilisation:
  1. Placez ce script dans le même répertoire que vos fichiers image.
  2. Exécutez le script depuis votre terminal:
     `python extract_meta_utf8.py`
  3. Utilisez le menu interactif pour choisir l'action désirée.

Fonctionnalités:
  - Extraction des métadonnées vers JSON
  - Nettoyage en lot des métadonnées spécifiques
  - Écriture d'informations d'auteur personnalisées

Champs extraits:
  - Nom du fichier, Taille, Type MIME, Largeur, Hauteur
  - Catégorie, Catégorie secondaire, Créateur, Description, Mots-clés, Titre
  - Caractéristiques hiérarchiques, Instructions (Perception), Instructions spéciales (Conte)

Gestion des erreurs:
  - Affiche un message si aucun fichier image n'est détecté.
  - Gère l'erreur si ExifTool n'est pas trouvé.
  - Gère les erreurs d'exécution d'ExifTool.
"""
import os
import json
import subprocess

# Extensions d'image supportées par le script
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp'}

def get_image_files():
    """
    Récupère la liste des fichiers image dans le répertoire courant.
    
    Returns:
        list: Liste des noms de fichiers image trouvés
    """
    # os.listdir('.') liste tous les fichiers et dossiers dans le répertoire actuel.
    # os.path.splitext(f) divise le nom de fichier en nom de base et extension.
    # [1].lower() prend l'extension et la convertit en minuscules pour une comparaison insensible à la casse.
    return [f for f in os.listdir('.') if os.path.splitext(f)[1].lower() in EXTENSIONS]

def debug_metadata_fields():
    """
    Fonction de débogage pour afficher tous les champs de métadonnées disponibles.
    Utile pour identifier les noms exacts des champs retournés par ExifTool.
    """
    print("\n=== DÉBOGAGE DES CHAMPS DE MÉTADONNÉES ===")
    
    files = get_image_files()
    if not files:
        print("Aucun fichier JPG ou PNG trouvé.")
        return
    
    # Prend le premier fichier pour le test
    test_file = files[0]
    print(f"Test avec le fichier : {test_file}")
    
    cmd = [
        'exiftool',
        '-charset', 'filename=utf8',
        '-charset', 'exiftool=utf8',
        '-j',
        test_file
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", check=True)
        raw_json = json.loads(result.stdout)
        
        if raw_json:
            print("\nTous les champs disponibles :")
            for key in sorted(raw_json[0].keys()):
                value = raw_json[0][key]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Erreur lors du débogage : {e}")

def extract_metadata():
    """
    Extrait les métadonnées des fichiers image et les exporte vers un fichier JSON.
    
    Cette fonction utilise ExifTool pour extraire les métadonnées EXIF, IPTC et XMP
    des fichiers image dans le répertoire courant et les sauvegarde dans un format JSON personnalisé.
    """
    print("\n🔍 Extraction des métadonnées en cours...")
    
    # Récupère la liste des fichiers image
    files = get_image_files()
    
    # Vérifie si des fichiers image ont été trouvés
    if not files:
        print("❌ Aucun fichier image détecté dans le répertoire courant avec les extensions supportées.")
        return
    
    print(f"📁 {len(files)} fichier(s) image détecté(s): {', '.join(files)}")
    
    # Construit la commande ExifTool avec les options et les champs à extraire.
    # '-charset filename=utf8' et '-charset exiftool=utf8' assurent la gestion correcte de l'UTF-8.
    # '-j' spécifie la sortie au format JSON.
    # Les champs listés sont ceux qui seront extraits des métadonnées des images.
    # CORRECTION: Utilisation des noms de champs corrects basés sur l'analyse ExifTool
    cmd = [
        'exiftool',
        '-charset', 'filename=utf8',
        '-charset', 'exiftool=utf8',
        '-j',
        '-FileName',
        '-FileSize',
        '-MIMEType',
        '-ExifImageWidth',
        '-ExifImageHeight',
        '-Category',  # IPTC Category
        '-SupplementalCategories',  # IPTC SupplementalCategories
        '-Artist',  # IFD0 Artist
        '-Description',  # XMP-dc Description
        '-Subject',  # XMP-dc Subject
        '-Title',  # XMP-dc Title
        '-Keywords',  # IPTC Keywords
        '-Instructions',  # XMP-photoshop Instructions
        '-Caption-Abstract'  # IPTC Caption-Abstract
    ] + files # Ajoute les noms des fichiers image à la commande
    
    # Exécution de la commande ExifTool
    try:
        # subprocess.run exécute la commande externe.
        # stdout=subprocess.PIPE capture la sortie standard.
        # stderr=subprocess.PIPE capture la sortie d'erreur.
        # encoding="utf-8" spécifie l'encodage pour la sortie.
        # check=True lève une CalledProcessError si la commande retourne un code d'erreur non nul.
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", check=True)
        # Charge la sortie JSON brute d'ExifTool.
        raw_json = json.loads(result.stdout)
        
        # Traite les données JSON brutes pour créer un format personnalisé.
        # CORRECTION: Les noms des champs doivent correspondre exactement aux noms retournés par ExifTool
        custom_json = []
        for item in raw_json:
            custom_json.append({
                "Fichier": item.get("SourceFile", ""), # Nom du fichier source
                "Taille": item.get("FileSize", ""), # Taille du fichier
                "Type": item.get("MIMEType", ""), # Type MIME de l'image
                "Largeur": item.get("ExifImageWidth", ""), # Largeur de l'image en pixels
                "Hauteur": item.get("ExifImageHeight", ""), # Hauteur de l'image en pixels
                # CORRECTION: Utilisation des noms exacts retournés par ExifTool
                "Categorie": item.get("Category", ""), # Catégorie IPTC
                "Categorie secondaire": item.get("SupplementalCategories", ""), # Catégories supplémentaires IPTC
                "Createur": item.get("Artist", ""), # Créateur (Artist field)
                "Description": item.get("Description", ""), # Description XMP/IPTC
                "Mots cles": item.get("Subject", []), # Mots-clés XMP (peut être une liste)
                "Titre": item.get("Title", ""), # Titre XMP
                "Caracteristiques": item.get("Keywords", []), # Mots-clés IPTC (liste)
                "Perception": item.get("Instructions", ""), # Instructions IPTC
                "Conte": item.get("Caption-Abstract", "") # Légende/Résumé IPTC
            })
        
        # Écrit les données JSON personnalisées dans un fichier.
        # "w" pour l'écriture, encoding="utf-8" pour supporter les caractères spéciaux.
        # ensure_ascii=False permet d'écrire des caractères non-ASCII directement.
        # indent=2 formate le JSON avec une indentation de 2 espaces pour la lisibilité.
        with open("export_meta_utf8.json", "w", encoding="utf-8") as f:
            json.dump(custom_json, f, ensure_ascii=False, indent=2)
        print("✅ export_meta_utf8.json créé avec succès.")
        
    # Gestion des erreurs spécifiques
    except FileNotFoundError:
        print("❌ Erreur : exiftool n'est pas installé ou n'est pas dans le PATH. Veuillez l'installer et vérifier votre configuration.")
    except subprocess.CalledProcessError as e:
        # Affiche l'erreur standard d'ExifTool si la commande échoue.
        print(f"❌ Erreur d'exécution ExifTool :\n{e.stderr}")
    except json.JSONDecodeError:
        # Gère les erreurs si la sortie d'ExifTool n'est pas un JSON valide.
        print("❌ Erreur : La sortie d'ExifTool n'est pas un JSON valide. Il peut y avoir un problème avec les métadonnées ou la commande.")
    except Exception as e:
        # Capture toute autre exception inattendue.
        print(f"❌ Une erreur inattendue s'est produite : {e}")

def clear_metadata_batch():
    """
    Efface en lot les métadonnées spécifiées pour tous les fichiers JPG et PNG du répertoire courant.
    
    Cette fonction supprime les champs Creator, By-line, Artist, XP Author, XP Subject et Software
    de tous les fichiers image compatibles.
    """
    print("\n🧹 Nettoyage des métadonnées en cours...")
    
    # Récupère uniquement les fichiers JPG et PNG
    files = [f for f in os.listdir('.') if os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg', '.png'}]
    
    if not files:
        print("❌ Aucun fichier JPG ou PNG détecté dans le répertoire courant.")
        return
    
    print(f"📁 {len(files)} fichier(s) à traiter: {', '.join(files)}")
    
    # Champs à effacer
    fields_to_clear = [
        "Creator",
        "By-line", 
        "Artist",
        "XPAuthor",  # Note: ExifTool utilise XPAuthor pour XP Author
        "XPSubject",
        "Software"
    ]
    
    for image_file in files:
        print(f"🔄 Traitement de {image_file}...")
        try:
            # Construit la commande pour effacer les champs
            clear_command = ["exiftool"]
            for field in fields_to_clear:
                clear_command.extend([f"-{field}="])
            clear_command.append(image_file)
            clear_command.append("-overwrite_original")  # Écrase le fichier original, ExifTool crée une sauvegarde par défaut
            
            # Exécute la commande de nettoyage
            subprocess.run(clear_command, check=True, capture_output=True, text=True)
            print(f"✅ Métadonnées effacées pour {image_file}")
            
        except FileNotFoundError:
            print("❌ Erreur : ExifTool non trouvé. Veuillez vous assurer qu'ExifTool est installé et dans votre PATH système.")
            break
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors du traitement de {image_file}: {e}")
            if e.stdout:
                print(f"Sortie: {e.stdout}")
            if e.stderr:
                print(f"Erreur: {e.stderr}")
        except Exception as e:
            print(f"❌ Une erreur inattendue s'est produite: {e}")
    
    print("🏁 Nettoyage des métadonnées terminé.")

def write_author_metadata():
    """
    Écrit 'Geoffroy Streit / Hylst' dans les champs Artist et XP Author
    pour tous les fichiers JPG et PNG du répertoire courant.
    
    Cette fonction ajoute les informations d'auteur spécifiées aux métadonnées des images.
    """
    print("\n✍️ Écriture des informations d'auteur en cours...")
    
    # Récupère uniquement les fichiers JPG et PNG
    files = [f for f in os.listdir('.') if os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg', '.png'}]
    
    if not files:
        print("❌ Aucun fichier JPG ou PNG détecté dans le répertoire courant.")
        return
    
    print(f"📁 {len(files)} fichier(s) à traiter: {', '.join(files)}")
    
    # Valeur à écrire
    author_value = "Geoffroy Streit / Hylst"
    
    # Champs à remplir
    fields_to_write = [
        "Artist",
        "XPAuthor"
    ]
    
    for image_file in files:
        print(f"🔄 Traitement de {image_file}...")
        try:
            # Construit la commande pour écrire les champs
            write_command = ["exiftool"]
            for field in fields_to_write:
                write_command.extend([f"-{field}={author_value}"])
            write_command.append(image_file)
            write_command.append("-overwrite_original")  # Écrase le fichier original, ExifTool crée une sauvegarde par défaut
            
            # Exécute la commande d'écriture
            subprocess.run(write_command, check=True, capture_output=True, text=True)
            print(f"✅ Informations d'auteur écrites pour {image_file}")
            
        except FileNotFoundError:
            print("❌ Erreur : ExifTool non trouvé. Veuillez vous assurer qu'ExifTool est installé et dans votre PATH système.")
            break
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors du traitement de {image_file}: {e}")
            if e.stdout:
                print(f"Sortie: {e.stdout}")
            if e.stderr:
                print(f"Erreur: {e.stderr}")
        except Exception as e:
            print(f"❌ Une erreur inattendue s'est produite: {e}")
    
    print("🏁 Écriture des informations d'auteur terminée.")

def view_all_metadata():
    """
    Affiche toutes les métadonnées disponibles pour un fichier image sélectionné.
    
    Cette fonction utilise ExifTool pour extraire et afficher tous les champs de métadonnées
    disponibles avec un formatage lisible et support complet des accents français.
    """
    print("\n🔍 Visualisation complète des métadonnées...")
    
    # Récupère la liste des fichiers image
    files = get_image_files()
    
    if not files:
        print("❌ Aucun fichier image détecté dans le répertoire courant.")
        return
    
    print(f"\n📁 Fichiers disponibles:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    try:
        choice = int(input("\n👉 Choisissez un fichier (numéro): ")) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice]
            print(f"\n🔍 Analyse de {selected_file}...")
            
            # Commande ExifTool pour extraire toutes les métadonnées
            cmd = [
                'exiftool',
                '-charset', 'filename=utf8',
                '-charset', 'exiftool=utf8',
                '-a',  # Permet les tags dupliqués
                '-G1',  # Affiche les groupes
                '-s',   # Format court
                selected_file
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  encoding="utf-8", check=True)
            
            print("\n" + "="*80)
            print(f"📋 MÉTADONNÉES COMPLÈTES - {selected_file}")
            print("="*80)
            print(result.stdout)
            print("="*80)
            
        else:
            print("❌ Numéro de fichier invalide.")
            
    except ValueError:
        print("❌ Veuillez entrer un numéro valide.")
    except FileNotFoundError:
        print("❌ ExifTool non trouvé. Veuillez l'installer.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur ExifTool: {e.stderr}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def view_useful_metadata():
    """
    Affiche une sélection de métadonnées utiles pour un fichier image sélectionné.
    
    Cette fonction extrait et affiche les champs de métadonnées les plus couramment utilisés
    dans un format structuré et lisible.
    """
    print("\n📊 Visualisation des métadonnées utiles...")
    
    files = get_image_files()
    
    if not files:
        print("❌ Aucun fichier image détecté dans le répertoire courant.")
        return
    
    print(f"\n📁 Fichiers disponibles:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    try:
        choice = int(input("\n👉 Choisissez un fichier (numéro): ")) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice]
            print(f"\n🔍 Analyse de {selected_file}...")
            
            # Champs utiles à extraire
            useful_fields = [
                'FileName', 'FileSize', 'MIMEType', 'ExifImageWidth', 'ExifImageHeight',
                'Make', 'Model', 'DateTime', 'DateTimeOriginal', 'CreateDate',
                'Artist', 'Creator', 'Copyright', 'Title', 'Description', 'Subject',
                'Keywords', 'Category', 'SupplementalCategories', 'Instructions',
                'SpecialInstructions', 'HierarchicalSubject', 'ColorSpace',
                'Orientation', 'XResolution', 'YResolution', 'Software'
            ]
            
            cmd = ['exiftool', '-charset', 'filename=utf8', '-charset', 'exiftool=utf8', '-j']
            for field in useful_fields:
                cmd.append(f'-{field}')
            cmd.append(selected_file)
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  encoding="utf-8", check=True)
            
            data = json.loads(result.stdout)[0]
            
            print("\n" + "="*80)
            print(f"📋 MÉTADONNÉES UTILES - {selected_file}")
            print("="*80)
            
            # Informations de base
            print("\n📄 INFORMATIONS DE BASE:")
            print(f"  Nom du fichier: {data.get('FileName', 'N/A')}")
            print(f"  Taille: {data.get('FileSize', 'N/A')}")
            print(f"  Type MIME: {data.get('MIMEType', 'N/A')}")
            print(f"  Dimensions: {data.get('ExifImageWidth', 'N/A')} x {data.get('ExifImageHeight', 'N/A')}")
            
            # Informations techniques
            print("\n🔧 INFORMATIONS TECHNIQUES:")
            print(f"  Appareil: {data.get('Make', 'N/A')} {data.get('Model', 'N/A')}")
            print(f"  Logiciel: {data.get('Software', 'N/A')}")
            print(f"  Orientation: {data.get('Orientation', 'N/A')}")
            print(f"  Espace colorimétrique: {data.get('ColorSpace', 'N/A')}")
            print(f"  Résolution: {data.get('XResolution', 'N/A')} x {data.get('YResolution', 'N/A')}")
            
            # Dates
            print("\n📅 DATES:")
            print(f"  Date de création: {data.get('CreateDate', 'N/A')}")
            print(f"  Date originale: {data.get('DateTimeOriginal', 'N/A')}")
            print(f"  Date de modification: {data.get('DateTime', 'N/A')}")
            
            # Métadonnées descriptives
            print("\n📝 MÉTADONNÉES DESCRIPTIVES:")
            print(f"  Artiste/Créateur: {data.get('Artist', data.get('Creator', 'N/A'))}")
            print(f"  Copyright: {data.get('Copyright', 'N/A')}")
            print(f"  Titre: {data.get('Title', 'N/A')}")
            print(f"  Description: {data.get('Description', 'N/A')}")
            
            # Mots-clés et catégories
            print("\n🏷️ MOTS-CLÉS ET CATÉGORIES:")
            keywords = data.get('Subject', data.get('Keywords', []))
            if isinstance(keywords, list):
                print(f"  Mots-clés: {', '.join(keywords) if keywords else 'N/A'}")
            else:
                print(f"  Mots-clés: {keywords if keywords else 'N/A'}")
            print(f"  Catégorie: {data.get('Category', 'N/A')}")
            print(f"  Catégories supplémentaires: {data.get('SupplementalCategories', 'N/A')}")
            print(f"  Sujets hiérarchiques: {data.get('HierarchicalSubject', 'N/A')}")
            
            # Instructions
            print("\n📋 INSTRUCTIONS:")
            print(f"  Instructions: {data.get('Instructions', 'N/A')}")
            print(f"  Instructions spéciales: {data.get('SpecialInstructions', 'N/A')}")
            
            print("="*80)
            
        else:
            print("❌ Numéro de fichier invalide.")
            
    except ValueError:
        print("❌ Veuillez entrer un numéro valide.")
    except FileNotFoundError:
        print("❌ ExifTool non trouvé. Veuillez l'installer.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur ExifTool: {e.stderr}")
    except json.JSONDecodeError:
        print("❌ Erreur de décodage JSON.")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def compare_metadata():
    """
    Compare les métadonnées entre deux fichiers image.
    
    Cette fonction permet de comparer côte à côte les métadonnées de deux images
    pour identifier les différences et similitudes.
    """
    print("\n🔄 Comparaison de métadonnées...")
    
    files = get_image_files()
    
    if len(files) < 2:
        print("❌ Au moins 2 fichiers image sont nécessaires pour la comparaison.")
        return
    
    print(f"\n📁 Fichiers disponibles:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    try:
        choice1 = int(input("\n👉 Choisissez le premier fichier (numéro): ")) - 1
        choice2 = int(input("👉 Choisissez le deuxième fichier (numéro): ")) - 1
        
        if 0 <= choice1 < len(files) and 0 <= choice2 < len(files) and choice1 != choice2:
            file1, file2 = files[choice1], files[choice2]
            print(f"\n🔍 Comparaison entre {file1} et {file2}...")
            
            # Extraction des métadonnées pour les deux fichiers
            cmd_base = ['exiftool', '-charset', 'filename=utf8', '-charset', 'exiftool=utf8', '-j']
            
            result1 = subprocess.run(cmd_base + [file1], stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, encoding="utf-8", check=True)
            result2 = subprocess.run(cmd_base + [file2], stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, encoding="utf-8", check=True)
            
            data1 = json.loads(result1.stdout)[0]
            data2 = json.loads(result2.stdout)[0]
            
            # Comparaison
            all_keys = set(data1.keys()) | set(data2.keys())
            common_keys = set(data1.keys()) & set(data2.keys())
            
            print("\n" + "="*100)
            print(f"📊 COMPARAISON DE MÉTADONNÉES")
            print("="*100)
            print(f"Fichier 1: {file1}")
            print(f"Fichier 2: {file2}")
            print(f"\nChamps communs: {len(common_keys)}")
            print(f"Champs uniques au fichier 1: {len(set(data1.keys()) - set(data2.keys()))}")
            print(f"Champs uniques au fichier 2: {len(set(data2.keys()) - set(data1.keys()))}")
            
            print("\n🔍 DIFFÉRENCES DÉTECTÉES:")
            differences_found = False
            for key in sorted(common_keys):
                val1, val2 = data1.get(key), data2.get(key)
                if val1 != val2:
                    differences_found = True
                    print(f"  {key}:")
                    print(f"    Fichier 1: {val1}")
                    print(f"    Fichier 2: {val2}")
            
            if not differences_found:
                print("  Aucune différence trouvée dans les champs communs.")
            
            print("="*100)
            
        else:
            print("❌ Sélection invalide. Choisissez deux fichiers différents.")
            
    except ValueError:
        print("❌ Veuillez entrer des numéros valides.")
    except FileNotFoundError:
        print("❌ ExifTool non trouvé. Veuillez l'installer.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur ExifTool: {e.stderr}")
    except json.JSONDecodeError:
        print("❌ Erreur de décodage JSON.")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def search_metadata():
    """
    Recherche des fichiers contenant une valeur spécifique dans leurs métadonnées.
    
    Cette fonction permet de rechercher tous les fichiers image qui contiennent
    une valeur particulière dans n'importe quel champ de métadonnées.
    """
    print("\n🔍 Recherche dans les métadonnées...")
    
    files = get_image_files()
    
    if not files:
        print("❌ Aucun fichier image détecté dans le répertoire courant.")
        return
    
    search_term = input("\n👉 Entrez le terme à rechercher: ").strip()
    if not search_term:
        print("❌ Terme de recherche vide.")
        return
    
    print(f"\n🔍 Recherche de '{search_term}' dans {len(files)} fichier(s)...")
    
    found_files = []
    
    try:
        for file in files:
            cmd = ['exiftool', '-charset', 'filename=utf8', '-charset', 'exiftool=utf8', '-j', file]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  encoding="utf-8", check=True)
            
            data = json.loads(result.stdout)[0]
            
            # Recherche dans toutes les valeurs
            for key, value in data.items():
                if isinstance(value, str) and search_term.lower() in value.lower():
                    found_files.append((file, key, value))
                    break
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and search_term.lower() in item.lower():
                            found_files.append((file, key, value))
                            break
        
        print("\n" + "="*80)
        print(f"📋 RÉSULTATS DE RECHERCHE POUR '{search_term}'")
        print("="*80)
        
        if found_files:
            for file, field, value in found_files:
                print(f"\n📄 {file}")
                print(f"  Champ: {field}")
                print(f"  Valeur: {value}")
        else:
            print("\nAucun résultat trouvé.")
        
        print("="*80)
        
    except FileNotFoundError:
        print("❌ ExifTool non trouvé. Veuillez l'installer.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur ExifTool: {e.stderr}")
    except json.JSONDecodeError:
        print("❌ Erreur de décodage JSON.")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def display_menu():
    """
    Affiche le menu principal de l'application.
    """
    print("\n" + "="*60)
    print("🖼️  GESTIONNAIRE DE MÉTADONNÉES D'IMAGES")
    print("="*60)
    print("1. 📤 Extraire les métadonnées vers JSON")
    print("2. 🧹 Nettoyer les métadonnées en lot")
    print("3. ✍️  Écrire les informations d'auteur")
    print("4. 👁️  Voir toutes les métadonnées d'un fichier")
    print("5. 📊 Voir les métadonnées utiles d'un fichier")
    print("6. 🔄 Comparer les métadonnées de deux fichiers")
    print("7. 🔍 Rechercher dans les métadonnées")
    print("8. 🔧 Déboguer les champs de métadonnées")
    print("9. ❌ Quitter")
    print("="*60)

def main():
    """
    Fonction principale qui gère le menu interactif et l'exécution des différentes fonctionnalités.
    
    Cette fonction présente un menu à l'utilisateur et exécute l'action choisie en boucle
    jusqu'à ce que l'utilisateur décide de quitter.
    """
    print("🎯 Bienvenue dans le gestionnaire de métadonnées d'images!")
    print("📋 Ce script utilise ExifTool pour gérer les métadonnées de vos images.")
    
    while True:
        display_menu()
        
        try:
            choice = input("\n👉 Choisissez une option (1-9): ").strip()
            
            if choice == "1":
                extract_metadata()
            elif choice == "2":
                print("\n⚠️  ATTENTION: Cette action va effacer définitivement les métadonnées spécifiées.")
                confirm = input("Êtes-vous sûr de vouloir continuer? (oui/non): ").strip().lower()
                if confirm in ['oui', 'o', 'yes', 'y']:
                    clear_metadata_batch()
                else:
                    print("❌ Opération annulée.")
            elif choice == "3":
                write_author_metadata()
            elif choice == "4":
                view_all_metadata()
            elif choice == "5":
                view_useful_metadata()
            elif choice == "6":
                compare_metadata()
            elif choice == "7":
                search_metadata()
            elif choice == "8":
                debug_metadata_fields()
            elif choice == "9":
                print("\n👋 Au revoir! Merci d'avoir utilisé le gestionnaire de métadonnées.")
                break
            else:
                print("❌ Option invalide. Veuillez choisir entre 1 et 9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interruption détectée. Au revoir!")
            break
        except Exception as e:
            print(f"❌ Une erreur inattendue s'est produite: {e}")
        
        # Pause pour permettre à l'utilisateur de lire les messages
        input("\n📝 Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
