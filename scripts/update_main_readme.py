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

    # 3. Strip existing dividers and old sections to rebuild
    content = re.sub(r'\n---\n', '\n', content)

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

    # 4. Update Table Links in Progress
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

    # 5. Legend Section with HTML Entity for Pipes
    # We use &#124; because a literal | breaks table columns in Markdown
    legend_section = r"""## ⌨️ Transcription Notation Legend
To maintain consistency across the archive, the following notations are used to indicate audio quality, speaker behavior, and transcription confidence:

| Notation | Description |
| :--- | :--- |
| `<text>` | Low confidence due to poor audio quality or group disagreement |
| `<<text>>` | Very low confidence due to extremely poor audio quality |
| `tex(t)` | Part of the word was not heard or dropped from speech |
| `[text]` | Transcriber’s notes or standard Grand Ronde (GR) spelling for non-standard pronunciation |
| `{text}` | English word used within Chinuk-Wawa speech |
| `<...>` | Unknown word(s) or voiced sound(s) |
| `text/` | Pause in speech following the word |
| `<text A/text B>` | Ambiguous; group members hear either A or B in even numbers |
| `&#124;text&#124;` | Pronunciation deviates significantly from GR dictionary variants |
| `..` | Hesitation or stutter |"""

    # 6. Build Research Section
    research_section = f"""## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs."""

    # 7. Reassemble with dividers
    sections = [intro, overview, structure, how_to, legend_section, research_section, progress, contributing]
    new_content = "\n\n---\n\n".join([s for s in sections if s])

    # 8. Update stats and Save
    new_content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {len(completed_ids)}/30', new_content)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content.strip() + "\n")
    
    print("README updated: Legend pipe formatting fixed using HTML entities.")

if __name__ == "__main__":
    update_readme()