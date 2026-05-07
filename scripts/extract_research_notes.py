import csv
import re
import os
from datetime import datetime

def extract_research_notes():
    csv_path = 'metadata/master_transcription_list.csv'
    output_path = 'exports/Research_Observations_Log.md'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV not found.")
        return

    # Categories and their display names
    categories = {
        "UNCERTAIN": {"title": "❓ Uncertain / Peer Review Needed", "items": []},
        "LING": {"title": "🗣️ Linguistic Observations", "items": []},
        "HIST": {"title": "📜 Historical & Cultural Context", "items": []},
        "EXAMPLE": {"title": "⭐ Great Speech Examples", "items": []},
        "GENERAL": {"title": "📝 General Observations", "items": []}
    }

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row['Text']
            # Find everything inside [brackets]
            found_notes = re.findall(r'\[(.*?)\]', text)
            
            for note in found_notes:
                upper_note = note.upper()
                # Clean the snippet to remove other brackets for readability
                snippet = re.sub(r'\[.*?\]', '', text).strip()
                entry = f"- **{row['ID']}** ({row['Time']}): {note}\n  > *Context: \"{snippet}\"*"
                
                # Sorting logic
                if any(k in upper_note for k in ["?", "UNCERT", "CHECK"]):
                    categories["UNCERTAIN"]["items"].append(entry)
                elif "LING" in upper_note:
                    categories["LING"]["items"].append(entry)
                elif "HIST" in upper_note:
                    categories["HIST"]["items"].append(entry)
                elif any(k in upper_note for k in ["EX", "EXAMPLE", "STAR"]):
                    categories["EXAMPLE"]["items"].append(entry)
                else:
                    categories["GENERAL"]["items"].append(entry)

    # Write the Markdown file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# 🔬 Research & Observations Log\n\n")
        f.write(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        f.write("This log aggregates all researcher notes found in `[brackets]` within the ELAN transcriptions.\n\n")
        
        # Table of Contents
        f.write("## Table of Contents\n")
        for key, cat in categories.items():
            if cat["items"]:
                f.write(f"- [{cat['title']}](#{key.lower()})\n")
        f.write("\n---\n\n")

        # Sections
        for key, cat in categories.items():
            if cat["items"]:
                f.write(f"<a name='{key.lower()}'></a>\n")
                f.write(f"## {cat['title']}\n")
                f.write("\n".join(cat["items"]) + "\n\n")

    print(f"Research Log updated successfully at {output_path}")

if __name__ == "__main__":
    extract_research_notes()