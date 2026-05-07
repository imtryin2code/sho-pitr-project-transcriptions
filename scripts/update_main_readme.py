import os
import re

def update_readme():
    readme_path = 'README.md'
    notes_path = 'exports/Research_Observations_Log.md'
    csv_path = 'metadata/master_transcription_list.csv'
    
    # 1. Basic Stats Gathering
    completed_count = 0
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Simple way to count unique IDs in the master list
            lines = f.readlines()
            unique_ids = set(line.split(',')[0] for line in lines[1:] if line.strip())
            completed_count = len(unique_ids)

    # 2. Research Notes Stats
    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            # Count the number of bullet points (observations)
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 3. Read current README
    if not os.path.exists(readme_path):
        print("README.md not found.")
        return
        
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. Update the Repository Structure Section
    struct_old = "├── exports/"
    struct_new = "├── exports/\n│   ├── Research_Observations_Log.md  <-- 🔬 Auto-generated research insights"
    if "Research_Observations_Log.md" not in content:
        content = content.replace(struct_old, struct_new)

    # 5. Update Progress Stats
    content = re.sub(r'Current Completion: \d+/30', f'Current Completion: {completed_count}/30', content)

    # 6. Add/Update Research Section
    research_section = f"""
## 🔬 Research & Observations
Our transcription process includes real-time tagging of linguistic and historical features.
- **Active Insights:** Currently tracking **{notes_count}** specific observations.
- **Access the Log:** Read the full [Research & Observations Log](./exports/Research_Observations_Log.md) for detailed notes on grammar, history, and peer-review needs.
"""
    
    if "## 🔬 Research & Observations" in content:
        content = re.sub(r'## 🔬 Research & Observations.*?(\n(?=##)|$)', research_section, content, flags=re.DOTALL)
    else:
        # Insert before Contributing
        content = content.replace("## 🤝 Contributing", research_section + "\n## 🤝 Contributing")

    # 7. Write back to README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"README updated: {completed_count}/30 recordings and {notes_count} research notes recorded.")

if __name__ == "__main__":
    update_readme()