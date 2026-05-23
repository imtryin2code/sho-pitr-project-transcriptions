import csv
import json
import os
import re
import html

def parse_elan_time(time_val):
    """Robustly parses ELAN time values into accurate float seconds."""
    if not time_val:
        return 0.0
    time_str = str(time_val).strip()
    if ':' in time_str:
        try:
            parts = time_str.split(':')
            if len(parts) == 2: # MM:SS.fff
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3: # HH:MM:SS.fff
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        except ValueError:
            pass
    try:
        numeric_val = float(time_str)
        if numeric_val > 36000 and '.' not in time_str:
            return numeric_val / 1000.0
        return numeric_val
    except ValueError:
        return 0.0

def clean_for_html(text):
    """Normalizes text content safely while preserving notation angle brackets for the UI."""
    if not text: return ""
    text = text.replace('|', '\\|')
    
    # Run standard HTML escaping first to protect everything else
    escaped = html.escape(text, quote=True)
    
    # Restore escaped angle brackets back to pure characters for the UI legend standard
    escaped = escaped.replace('&lt;', '<').replace('&gt;', '>')
    return escaped

def clean_for_data_attr(text):
    """Cleans text for safe placement inside HTML data attributes without breaking boundaries."""
    if not text: return ""
    # Strip quotes but allow the standard angle brackets to remain intact
    cleaned = text.replace('"', '').replace("'", "")
    return html.escape(cleaned, quote=True).replace('&lt;', '<').replace('&gt;', '>')

def generate_web_portal():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    
    html_output_main = 'docs/index.html'
    html_output_dict = 'docs/dictionary.html'
    html_output_obs = 'docs/observations.html'
    html_output_vars = 'docs/variations.html'
    
    os.makedirs('docs', exist_ok=True)

    # 1. PARSE INCOMING DATA METRICS & ROWS
    completed_ids = []
    raw_rows = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []
            for row in reader:
                raw_rows.append(row)
                rec_id = row.get('ID', '').strip()
                if rec_id and rec_id not in completed_ids:
                    completed_ids.append(rec_id)

    completed_ids.sort()

    glossary = {}
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            glossary = json.load(f)

    dict_word_count = len([w for w, d in glossary.items() if d.get('count', 0) > 0])
    sorted_by_freq = sorted(
        [item for item in glossary.items() if item[1].get('count', 0) > 0],
        key=lambda x: x[1]['count'],
        reverse=True
    )[:10]

    categories = {
        '[LING]': '🗣️ Linguistic Observations',
        '[HIST]': '📜 Cultural & Historical Logs',
        '[INFO]': '💡 Informational Notes',
        '[TEX]': '🎓 Teaching Examples',
        '[VEX]': '🎵 Vocalization Examples',
        '[OTL]': '🌐 Other Languages',
        '[NOTE]': '📝 Workspace Comments',
        '[UNCERTAIN]': '❓ Uncertain Segments'
    }
    
    observations_data = {tag: [] for tag in categories.keys()}
    observations_data['[UNCATEGORIZED]'] = []
    variations_data = []

    # Process segments using explicit ELAN boundaries
    for row in raw_rows:
        tier = row.get('Notes_Tier', '').strip()
        note = row.get('Notes_Text', '').strip()
        text = row.get('Text', '').strip()
        rec_id = row.get('ID', 'UNKNOWN').strip()
        speaker = row.get('Speaker', 'Unknown').strip()
        
        raw_start = row.get('Start Time', row.get('Time', '00:00')).strip()
        raw_end = row.get('End Time', '').strip()
        
        start_seconds = parse_elan_time(raw_start)
        
        if raw_end:
            end_seconds = parse_elan_time(raw_end)
            duration = max(0.1, end_seconds - start_seconds)
        else:
            duration = 6.0 

        if ':' in raw_start:
            display_time = raw_start
        else:
            mins = int(start_seconds) // 60
            secs = int(start_seconds) % 60
            display_time = f"{mins:02d}:{secs:02d}"

        matched_tag = None
        if '[?]' in note or '[UNCERTAIN]' in note or '[?]' in tier or '[UNCERTAIN]' in tier:
            matched_tag = '[UNCERTAIN]'
        else:
            for tag in categories.keys():
                if tag in note or tag in tier:
                    matched_tag = tag
                    break

        if not matched_tag and not note:
            continue

        actual_payload = note if note else text
        if not actual_payload:
            continue

        item = {
            'id': rec_id, 'time': display_time, 'speaker': speaker,
            'transcription': clean_for_html(text), 'note': clean_for_html(actual_payload),
            'transcription_raw': clean_for_data_attr(text), 'note_raw': clean_for_data_attr(actual_payload),
            'seconds': start_seconds, 'duration': duration
        }

        if matched_tag:
            observations_data[matched_tag].append(item)
        else:
            observations_data['[UNCATEGORIZED]'].append(item)

        # REVERTED TO NATIVE ARCHIVE NOTATIONS: Target explicit double bracket variations << >>
        if matched_tag in ['[LING]', '[UNCERTAIN]'] and ('|' in actual_payload or '<<' in actual_payload):
            clean_variant = "-"
            pipe_match = re.search(r'\|([^\|]+)\|', actual_payload)
            if pipe_match: clean_variant = pipe_match.group(1).strip()

            clean_gr = "-"
            gr_match = re.search(r'<<([^>]+)>>', actual_payload)
            if gr_match: clean_gr = gr_match.group(1).strip()

            variations_data.append({
                'id': rec_id, 'time': display_time, 'speaker': speaker,
                'transcription': clean_for_html(text),
                'variant': clean_for_html(clean_variant), 'gr_standard': clean_for_html(clean_gr),
                'raw_content': clean_for_html(actual_payload), 
                'transcription_raw': clean_for_data_attr(text),
                'variant_raw': clean_for_data_attr(clean_variant), 'gr_standard_raw': clean_for_data_attr(clean_gr),
                'raw_content_raw': clean_for_data_attr(actual_payload),
                'seconds': start_seconds, 'duration': duration
            })

    total_obs = sum(len(observations_data[c]) for c in observations_data)
    total_vars = len(variations_data)

    # 2. SHARED LAYOUT STYLES & NAV COMPONENT ENGINE
    shared_css = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f4f4f4; padding-bottom: 120px; }
    header { background: #8c1b1b; color: white; padding: 35px 20px; border-radius: 8px 8px 0 0; text-align: center; position: relative; }
    .repo-link { position: absolute; top: 15px; right: 20px; color: white; text-decoration: none; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.4); padding: 5px 12px; border-radius: 4px; }
    nav { background: #333; color: white; padding: 14px; text-align: center; border-radius: 0 0 8px 8px; margin-bottom: 30px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    nav a { color: white; text-decoration: none; margin: 0 15px; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    nav a:hover, nav a.active { color: #ffcccb; border-bottom: 2px solid #ffcccb; padding-bottom: 3px; }
    .section { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h2 { color: #8c1b1b; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
    .btn { display: inline-block; background: #8c1b1b; color: white; padding: 8px 14px; text-decoration: none; border-radius: 4px; font-size: 0.8rem; font-weight: bold; margin-top: 5px; cursor: pointer; border: none; }
    .btn:hover { background: #6b1414; }
    .search-container { margin: 20px 0; }
    .search-bar { width: 100%; padding: 14px 20px; border: 2px solid #eee; border-radius: 25px; font-size: 1rem; outline: none; box-sizing: border-box; transition: border-color 0.3s; }
    .search-bar:focus { border-color: #8c1b1b; }
    .audio-btn { background: #2c3e50; font-size: 0.75rem; padding: 4px 8px; border-radius: 3px; color: white; text-decoration: none; display: inline-block; font-weight: bold; cursor: pointer; border: none; }
    .audio-btn:hover { background: #1a252f; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.9rem; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #f8f9fa; color: #333; font-weight: bold; }
    tr.hidden { display: none !important; }
    tr:nth-child(even) { background-color: #fdfdfd; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
    
    .occ-links-container { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .occ-chip-wrapper { position: relative; display: inline-block; }
    .occ-link-btn { display: inline-block; font-size: 0.72rem; background: #f5f4ef; padding: 5px 9px; border-radius: 4px; text-decoration: none; color: #333; border: 1px solid #ddd; cursor: pointer; transition: background 0.15s; font-weight: 500; }
    .occ-link-btn:hover { background: #e0dbd3; border-color: #bbb; }
    .occ-class-lbl { color: #8c1b1b; font-style: italic; font-weight: bold; text-transform: lowercase; }
    
    .occ-popover { visibility: hidden; opacity: 0; position: absolute; bottom: 135%; left: 50%; transform: translateX(-50%); width: 290px; background: #1e1c1b; color: #fff; padding: 12px 14px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 10000; pointer-events: none; transition: opacity 0.2s, visibility 0.2s; font-size: 0.8rem; line-height: 1.4; }
    .occ-popover::after { content: ""; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border-width: 6px; border-style: solid; border-color: #1e1c1b transparent transparent transparent; }
    .occ-chip-wrapper:hover .occ-popover { visibility: visible; opacity: 1; }
    .popover-context-line { display: block; margin-bottom: 5px; color: #f4f4f4; font-style: normal; }
    .popover-hint { display: block; font-size: 0.68rem; color: #aaa; border-top: 1px solid #444; padding-top: 4px; margin-top: 4px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }

    #globalAudioPlayer { position: fixed; bottom: 0; left: 0; width: 100%; background: #222; color: white; padding: 15px 20px; box-shadow: 0 -3px 10px rgba(0,0,0,0.2); display: none; z-index: 9999; box-sizing: border-box; }
    .player-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px; }
    .player-info { font-size: 0.85rem; font-weight: bold; color: #ffcccb; }
    audio { outline: none; width: 400px; max-width: 100%; }
    """

    audio_dock_html = r"""
    <div id="globalAudioPlayer">
        <div class="player-inner">
            <div class="player-info" id="playerTrackInfo">Track: None</div>
            <audio id="html5AudioWidget" controls preload="auto"></audio>
            <button onclick="document.getElementById('globalAudioPlayer').style.display='none'" style="background:#555; color:white; border:none; padding:5px 10px; border-radius:3px; cursor:pointer; font-size:0.75rem;">✕ Close Bar</button>
        </div>
    </div>
    <script>
        let globalTimeUpdateListener = null;

        function getTrueAudioFilename(trackId) {
            let cleanId = trackId.trim();
            let match = cleanId.match(/^(\d+)-[sS](\d+)$/);
            if (match) {
                let trackNum = match[1].padStart(8, '0');
                let sideNum = match[2];
                return "sinaa_" + trackNum + "_side" + sideNum + ".mp3";
            }
            if (!cleanId.endsWith('.mp3')) {
                return cleanId + ".mp3";
            }
            return cleanId;
        }

        function triggerAudioFromElement(btnElement) {
            const trackId = btnElement.getAttribute('data-track');
            const startSeconds = btnElement.getAttribute('data-start');
            const durationSeconds = btnElement.getAttribute('data-duration');
            playAudioSnippet(trackId, startSeconds, durationSeconds);
        }

        function playAudioSnippet(trackId, startSeconds, durationSeconds) {
            const playerBar = document.getElementById('globalAudioPlayer');
            const audio = document.getElementById('html5AudioWidget');
            const infoText = document.getElementById('playerTrackInfo');
            
            const startTimeParsed = parseFloat(startSeconds);
            const durationTimeParsed = parseFloat(durationSeconds);
            
            const audioFile = getTrueAudioFilename(trackId);
            infoText.innerText = "Loading Track: " + audioFile + "...";
            playerBar.style.display = "block";
            
            if (globalTimeUpdateListener) {
                audio.removeEventListener('timeupdate', globalTimeUpdateListener);
                globalTimeUpdateListener = null;
            }
            
            let localPath = "audio-previews/" + audioFile;
            if (window.location.hostname.includes("github.io")) {
                localPath = "/sho-pitr-project-transcriptions/audio-previews/" + audioFile;
            } else if (window.location.pathname.includes("/docs/")) {
                localPath = "../audio-previews/" + audioFile;
            }
            
            audio.src = localPath;
            audio.load();
            
            audio.oncanplay = function() {
                audio.currentTime = startTimeParsed;
                let clipInfo = "Playing Track: " + trackId + " @ " + startTimeParsed.toFixed(2) + "s";
                
                if (durationTimeParsed && durationTimeParsed > 0) {
                    clipInfo += " [" + durationTimeParsed.toFixed(2) + "s Segment]";
                    const stopTargetTime = startTimeParsed + durationTimeParsed;
                    
                    globalTimeUpdateListener = function() {
                        if (audio.currentTime >= stopTargetTime) {
                            audio.pause();
                            audio.removeEventListener('timeupdate', globalTimeUpdateListener);
                            globalTimeUpdateListener = null;
                            infoText.innerText = "Track: " + trackId + " (Segment Finished)";
                        }
                    };
                    audio.addEventListener('timeupdate', globalTimeUpdateListener);
                }
                
                infoText.innerText = clipInfo;
                audio.play().catch(function(err) {
                    console.log("Context baseline handled:", err);
                });
                audio.oncanplay = null;
            };

            audio.onerror = function() {
                if (globalTimeUpdateListener) {
                    audio.removeEventListener('timeupdate', globalTimeUpdateListener);
                    globalTimeUpdateListener = null;
                }
                
                audio.src = "https://raw.githubusercontent.com/imtryin2code/sho-pitr-project-transcriptions/main/audio-previews/" + audioFile;
                audio.load();
                audio.oncanplay = function() {
                    audio.currentTime = startTimeParsed;
                    let clipInfo = "Playing Track: " + trackId + " (Remote) @ " + startTimeParsed.toFixed(2) + "s";
                    
                    if (durationTimeParsed && durationTimeParsed > 0) {
                        clipInfo += " [" + durationTimeParsed.toFixed(2) + "s Segment]";
                        const stopTargetTime = startTimeParsed + durationTimeParsed;
                        
                        globalTimeUpdateListener = function() {
                            if (audio.currentTime >= stopTargetTime) {
                                audio.pause();
                                audio.removeEventListener('timeupdate', globalTimeUpdateListener);
                                globalTimeUpdateListener = null;
                                infoText.innerText = "Track: " + trackId + " (Segment Finished)";
                            }
                        };
                        audio.addEventListener('timeupdate', globalTimeUpdateListener);
                    }
                    
                    infoText.innerText = clipInfo;
                    audio.play();
                    audio.oncanplay = null;
                };
                audio.onerror = null;
            };
        }
    </script>
    """

    def generate_nav(active_page):
        return f"""
        <nav>
            <a href="index.html" class="{"active" if active_page == "home" else ""}">🏠 Dashboard</a>
            <a href="dictionary.html" class="{"active" if active_page == "dict" else ""}">📕 Dictionary ({dict_word_count})</a>
            <a href="observations.html" class="{"active" if active_page == "obs" else ""}">🔬 Research Logs ({total_obs})</a>
            <a href="variations.html" class="{"active" if active_page == "vars" else ""}">🔊 Variations ({total_vars})</a>
        </nav>
        """

    # =========================================================
    # PAGE BUILD 1: INDEX.HTML
    # =========================================================
    html_cards = "".join([f"""
        <div style="background:white; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); border-top:5px solid #8c1b1b;">
            <h3>Recording {cid}</h3>
            <p>Digitized transcription of 1941 metal disc recordings.</p>
            <div style="display:flex; gap:10px;">
                <a class="btn" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/exports/markdown/{cid}_Reading_Guide.md" target="_blank">View Guide</a>
                <button class="btn" style="background:#444;" data-track="{cid}" data-start="0" data-duration="0" onclick="triggerAudioFromElement(this)">🎚️ Play Audio</button>
            </div>
        </div>""" for cid in completed_ids])

    index_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>Joe Peter Project Archive</title>
        <style>{shared_css}</style>
    </head>
    <body>
    <header>
        <a class="repo-link" href="https://github.com/imtryin2code/sho-pitr-project-transcriptions">← GitHub Repo</a>
        <h1>Joe Peter Project Archive</h1>
        <p>1941 Chinook Jargon Transcriptions of Joe Peter and Jack Marr</p>
    </header>
    {generate_nav("home")}
    
    <div class="section">
        <h2>Our Mission & Revitalization</h2>
        <p>Our mission as a group is to listen to all of the <strong>30 recordings totaling 10 hours</strong> and transcribe as much as possible with the knowledge and technology we have available to us. By doing so, we ensure the language knowledge held within them is available to teach and research from, aiding in the <strong>continuation of Chinuk Wawa (Chinook Jargon)</strong>.</p>
        <a class="btn" href="https://tilixam.com/wp-content/uploads/2024/10/icsnl59_jpctp_final.pdf" target="_blank">📖 Read our Published UBC Paper</a>
    </div>

    <div class="section">
        <h2>History & Hardware</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:20px; margin-top:15px;">
            <div style="background:#fff; padding:20px; border-radius:8px; border:1px solid #eee; border-left:5px solid #8c1b1b;">
                <h3>Fairchild Disc Recorder</h3>
                <p>16-year-old Jack Marr utilized a heavy-duty portable disc recorder—identified in archival records as a <strong>Fairchild</strong>—to cut direct-to-disc recordings on bare aluminum.</p>
            </div>
            <div style="background:#fff; padding:20px; border-radius:8px; border:1px solid #eee; border-left:5px solid #8c1b1b;">
                <h3>The Discovery</h3>
                <p>Originally seeking "Pure Chinook," the project instead captured 10 hours of high-level Chinook Jargon, preserving a unique dialect and a snapshot of fluent 1941 speech.</p>
            </div>
            <div style="background:#fff; padding:20px; border-radius:8px; border:1px solid #eee; border-left:5px solid #8c1b1b;">
                <h3>J.P. Harrington Collection</h3>
                <p>Part of the Smithsonian's extensive J.P. Harrington papers, these recordings were brought to light through modern linguistic scholarship and community collaboration.</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Linguistic Pipeline Telemetry</h2>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:20px; margin-top:15px;">
            <div style="background:#fff5f5; padding:20px; border-radius:8px; border:1px solid #ffcccc; text-align:center;">
                <span style="display:block; font-size:2.3rem; font-weight:bold; color:#8c1b1b;">{dict_word_count}</span>
                <p style="margin: 5px 0 12px 0; font-weight: bold; color: #333;">Documented Glossary Terms</p>
                <a class="btn" href="dictionary.html">Open Dictionary</a>
            </div>
            <div style="background:#fff5f5; padding:20px; border-radius:8px; border:1px solid #ffcccc; text-align:center;">
                <span style="display:block; font-size:2.3rem; font-weight:bold; color:#8c1b1b;">{total_obs}</span>
                <p style="margin: 5px 0 12px 0; font-weight: bold; color: #333;">Active Research Insights</p>
                <a class="btn" href="observations.html">View Insights Log</a>
            </div>
            <div style="background:#fff5f5; padding:20px; border-radius:8px; border:1px solid #ffcccc; text-align:center;">
                <span style="display:block; font-size:2.3rem; font-weight:bold; color:#8c1b1b;">{total_vars}</span>
                <p style="margin: 5px 0 12px 0; font-weight: bold; color: #333;">Pronunciation Variants</p>
                <a class="btn" href="variations.html">View Variations</a>
            </div>
        </div>
    </div>

    <h2>Transcription Reading Gallery</h2>
    <div class="grid" style="margin-bottom:30px;">{html_cards}</div>

    <footer>
        <p style="text-align:center; margin:50px 0 20px 0; color:#777; border-top: 1px solid #ddd; padding-top: 20px;">
            &copy; 2026 Joe Peter Project Team. Powered by the J.P. Harrington Collection.
        </p>
    </footer>
    {audio_dock_html}
    </body>
    </html>"""

    with open(html_output_main, 'w', encoding='utf-8') as f: f.write(index_body)

    # =========================================================
    # PAGE BUILD 2: DICTIONARY.HTML
    # =========================================================
    spotlights = "".join([f'<div style="background:#8c1b1b; color:white; padding:6px 14px; border-radius:50px; font-size:0.8rem; font-weight:bold;">{w} ({d["count"]}x)</div>' for w, d in sorted_by_freq])

    dict_cards = ""
    for word, d in glossary.items():
        if d.get('count', 0) > 0:
            occ_links = ""
            for o in d.get('occurrences', []):
                sec_val = parse_elan_time(o.get("start_time", o.get("time", "00:00")))
                track_id = o.get("id", "Unknown")
                time_lbl = o.get("start_time", o.get("time", "00:00"))
                word_class = o.get("word_class", "Unclassified")
                
                clean_context = clean_for_html(o.get("context_line", ""))
                
                occ_links += f"""
                <div class="occ-chip-wrapper">
                    <button class="occ-link-btn" data-track="{track_id}" data-start="{sec_val}" data-duration="4.5" onclick="triggerAudioFromElement(this)">
                        {track_id}@{time_lbl} • <span class="occ-class-lbl">{word_class}</span> 🔊
                    </button>
                    <div class="occ-popover">
                        <span class="popover-context-line"><strong>Context:</strong> "{clean_context}"</span>
                        <span class="popover-hint">Click token to stream segment</span>
                    </div>
                </div>"""
            
            safe_term = clean_for_data_attr(word.lower())
            safe_def = clean_for_data_attr(d['definition'].lower())
            
            dict_cards += f"""
            <div class="dict-card" data-term="{safe_term}" data-def="{safe_def}" style="background:#fff; border:1px solid #ddd; padding:15px; border-radius:6px; position:relative;">
                <strong style="color:#8c1b1b; font-size:1.1rem;">{word}</strong> <small style="color:#777;">({d['count']}x)</small>
                <p style="margin:5px 0; font-size:0.85rem; color:#444;">{d['definition']}</p>
                <div class="occ-links-container">{occ_links}</div>
            </div>"""

    dict_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>Chinuk Wawa Dictionary & Concordance</title>
        <style>{shared_css}</style>
    </head>
    <body>
    <header>
        <a class="repo-link" href="index.html">← Dashboard Home</a>
        <h1>📕 Chinuk Wawa Dictionary & Concordance</h1>
        <p>Searchable lexical reference compiled directly from processed text layers.</p>
    </header>
    {generate_nav("dict")}

    <div class="section">
        <h2>Dictionary Term Lookup</h2>
        <div class="search-container">
            <input type="text" id="dictSearch" class="search-bar" placeholder="Search dictionary for terms or definitions..." onkeyup="filterDictionary()">
        </div>
        <p style="margin-bottom:8px; font-weight:bold; font-size:0.8rem; color:#666;">🔥 TOP 10 FREQUENT WORDS IN CURRENT LOGS</p>
        <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:25px;">{spotlights}</div>
        
        <div id="dictionaryGrid" class="grid">{dict_cards}</div>
    </div>

    <script>
        function filterDictionary() {{
            const filter = document.getElementById('dictSearch').value.toLowerCase();
            const cards = document.getElementById('dictionaryGrid').getElementsByClassName('dict-card');
            for (let i = 0; i < cards.length; i++) {{
                const term = cards[i].getAttribute('data-term');
                const def = cards[i].getAttribute('data-def');
                if (term.includes(filter) || def.includes(filter)) {{
                    cards[i].style.display = "";
                }} else {{
                    cards[i].style.display = "none";
                }}
            }}
        }}
    </script>
    {audio_dock_html}
    </body>
    </html>"""

    with open(html_output_dict, 'w', encoding='utf-8') as f: f.write(dict_body)

    # =========================================================
    # PAGE BUILD 3: OBSERVATIONS.HTML
    # =========================================================
    obs_rows_html = ""
    for tag, entries in observations_data.items():
        for e in entries:
            safe_text_attr = f"{e['id'].lower()} {e['speaker'].lower()} {e['note_raw'].lower()} {e['transcription_raw'].lower()}"
            
            obs_rows_html += f"""
            <tr class="obs-row" data-tag="{tag}" data-text="{safe_text_attr}">
                <td><span style="background:#8c1b1b; color:white; padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold;">{tag}</span></td>
                <td><code>{e['id']}</code></td>
                <td><button class="audio-btn" data-track="{e['id']}" data-start="{e['seconds']}" data-duration="{e['duration']}" onclick="triggerAudioFromElement(this)">{e['time']} 🔊</button></td>
                <td><strong>{e['speaker']}</strong></td>
                <td><small style="color:#555;">{e['transcription']}</small></td>
                <td>{e['note']}</td>
            </tr>"""

    obs_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>Research Observations Log</title>
        <style>{shared_css}</style>
    </head>
    <body>
    <header>
        <a class="repo-link" href="index.html">← Dashboard Home</a>
        <h1>🔬 Master Research & Observations Log</h1>
        <p>Cross-referenced track classifications parsed directly from transcription tiers.</p>
    </header>
    {generate_nav("obs")}

    <div class="section">
        <h2>Interactive Field Log Browser</h2>
        <div class="search-container">
            <input type="text" id="obsSearch" class="search-bar" placeholder="Search across tags, IDs, notes, or speakers..." onkeyup="filterObservations()">
        </div>
        <div style="margin:10px 0 20px 0; font-size:0.9rem;">
            <strong>Filter by Category:</strong>
            <select id="tagSelect" onchange="filterObservations()" style="padding:6px 12px; border-radius:4px; border:1px solid #ccc; font-size:0.85rem; margin-left:10px;">
                <option value="ALL">All Log Categories ({total_obs} items)</option>
                {"".join([f'<option value="{t}">{l} ({len(observations_data[t])})</option>' for t, l in categories.items()])}
                <option value="[UNCATEGORIZED]">⚠️ Uncategorized Comments ({len(observations_data['[UNCATEGORIZED]'])})</option>
            </select>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width:12%;">Category</th>
                    <th style="width:10%;">Track ID</th>
                    <th style="width:10%;">Timestamp</th>
                    <th style="width:12%;">Speaker</th>
                    <th style="width:26%;">Dialogue Context</th>
                    <th style="width:30%;">Observation Annotation Note</th>
                </tr>
            </thead>
            <tbody id="obsTableBody">{obs_rows_html}</tbody>
        </table>
    </div>

    <script>
        function filterObservations() {{
            const filter = document.getElementById('obsSearch').value.toLowerCase();
            const tagFilter = document.getElementById('tagSelect').value;
            const rows = document.getElementById('obsTableBody').getElementsByClassName('obs-row');
            
            for (let i = 0; i < rows.length; i++) {{
                const rowText = rows[i].getAttribute('data-text');
                const rowTag = rows[i].getAttribute('data-tag');
                
                const matchesSearch = rowText.includes(filter);
                const matchesTag = (tagFilter === "ALL" || rowTag === tagFilter);
                
                if (matchesSearch && matchesTag) {{
                    rows[i].classList.remove('hidden');
                }} else {{
                    rows[i].classList.add('hidden');
                }}
            }}
        }}
    </script>
    {audio_dock_html}
    </body>
    </html>"""

    with open(html_output_obs, 'w', encoding='utf-8') as f: f.write(obs_body)

    # =========================================================
    # PAGE BUILD 4: VARIATIONS.HTML
    # =========================================================
    var_rows_html = ""
    for v in variations_data:
        safe_var_text_attr = f"{v['id'].lower()} {v['speaker'].lower()} {v['variant_raw'].lower()} {v['gr_standard_raw'].lower()} {v['raw_content_raw'].lower()} {v['transcription_raw'].lower()}"
        
        var_rows_html += f"""
        <tr class="var-row" data-text="{safe_var_text_attr}">
            <td><code>{v['id']}</code></td>
            <td><button class="audio-btn" data-track="{v['id']}" data-start="{v['seconds']}" data-duration="{v['duration']}" onclick="triggerAudioFromElement(this)">{v['time']} 🔊</button></td>
            <td><strong>{v['speaker']}</strong></td>
            <td><small style="color:#555;">{v['transcription']}</small></td>
            <td style="color:#8c1b1b; font-weight:bold; font-size:1rem;">{v['variant']}</td>
            <td style="font-style:italic; color:#2c3e50;">{v['gr_standard']}</td>
            <td><small style="color:#444;">{v['raw_content']}</small></td>
        </tr>"""

    vars_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>Dialect Variation Report</title>
        <style>{shared_css}</style>
    </head>
    <body>
    <header>
        <a class="repo-link" href="index.html">← Dashboard Home</a>
        <h1>🔊 Dialect Variation & Pronunciation Report</h1>
        <p>Isolating segments where Joe Peter's phonetic delivery deviates from traditional Grand Ronde standards.</p>
    </header>
    {generate_nav("vars")}

    <div class="section">
        <h2>Searchable Variation Index</h2>
        <div class="search-container">
            <input type="text" id="varSearch" class="search-bar" placeholder="Filter pronunciation records by deviations, keywords, or track IDs..." onkeyup="filterVariations()">
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width:10%;">Track ID</th>
                    <th style="width:10%;">Timestamp</th>
                    <th style="width:12%;">Speaker</th>
                    <th style="width:24%;">Dialogue Context</th>
                    <th style="width:16%;">Phonetic Deviation</th>
                    <th style="width:16%;">Standard GR Spelling Reference</th>
                    <th style="width:12%;">Full Content Audit String</th>
                </tr>
            </thead>
            <tbody id="varTableBody">{var_rows_html}</tbody>
        </table>
    </div>

    <script>
        function filterVariations() {{
            const filter = document.getElementById('varSearch').value.toLowerCase();
            const rows = document.getElementById('varTableBody').getElementsByClassName('var-row');
            for (let i = 0; i < rows.length; i++) {{
                const rowText = rows[i].getAttribute('data-text');
                if (rowText.includes(filter)) {{
                    rows[i].classList.remove('hidden');
                }} else {{
                    rows[i].classList.add('hidden');
                }}
            }}
        }}
    </script>
    {audio_dock_html}
    </body>
    </html>"""

    with open(html_output_vars, 'w', encoding='utf-8') as f: f.write(vars_body)

    print("🚀 Success! Portal synchronized directly with native angle bracket notations.")

if __name__ == "__main__":
    generate_web_portal()