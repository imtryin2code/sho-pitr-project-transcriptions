import csv
import os

def generate_research_log():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/markdown/Research_Observations_Log.md'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV list not found.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Dictionary mapping category codes to clean, human-readable sections
    categories = {
        'LING': '🗣️ Linguistic & Phonetic Observations',
        'HIST': '📜 Cultural & Historical Context Logs',
        'INFO': '💡 General Informational Notes',
        'TEX': '🎓 Exemplary Teaching Examples',
        'VEX': '🎵 High-Quality Vocalization Examples',
        'OTL': '🌐 Other Languages Utilized (English/Marr/etc.)',
        'NOTE': '📝 Workspace Footnotes & General Comments',
        'UNCERTAIN': '❓ Uncertain Segments Requiring Peer Review'
    }

    # Initialize storage matrix for each category
    log_data = {code: [] for code in categories.keys()}
    log_data['UNKNOWN'] = [] # Catch-all for mislabeled categories

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tier = row.get('Notes_Tier', '').strip().upper()
            text = row.get('Notes_Text', '').strip()
            
            # Skip rows that don't have active research annotations
            if not text:
                continue
                
            # Clean category tokens like [LING] down to LING
            clean_tier = tier.replace('[', '').replace(']', '').replace('?', 'UNCERTAIN')
            
            item = {
                'id': row['ID'],
                'time': row['Time'],
                'speaker': row['Speaker'],
                'transcription': row['Text'],
                'note': text
            }
            
            if clean_tier in log_data:
                log_data[clean_tier].append(item)
            else:
                log_data['UNKNOWN'].append(item)

    # Write out the styled markdown report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔬 Master Research & Observations Log\n\n")
        f.write("> This log compiles cross-repository annotations parsed directly from dependent notes tiers.\n\n")
        
        # Table of Contents
        f.write("## 🗂️ Category Index\n")
        for code, section_title in categories.items():
            count = len(log_data[code])
            f.write(f"- [{section_title}](#{code.lower()}) ({count} entries)\n")
        f.write("\n---\n\n")

        # Generate each category section
        for code, section_title in categories.items():
            f.write(f"## <a name=\"{code.lower()}\"></a>{section_title}\n\n")
            entries = log_data[code]
            
            if not entries:
                f.write("_No entries recorded in this category._\n\n")
                continue
                
            f.write("| Source ID | Time | Speaker | Transcription Segment | Observation Note |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for e in entries:
                f.write(f"| `{e['id']}` | {e['time']} | {e['speaker']} | {e['transcription']} | {e['note']} |\n")
            f.write("\n")
            
        # Append Unclassified data if it exists
        if log_data['UNKNOWN']:
            f.write("## ⚠️ Unclassified Notes\n")
            f.write("| Source ID | Time | Speaker | Text | Raw Note |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for e in log_data['UNKNOWN']:
                f.write(f"| `{e['id']}` | {e['time']} | {e['speaker']} | {e['transcription']} | {e['note']} |\n")

    print(f"Success! Rebuilt Research Observations Log sorted by clean category matrices.")

if __name__ == "__main__":
    generate_research_log()