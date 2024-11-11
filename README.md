### Files Filter

Python script to process images and PDFs in a directory by removing duplicates, renaming files based on content, or both. Uses OCR for text extraction and Cohere's AI to generate concise filenames.

### Features:
- **Remove Duplicates**: Identify and remove duplicate files based on hash comparison.
- **Rename Files**: Automatically rename image and PDF files based on extracted text using Cohere's AI model.
- **Flexible Operations**: Choose to remove duplicates, rename files, or perform both operations.
- **OCR Support**: Extract text from images using Tesseract OCR and PDFs using `pdfplumber`.

### Requirements:
- Python 3.x
- `pytesseract` for OCR (Tesseract must be installed separately).
- `pdfplumber` for PDF text extraction.
- `cohere` for AI-generated file renaming.
- `opencv` and `PIL` for image processing.

### Setup:
1. Clone the repository.
2. Install the required libraries:
   
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your [Cohere API key](https://cohere.ai/) in a `.env` file:
   
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   ```
6. Run the script using the command-line options:
   - Remove duplicates: `python media_file_processor.py "path/to/your/directory" --remove-dupes`
   - Rename files: `python media_file_processor.py "path/to/your/directory" --rename-files`
   - Perform both operations: `python media_file_processor.py "path/to/your/directory" --both`

### Usage:
This script is ideal for organizing media libraries by removing duplicate files and automatically renaming them to reflect their content.
