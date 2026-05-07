import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    
    # 1. Gather Stats
    completed_count = 0
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Count unique IDs skipping header
            unique_ids = set(line.split(',')[0] for line in lines[1:] if line.strip())
            completed_count = len(unique_ids)

    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 2. Read current README
    if not os.path.exists(readme_path):
        print("README.md not found.")
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. Update Repository Structure Section
    if "Research_Observations_Log.md" not in content:
        content = content.replace(
            "├── exports/", 
            "├── exports/\n│   ├── Research_Observations_Log.md  <-- 🔬 Auto-generated research insights"
        )

    # 4. Prepare the Research Section
    research_section = f"""
## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.
"""

    # 5. Clean up old instances of the Research section to avoid duplicates
    content = re.sub(r'## 🔬 Research & Observations.*?(\n(?=##)|$)', '', content, flags=re.DOTALL)

    # 6. Insert Research section BEFORE Project Progress
    if "## 📈 Project Progress" in content:
        content = content.replace("## 📈 Project Progress", research_section + "\n## 📈 Project Progress")
    else:
        # Fallback if progress section isn't found
        content += research_section

    # 7. Update Completion Count
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {completed_count}/30', content)

    # 8. Write back to README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
    
    print(f"README updated: Research section moved above Progress. Stats: {completed_count} recordings, {notes_count} notes.")

if __name__ == "__main__":
    update_readme()