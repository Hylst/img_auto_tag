import io
import json
import logging
import re
import time
import pathlib
import shutil
import unicodedata
from typing import Dict
import google.generativeai as genai
from xml.sax.saxutils import escape
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from google.cloud import vision_v1
import pyexiv2

class ImageProcessor:
    def __init__(self, vision_client, gemini_model, lang="fr"):
        self.vision_client = vision_client
        self.gemini_model = gemini_model
        self.lang = lang.lower().strip()  # Normalisation renforcée
        logging.info(f"Paramètre langue confirmé : {self.lang.upper()}")
        self._init_prompts()

    def _init_prompts(self):
        self.prompts = {
            "fr": {
                "main": """Analyse cette image et retourne un JSON avec :
                {
                    "title": "Titre (3-7 mots)",
                    "description": "Description détaillée",
                    "comment": "Interprétation poétique/philosophique (3-5 phrases)",
                    "main_genre": "Genre principal",
                    "secondary_genre": "Sous-genre", 
                    "keywords": ["mot1", "mot2"]
                }""",
                "comment_instruction": "Rédige une interprétation poétique en 3-5 phrases"
            },
            "en": {
                "main": """Analyze this image and return JSON with:
                {
                    "title": "Title (3-7 words)",
                    "description": "Detailed description",
                    "comment": "Poetic interpretation (3-5 sentences)",
                    "main_genre": "Main genre",
                    "secondary_genre": "Sub-genre",
                    "keywords": ["word1", "word2"]
                }""",
                "comment_instruction": "Write a poetic interpretation in 3-5 sentences"
            }
        }


    def _sanitize_filename(self, title: str) -> str:
        normalized = unicodedata.normalize('NFKD', title)
        cleaned = normalized.encode('ASCII', 'ignore').decode('ASCII')
        sanitized = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in cleaned.strip())
        return sanitized[:50]


    def resize_image(self, image_path: str) -> bytes:
        try:
            with Image.open(image_path) as img:
                if img.mode in ['P', 'RGBA']:
                    img = img.convert('RGB')
                
                img.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                return buffer.getvalue()
        except Exception as e:
            logging.warning(f"Redimensionnement échoué : {str(e)}")
            with open(image_path, "rb") as f:
                return f.read()


    def process_single_image(self, image_path: str) -> Dict:
        try:
            start_time = time.time()
            original_path = pathlib.Path(image_path)
            image_bytes = self.resize_image(str(original_path))
            
            mime_type = "image/jpeg"
            if original_path.suffix.lower() == '.png':
                mime_type = "image/png"

            vision_data = self._analyze_with_vision(image_bytes)
            gemini_data = self._analyze_with_gemini(image_bytes, mime_type, vision_data)
            
            new_path = self._rename_file(original_path, gemini_data.get('title', ''))
            metadata_status = self._write_metadata(new_path, gemini_data)
            
            return {
                "original_file": original_path.name,
                "new_file": pathlib.Path(new_path).name,
                "path": str(new_path),
                **gemini_data,
                "metadata_written": metadata_status,
                "processing_time": time.time() - start_time
            }
        except Exception as e:
            logging.error(f"Échec du traitement : {str(e)}")
            return {"error": str(e)}


    def _analyze_with_vision(self, image_bytes: bytes) -> Dict:
        image = vision_v1.Image(content=image_bytes)
        context = vision_v1.ImageContext(
            language_hints=["fr" if self.lang == "fr" else "en"]
        )
        
        response = self.vision_client.annotate_image({
            "image": image,
            "image_context": context,
            "features": [
                {"type_": vision_v1.Feature.Type.LABEL_DETECTION},
                {"type_": vision_v1.Feature.Type.WEB_DETECTION},
                {"type_": vision_v1.Feature.Type.IMAGE_PROPERTIES}
            ]
        })
        
        return {
            "labels": [label.description for label in response.label_annotations],
            "web_entities": [entity.description for entity in response.web_detection.web_entities],
            "colors": [color.color for color in response.image_properties_annotation.dominant_colors.colors]
        }

    def _analyze_with_gemini(self, image_bytes: bytes, mime_type: str, vision_data: Dict) -> Dict:
        """Appel Gemini API avec contexte linguistique strict"""
        try:
            # Instruction système explicite
            system_instruction = {
                "fr": "Rédige toutes tes réponses en français. ",
                "en": "Respond in English only. "
            }[self.lang]

            full_prompt = f"{system_instruction}\n{self.prompts[self.lang]['main']}"
            
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
            logging.debug(f"Réponse Gemini brute: {response.text}")  # Debug

            # Fallback de génération du commentaire
            if not data.get("comment"):
                comment_prompt = f"{system_instruction}\n{self.prompts[self.lang]['comment_instruction']}"
                response = self.gemini_model.generate_content([
                    {"mime_type": mime_type, "data": image_bytes},
                    comment_prompt
                ])
                data["comment"] = response.text

            return data
        except Exception as e:
            logging.error(f"Erreur Gemini : {str(e)}", exc_info=True)
            return {}

    @staticmethod
    def _parse_gemini_response(text: str) -> Dict:
        """Extrait le JSON de la réponse Gemini"""
        try:
            json_str = re.search(r'({.*})', text, re.DOTALL).group(1)
            return json.loads(json_str)
        except Exception as e:
            logging.error(f"Échec de l'analyse JSON : {str(e)}")
            return {}

    def _rename_file(self, original_path: pathlib.Path, title: str) -> pathlib.Path:
        try:
            sanitized = self._sanitize_filename(title)
            ext = original_path.suffix
            new_name = f"{sanitized}{ext}"
            new_path = original_path.with_name(new_name)
            
            counter = 1
            while new_path.exists():
                new_name = f"{sanitized}_{counter}{ext}"
                new_path = original_path.with_name(new_name)
                counter += 1
                
            original_path.rename(new_path)
            return new_path
        except Exception as e:
            logging.error(f"Échec renommage : {str(e)}")
            return original_path

    def _write_metadata(self, image_path: pathlib.Path, metadata: dict) -> bool:
        try:
            # Ajouter les genres aux keywords
            keywords = []
            if metadata.get('main_genre'):
                keywords.append(metadata['main_genre'])
            if metadata.get('secondary_genre'):
                keywords.append(metadata['secondary_genre'])
            keywords.extend(metadata.get('keywords', []))
            
            # Créer une description combinée
            full_description = f"{metadata.get('description', '')}\n\n{metadata.get('comment', '')}".strip()

            with pyexiv2.Image(str(image_path)) as img:
                # XMP
                img.modify_xmp({
                    'Xmp.dc.title': metadata.get('title', ''),
                    'Xmp.dc.description': full_description,
                    'Xmp.dc.subject': keywords,
                    'Xmp.Iptc4xmpCore.Category': metadata.get('main_genre', ''),
                    'Xmp.Iptc4xmpCore.SupplementalCategories': [metadata.get('secondary_genre', '')]
                })

                # IPTC pour JPG
                if image_path.suffix.lower() in ('.jpg', '.jpeg'):
                    img.modify_iptc({
                        'Iptc.Envelope.CharacterSet': '\x1b%G',
                        'Iptc.Application2.ObjectName': metadata.get('title', ''),
                        'Iptc.Application2.Headline': metadata.get('title', ''),
                        'Iptc.Application2.Caption': full_description,
                        'Iptc.Application2.Keywords': keywords,
                        'Iptc.Application2.Category': metadata.get('main_genre', ''),
                        'Iptc.Application2.SuppCategory': metadata.get('secondary_genre', '')
                    })

            # Fallback PNG
            if image_path.suffix.lower() == '.png':
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
                    img.save(image_path, pnginfo=png_info, optimize=True)

            return True
        except Exception as e:
            logging.error(f"Erreur métadonnées : {str(e)}")
            return False