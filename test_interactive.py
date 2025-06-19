#!/usr/bin/env python3
"""
Test script for interactive model selection and API key input functionality.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import (
    get_available_gemini_models,
    prompt_for_model_selection,
    prompt_for_api_key
)

def test_interactive_features():
    """Test the interactive model selection and API key input features."""
    print("🧪 Testing Interactive Features")
    print("=" * 50)
    
    # Test 1: Show available models
    print("\n📋 Available Gemini Models:")
    models = get_available_gemini_models()
    for model_id, description in models.items():
        print(f"  - {model_id}: {description}")
    
    # Test 2: Interactive model selection
    print("\n🤖 Testing Model Selection:")
    try:
        selected_model = prompt_for_model_selection()
        print(f"✅ Selected model: {selected_model}")
    except KeyboardInterrupt:
        print("\n⚠️ Model selection cancelled")
        return
    
    # Test 3: Interactive API key input
    print("\n🔑 Testing API Key Configuration:")
    try:
        api_key = prompt_for_api_key()
        if api_key:
            # Mask the API key for security
            masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:] if len(api_key) > 12 else "*" * len(api_key)
            print(f"✅ API key configured: {masked_key}")
        else:
            print("❌ No API key configured")
    except KeyboardInterrupt:
        print("\n⚠️ API key configuration cancelled")
        return
    
    print("\n✅ Interactive features test completed successfully!")
    print("\n💡 Usage examples:")
    print("  # Interactive mode:")
    print("  python src/main.py ./imgs --interactive")
    print("\n  # Command line options:")
    print("  python src/main.py ./imgs --gemini-model gemini-1.5-flash --gemini-api-key YOUR_API_KEY")

if __name__ == "__main__":
    test_interactive_features()