#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from src.image_processor import ImageProcessor
from src.config import initialize_apis
from src.logging_utils import configure_logging, LogLevel

# Configure debug logging
configure_logging(console_level=LogLevel.DEBUG, file_level=LogLevel.DEBUG)

try:
    # Initialize APIs
    vision_client, gemini_model = initialize_apis('config/service-account.json', 'your-project-id')
    
    # Create processor with verbose level 3 to see all debug output including raw responses
    processor = ImageProcessor(vision_client, gemini_model, 'fr', True, 1, 'vision')
    processor.verbose = 3
    
    # Test with one image
    test_image = './imgs/Art.jpg'
    if os.path.exists(test_image):
        print(f"Processing {test_image}...")
        result = processor.process_single_image(test_image)
        print(f"Result: {result}")
        
        # Debug output
        print(f"Processing completed successfully")
    else:
        print(f"Test image {test_image} not found")
        # List available images
        imgs_dir = './imgs'
        if os.path.exists(imgs_dir):
            images = [f for f in os.listdir(imgs_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                test_image = os.path.join(imgs_dir, images[0])
                print(f"Using first available image: {test_image}")
                result = processor.process_single_image(test_image)
                print(f"Result: {result}")
                
                # Debug output
                print(f"Processing completed successfully")
            else:
                print("No images found in imgs directory")
        else:
            print("imgs directory not found")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Write error details to file
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"Exception: {e}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")