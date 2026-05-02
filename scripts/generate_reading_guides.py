import csv
import os

def generate_guides():
    csv_path = 'metadata/master_transcription_list.csv'
    output_base = 'exports'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV not found. Run extract_transcriptions.py first.")
        return

    # Grouping data by ID (e.g., 682-S1)
    stories = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            story_id = row['ID']
            if story_id not in stories:
                stories[story_id] = []
            stories[story_id].append(row)

    for story_id, rows in stories.items():
        # Create a readable Markdown file
        md_filename = f"{story_id}_Reading_Guide.md"
        md_path = os.path.join(output_base, md_filename)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Reading Guide: {story_id}\n")
            f.write(f"**Source:** 1941 Metal Disc Recording\n")
            f.write(f"**Participants:** Jack Marr (English) & Joe Peter (Chinook Jargon)\n\n")
            f.write("| Time | Speaker | Text |\n")
            f.write("| :--- | :--- | :--- |\n")
            
            for row in rows:
                # Bold Joe Peter's lines to make them stand out
                text = row['Text']
                if "Joe" in row['Speaker'] or "Peter" in row['Speaker']:
                    text = f"**{text}**"
                
                f.write(f"| {row['Time']} | {row['Speaker']} | {text} |\n")
        
        print(f"Generated guide for {story_id} in {output_base}")

if __name__ == "__main__":
    generate_guides()