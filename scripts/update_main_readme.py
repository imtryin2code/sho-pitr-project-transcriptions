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
    if not os.path.exists(readme_path): return
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. Step 1: Strip ALL existing horizontal rules to prevent stacking
    content = re.sub(r'\n---\n', '\n', content)

    # 4. Step 2: Define our clean sections
    # We will split the content by headers to rebuild it
    def get_section(header_name, full_text):
        pattern = rf"## {header_name}.*?(?=\n## |$)"
        match = re.search(pattern, full_text, re.DOTALL)
        return match.group(0).strip() if match else ""

    intro = content.split('## ')[0].strip()
    overview = get_section("📜 Project Overview", content)
    structure = get_section("📂 Repository Structure", content)
    how_to = get_section("🛠 How to Use This Archive", content)
    progress = get_section("📈 Project Progress", content)
    contributing = get_section("🤝 Contributing", content)

    # 5. Step 3: Update Table Links in the Progress section
    progress_lines = progress.split('\n')
    updated_progress_lines = []
    for line in progress_lines:
        if line.count('|') >= 4 and not line.strip().startswith('| ---'):
            cells = line.split('|')
            raw_id = re.sub(r'[*`_\[\]\(\)]', '', cells[1]).strip()
            if raw_id in completed_ids:
                link = f"https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/{audio_dir}/{raw_id}.mp3"
                cells[1] = f" [{raw_id}]({link}) "
            line = "|".join(cells)
        updated_progress_lines.append(line)
    progress = "\n".join(updated_progress_lines)

    # 6. Step 4: Build the Research Section
    research_section = f"""## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs."""

    # 7. Step 5: Assemble the "Sandwich" with dividers between EVERY section
    sections = [intro, overview, structure, how_to, research_section, progress, contributing]
    # Filter out any empty strings and join with a divider
    new_content = "\n\n---\n\n".join([s for s in sections if s])

    # 8. Step 6: Update final stats
    new_content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', new_content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content.strip() + "\n")
    
    print(f"README updated with universal dividers. Links: {len(completed_ids)}, Notes: {notes_count}")

if __name__ == "__main__":
    update_readme()