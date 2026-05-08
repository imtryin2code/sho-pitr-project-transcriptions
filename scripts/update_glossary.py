import csv
import json
import os
import re

def update_glossary():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    repo_url = "https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/metadata/master_transcription_list.csv"
    
    # Expanded stopwords and specific discards
    english_stopwords = {
        'the', 'and', 'was', 'for', 'with', 'that', 'this', 'from', 'they', 
        'have', 'had', 'been', 'were', 'not', 'are', 'his', 'her', 'she', 'him',
        'fix', 'next', 'example', 'extra', "couldn't", 'answer', 'audio', 
        'cutoff', 'concentrate', 'missed', 'line', 'by', 'middle', 'page', 
        'put', 'shoot', 'will', 'hmm', 'jm', 'pg'
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
                
                # 1. Strip out ***notes***
                jp_text = re.sub(r'\*\*\*.*?\*\*\*', '', jp_text)
                
                # 2. Handle ellipses and dots
                jp_text = jp_text.replace('...', ' ')
                jp_text = re.sub(r'\.+', ' ', jp_text)

                # 3. Strip out transcriber notes [] and phonetic helpers <> 
                # (Note: we leave pipes and braces for logic below)
                jp_text = re.sub(r'\[.*?\]', '', jp_text) 
                jp_text = re.sub(r'<.*?>', '', jp_text)   

                tokens = jp_text.split()
                
                for i, token in enumerate(tokens):
                    # Check if previous word was Joe's pronunciation |text|
                    prev_was_pipe = False
                    if i > 0 and tokens[i-1].startswith('|') and tokens[i-1].endswith('|'):
                        prev_was_pipe = True

                    # Logic for English words in {}
                    is_marked_english = re.match(r'\{(.*?)\}', token)
                    
                    if is_marked_english:
                        # NEW REQUIREMENT: Skip if it follows a |pipe| word
                        if prev_was_pipe:
                            continue
                        word = is_marked_english.group(0).lower()
                    else:
                        # Clean word (including stripping pipes for the dictionary key)
                        clean_word = re.sub(r'[^-\wɬx̣ʔ]', '', token.lower())
                        
                        # Filter out expanded stopwords and specific discards
                        if clean_word in english_stopwords:
                            continue
                            
                        word = clean_word

                    # Normalize elongation
                    word = re.sub(r'(.)\1{2,}', r'\1', word)
                    word = word.strip('-')

                    if len(word) < 2 or word.isdigit():
                        continue
                        
                    if word not in glossary:
                        glossary[word] = {"definition": "TBD", "count": 0, "occurrences": []}
                    
                    glossary[word]['count'] += 1
                    
                    occ = {"id": rec_id, "time": timestamp, "url": f"{repo_url}#L{line_num}"}
                    if occ not in glossary[word]['occurrences']:
                        glossary[word]['occurrences'].append(occ)

    # Sort
    sorted_glossary = dict(sorted(
        glossary.items(), 
        key=lambda item: (item[0].startswith('{'), item[0])
    ))

    with open(glossary_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_glossary, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    print(f"Glossary updated: Filtered double-transcriptions and expanded stopwords.")

if __name__ == "__main__":
    update_glossary()