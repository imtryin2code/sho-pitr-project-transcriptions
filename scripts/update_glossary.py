import csv
import json
import os
import re

def update_glossary():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    repo_url = "https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/metadata/master_transcription_list.csv"
    
    # Updated stopwords to filter out meta-commentary and common English fillers
    english_stopwords = {
        'the', 'and', 'was', 'for', 'with', 'that', 'this', 'from', 'they', 
        'have', 'had', 'been', 'were', 'not', 'are', 'his', 'her', 'she', 'him',
        'fix', 'next', 'example', 'extra'
    }

    if not os.path.exists(csv_path):
        print("Error: master_transcription_list.csv not found.")
        return

    glossary = {}
    if os.path.exists(glossary_path):
        try:
            with open(glossary_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    glossary = json.loads(content)
        except json.JSONDecodeError:
            glossary = {}

    # Reset counts for the new run
    for word in glossary:
        glossary[word]['count'] = 0
        glossary[word]['occurrences'] = []

    skip_patterns = [r"ENDED HERE", r"DELETE THIS SEGMENT", r"EXTEND THIS SEGMENT", r"DATE\??"]

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2): 
            if any(name in row['Speaker'] for name in ["Joe", "Peter"]):
                full_text = row['Text']
                rec_id = row['ID']
                timestamp = row['Time']

                if any(re.search(p, full_text, re.IGNORECASE) for p in skip_patterns):
                    continue

                jp_match = re.search(r'JP:\s*(.*)', full_text)
                if not jp_match:
                    continue
                
                jp_text = jp_match.group(1)
                
                # 1. Strip out ***notes*** (using non-greedy match .*?)
                jp_text = re.sub(r'\*\*\*.*?\*\*\*', '', jp_text)
                
                # 2. Handle ellipses and dots as separators
                jp_text = jp_text.replace('...', ' ')
                jp_text = re.sub(r'\.+', ' ', jp_text)

                # 3. Strip out transcriber notes [] and phonetic/audio helpers <>
                jp_text = re.sub(r'\[.*?\]', '', jp_text) 
                jp_text = re.sub(r'<.*?>', '', jp_text)   

                tokens = jp_text.split()
                
                for token in tokens:
                    is_marked_english = re.match(r'\{(.*?)\}', token)
                    
                    if is_marked_english:
                        # Keep explicitly marked English in the glossary (e.g. {store})
                        word = is_marked_english.group(0).lower()
                    else:
                        # Clean word: keep alphanumeric, hyphens, and specific Chinook chars
                        clean_word = re.sub(r'[^-\wɬx̣ʔ]', '', token.lower())
                        
                        # Filter out our expanded stopwords
                        if clean_word in english_stopwords:
                            continue
                            
                        word = clean_word

                    # Normalize elongated speech (e.g. hayaaaa -> haya)
                    word = re.sub(r'(.)\1{2,}', r'\1', word)
                    word = word.strip('-')

                    if len(word) < 2 or word.isdigit():
                        continue
                        
                    if word not in glossary:
                        glossary[word] = {"definition": "TBD", "count": 0, "occurrences": []}
                    
                    glossary[word]['count'] += 1
                    
                    # Log occurrence with deep-link
                    occ = {
                        "id": rec_id, 
                        "time": timestamp,
                        "url": f"{repo_url}#L{line_num}"
                    }
                    
                    if occ not in glossary[word]['occurrences']:
                        glossary[word]['occurrences'].append(occ)

    # Sort: Chinook (plain) first, English ({}) second
    sorted_glossary = dict(sorted(
        glossary.items(), 
        key=lambda item: (item[0].startswith('{'), item[0])
    ))

    with open(glossary_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_glossary, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    print(f"Glossary updated: Added new stopwords and stripped triple-asterisk notes.")

if __name__ == "__main__":
    update_glossary()