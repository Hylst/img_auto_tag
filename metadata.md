# Guide des Métadonnées IPTC/XMP

## Vue d'ensemble

Cette application écrit automatiquement des métadonnées dans les fichiers d'images analysés en utilisant les standards IPTC et XMP. Les métadonnées permettent d'enrichir les images avec des informations descriptives, des mots-clés et des données de classification.

## Champs de métadonnées actuellement écrits

### Métadonnées XMP (pour tous les formats)

| Champ JSON | Champ XMP | Description | Exemple |
|------------|-----------|-------------|----------|
| `title` | `Xmp.dc.title` | Titre principal de l'image | "Rose Mécanique Steampunk" |
| `description` + `comment` | `Xmp.dc.description` | Description complète combinée | "Dessin au crayon..." + "Ce dessin évoque..." |
| `keywords` + genres | `Xmp.dc.subject` | Mots-clés et catégories | ["Steampunk", "Rose", "Mécanique"] |
| `main_genre` | `Xmp.Iptc4xmpCore.Category` | Genre principal | "Art visuel" |
| `secondary_genre` | `Xmp.Iptc4xmpCore.SupplementalCategories` | Genre secondaire | "Dessin Steampunk" |

### Métadonnées IPTC (pour fichiers JPG/JPEG uniquement)

| Champ JSON | Champ IPTC | Description | Exemple |
|------------|------------|-------------|----------|
| - | `Iptc.Envelope.CharacterSet` | Encodage des caractères | UTF-8 |
| `title` | `Iptc.Application2.ObjectName` | Nom de l'objet | "Rose Mécanique Steampunk" |
| `title` | `Iptc.Application2.Headline` | Titre/En-tête | "Rose Mécanique Steampunk" |
| `description` + `comment` | `Iptc.Application2.Caption` | Légende complète | Description + commentaire combinés |
| `keywords` + genres | `Iptc.Application2.Keywords` | Mots-clés | ["Steampunk", "Rose", "Mécanique"] |
| `main_genre` | `Iptc.Application2.Category` | Catégorie principale | "Art visuel" |
| `secondary_genre` | `Iptc.Application2.SuppCategory` | Catégorie supplémentaire | "Dessin Steampunk" |

## Proposition d'ajout : Champ "Story"

### Nouveau champ proposé

**Nom** : `story`  
**Description** : Présentation lyrique, artistique ou commerciale. Une histoire racontée qui fait penseur ou rêver.  
**Longueur** : Similaire au champ `comment`  
**Usage** : Narration créative, description poétique, histoire inspirante

### Mapping XMP recommandé pour "Story"

**Champ XMP suggéré** : `Xmp.dc.rights` <mcreference link="https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata" index="1">1</mcreference> <mcreference link="https://experienceleague.adobe.com/en/docs/experience-manager-65/content/assets/administer/metadata-concepts" index="2">2</mcreference>

**Justification** :
- Le champ `dc.rights` du Dublin Core est traditionnellement utilisé pour les informations de droits
- Cependant, il peut être réinterprété pour contenir une "histoire des droits créatifs" ou "narrative artistique"
- Alternative : `Xmp.photoshop.Instructions` pour des instructions créatives
- Alternative : Créer un champ personnalisé `Xmp.custom.story`

**Recommandation finale** : `Xmp.photoshop.Instructions`  
Ce champ est plus approprié car il est conçu pour contenir des instructions ou descriptions étendues liées à l'image.

## Standards et compatibilité

### Standards utilisés

- **IPTC Core** : Standard international pour les métadonnées photo <mcreference link="https://iptc.org/standards/photo-metadata/iptc-standard/" index="3">3</mcreference>
- **Dublin Core** : Schéma de métadonnées universel <mcreference link="https://experienceleague.adobe.com/en/docs/experience-manager-65/content/assets/administer/metadata-concepts" index="2">2</mcreference>
- **XMP** : Plateforme de métadonnées extensible d'Adobe <mcreference link="https://photometadata.org/META-Resources-metadata-types-standards-XMP" index="5">5</mcreference>

### Compatibilité logicielle

Les métadonnées écrites sont compatibles avec :
- Adobe Photoshop, Lightroom, Bridge
- Logiciels de gestion d'images professionnels
- Bibliothèques et systèmes de gestion numérique
- Moteurs de recherche d'images

## Traitement spécial par format

### Fichiers JPG/JPEG
- Métadonnées XMP + IPTC
- Double écriture pour compatibilité maximale
- Support complet des standards

### Fichiers PNG
- Métadonnées XMP uniquement
- Intégration dans les chunks PNG
- Format XML personnalisé

## Structure des mots-clés

Les mots-clés sont automatiquement compilés à partir de :
1. `main_genre` (genre principal)
2. `secondary_genre` (genre secondaire)  
3. `keywords` (mots-clés spécifiques)

Dédoublonnage automatique pour éviter les répétitions.

## Exemple de métadonnées complètes

```json
{
  "title": "Rose Mécanique Steampunk",
  "description": "Dessin au crayon représentant une rose au centre, entourée d'éléments mécaniques steampunk complexes...",
  "comment": "Ce dessin évoque une fusion entre la nature et la technologie...",
  "story": "Dans un monde où les rouages du temps s'entremêlent aux pétales de l'éternité, cette rose mécanique raconte l'histoire d'un amour impossible entre l'âme et la machine. Chaque engrenage murmure une promesse, chaque chaîne tisse un rêve...",
  "main_genre": "Art visuel",
  "secondary_genre": "Dessin Steampunk",
  "keywords": ["Steampunk", "Rose", "Mécanique", "Engrenages", "Mandala"]
}
```

## Références techniques

- [IPTC Photo Metadata Standard 2024.1](https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata)
- [Adobe XMP Specification](https://experienceleague.adobe.com/en/docs/experience-manager-65/content/assets/administer/metadata-concepts)
- [Dublin Core Metadata Initiative](http://dublincore.org/)
- [Guide des champs de métadonnées photo](http://www.photometadata.org/META-Resources-Field-Guide-to-Metadata)