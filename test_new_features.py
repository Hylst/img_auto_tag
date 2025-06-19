#!/usr/bin/env python3
"""
Test script for new features:
1. Filename slugification
2. Interactive model selection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.image_processor import ImageProcessor
from src.config import select_gemini_model

def test_filename_slugification():
    """Test the new slugification feature"""
    print("\n=== Testing Filename Slugification ===")
    
    # Create a dummy ImageProcessor instance
    processor = ImageProcessor(None, None, lang="fr")
    
    test_cases = [
        "Rose Mécanique Steampunk",
        "Château de Versailles - Vue d'ensemble",
        "Café parisien & croissants",
        "Éléphant d'Afrique (Savane)",
        "Art moderne: abstraction géométrique",
        "Montagne enneigée - Alpes françaises"
    ]
    
    print("Original Title → Slugified Filename")
    print("-" * 50)
    
    for title in test_cases:
        slugified = processor._sanitize_filename(title)
        print(f"{title:<30} → {slugified}")

def test_model_selection_demo():
    """Demonstrate the model selection interface"""
    print("\n=== Model Selection Demo ===")
    print("This would show the interactive model selection:")
    print("")
    print("🤖 Sélection du modèle Gemini")
    print("┌────────┬─────────────────────────┬──────────────────────────────────┐")
    print("│ Option │ Modèle                  │ Description                      │")
    print("├────────┼─────────────────────────┼──────────────────────────────────┤")
    print("│ 1      │ gemini-2.5-flash-preview│ ⚡ Rapide et efficace (Recommandé)│")
    print("│ 2      │ gemini-2.5-pro-preview  │ 🧠 Plus puissant et précis       │")
    print("│ 3      │ gemini-1.5-pro-latest   │ 🔄 Version stable (fin de vie)   │")
    print("└────────┴─────────────────────────┴──────────────────────────────────┘")
    print("")
    print("Note: Use the actual application to see the interactive selection.")

if __name__ == "__main__":
    print("🧪 Testing New Features")
    test_filename_slugification()
    test_model_selection_demo()
    print("\n✅ Feature tests completed!")