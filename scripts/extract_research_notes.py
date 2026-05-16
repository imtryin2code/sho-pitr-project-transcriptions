import csv
import os
import re

def generate_research_log():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/markdown/Research_Observations_Log.md'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV list not found.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

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
    log_data['[UNCATEGORIZED]'] = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []

        for row in reader:
            tier_content = row.get('Notes_Tier', '').strip()
            note_content = row.get('Notes_Text', '').strip()
            primary_text = row.get('Text', '').strip()
            
            matched_tag = None
            
            if '[?]' in note_content or '[UNCERTAIN]' in note_content or '[?]' in tier_content or '[UNCERTAIN]' in tier_content:
                matched_tag = '[UNCERTAIN]'
            else:
                for tag in categories.keys():
                    if tag in note_content or tag in tier_content:
                        matched_tag = tag
                        break
            
            if not matched_tag and not note_content:
                continue

            actual_note = note_content if note_content else primary_text
            if not actual_note:
                continue

            # --- ESCAPE ENGINE: Protect Pipes AND Angle Brackets ---
            # 1. Escape pipes so they don't break table column layouts
            safe_transcription = primary_text.replace('|', '\\|') if primary_text else "[Note Only]"
            safe_note = actual_note.replace('|', '\\|')

            # 2. Convert < and > into safe text entities so Markdown doesn't treat them like HTML tags
            safe_transcription = safe_transcription.replace('<', '&lt;').replace('>', '&gt;')
            safe_note = safe_note.replace('<', '&lt;').replace('>', '&gt;')

            item = {
                'id': row.get('ID', 'UNKNOWN').strip(),
                'time': row.get('Time', '00:00').strip(),
                'speaker': row.get('Speaker', 'Unknown').strip(),
                'transcription': safe_transcription,
                'note': safe_note
            }

            if matched_tag:
                log_data[matched_tag].append(item)
            else:
                log_data['[UNCATEGORIZED]'].append(item)

    # Write out the Markdown Document
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔬 Master Research & Observations Log\n\n")
        f.write("> This log compiles cross-repository annotations parsed directly from dependent notes fields.\n\n")
        
        f.write("## 🗂️ Category Index\n")
        for tag, section_title in categories.items():
            count = len(log_data[tag])
            f.write(f"- [{section_title}](#{tag.lower().replace('[','').replace(']','')}) ({count} entries)\n")
        
        uncat_count = len(log_data['[UNCATEGORIZED]'])
        if uncat_count > 0:
            f.write(f"- [⚠️ Uncategorized Notes](#uncategorized) ({uncat_count} entries)\n")
        f.write("\n---\n\n")

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
            
        if log_data['[UNCATEGORIZED]']:
            f.write("## <a name=\"uncategorized\"></a>⚠️ Uncategorized Notes\n\n")
            f.write("| Source ID | Time | Speaker | Transcription Segment | Observation Note |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for e in log_data['[UNCATEGORIZED]']:
                f.write(f"| `{e['id']}` | {e['time']} | {e['speaker']} | {e['transcription']} | {e['note']} |\n")
            f.write("\n")

    total_found = sum(len(log_data[c]) for c in log_data)
    print(f"✅ Success! Rebuilt Research Log. Found {total_found} cross-referenced entries.")

if __name__ == "__main__":
    generate_research_log()