import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    audio_dir = 'audio-previews'
    
    # 1. Gather Stats & Audio Availability
    completed_ids = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            completed_ids = list(set(line.split(',')[0] for line in lines[1:] if line.strip()))
    
    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 2. Read current README
    if not os.path.exists(readme_path):
        print("README.md not found.")
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    in_table = False

    for line in lines:
        # Detect Table Rows (Example: | *682-S1* | ... |)
        if line.strip().startswith('|') and not line.strip().startswith('| ---'):
            cells = [c.strip() for c in line.split('|')]
            if len(cells) > 2:
                # Extract the ID (cleaning out existing markdown links or bolding)
                raw_id = re.sub(r'[\*\[\]\(\)]', '', cells[1]).split('/')[-1].strip()
                
                if raw_id in completed_ids:
                    # Check for MP3 link (GitHub Pages style or relative path)
                    mp3_filename = f"{raw_id}.mp3"
                    mp3_path = os.path.join(audio_dir, mp3_filename)
                    
                    if os.path.exists(mp3_path):
                        # Create the link on the ID
                        # Using relative path so it works on both GitHub and the Web Page
                        cells[1] = f"[*[{raw_id}]*](./audio-previews/{mp3_filename})"
                    else:
                        cells[1] = f"*{raw_id}*"
                
                line = " | ".join(cells) + "\n"
        
        updated_lines.append(line)

    # 3. Handle Research & Progress Section Updates
    content = "".join(updated_lines)
    
    # Update Research Section
    research_section = f"""
## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.
"""
    content = re.sub(r'## 🔬 Research & Observations.*?(\n(?=##)|$)', research_section + "\n", content, flags=re.DOTALL)
    
    # Update Completion Text
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', content)

    # 4. Save Changes
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"README updated: Links added for {len(completed_ids)} recordings.")

if __name__ == "__main__":
    update_readme()