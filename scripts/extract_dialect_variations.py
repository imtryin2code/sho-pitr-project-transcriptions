import csv
import os
import re

def extract_dialect_variations():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/markdown/Dialect_Variation_Report.md'
    
    # Pattern: looks for |word| followed by [word]
    pattern = r"\|([^|]+)\| \s*\[([^\]]+)\]"

    variations = []

    if not os.path.exists(csv_path):
        print("Error: Master CSV not found.")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if any(name in row['Speaker'] for name in ["Joe", "Peter"]):
                matches = re.findall(pattern, row['Text'])
                for match in matches:
                    variations.append({
                        'ID': row['ID'],
                        'Time': row['Time'],
                        'Joe_Pronunciation': match[0],
                        'GR_Standard': match[1],
                        'Full_Context': row['Text']
                    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Dialect Variation Study: Joe Peter vs. Standard Grand Ronde\n\n")
        f.write("This report extracts instances where Joe Peter's pronunciation deviates from the standard GR dictionary.\n\n")
        f.write("| Recording | Time | Joe's Pronunciation | GR Standard Spelling | Full Context |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for v in variations:
            # We use &#124; to represent the pipe character | so it doesn't break the table
            joe_variant = f"&#124;{v['Joe_Pronunciation']}&#124;"
            gr_standard = f"[{v['GR_Standard']}]"
            
            # Clean context: replace literal pipes with HTML pipes to keep the table cell intact
            clean_context = v['Full_Context'].replace('|', '&#124;')
            
            f.write(f"| {v['ID']} | {v['Time']} | {joe_variant} | {gr_standard} | {clean_context} |\n")

    print(f"Success! Found {len(variations)} variations. Report saved to {output_path}")

if __name__ == "__main__":
    extract_dialect_variations()