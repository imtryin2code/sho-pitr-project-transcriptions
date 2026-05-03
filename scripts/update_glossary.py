import csv
import json
import os
import re

def update_glossary():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    repo_url = "https://github.com/imtryin2code/sho-pitr-project-transcriptions/blob/main/metadata/master_transcription_list.csv"
    
    if not os.path.exists(csv_path):
        print("Error: master_transcription_list.csv not found.")
        return

    # Load existing glossary safely to preserve manual definitions
    glossary = {}
    if os.path.exists(glossary_path):
        try:
            with open(glossary_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    glossary = json.loads(content)
        except json.JSONDecodeError:
            glossary = {}

    # Reset counts and occurrences for a fresh tally
    for word in glossary:
        glossary[word]['count'] = 0
        glossary[word]['occurrences'] = []

    skip_patterns = [r"ENDED HERE", r"DELETE THIS SEGMENT", r"EXTEND THIS SEGMENT", r"DATE\??"]

    with open(csv_path, 'r', encoding='utf-8') as f:
        # We use enumerate to get the line number for GitHub deep-linking
        # GitHub line numbers start at 1, and CSV headers are line 1.
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2): 
            if "Joe" in row['Speaker'] or "Peter" in row['Speaker']:
                full_text = row['Text']
                rec_id = row['ID']
                timestamp = row['Time']

                # Skip metadata lines
                if any(re.search(p, full_text, re.IGNORECASE) for p in skip_patterns):
                    continue

                # Strictly isolate JP's speech
                jp_match = re.search(r'JP:\s*(.*)', full_text)
                if not jp_match:
                    continue
                
                jp_text = jp_match.group(1)
                jp_text = re.sub(r'\[.*?\]', '', jp_text) # Remove [notes]
                jp_text = re.sub(r'<.*?>', '', jp_text)   # Remove <phonetics>

                tokens = jp_text.split()
                
                for token in tokens:
                    is_marked_english = re.match(r'\{(.*?)\}', token)
                    
                    if is_marked_english:
                        word = is_marked_english.group(0).lower()
                    else:
                        # Filter for Chinook-only (clean word and check against unmarked English)
                        clean_word = re.sub(r'[^-\w\sɬx̣ʔ]', '', token.lower())
                        has_chinook_char = any(c in clean_word for c in 'ɬx̣ʔ')
                        
                        if not has_chinook_char and re.fullmatch(r'[a-z]+', clean_word):
                            continue
                        word = clean_word

                    # Handle elongated speech (altaaaa -> alta)
                    word = re.sub(r'(.)\1{2,}', r'\1', word)
                    word = word.strip('-')

                    if len(word) < 2 or word.isdigit():
                        continue
                        
                    if word not in glossary:
                        glossary[word] = {"definition": "TBD", "count": 0, "occurrences": []}
                    
                    glossary[word]['count'] += 1
                    
                    # Create the occurrence with a deep-link to the CSV line on GitHub
                    occ = {
                        "id": rec_id, 
                        "time": timestamp,
                        "url": f"{repo_url}#L{line_num}"
                    }
                    
                    # Prevent duplicate occurrences for the same word in the same segment
                    if occ not in glossary[word]['occurrences']:
                        glossary[word]['occurrences'].append(occ)

    # Sort: Chinook alphabetical first, English { } last
    sorted_glossary = dict(sorted(
        glossary.items(), 
        key=lambda item: (item[0].startswith('{'), item[0])
    ))

    with open(glossary_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_glossary, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    print(f"Glossary & Concordance updated. Processed {len(sorted_glossary)} unique terms.")

if __name__ == "__main__":
    update_glossary()