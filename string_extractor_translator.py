import os
import re
import json
import requests
import argparse
from typing import List, Dict, Set, Tuple
from openai import OpenAI
import openai
from typing import List, Dict, Callable

# QQuote key
""" qquote_openai_api_key = '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'
client = OpenAI(
    api_key=qquote_openai_api_key,
) """


class StringExtractor:
    # extract strings from code files

    def __init__(self, file_extensions=None):
        # initialize with file extensions to scan
        self.file_extensions = file_extensions or ['.js', '.jsx', '.ts', '.tsx', '.html', '.vue', '.py']

    def is_valid_file(self, file_path: str) -> bool:
        # check if the file has a valid extension
        _, ext = os.path.splitext(file_path)
        return ext in self.file_extensions
    
    def _extract_quoted_strings(self, content: str, quote_char: str) -> Set[str]:
        """Extract strings with specified quote character."""
        pattern = fr'{quote_char}((?:[^{quote_char}\\]|\\.)*){quote_char}'
        strings = set()
        
        for match in re.finditer(pattern, content):
            text = match.group(1)
            if self._is_english_text(text):
                strings.add(text)
                
        return strings
        
    def _extract_template_literals(self, content: str) -> Set[str]:
        """Extract template literals (backtick strings in JS)."""
        strings = set()
        template_literals = re.finditer(r'`((?:[^`\\]|\\.)*)`', content)
        
        for match in template_literals:
            text = match.group(1)
            if self._is_english_text(text):
                # remove template expressions ${...}
                clean_text = re.sub(r'\${[^}]*}', '', text)
                if clean_text.strip():
                    strings.add(clean_text)
                    
        return strings

    def extract_strings_from_file(self, file_path: str) -> Set[str]:
        # extract strings from a single file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # regex to find strings in various formats

            strings = set()

            # extract visible jsx/html strings
            tag_texts = re.findall(r'>\s*([^<>{}]+)\s*<', content)
            for t in tag_texts:
                t = t.strip()
                if self._is_english_text(t):
                    strings.add(t)

            # extract strings with different quotes
            strings.update(self._extract_quoted_strings(content, '"'))
            strings.update(self._extract_quoted_strings(content, "'"))

            # template literals (JS backticks)
            js_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue']
            if any(file_path.endswith(ext) for ext in js_extensions):
                strings.update(self._extract_template_literals(content))
            
            return strings
        
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return set()
        
    def _is_english_text(self, text: str) -> bool:
        # check if the text is in English

        # skip empty strings
        if not text.strip():
            return False
        
        # skip likely variable names, function names, etc.
        if re.match(r'^(\w)+$', text) and '_' in text:
            return False

        # skip URL patterns
        if re.match(r'^https?://', text) or text.startswith('www.'):
            return False
        
        # skip CSS or HTML class names
        if text.startswith('#') or text.startswith('.') or text.startswith('<'):
            return False
        
        # skip strings that contain numbers or special characters
        if re.search(r'[\d@/_\-]', text):
            return False
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        # skip ternary-like syntax
        if re.search(r'\?\s*[\w\d"\']+\s*:', text):
            return False

        # skip accessor chains like user?.info or obj.prop
        if len(text.split()) <= 3 and re.search(r'\b\w+(\?\.)?\w+\b', text) and '.' in text:
            return False

        # skip `return (` or similar
        if re.match(r'^\s*return\s*\(', text):
            return False

        # skip if it's only parenthesis or symbols
        if re.fullmatch(r'[\s(){}[\];.,]*', text):
            return False

        return True
    


    def scan_directory(self, directory: str) -> Dict[str, List[str]]:
        # scan a directory recursively and extract strings from all valid files
        # returns a dictionary with file paths as keys and lists of strings as values
        results = {}
        seen_strings = set()

        for root, _, files in os.walk(directory):
            for file in files:
                if self.is_valid_file(file):
                    file_path = os.path.join(root, file)
                    strings = self.extract_strings_from_file(file_path)
                    filtered = []
                    for s in strings:
                        if s.lower() in seen_strings:
                            continue
                        if s.endswith(".xlsx"):
                            continue
                        if not s.startswith('[') and not s.startswith('{') and not s.endswith(']') and not s.endswith('}'):
                            seen_strings.add(s.lower())
                            filtered.append(s)
                    if filtered:
                        results[file_path] = filtered
        return results
    
""" 
class OpenAIFilter:
    #Filter strings to keep user-facing UI texts and remove others.
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.api_key = qquote_openai_api_key

    def filter_single_batch(self, texts: List[str]) -> Dict[str, str]:
        prompt = (
            "Filter the following strings to keep only clearly user-facing UI texts. (like button labels, messages, etc.)\n"
            "If a string is not user-facing (variable names, expressions, code, keys, selectors, etc.), remove it.\n"
        )

        try:
            response = client.responses.create(
                model=self.model,
                instructions=prompt,
                input="Strings: \n" + "\n".join(f"- {s}" for s in texts),
                temperature=0.2,
            )
            content = response.output_text
            filtered_strings = [line.strip("- ") for line in content.splitlines() if line.strip().startswith("- ")]
            return filtered_strings
            # return {text: ("KEEP" if text in filtered_strings else "REMOVE") for text in texts}

        except Exception as e:
            print(f"OpenAI_ERROR: {str(e)}")
            return []
        
    def filter(self, texts: List[str], batch_size=30) -> List[str]:
        filtered_all = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            filtered_strings = self.filter_single_batch(batch)
            filtered_all.extend(filtered_strings)
        return filtered_all
 """

class DeepLTranslator:
    # Translate strings using DeepL API
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-free.deepl.com/v2/translate"

    def translate(self, text: str, target_lang= "FR") -> str:
        params = {
            "auth_key": self.api_key,
            "text": [text],
            "target_lang": target_lang,
        }
        try:
            response = requests.post(self.base_url, data=params)
            response.raise_for_status()
            result = response.json()
            return result["translations"][0]["text"]
        except Exception as e:
            print(f"DeepL API error for '{text}': {str(e)}")
            return f"{str(e)}"
    
    def batch_translate(self, texts: List[str], target_lang= "FR", batch_size=30) -> Dict[str, str]:
        # Translate in batches to avoid hitting API limits
        # Returns a dictionary with original text as keys and translated text as values
        translations = {}
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            params = {
                "auth_key": self.api_key,
                "text": batch,
                "target_lang": target_lang,
            }
            try:
                response = requests.post(self.base_url, data=params)
                response.raise_for_status()
                result = response.json()
                for original, translation in zip(batch, result["translations"]):
                    translations[original] = translation["text"]
                print(f"Translated batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")

            except Exception as e:
                print(f"DeepL API error for batch: {str(e)}")
                for text in batch:
                    if text not in translations:
                        translations[text] = f"Error: {str(e)}"

        return translations
    
def create_translation_list(extracted_strings: Dict[str, List[str]], translator: DeepLTranslator) -> List[Dict]:
    # Create a list of dictionaries with original and translated strings
    english_strings = []

    for file_strings in extracted_strings.values():
        english_strings.extend(file_strings)

    # translating all strings
    print(f"Translating {len(extracted_strings)} strings...")
    translations = translator.batch_translate(english_strings)

    result = []
    for english in english_strings:
        french = translations.get(english, "TRANSLATION_MISSING")
        result.append({
            "english": english,
            "french": french
        })

    return result

def main():
    parser = argparse.ArgumentParser(description="Extract strings from code files.")
    
    #parser.add_argument('directory', type=str, help='Directory to scan for code files.')
    directory = "qquote-next/src/components"
    #parser.add_argument("--api-key", required=True, help="DeepL API key")
    deepl_key = "7e1b70af-9388-48b2-832d-48e1e52456cc:fx"
    """
    parser.add_argument('--extensions', type=str, nargs='+', default=['.js', '.jsx', '.ts', '.tsx', '.html', '.vue', '.py'],
                        help='List of file extensions to scan (e.g., .js .jsx .ts).')
    """
    
    args = parser.parse_args()

    # initialize the extractor and translator
    extractor = StringExtractor()
    translator = DeepLTranslator(deepl_key)

    # extract strings from the specified directory
    #print(f"Scanning directory: {directory}")
    extracted_strings = extractor.scan_directory(directory)

    """ # count total and unique strings
    print(f"Character count: {sum(len(s) for strings in extracted_strings.values() for s in strings)}")
    
    total_strings = sum(len(strings) for strings in extracted_strings.values())

    print(f"Found {total_strings} total strings in {len(extracted_strings)} files")

    # save results to JSON file
    with open('extracted_strings.json', 'w', encoding='utf-8') as json_file:
        json.dump(extracted_strings, json_file, ensure_ascii=False, indent=4)
    print(f"Extracted strings saved to extracted_strings.json") """

    #filtered_strings = OpenAIFilter(api_key=qquote_openai_api_key).filter(list(extracted_strings.values())[:30])

    # count total filtered strings
    #print(f"Filtered {len(filtered_strings)} from {total_strings} strings")

    # save results to JSON file
    """ with open('filtered_strings.json', 'w', encoding='utf-8') as json_file:
        json.dump(filtered_strings, json_file, ensure_ascii=False, indent=4)
    print(f"Filtered strings saved to filtered_strings.json") """

    # translate strings
    translations = create_translation_list(extracted_strings, translator)

    # save translations to JSON file
    with open('translations.json', 'w', encoding='utf-8') as json_file:
        json.dump(translations, json_file, ensure_ascii=False, indent=4)
    print(f"{len(translations)} saved to translations.json")

    


if __name__ == "__main__":
    main()

