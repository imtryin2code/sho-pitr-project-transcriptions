import csv
import json
import os

def generate_index_html():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    html_output = 'docs/index.html'
    
    # 1. Load Recording IDs for the Gallery
    completed_ids = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID'] not in completed_ids:
                    completed_ids.append(row['ID'])

    # 2. Load Glossary for the Dictionary
    glossary = {}
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            glossary = json.load(f)

    # 3. HTML Header & Mission
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joe Peter Project Archive</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f4f4f4; }
        header { background: #8c1b1b; color: white; padding: 40px 20px; border-radius: 8px; margin-bottom: 30px; text-align: center; position: relative; }
        .repo-link { position: absolute; top: 10px; right: 20px; color: white; text-decoration: none; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.4); padding: 5px 10px; border-radius: 4px; }
        .section { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        h2 { color: #8c1b1b; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 5px solid #8c1b1b; }
        .btn { display: inline-block; background: #8c1b1b; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 0.8rem; font-weight: bold; margin-top: 10px; }
        .dict-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        .dict-card { background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 6px; }
        .occ-link { display: inline-block; font-size: 0.7rem; background: #f0f0f0; padding: 2px 6px; margin: 2px; border-radius: 3px; text-decoration: none; color: #555; border: 1px solid #ddd; }
        .occ-link:hover { background: #e0e0e0; color: #000; }
        .tag { background: #eee; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; color: #666; }
    </style>
</head>
<body>
<header>
    <a class="repo-link" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions">← Back to GitHub Repo</a>
    <h1>Joe Peter Project Archive</h1>
    <p>1941 Chinook Jargon Transcriptions • Joe Peter & Jack Marr</p>
</header>

<div class="section">
    <h2>Mission & Research</h2>
    <p>This archive supports <strong>Chinuk Wawa</strong> revitalization by digitizing the 1941 field recordings of Joe Peter. Our team uses time-aligned transcription methods to preserve the authentic speech and cadence of these historical records.</p>
    <a class="btn" style="background:#2c3e50;" href="https://tilixam.com/wp-content/uploads/2024/10/icsnl59_jpctp_final.pdf" target="_blank">📖 Read the UBC Paper (ICSNL 59)</a>
</div>

<div class="section">
    <h2>Chinuk Wawa Dictionary & Concordance</h2>
    <p>Click a recording ID to view the specific line in the [Master Transcription List](https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/metadata/master_transcription_list.csv).</p>
    <div class="dict-grid">
"""

    # 4. Generate Dictionary Cards
    for word, data in glossary.items():
        if data['count'] > 0:
            occ_links = "".join([
                f'<a class="occ-link" href="{o["url"]}" target="_blank">{o["id"]} @ {o["time"]}</a>' 
                for o in data['occurrences']
            ])
            
            html_content += f"""
        <div class="dict-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:#8c1b1b; font-size:1.2rem;">{word}</strong>
                <span class="tag">Used {data['count']}x</span>
            </div>
            <p style="margin: 8px 0; font-size: 0.9rem; color: #444;">{data['definition']}</p>
            <div style="margin-top:10px;">{occ_links}</div>
        </div>"""

    html_content += """
    </div>
</div>

<div class="section" style="background:transparent; box-shadow:none; padding:0;">
    <h2>Transcription Gallery</h2>
    <div class="grid">
"""

    # 5. Generate Gallery Cards
    for cid in completed_ids:
        html_content += f"""
        <div class="card">
            <h3>Recording {cid}</h3>
            <p style="font-size:0.9rem; color:#666;">Digitized from 1941 Presto aluminum discs.</p>
            <div style="display:flex; gap:5px;">
                <a class="btn" style="flex:1;" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/exports/markdown/{cid}_Reading_Guide.md">View</a>
                <a class="btn" style="flex:1; background:#444;" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/raw/main/exports/pdfs/{cid}_Reading_Guide.pdf">PDF</a>
            </div>
        </div>"""

    html_content += """
    </div>
</div>

<footer>
    <p style="text-align:center; margin-top:50px; color:#777; border-top: 1px solid #ddd; padding-top: 20px;">
        &copy; 2026 Joe Peter Project Team. Original recordings curated by John Peabody Harrington.
    </p>
</footer>
</body>
</html>"""

    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Success: Updated {html_output} with dictionary and gallery.")

if __name__ == "__main__":
    generate_index_html()