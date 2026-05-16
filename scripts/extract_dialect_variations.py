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
            
            if not note_content:
                continue
                
            if '[LING]' not in note_content and '[?]' not in note_content:
                continue
                
            if '|' not in note_content and '[[' not in note_content:
                continue
                
            # 1. Extract and clean phonetic deviations (strip the outer pipes)
            clean_variant = "-"
            pipe_match = re.search(r'\|([^\|]+)\|', note_content)
            if pipe_match:
                clean_variant = pipe_match.group(1).strip() # Squeezes out raw text inside | |
            
            # 2. Extract and clean standard GR spellings (strip the outer double brackets)
            clean_gr_spelling = "-"
            gr_match = re.search(r'\[\[([^\]]+)\]\]', note_content)
            if gr_match:
                clean_gr_spelling = gr_match.group(1).strip() # Squeezes out raw text inside [[ ]]
            
            # 3. Handle the Markdown pipe-breaker safety for the raw complete column
            safe_content = note_content.replace('|', '\\|')
            
            variations.append({
                'id': row.get('ID', 'UNKNOWN').strip(),
                'time': row.get('Time', '00:00').strip(),
                'speaker': row.get('Speaker', 'Unknown').strip(),
                'variant': clean_variant,
                'gr_standard': clean_gr_spelling,
                'raw_content': safe_content
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔊 Dialect Variation & Pronunciation Report\n\n")
        f.write("> Isolated logs capturing speech segments where Joe Peter's pronunciation shifts from traditional Grand Ronde standards.\n\n")
        f.write(f"**Total Variations Logged:** {len(variations)} identified variations across tracks.\n\n")
        
        # Updated table headers to reflect the clean text display
        f.write("| Recording ID | Timestamp | Speaker | Phonetic Deviation | Standard GR Spelling | Complete Annotation Entry |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        if not variations:
            f.write("| - | - | - | - | - | - |\n")
        else:
            for v in variations:
                # Keeps variant and standard spelling columns clean, while raw_content retains wrappers
                f.write(f"| `{v['id']}` | {v['time']} | {v['speaker']} | {v['variant']} | *{v['gr_standard']}* | {v['raw_content']} |\n")
                
    print(f"✅ Success! Rebuilt Variation Report. Display formatting cleaned up for {len(variations)} entries.")

if __name__ == "__main__":
    generate_variation_report()