import json
import csv

def write_json_to_csv(json_file_path, csv_output_path):
    with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

    header = data[0].keys()

    # create a CSV version for easier viewing
    with open(csv_output_path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    json_file = "translations.json"
    csv_output = "english_french_strings.csv"

    write_json_to_csv(json_file, csv_output)
    print(f"Data from '{json_file}' has been written to '{csv_output}'")