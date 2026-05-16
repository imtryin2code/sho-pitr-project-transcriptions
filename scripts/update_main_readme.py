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
    
    # 2. Count Research Notes (Robust Dynamic Counting)
    # Counts active data rows inside the generated Markdown tables, skipping header structural elements
    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Count lines that start with a table bar, but aren't headers or dividers
                if line.strip().startswith('|') and not any(k in line for k in ['Source ID', ':---', '---:']):
                    # Ensure it's not an empty placeholder line
                    if '_No entries recorded_' not in line:
                        notes_count += 1

    # 3. Count Dialect Variations
    # Dynamically reads table lines from the standalone variation report
    variation_count = 0
    if os.path.exists(variation_path):
        with open(variation_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('|') and not any(k in line for k in ['Recording ID', ':---', '---:', 'Total Variations']):
                    # Check that it isn't the fallback empty line
                    if '| - | - |' not in line:
                        variation_count += 1

    if not os.path.exists(readme_path): 
        print(f"Error: {readme_path} not found.")
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean out all existing dividers
    content = re.sub(r'\n+---\n+', '\n\n', content)

    def get_section(header_name, full_text):
        pattern = rf"## {header_name}.*?(?=\n## |$)"
        match = re.search(pattern, full_text, re.DOTALL)
        return match.group(0).strip() if match else ""

    # 4. Dashboard
    dashboard = f"""# Joe Peter Project: 1941 Chinook Jargon Transcriptions

> ### 🌐 [Explore the Interactive Archive & Dictionary](https://imtryin2code.github.io/sho-pitr-project-transcriptions/)
> **The Project Web Page** provides a searchable dictionary, live frequency counts of Joe Peter's vocabulary, and formatted reading guides. It is the primary interface for this archive.

- **Current Progress:** {len(completed_ids)}/30 recordings transcribed.
- **Project History:** 3 years of active transcription completed.
- **Estimated Completion:** 2032 (Approx. 6 years remaining)."""

    overview = get_section("📜 Project Overview", content)
    structure = get_section("📂 Repository Structure", content)
    how_to = get_section("🛠 How to Use This Archive", content)
    progress = get_section("📈 Project Progress", content)
    contributing = get_section("🤝 Contributing", content)

    # 5. Update Table Links in Progress
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

    # 6. Primary Dialogue Legend Section (Updated and Refined)
    legend_section = r"""## ⌨️ Transcription Notation Legend
To maintain consistency across the archive, the following notations are used to indicate audio quality, speaker behavior, and transcription confidence within the **primary transcription lines**:

| Notation | Description |
| :--- | :--- |
| `<text>` | Low confidence due to poor audio quality or group disagreement |
| `<<text>>` | Very low confidence due to extremely poor audio quality |
| `tex(t)` | Part of the word was not heard or dropped from speech |
| `{text}` | English word used within Chinuk-Wawa speech |
| `{{text}}` | English word(s) spoken by Joe Peter in conversation with Jack Marr |
| `<...>` | Unknown word(s) or voiced sound(s) |
| `text/` | Pause in speech following the word |
| `<text A/text B>` | Ambiguous; group members hear either A or B in even numbers |
| `..` | Hesitation or stutter |

### 🔍 Research Notes Categories & Bracket Structural Rules
The parsing engine reads the `Notes_Text` fields directly, sorting entries dynamically into specialized tracking files using these exact bracketed identifiers and syntax wrappers:

| Tag Indicator | Associated Category / Structural Rule | Core Purpose |
| :--- | :--- | :--- |
| `[LING]` | 🗣️ Linguistic & Phonetic Observations | Tracks shifts in pronunciation, phonetic deviations, and grammar logs. |
| `[HIST]` | 📜 Cultural & Historical Context Logs | Captures background context, historical references, and community anecdotes. |
| `[INFO]` | 💡 General Informational Notes | General observations, track metadata markers, or structural explanations. |
| `[TEX]` | 🎓 Exemplary Teaching Examples | Highlights excellent data segments optimized for language learning materials. |
| `[VEX]` | 🎵 High-Quality Vocalization Examples | Isolates distinct vocal inflections, expressions, or exceptional audio clarity. |
| `[OTL]` | 🌐 Other Languages Utilized | Notes where English, Marr, or outside linguistic fragments overlap text segments. |
| `[NOTE]` | 📝 Workspace Footnotes & Comments | General internal commentary, alignment flags, or raw project reminders. |
| `[?]` / `[UNCERTAIN]` | ❓ Uncertain Segments Requiring Review | Flags questionable translations or unclear phonetics requiring peer review. |
| `\|text\|` | Phonetic Deviation Indicator | Applied inside notes to isolate specific speech variants from standard dictionary records. |
| `[[text]]` | Standard GR Spelling Variant | Applied inside notes to link non-standard pronunciations back to standard Grand Ronde spellings. |"""

    # 7. Research Section
    research_section = f"""## 🔬 Research & Observations
- **Active Insights:** {notes_count} specific linguistic observations.
- **Dialect Variations:** {variation_count} identified pronunciation patterns.
- **Logs:** [Research Log](./exports/markdown/Research_Observations_Log.md) | [Variation Report](./exports/markdown/Dialect_Variation_Report.md)"""

    # 8. Tools & Citation Section
    tools_section = r"""## 🛠 Tools & Citation
All transcriptions in this archive are created and managed using [ELAN](https://archive.mpi.nl/tla/elan), developed by the Max Planck Institute for Psycholinguistics.

**To cite the software used in this project:**
> ELAN (Version 7.1) [Computer software]. (2026). Nijmegen: Max Planck Institute for Psycholinguistics. Retrieved from https://archive.mpi.nl/tla/elan"""

    # 9. Reassemble
    sections = [
        dashboard, 
        overview, 
        structure, 
        how_to, 
        legend_section, 
        research_section, 
        tools_section,
        progress, 
        contributing
    ]
    
    new_content = "\n\n---\n\n".join([s for s in sections if s.strip()])

    with open(readme_path, 'w', newline='', encoding='utf-8') as f:
        f.write(new_content.strip() + "\n")
    
    print(f"README updated successfully: Recalculated dynamic index values based on generated Markdown tables.")

if __name__ == "__main__":
    update_readme()