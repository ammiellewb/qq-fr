from typing import List, Dict
from openai import OpenAI

class OpenAIFilter:
    # filter strings to keep user-facing UI texts and remove others.
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def filter_single_batch(self, texts: List[str]) -> Dict[str, str]:
        prompt = (
            "Filter the following strings to keep only clearly user-facing UI texts. (like button labels, messages, etc.)\n"
            "If a string is not user-facing (variable names, expressions, code, keys, selectors, etc.), remove it.\n"
            "Return only the strings that are user-facing, one per line, each prefixed with '- '.\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Strings: \n" + "\n".join(f"- {s}" for s in texts)}
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            filtered_strings = [line.strip("- ") for line in content.splitlines() if line.strip().startswith("- ")]
            return filtered_strings

        except Exception as e:
            print(f"OpenAI_ERROR: {str(e)}")
            return []
        
    def filter(self, texts: List[str], batch_size=30) -> List[str]:
        filtered_all = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            print(f"Filtering batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            filtered_strings = self.filter_single_batch(batch)
            filtered_all.extend(filtered_strings)
        return filtered_all
