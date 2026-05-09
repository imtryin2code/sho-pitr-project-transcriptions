import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/markdown/Research_Observations_Log.md'
    variation_path = 'exports/markdown/Dialect_Variation_Report.md'
    csv_path = 'metadata/master_transcription_list.csv'
    audio_dir = 'audio-previews'
    
    # 1. Gather Completion Stats
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

    # 3. Count Dialect Variations
    variation_count = 0
    if os.path.exists(variation_path):
        with open(variation_path, 'r', encoding='utf-8') as f:
            variation_count = len([l for l in f.readlines() if l.startswith('| 6')])

    # 4. Read current README
    if not os.path.exists(readme_path): return
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def get_section(header_name, full_text):
        pattern = rf"## {header_name}.*?(?=\n## |$)"
        match = re.search(pattern, full_text, re.DOTALL)
        return match.group(0).strip() if match else ""

    # 5. Build New Dynamic Intro/Dashboard
    # This replaces the old # sho-pitr-project-transcriptions header
    dashboard = f"""# Joe Peter Project: 1941 Chinook Jargon Transcriptions

> ### 🌐 [Explore the Interactive Archive & Dictionary](https://imtryin2code.github.io/sho-pitr-project-transcriptions/)
> **The Project Web Page** provides a searchable dictionary, live frequency counts of Joe Peter's vocabulary, and formatted reading guides for all completed transcriptions. It is the primary way to engage with the data collected in this repository.

Current Completion: **{len(completed_ids)}/30** recordings transcribed."""

    overview = get_section("📜 Project Overview", content)
    structure = get_section("📂 Repository Structure", content)
    how_to = get_section("🛠 How to Use This Archive", content)
    progress = get_section("📈 Project Progress", content)
    contributing = get_section("🤝 Contributing", content)

    # 6. Update Table Links in Progress
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

    # 7. Legend Section
    legend_section = r"""## ⌨️ Transcription Notation Legend
To maintain consistency across the archive, the following notations are used:

| Notation | Description |
| :--- | :--- |
| `<text>` | Low confidence due to poor audio quality |
| `[text]` | Transcriber’s notes or standard spelling for non-standard pronunciation |
| `{text}` | English word used within Chinuk-Wawa speech |
| `\|text\|` | Pronunciation deviates significantly from dictionary variants |
| `..` | Hesitation or stutter |"""

    # 8. Research Section
    research_section = f"""## 🔬 Research & Observations
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Dialect Variations:** Identified **{variation_count}** instances of Joe Peter's unique pronunciation patterns.
- **Access the Logs:** Read the [Research & Observations Log](./exports/markdown/Research_Observations_Log.md) or the [Dialect Variation Report](./exports/markdown/Dialect_Variation_Report.md)."""

    # 9. Reassemble (Dashboard replaces Intro)
    sections = [dashboard, overview, structure, how_to, legend_section, research_section, progress, contributing]
    
    # Filter out empty sections and join with horizontal rules
    new_content = "\n\n---\n\n".join([s for s in sections if s])

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content.strip() + "\n")
    
    print(f"README updated: New dashboard and project link added.")

if __name__ == "__main__":
    update_readme()