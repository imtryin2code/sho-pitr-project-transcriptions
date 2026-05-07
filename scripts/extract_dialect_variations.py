import csv
import os
import re

def extract_dialect_variations():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/markdown/Dialect_Variation_Report.md'
    
    # Pattern: looks for |word| followed by [word]
    # Group 1: The Joe Peter pronunciation (|text|)
    # Group 2: The standard GR spelling ([text])
    pattern = r"\|([^|]+)\| \s*\[([^\]]+)\]"

    variations = []

    if not os.path.exists(csv_path):
        print("Error: Master CSV not found.")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # We only care about Joe Peter's speech
            if "Joe" in row['Speaker'] or "Peter" in row['Speaker']:
                matches = re.findall(pattern, row['Text'])
                for match in matches:
                    variations.append({
                        'ID': row['ID'],
                        'Time': row['Time'],
                        'Joe_Pronunciation': match[0],
                        'GR_Standard': match[1],
                        'Full_Context': row['Text']
                    })

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the results to a Markdown Table
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Dialect Variation Study: Joe Peter vs. Standard Grand Ronde\n\n")
        f.write("This report extracts instances where Joe Peter's pronunciation deviates from the standard GR dictionary.\n\n")
        f.write("| Recording | Time | Joe's Pronunciation | GR Standard Spelling | Full Context |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for v in variations:
            f.write(f"| {v['ID']} | {v['Time']} | `|{v['Joe_Pronunciation']}|` | `[{v['GR_Standard']}]` | {v['Full_Context']} |\n")

    print(f"Success! Found {len(variations)} variations. Report saved to {output_path}")

if __name__ == "__main__":
    extract_dialect_variations()