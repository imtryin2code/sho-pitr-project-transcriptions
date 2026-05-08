import csv
import json
import os
import re

def generate_index_html():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    variation_path = 'exports/markdown/Dialect_Variation_Report.md'
    notes_path = 'exports/markdown/Research_Observations_Log.md'
    html_output = 'docs/index.html'
    
    # 1. Load Data
    completed_ids = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID'] not in completed_ids:
                    completed_ids.append(row['ID'])

    glossary = {}
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            glossary = json.load(f)

    dict_word_count = len([w for w, d in glossary.items() if d['count'] > 0])

    sorted_by_freq = sorted(
        [item for item in glossary.items() if item[1]['count'] > 0],
        key=lambda x: x[1]['count'],
        reverse=True
    )[:10]

    variation_count = 0
    if os.path.exists(variation_path):
        with open(variation_path, 'r', encoding='utf-8') as f:
            variation_count = len([l for l in f.readlines() if l.startswith('| 6')])

    notes_count = 0
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_count = len(re.findall(r'^- \*\*', f.read(), re.MULTILINE))

    # 2. HTML HEADER & STYLES
    html_start = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joe Peter Project Archive</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f4f4f4; scroll-behavior: smooth; }}
        header {{ background: #8c1b1b; color: white; padding: 40px 20px; border-radius: 8px 8px 0 0; text-align: center; position: relative; }}
        .repo-link {{ position: absolute; top: 10px; right: 20px; color: white; text-decoration: none; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.4); padding: 5px 10px; border-radius: 4px; }}
        
        nav {{ background: #333; color: white; padding: 12px; text-align: center; border-radius: 0 0 8px 8px; margin-bottom: 30px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        nav a {{ color: white; text-decoration: none; margin: 0 15px; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
        nav a:hover {{ color: #ffcccb; }}

        .section {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        h2 {{ color: #8c1b1b; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 5px solid #8c1b1b; }}
        .btn {{ display: inline-block; background: #8c1b1b; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; font-size: 0.85rem; font-weight: bold; margin-top: 10px; }}
        
        .history-grid, .research-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }}
        .history-card {{ background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #eee; border-left: 5px solid #8c1b1b; }}
        .research-card {{ background: #fff5f5; padding: 20px; border-radius: 8px; border: 1px solid #ffcccc; text-align: center; }}
        .stat-number {{ display: block; font-size: 2.5rem; font-weight: bold; color: #8c1b1b; }}

        .spotlight-container {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0 25px 0; }}
        .spotlight-card {{ background: #8c1b1b; color: white; padding: 8px 18px; border-radius: 50px; font-size: 0.85rem; font-weight: bold; }}
        .dict-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
        .dict-card {{ background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 6px; }}
        .occ-link {{ display: inline-block; font-size: 0.7rem; background: #f8f8f8; padding: 2px 5px; margin: 2px; border-radius: 3px; text-decoration: none; color: #555; border: 1px solid #ccc; }}
        .occ-link:hover {{ background: #8c1b1b; color: white; }}
    </style>
</head>
<body>
<header>
    <a class="repo-link" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions">← Back to GitHub Repo</a>
    <h1>Joe Peter Project Archive</h1>
    <p>1941 Chinook Jargon Transcriptions of Joe Peter and Jack Marr</p>
</header>

<nav>
    <a href="#mission">Mission</a>
    <a href="#history">History & Hardware</a>
    <a href="#research">Research Insights</a>
    <a href="#gallery">Gallery</a>
    <a href="#dictionary">Dictionary</a>
</nav>

<div id="mission" class="section">
    <h2>Our Mission & Revitalization</h2>
    <p>Our mission as a group is to listen to all of the <strong>30 recordings totaling 10 hours</strong> and transcribe as much as possible with the knowledge and technology we have available to us. By doing so, we ensure the language knowledge held within them is available to teach and research from, aiding in the <strong>continuation of Chinuk Wawa (Chinook Jargon)</strong>.</p>
    <a class="btn" style="background:#2c3e50;" href="https://tilixam.com/wp-content/uploads/2024/10/icsnl59_jpctp_final.pdf" target="_blank">📖 Read our Published UBC Paper</a>
</div>

<div id="history" class="section">
    <h2>History & Hardware</h2>
    <div class="history-grid">
        <div class="history-card">
            <h3>Fairchild Disc Recorder</h3>
            <p>16-year-old Jack Marr utilized a heavy-duty portable disc recorder—identified in archival records as a <strong>Fairchild</strong>—to cut direct-to-disc recordings on bare aluminum.</p>
        </div>
        <div class="history-card">
            <h3>The Discovery</h3>
            <p>Originally seeking "Pure Chinook," the project instead captured 10 hours of high-level Chinook Jargon, preserving a unique dialect and a snapshot of fluent 1941 speech.</p>
        </div>
        <div class="history-card">
            <h3>J.P. Harrington Collection</h3>
            <p>Part of the Smithsonian's extensive J.P. Harrington papers, these recordings were brought to light through modern linguistic scholarship and community collaboration.</p>
        </div>
    </div>
</div>

<div id="research" class="section">
    <h2>Research Data Stats</h2>
    <div class="research-grid">
        <div class="research-card">
            <span class="stat-number">{notes_count}</span>
            <strong>Linguistic Observations</strong>
            <p><small>Detailed notes on grammar and syntax.</small></p>
            <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/exports/markdown/Research_Observations_Log.md">View Log</a>
        </div>
        <div class="research-card">
            <span class="stat-number">{variation_count}</span>
            <strong>Dialect Variations</strong>
            <p><small>Instances of unique pronunciation.</small></p>
            <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/exports/markdown/Dialect_Variation_Report.md">View Report</a>
        </div>
        <div class="research-card">
            <span class="stat-number">{dict_word_count}</span>
            <strong>Unique Terms</strong>
            <p><small>Recorded in our living dictionary.</small></p>
            <a class="btn" href="#dictionary">Go to Dictionary</a>
        </div>
    </div>
</div>

<div id="gallery" class="section" style="background:transparent; box-shadow:none; padding:0;">
    <h2>Transcription Gallery</h2>
    <div class="grid">"""

    # [Rest of the dynamic card generation and dictionary logic remains the same]
    html_cards = ""
    for cid in completed_ids:
        html_cards += f"""
        <div class="card">
            <h3>Recording {cid}</h3>
            <p>Digitized transcription of 1941 metal disc recordings.</p>
            <div style="display:flex; gap:10px;">
                <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/exports/markdown/{cid}_Reading_Guide.md">View Online</a>
                <a class="btn" style="background:#444;" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/raw/main/exports/pdfs/{cid}_Reading_Guide.pdf">PDF</a>
            </div>
        </div>"""

    html_dict_start = f"""
    </div>
</div>

<div id="dictionary" class="section">
    <h2>Chinuk Wawa Dictionary & Concordance</h2>
    <p style="margin-bottom:5px; font-weight:bold; font-size:0.9rem; color:#666;">🔥 TOP 10 FREQUENT WORDS</p>
    <div class="spotlight-container">"""
    
    for word, data in sorted_by_freq:
        html_dict_start += f'<div class="spotlight-card">{word} ({data["count"]}x)</div>'
    
    html_dict_start += """
    </div>
    <div class="dict-grid">"""

    html_dict_cards = ""
    for word, data in glossary.items():
        if data['count'] > 0:
            occ_links = "".join([
                f'<a class="occ-link" href="{o["url"]}" target="_blank">{o["id"]}@{o["time"]}</a>' 
                for o in data['occurrences']
            ])
            html_dict_cards += f"""
        <div class="dict-card">
            <strong style="color:#8c1b1b;">{word}</strong> <small style="color:#999;">({data['count']})</small>
            <p style="margin: 5px 0; font-size: 0.85rem; color:#444;">{data['definition']}</p>
            <div style="margin-top:8px;">{occ_links}</div>
        </div>"""

    html_end = """
    </div>
</div>

<footer>
    <p style="text-align:center; margin:50px 0 20px 0; color:#777; border-top: 1px solid #ddd; padding-top: 20px;">
        &copy; 2026 Joe Peter Project Team. Powered by the J.P. Harrington Collection.
    </p>
</footer>
</body>
</html>"""

    full_html = html_start + html_cards + html_dict_start + html_dict_cards + html_end
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Success: index.html updated. History restored and Top 10 spotlight active.")

if __name__ == "__main__":
    generate_index_html()