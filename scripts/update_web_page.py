import csv
import os

def generate_index_html():
    csv_path = 'metadata/master_transcription_list.csv'
    html_output = 'docs/index.html'
    
    if not os.path.exists(csv_path):
        print("Error: Master CSV not found.")
        return

    # Get unique IDs from the CSV
    completed_ids = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ID'] not in completed_ids:
                completed_ids.append(row['ID'])

    # HTML Header & Style
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joe Peter Project Archive</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f4f4f4; }
        header { background: #8c1b1b; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 5px solid #8c1b1b; }
        .btn { display: inline-block; background: #8c1b1b; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; margin-top: 10px; font-size: 0.85rem; }
        .btn:hover { background: #5a1111; }
        h3 { margin-top: 0; }
    </style>
</head>
<body>
<header>
    <h1>Joe Peter Project Archive</h1>
    <p>1941 Chinook Jargon Transcription Collection</p>
</header>
<div class="grid">"""

    # Add a card for every ID found in the CSV
    for cid in completed_ids:
        html_content += f"""
    <div class="card">
        <h3>Recording {cid}</h3>
        <p>Digitized transcription of 1941 metal disc recordings.</p>
        <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/exports/markdown/{cid}_Reading_Guide.md">View Online</a>
        <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/raw/main/exports/pdfs/{cid}_Reading_Guide.pdf">Download PDF</a>
        <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/raw/main/exports/word-docs/{cid}_Reading_Guide.docx">Word Doc</a>
    </div>"""

    html_content += """
</div>
<footer>
    <p style="text-align:center; margin-top:40px; color:#666;">&copy; 2026 Joe Peter Project Archive</p>
</footer>
</body>
</html>"""

    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Web page updated with {len(completed_ids)} recordings.")

if __name__ == "__main__":
    generate_index_html()