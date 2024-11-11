import os
import hashlib
import pytesseract
import pdfplumber
import cohere
from PIL import Image
import cv2
import re
import dotenv
import argparse

# Load environment variables from .env file
dotenv.load_dotenv()

# Retrieve Cohere API key from environment variables (make sure to set your API key in .env file)
api_key = os.getenv('COHERE_API_KEY')

if not api_key:
    raise ValueError("Cohere API key is missing. Please set it in the .env file or as an environment variable.")

# Initialize Cohere client
co = cohere.Client(api_key)

def hash_file(filepath):
    """Return the SHA-256 hash of the file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def remove_duplicates(directory):
    """Remove duplicate files in a directory based on hash comparison."""
    seen_hashes = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_hash = hash_file(filepath)
            if file_hash in seen_hashes:
                print(f"Duplicate found: {filepath} (Removing)")
                os.remove(filepath)
            else:
                seen_hashes[file_hash] = filepath

def extract_text_from_image(filepath):
    """Extract text from an image file using OCR."""
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)

def extract_text_from_pdf(filepath):
    """Extract text from a PDF file."""
    text_content = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() or ""
    return text_content

def get_cohere_suggested_name(content):
    """Generate a filename using Cohere based on content."""
    response = co.generate(
        model='command-xlarge',
        prompt=f"Generate a concise and descriptive name for the following content (name for a file and make it short)(return name only)(dont use symbols and emojis just words)(Always name based in title, chapter name, the most repeated word)(output just the name)(dont say 'Here is a proposed name for the file based on' or something like this just give me the name)(dont return anything like your own dialog)(dont use this line 'Here is a proposed name for the file based on'):\n\n{content[:200]}",
        max_tokens=10
    )
    return response.generations[0].text.strip()

def sanitize_filename(filename):
    """Remove invalid characters and handle special cases for Windows compatibility."""
    sanitized = re.sub(r'[<>:"/\\|?*\n\r]', "", filename)
    sanitized = re.sub(r'[^\x00-\x7F]+', "", sanitized)
    return sanitized[:100].strip() or "Untitled"

def rename_file(filepath, new_name):
    """Rename file with a sanitized new name, adding a counter if needed to avoid duplicates."""
    dirpath, ext = os.path.splitext(filepath)
    sanitized_name = sanitize_filename(new_name)
    base_path = os.path.join(os.path.dirname(filepath), sanitized_name)
    new_filepath = f"{base_path}{ext}"
    counter = 1

    while os.path.exists(new_filepath):
        new_filepath = f"{base_path}_{counter}{ext}"
        counter += 1

    try:
        os.rename(filepath, new_filepath)
        print(f"Renamed: {filepath} -> {new_filepath}")
    except OSError as e:
        print(f"Failed to rename {filepath} to {new_filepath}: {e}")

def process_directory(directory, remove_dupes=True, rename_files=True):
    """Process files in a directory: remove duplicates and rename based on content."""
    if remove_dupes:
        print("Removing duplicates...")
        remove_duplicates(directory)

    if rename_files:
        print("Renaming files...")
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                content = ""

                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    content = extract_text_from_image(filepath).strip()
                elif filename.lower().endswith('.pdf'):
                    content = extract_text_from_pdf(filepath).strip()

                if content:
                    suggested_name = get_cohere_suggested_name(content)
                    if suggested_name:
                        rename_file(filepath, suggested_name)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process media files (images, PDFs) to remove duplicates and rename based on content.")
    parser.add_argument('directory', help="Directory to process")
    parser.add_argument('--remove-dupes', action='store_true', help="Remove duplicate files")
    parser.add_argument('--rename-files', action='store_true', help="Rename files based on content")
    parser.add_argument('--both', action='store_true', help="Perform both operations (remove duplicates and rename files)")

    args = parser.parse_args()

    # If neither remove-dupes nor rename-files is specified, default to both operations
    if not args.remove_dupes and not args.rename_files and not args.both:
        args.both = True  # By default, perform both operations if no other options are provided

    if args.both:
        print("Performing both operations: removing duplicates and renaming files.")
        process_directory(args.directory, remove_dupes=True, rename_files=True)
    else:
        # Perform operations based on user's choice
        process_directory(args.directory, remove_dupes=args.remove_dupes, rename_files=args.rename_files)
