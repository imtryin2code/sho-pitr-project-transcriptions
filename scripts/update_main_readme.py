import os
import re

def update_readme():
    readme_path = 'README.md'
    exports_dir = 'exports'
    
    if not os.path.exists(readme_path):
        print("Error: README.md not found.")
        return

    # 1. Map existing files
    formats_map = {}
    subdirs = {'MD': 'markdown', 'PDF': 'pdfs', 'DOCX': 'word-docs'}
    
    for fmt_label, folder in subdirs.items():
        folder_path = os.path.join(exports_dir, folder)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                # Matches patterns like 682-S1
                match = re.search(r'([0-9]{3}-S[1-2])', file)
                if match:
                    rid = match.group(1)
                    if rid not in formats_map:
                        formats_map[rid] = []
                    formats_map[rid].append(fmt_label)

    # 2. Build the list of IDs (682-696)
    all_ids = []
    for num in range(682, 697):
        all_ids.append(f"{num}-S1")
        all_ids.append(f"{num}-S2")

    # 3. Create the New Table
    new_table = "\n| Recording ID | Description | Status | Formats Available |\n"
    new_table += "| :--- | :--- | :--- | :--- |\n"
    
    completed_count = 0
    for rid in all_ids:
        formats = formats_map.get(rid, [])
        if formats:
            completed_count += 1
            status = "✅ Completed"
            # Sort to ensure MD, PDF, DOCX order
            format_str = ", ".join(sorted(formats, reverse=True)) 
        else:
            status = "🟡 In Progress"
            format_str = ""
        new_table += f"| **{rid}** | Boas Text Recitation | {status} | {format_str} |\n"

    # 4. Read and Replace safely
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # This regex looks for the Progress header and stops before the Contributing header
    # It preserves your icons and headings exactly.
    pattern = r"(## 📈 Project Progress\n)([\s\S]*?)(?=\n## 🤝 Contributing)"
    
    if re.search(pattern, content):
        # We keep the header, insert the completion stat, then the table
        header_plus_stat = f"## 📈 Project Progress\n\n**Current Completion:** {completed_count}/{len(all_ids)} recordings processed.\n"
        updated_content = re.sub(pattern, header_plus_stat + new_table, content)
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"README updated: {completed_count} recordings detected.")
    else:
        print("Could not find the Progress section. Check if the heading text matches exactly.")

if __name__ == "__main__":
    update_readme()