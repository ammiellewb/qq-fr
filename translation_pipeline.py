from typing import Dict, List
import argparse
import os

from extractor import StringExtractor
from filter import OpenAIFilter
from translator import DeepLTranslator
from file_service import FileService


class TranslationPipeline:
    """Process for extracting, filtering, and translating strings from a codebase."""
    
    def __init__(self, openai_api_key: str, deepl_api_key: str, file_extensions=None):
        """Initialize the pipeline with API keys and file extensions to scan."""
        self.extractor = StringExtractor(file_extensions)
        self.filter = OpenAIFilter(openai_api_key)
        self.translator = DeepLTranslator(deepl_api_key)
        self.file_service = FileService()
    
    def flatten_extracted_strings(self, extracted_strings: Dict[str, List[str]]) -> List[str]:
        """Flatten the dictionary of extracted strings into a single list."""
        all_strings = []
        for file_strings in extracted_strings.values():
            all_strings.extend(file_strings)
        return all_strings
    
    def create_translation_list(self, strings: List[str], target_lang="FR") -> List[Dict]:
        """Create a list of dictionaries with original and translated strings."""
        print(f"Translating {len(strings)} strings...")
        translations = self.translator.batch_translate(strings, target_lang)

        result = []
        for english in strings:
            translation = translations.get(english, "TRANSLATION_MISSING")
            result.append({
                "english": english,
                "french": translation
            })

        return result
    
    def run(self, directory: str, target_lang="FR", save_intermediates=False) -> None:
        """Run the complete pipeline."""
        print(f"Scanning directory: {directory}")
        
        # Step 1: Extract strings
        extracted_strings = self.extractor.scan_directory(directory)
        all_strings = self.flatten_extracted_strings(extracted_strings)
        print(f"Found {len(all_strings)} total strings in {len(extracted_strings)} files")
        
        if save_intermediates:
            self.file_service.save_to_json(extracted_strings, 'json_files/extracted_strings.json')
        
        # Step 2: Filter strings to keep only user-facing text
        filtered_strings = self.filter.filter(all_strings)
        print(f"Filtered to {len(filtered_strings)} user-facing strings")
        
        if save_intermediates:
            self.file_service.save_to_json({"filtered": filtered_strings}, 'json_files/filtered_strings.json')
        
        # Step 3: Translate strings
        translations = self.create_translation_list(filtered_strings, target_lang)
        
        # Step 4: Save translations
        self.file_service.save_translations_to_json(translations, 'json_files/translations.json')
        
        # Step 5: Convert to CSV
        self.file_service.write_json_to_csv('json_files/translations.json', f'csv_files/english_{target_lang.lower()}_strings.csv')


def main():
    parser = argparse.ArgumentParser(description="Extract, filter, and translate strings from code files.")
    
    parser.add_argument('directory', type=str, help='Directory to scan for code files')
    parser.add_argument('--openai-key', type=str, required=True, help='OpenAI API key')
    parser.add_argument('--deepl-key', type=str, required=True, help='DeepL API key')
    parser.add_argument('--target-lang', type=str, default='FR', help='Target language code (default: FR)')
    parser.add_argument('--save-intermediates', action='store_true', help='Save intermediate results to files')
    parser.add_argument('--extensions', type=str, nargs='+', 
                        default=['.js', '.jsx', '.ts', '.tsx', '.html', '.vue', '.py'],
                        help='List of file extensions to scan (e.g., .js .jsx .ts)')
    
    args = parser.parse_args()
    
    pipeline = TranslationPipeline(
        openai_api_key=args.openai_key,
        deepl_api_key=args.deepl_key,
        file_extensions=args.extensions
    )
    
    pipeline.run(
        directory=args.directory,
        target_lang=args.target_lang,
        save_intermediates=args.save_intermediates
    )


if __name__ == "__main__":
    main()