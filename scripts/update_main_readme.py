import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    audio_dir = 'audio-previews'
    
    # 1. Gather Stats
    completed_ids = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            completed_ids = list(set(line.split(',')[0].strip() for line in lines[1:] if line.strip()))
    
    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 2. Read current README
    if not os.path.exists(readme_path):
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 3. Update Table Links
    updated_lines = []
    for line in lines:
        if line.count('|') >= 4 and not line.strip().startswith('| ---'):
            cells = line.split('|')
            raw_content = cells[1].strip()
            clean_id = re.sub(r'[*`_]', '', raw_content)

            if clean_id in completed_ids:
                # Force the GitHub URL for the audio file
                mp3_url = f"https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/{audio_dir}/{clean_id}.mp3"
                cells[1] = f" [{clean_id}]({mp3_url}) "
            
            line = "|".join(cells)
        updated_lines.append(line)

    content = "".join(updated_lines)
    
    # 4. Define the Research Section with horizontal rules included
    research_section = f"""
---

## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.

---
"""

    # 5. Clean and Re-insert
    # This regex removes the old section and any surrounding horizontal rules to avoid double-stacking
    content = re.sub(r'\n---\n\n## 🔬 Research & Observations.*?(\n---\n|\n(?=##)|$)', '', content, flags=re.DOTALL)

    if "## 📈 Project Progress" in content:
        content = content.replace("## 📈 Project Progress", research_section + "\n## 📈 Project Progress")
    
    # 6. Final Stats Update
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
    
    print(f"README updated with dividers and {len(completed_ids)} audio links.")

if __name__ == "__main__":
    update_readme()