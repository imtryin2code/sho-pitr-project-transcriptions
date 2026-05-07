import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    # Use the folder name as it appears in your repo
    audio_dir = 'audio-previews'
    
    # 1. Gather Completed IDs from CSV
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

    # 3. Read and Update README
    if not os.path.exists(readme_path):
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        # Check if line is a table row with a Recording ID
        if line.count('|') >= 4 and not line.strip().startswith('| ---'):
            cells = line.split('|')
            # Clean the ID cell
            raw_content = cells[1].strip()
            clean_id = re.sub(r'[*`_]', '', raw_content)

            if clean_id in completed_ids:
                # We know the files exist in your repo under audio-previews/
                # We will force the link if it's in our completed list
                mp3_url = f"https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/{audio_dir}/{clean_id}.mp3"
                cells[1] = f" [{clean_id}]({mp3_url}) "
            
            line = "|".join(cells)
        
        updated_lines.append(line)

    content = "".join(updated_lines)
    
    # 4. Update Research & Completion Stats
    research_section = f"""
## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.
"""
    if "## 🔬 Research & Observations" in content:
        content = re.sub(r'## 🔬 Research & Observations.*?(\n(?=##)|$)', research_section + "\n", content, flags=re.DOTALL)
    
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated README with {len(completed_ids)} audio links.")

if __name__ == "__main__":
    update_readme()