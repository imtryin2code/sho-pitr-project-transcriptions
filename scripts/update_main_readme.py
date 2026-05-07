import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    audio_dir = 'audio-previews'
    
    # 1. Gather Completed IDs
    completed_ids = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            completed_ids = list(set(line.split(',')[0].strip() for line in lines[1:] if line.strip()))
    
    # 2. Count Research Notes
    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 3. Read README
    if not os.path.exists(readme_path):
        return
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. Clean up BOTH old Research sections and any stray horizontal rules
    # This regex is now broader to catch variations of the header and dividers
    content = re.sub(r'---?\s*?\n\n## 🔬 Research & Observations.*?(?=\n---?\n|\n## 📈|$)', '', content, flags=re.DOTALL)
    # Second pass to catch any sections that might not have dividers
    content = re.sub(r'## 🔬 Research & Observations.*?(\n(?=##)|$)', '', content, flags=re.DOTALL)

    # 5. Process Table Links
    lines = content.split('\n')
    updated_lines = []
    for line in lines:
        if line.count('|') >= 4 and not line.strip().startswith('| ---'):
            cells = line.split('|')
            raw_id = re.sub(r'[*`_\[\]\(\)]', '', cells[1]).strip()
            
            if raw_id in completed_ids:
                # Direct link to the file in the repository
                link = f"https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/{audio_dir}/{raw_id}.mp3"
                cells[1] = f" [{raw_id}]({link}) "
            line = "|".join(cells)
        updated_lines.append(line)
    
    content = "\n".join(updated_lines)

    # 6. Define & Insert fresh Research Section
    research_section = f"""
---

## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.

---
"""
    if "## 📈 Project Progress" in content:
        content = content.replace("## 📈 Project Progress", research_section + "\n## 📈 Project Progress")
    
    # 7. Final Completion update
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
    
    print(f"README cleaned and updated. Links: {len(completed_ids)}, Notes: {notes_count}")

if __name__ == "__main__":
    update_readme()