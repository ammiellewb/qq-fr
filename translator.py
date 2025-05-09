import requests
from typing import List, Dict

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
            return f"ERROR: {str(e)}"
    
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
    