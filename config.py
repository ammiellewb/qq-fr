"""
Configuration module for the translation pipeline.
Place your API keys here or load them from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv('translation-pipeline/.gitignore/.env')

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# DeepL API configuration
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")

# Default directory to scan
DEFAULT_DIRECTORY = os.getenv("DEFAULT_DIRECTORY", "/Users/ammiellewambobecker/QQuote/qquote-next/src/")

# Default target language
DEFAULT_TARGET_LANGUAGE = os.getenv("DEFAULT_TARGET_LANGUAGE", "FR")

# File extensions to scan
DEFAULT_FILE_EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx', '.html', '.vue', '.py']

# Output filenames
TRANSLATIONS_JSON = "json_files/translations.json"
TRANSLATIONS_CSV = "csv_files/english_french_strings.csv"
EXTRACTED_STRINGS_JSON = "json_files/extracted_strings.json"
FILTERED_STRINGS_JSON = "json_files/filtered_strings.json"