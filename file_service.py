import json
import csv
from typing import List, Dict

class FileService:
     # file operations for translation pipeline

    @staticmethod
    def save_to_json(data: Dict, file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_path}")

    @staticmethod
    def save_translations_to_json(translations: List[Dict], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(translations, json_file, ensure_ascii=False, indent=4)
        print(f"{len(translations)} translations saved to {file_path}")

    @staticmethod
    def write_json_to_csv(json_file_path, csv_output_path) -> None:
        with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

        if not data:
            print(f"No data found in {json_file_path}")
            return
        
        header = data[0].keys()

        # create a CSV version for easier viewing
        with open(csv_output_path, 'w', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)

        print(f"Data from '{json_file_path}' has been written to '{csv_output_path}'")

