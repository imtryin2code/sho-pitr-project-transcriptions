import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    audio_dir = 'audio-previews'
    
    # 1. Gather Completed IDs from CSV
    completed_ids = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Extract unique IDs from the first column
            completed_ids = list(set(line.split(',')[0].strip() for line in lines[1:] if line.strip()))
    
    # 2. Gather Research Note Count
    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 3. Read current README
    if not os.path.exists(readme_path):
        print("README.md not found.")
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        # Detect Table Rows by checking for multiple pipes
        if line.count('|') >= 4 and not line.strip().startswith('| ---'):
            cells = line.split('|')
            # The Recording ID is in the second cell (index 1)
            raw_content = cells[1].strip()
            # Strip markdown formatting like * or ` to get the clean ID
            clean_id = re.sub(r'[*`_]', '', raw_content)

            if clean_id in completed_ids:
                mp3_filename = f"{clean_id}.mp3"
                # Check if the mp3 actually exists in the previews folder
                if os.path.exists(os.path.join(audio_dir, mp3_filename)):
                    # Update cell with a link to the audio preview
                    cells[1] = f" [{clean_id}](./{audio_dir}/{mp3_filename}) "
                else:
                    cells[1] = f" {clean_id} "
            
            line = "|".join(cells)
        
        updated_lines.append(line)

    content = "".join(updated_lines)
    
    # 4. Update Research & Stats Sections
    research_section = f"""
## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.
"""
    # Replace old research section if it exists, otherwise insert before Progress
    if "## 🔬 Research & Observations" in content:
        content = re.sub(r'## 🔬 Research & Observations.*?(\n(?=##)|$)', research_section + "\n", content, flags=re.DOTALL)
    
    # Update Current Completion count
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', content)

    # 5. Save Changes
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"README updated: Linked {len(completed_ids)} IDs to audio previews.")

if __name__ == "__main__":
    update_readme()