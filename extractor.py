import os
import re
from typing import List, Dict, Set, Tuple

class StringExtractor:
    # extract strings from code files

    def __init__(self, file_extensions=None):
        # initialize with file extensions to scan
        self.file_extensions = file_extensions or ['.js', '.jsx', '.ts', '.tsx', '.html', '.vue', '.py']

    def is_valid_file(self, file_path: str) -> bool:
        # check if the file has a valid extension
        _, ext = os.path.splitext(file_path)
        return ext in self.file_extensions
    
    def _clean_string(self, text: str) -> str:
        # clean the string by removing unwanted characters
        text = text.strip()
        text = text.strip('*')
        text = re.sub(r'[\n\t\r]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _extract_quoted_strings(self, content: str, quote_char: str) -> Set[str]:
        # extract strings with specified quote character
        pattern = fr'{quote_char}((?:[^{quote_char}\\]|\\.)*){quote_char}'
        strings = set()
        
        for match in re.finditer(pattern, content):
            text = match.group(1)
            if self._is_english_text(text):
                strings.add(text)
                
        return strings
        
    def _extract_template_literals(self, content: str) -> Set[str]:
        # extract template literals (backtick strings in JS)
        strings = set()
        template_literals = re.finditer(r'`((?:[^`\\]|\\.)*)`', content)
        
        for match in template_literals:
            text = match.group(1)
            # remove template expressions ${...}
            clean_text = re.sub(r'\${[^}]*}', '', text)
            clean_text = self._clean_string(clean_text)
        
            if clean_text and self._is_english_text(clean_text) and len(clean_text) > 1:
                strings.add(clean_text)
                
        return strings

    def extract_strings_from_file(self, file_path: str) -> Set[str]:
        # extract strings from a single file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            all_strings = set()

            # extract visible jsx/html strings
            tag_texts = re.findall(r'>\s*([^<>{}]+)\s*<', content)
            for t in tag_texts:
                clean_text = self._clean_string(t)
                if clean_text and self._is_english_text(clean_text) and len(clean_text) > 1:
                    all_strings.add(clean_text)

            # extract strings with different quotes
            all_strings.update(self._extract_quoted_strings(content, '"'))
            all_strings.update(self._extract_quoted_strings(content, "'"))

            # template literals (JS backticks)
            js_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue']
            if any(file_path.endswith(ext) for ext in js_extensions):
                all_strings.update(self._extract_template_literals(content))
            
            return all_strings
        
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return set()
        
    def _is_english_text(self, text: str) -> bool:
        # check if the text is in English

        # skip empty strings
        if not text.strip():
            return False
        
        # skip strings that are too short
        if len(text.strip()) <= 1:
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
                file_path = os.path.join(root, file)
                if self.is_valid_file(file_path):
                    strings = self.extract_strings_from_file(file_path)
                    filtered = []
                    for s in strings:
                        if s.lower() in seen_strings:
                            continue
                        if any(s.endswith(ext) for ext in ['.xlsx', '.csv', '.json', '.pdf', '.png', '.jpg']):
                            continue
                        if (s.startswith('[') and s.endswith(']')) or (s.startswith('{') and s.endswith('}')):
                            continue

                        seen_strings.add(s.lower())
                        filtered.append(s)

                    if filtered:
                        results[file_path] = filtered
            
        return results
    
def main():
    directory = "/Users/ammiellewambobecker/QQuote/qquote-next/src/"
    extracted_strings = StringExtractor().scan_directory(directory)

    # count total and unique strings

    print(f"Character count: {sum(len(s) for strings in extracted_strings.values() for s in strings)}")
    
    total_strings = sum(len(strings) for strings in extracted_strings.values())

    print(f"Found {total_strings} total strings in {len(extracted_strings)} files")
    
if __name__ == "__main__":
    main()