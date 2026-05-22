import csv
import json
import os
import re

def clean_word_key(word):
    """Normalizes variation text keys cleanly without breaking Unicode orthography."""
    if not word: return ""
    
    # Lowercase and strip outer spaces
    cleaned = word.strip().lower()
    
    # If the token contains the explicit stutter notation "..", discard it instantly
    if '..' in cleaned:
        return ""
        
    # STRICT WHITELIST FILTER: Keep alphanumeric characters (\w), ɬ, x̣ (including combining dot), 
    # the glottal stop ʔ, and hyphens. Strip away outer notation brackets/punctuation symbols.
    cleaned = re.sub(r'[^\wɬx̣\u0323ʔ\-]', '', cleaned)
    
    # Trim remaining trailing/leading hyphens left over from notation removals
    cleaned = cleaned.strip('-')
    
    # EXCLUSION GUARD: Explicitly prevent "jp" or "jm" from being counted as valid words
    if cleaned in ['jp', 'jm']:
        return ""
    
    # Reject empty strings, purely numeric tokens, or lone placeholder characters
    if not cleaned or cleaned.isdigit() or len(cleaned) <= 1:
        return ""
    return cleaned

def rebuild_glossary_database():
    csv_path = 'metadata/master_transcription_list.csv'
    glossary_path = 'metadata/glossary.json'
    
    # 1. READ EXISTING GLOSSARY TO PRESERVE MANUALLY COMPILED DEFINITIONS
    existing_glossary = {}
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            try:
                existing_glossary = json.load(f)
                print(f"Loaded {len(existing_glossary)} baseline words from existing glossary.")
            except Exception:
                print("⚠️ Warning: Existing glossary.json was unreadable or empty. Discovering fresh...")

    # Build our tracking baseline map, migrating historical data cleanly if found
    new_glossary = {}
    for word, payload in existing_glossary.items():
        clean_k = clean_word_key(word)
        if not clean_k: continue
        
        # Keep global definitions intact
        new_glossary[clean_k] = {
            'definition': payload.get('definition', 'TBD'),
            'count': 0,
            'occurrences': []
        }
        
        # Legacy structural migration: If an old file has a top-level word_class, 
        # we remember it to use as a fallback default for incoming occurrences.
        if 'word_class' in payload:
            new_glossary[clean_k]['_legacy_class'] = payload['word_class']

    # 2. SCAN MASTER CSV WITH CONTEXT AND OCCURRENCE-LEVEL SYNTAX POOLS
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []
            
            for row in reader:
                track_id = row.get('ID', '').strip()
                speaker_tier = row.get('Speaker', '').strip().upper()
                transcription_text = row.get('Text', '').strip()
                
                start_time = row.get('Start Time', row.get('Time', '00:00.000')).strip()
                end_time = row.get('End Time', start_time).strip()
                
                if not transcription_text or not track_id:
                    continue
                
                # GUARD 1: Tier Name Filtering (Skip Jack Marr & analysis notation layers)
                if any(x in speaker_tier for x in ['JM', 'NOTE', 'LING', 'HIST', 'INFO', 'TEX']):
                    continue
                
                # GUARD 2: Direct Content Prefix Filtering (Catch conversational leaks)
                if transcription_text.upper().startswith('JM:'):
                    continue
                
                # Strip prefix "JP:" if it exists at the front of the line
                cleaned_text = re.sub(r'^JP:\s*', '', transcription_text, flags=re.IGNORECASE)
                
                # GUARD 3: Clear conversational English block notations {{text}} completely
                cleaned_text = re.sub(r'\{\{[^}]+?\}\}', '', cleaned_text)
                if not cleaned_text.strip():
                    continue

                # NOTATION PASSTHROUGH: Handle alternatives separator inside brackets first
                def split_bracketed_alternatives(match):
                    content = match.group(0)
                    if '/' in content:
                        return content.replace('/', ' ')
                    return content

                cleaned_text = re.sub(r'<<[^>]+?>>', split_bracketed_alternatives, cleaned_text)
                cleaned_text = re.sub(r'<[^>]+?>', split_bracketed_alternatives, cleaned_text)

                # SPACE-FIRST TOKENIZATION: Splits strictly by whitespace characters
                raw_tokens = cleaned_text.split()
                
                # Look-ahead filter loop to spot and intercept incomplete stutters before indexing
                for idx, token in enumerate(raw_tokens):
                    if '..' in token:
                        continue
                        
                    term = clean_word_key(token)
                    if not term:
                        continue
                    
                    # STUTTER INTERCEPTOR 1: Look ahead one word (e.g. "an" -> "anqa")
                    if idx + 1 < len(raw_tokens):
                        next_term = clean_word_key(raw_tokens[idx + 1])
                        if next_term and next_term.startswith(term) and term != next_term:
                            continue
                            
                    # STUTTER INTERCEPTOR 2: Look ahead two words (e.g. "an anqa anqati")
                    if idx + 2 < len(raw_tokens):
                        future_term = clean_word_key(raw_tokens[idx + 2])
                        if future_term and future_term.startswith(term) and term != future_term:
                            continue

                    # DYNAMIC DISCOVERY: Register word safely if it is missing from baseline dictionary
                    if term not in new_glossary:
                        new_glossary[term] = {
                            'definition': 'TBD',
                            'count': 0,
                            'occurrences': []
                        }
                    
                    new_glossary[term]['count'] += 1
                    
                    # Find what default label to hand the new occurrence item
                    default_class = new_glossary[term].get('_legacy_class', 'Unclassified')
                    
                    # Store unique occurrences with word_class assigned directly to the instance
                    if not any(occ['id'] == track_id and occ['start_time'] == start_time for occ in new_glossary[term]['occurrences']):
                        new_glossary[term]['occurrences'].append({
                            'id': track_id,
                            'start_time': start_time,
                            'end_time': end_time,
                            'word_class': default_class,  # <--- Moved to individual occurrence level
                            'context_line': transcription_text  
                        })

    # 3. CLEANUP TEMPORARY TRACKING KEYS AND SAVE RESTRUCTURED DATABASE
    for term in new_glossary.keys():
        new_glossary[term].pop('_legacy_class', None)

    final_glossary = {k: v for k, v in new_glossary.items() if v['count'] > 0 or v['definition'] != 'TBD'}
    sorted_glossary = dict(sorted(final_glossary.items()))
    
    os.makedirs(os.path.dirname(glossary_path), exist_ok=True)
    with open(glossary_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_glossary, f, ensure_ascii=False, indent=2)
        
    print(f"🚀 Success! Dictionary glossary compiled. Word classifications moved to occurrence lists.")

if __name__ == "__main__":
    rebuild_glossary_database()