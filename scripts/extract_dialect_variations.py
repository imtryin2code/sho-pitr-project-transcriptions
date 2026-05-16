import csv
import os
import re

def generate_variation_report():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/markdown/Dialect_Variation_Report.md'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV list not found.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    variations = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []

        for row in reader:
            note_content = row.get('Notes_Text', '').strip()
            primary_text = row.get('Text', '').strip()
            
            # Non-negotiable check: It must have note content
            if not note_content:
                continue
                
            # Gatekeeper: Only grab it if it's explicitly labeled [LING] or an uncertain question [?]
            if '[LING]' not in note_content and '[?]' not in note_content:
                continue
                
            # Check if it actually contains the linguistic structural markers (|text| or [[text]])
            # This keeps the report focused purely on phonetic variations
            if '|' not in note_content and '[[' not in note_content:
                continue
                
            # Pull localized deviation strings out cleanly via regex
            extracted_variant = "-"
            pipe_match = re.search(r'\|([^\|]+)\|', note_content)
            if pipe_match:
                extracted_variant = f"|{pipe_match.group(1)}|"
            
            gr_spelling = "-"
            gr_match = re.search(r'\[\[([^\]]+)\]\]', note_content)
            if gr_match:
                gr_spelling = f"[[{gr_match.group(1)}]]"
            
            variations.append({
                'id': row.get('ID', 'UNKNOWN').strip(),
                'time': row.get('Time', '00:00').strip(),
                'speaker': row.get('Speaker', 'Unknown').strip(),
                'variant': extracted_variant,
                'gr_standard': gr_spelling,
                'raw_content': note_content
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔊 Dialect Variation & Pronunciation Report\n\n")
        f.write("> Isolated logs capturing speech segments where Joe Peter's pronunciation shifts from traditional Grand Ronde standards.\n\n")
        f.write(f"**Total Variations Logged:** {len(variations)} identified variations across tracks.\n\n")
        
        f.write("| Recording ID | Timestamp | Speaker | Phonetic Deviation (`\|text\|`) | Standard GR Spelling (`[[text]]`) | Complete Annotation Entry |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        if not variations:
            f.write("| - | - | - | - | - | - |\n")
        else:
            for v in variations:
                f.write(f"| `{v['id']}` | {v['time']} | {v['speaker']} | **{v['variant']}** | *{v['gr_standard']}* | {v['raw_content']} |\n")
                
    print(f"✅ Success! Rebuilt Variation Report. Found {len(variations)} dialect variation entries.")

if __name__ == "__main__":
    generate_variation_report()