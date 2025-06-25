import subprocess
import os

def clear_and_write_metadata():
    """
    Clears specified metadata fields and writes 'Hylst' to other fields
    for all JPG and PNG files in the current directory using ExifTool.
    """
    print("Starting metadata operations...")

    # Define the metadata fields to clear
    fields_to_clear = [
        "Creator",
        "By-line",
        "Artist",
        "XPAthor",  # Note: ExifTool uses XPAthor for XP Author
        "XPSubject",
        "Software"
    ]

    # Define the fields to write 'Hylst' to
    fields_to_write_hylst = [
        "Artist",
        "XPAthor"
    ]

    # Get all JPG and PNG files in the current directory
    image_files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not image_files:
        print("No JPG or PNG files found in the current directory.")
        return

    for image_file in image_files:
        print(f"Processing {image_file}...")
        try:
            # Construct the command to clear fields
            clear_command = ["exiftool"]
            for field in fields_to_clear:
                clear_command.extend([f"-{field}="])
            clear_command.append(image_file)
            clear_command.append("-overwrite_original") # Overwrite original file, ExifTool creates a backup by default

            # Execute the clear command
            print(f"Clearing fields for {image_file}...")
            subprocess.run(clear_command, check=True, capture_output=True, text=True)
            print(f"Successfully cleared fields for {image_file}.")

            # Construct the command to write 'Hylst' to fields
            write_command = ["exiftool"]
            for field in fields_to_write_hylst:
                write_command.extend([f"-{field}=Hylst"])
            write_command.append(image_file)
            write_command.append("-overwrite_original") # Overwrite original file, ExifTool creates a backup by default

            # Execute the write command
            print(f"Writing 'Hylst' to fields for {image_file}...")
            subprocess.run(write_command, check=True, capture_output=True, text=True)
            print(f"Successfully wrote 'Hylst' to fields for {image_file}.")

        except FileNotFoundError:
            print("Error: ExifTool not found. Please ensure ExifTool is installed and in your system's PATH.")
            break
        except subprocess.CalledProcessError as e:
            print(f"Error processing {image_file}: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print("Metadata operations completed.")

if __name__ == "__main__":
    clear_and_write_metadata()