import csv
import os

def generate_research_log():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/markdown/Research_Observations_Log.md'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV list not found.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Clean category definitions matching your readme tags perfectly
    categories = {
        '[LING]': '🗣️ Linguistic & Phonetic Observations',
        '[HIST]': '📜 Cultural & Historical Context Logs',
        '[INFO]': '💡 General Informational Notes',
        '[TEX]': '🎓 Exemplary Teaching Examples',
        '[VEX]': '🎵 High-Quality Vocalization Examples',
        '[OTL]': '🌐 Other Languages Utilized',
        '[NOTE]': '📝 Workspace Footnotes & General Comments',
        '[UNCERTAIN]': '❓ Uncertain Segments Requiring Review'
    }

    log_data = {tag: [] for tag in categories.keys()}
    log_data['[UNCATEGORIZED]'] = []  # Catch-all for notes without explicit tags

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Strip potential spaces out of headers during initialization 
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []

        for row in reader:
            # Look at your target text cells safely
            note_content = row.get('Notes_Text', '').strip()
            primary_text = row.get('Text', '').strip()
            
            # Non-negotiable check: If there is no note content, skip it entirely!
            if not note_content:
                continue

            # Identify the category by looking for the explicit [TAG] inside the text string
            matched_tag = None
            for tag in categories.keys():
                if tag in note_content:
                    matched_tag = tag
                    break
            
            item = {
                'id': row.get('ID', 'UNKNOWN').strip(),
                'time': row.get('Time', '00:00').strip(),
                'speaker': row.get('Speaker', 'Unknown').strip(),
                'transcription': primary_text if primary_text else "[Note Only]",
                'note': note_content
            }

            if matched_tag:
                log_data[matched_tag].append(item)
            else:
                log_data['[UNCATEGORIZED]'].append(item)

    # Write out the Markdown Document
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔬 Master Research & Observations Log\n\n")
        f.write("> This log compiles cross-repository annotations parsed directly from dependent notes text fields.\n\n")
        
        f.write("## 🗂️ Category Index\n")
        for tag, section_title in categories.items():
            count = len(log_data[tag])
            f.write(f"- [{section_title}](#{tag.lower().replace('[','').replace(']','')}) ({count} entries)\n")
        
        uncat_count = len(log_data['[UNCATEGORIZED]'])
        f.write(f"- [⚠️ Uncategorized Notes](#uncategorized) ({uncat_count} entries)\n")
        f.write("\n---\n\n")

        # Generate output sections for matched categories
        for tag, section_title in categories.items():
            anchor = tag.lower().replace('[','').replace(']','')
            f.write(f"## <a name=\"{anchor}\"></a>{section_title}\n\n")
            entries = log_data[tag]
            
            if not entries:
                f.write("_No entries recorded in this category._\n\n")
                continue
                
            f.write("| Source ID | Time | Speaker | Transcription Segment | Observation Note |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for e in entries:
                f.write(f"| `{e['id']}` | {e['time']} | {e['speaker']} | {e['transcription']} | {e['note']} |\n")
            f.write("\n")
            
        # Write uncategorized section if it caught any notes
        if log_data['[UNCATEGORIZED]']:
            f.write("## <a name=\"uncategorized\"></a>⚠️ Uncategorized Notes\n\n")
            f.write("| Source ID | Time | Speaker | Transcription Segment | Observation Note |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for e in log_data['[UNCATEGORIZED]']:
                f.write(f"| `{e['id']}` | {e['time']} | {e['speaker']} | {e['transcription']} | {e['note']} |\n")
            f.write("\n")

    total_found = sum(len(log_data[c]) for c in log_data)
    print(f"✅ Success! Rebuilt Research Log. Found {total_found} entries total.")

if __name__ == "__main__":
    generate_research_log()