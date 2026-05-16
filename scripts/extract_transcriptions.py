import xml.etree.ElementTree as ET
import os
import csv

def parse_eaf(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    identifier = os.path.basename(os.path.dirname(file_path))
    
    # 1. Map Time Slots
    time_order = root.find('TIME_ORDER')
    time_slots = {}
    if time_order is not None:
        for slot in time_order.findall('TIME_SLOT'):
            time_slots[slot.get('TIME_SLOT_ID')] = slot.get('TIME_VALUE')

    # Data structures to manage tier relationships
    alignable_annotations = {} # annotation_id -> {start_time, speaker, text}
    ref_annotations = []       # List of dictionaries for dependent annotations

    # 2. Parse all tiers dynamically
    for tier in root.findall('TIER'):
        tier_id = tier.get('TIER_ID')
        
        # Process primary time-aligned parent tiers
        for ann in tier.findall('.//ALIGNABLE_ANNOTATION'):
            ann_id = ann.get('ANNOTATION_ID')
            ts_ref = ann.get('TIME_SLOT_REF1')
            start_time = int(time_slots.get(ts_ref, 0))
            
            text_el = ann.find('ANNOTATION_VALUE')
            text = text_el.text if text_el is not None else ""
            
            alignable_annotations[ann_id] = {
                'ID': identifier,
                'Raw_MS': start_time,
                'Speaker': tier_id,
                'Text': text,
                'Notes_Tier': "",
                'Notes_Text': ""
            }
            
        # Process structural child tiers (Notes, Categories, Labels)
        for ann in tier.findall('.//REF_ANNOTATION'):
            ref_ann_id = ann.get('ANNOTATION_REF')
            text_el = ann.find('ANNOTATION_VALUE')
            text = text_el.text if text_el is not None else ""
            
            ref_annotations.append({
                'Parent_Ref': ref_ann_id,
                'Tier_Name': tier_id,
                'Text': text
            })

    # 3. Attach notes and categories to their parent dialogue tokens
    for ref in ref_annotations:
        parent_id = ref['Parent_Ref']
        if parent_id in alignable_annotations:
            # If a parent already has notes, append with a separator, else write fresh
            existing_tier = alignable_annotations[parent_id]['Notes_Tier']
            existing_text = alignable_annotations[parent_id]['Notes_Text']
            
            if existing_text:
                alignable_annotations[parent_id]['Notes_Tier'] = f"{existing_tier} | {ref['Tier_Name']}"
                alignable_annotations[parent_id]['Notes_Text'] = f"{existing_text} | {ref['Text']}"
            else:
                alignable_annotations[parent_id]['Notes_Tier'] = ref['Tier_Name']
                alignable_annotations[parent_id]['Notes_Text'] = ref['Text']

    # 4. Format timelines and convert milliseconds to MM:SS
    final_rows = []
    for ann in alignable_annotations.values():
        seconds = (ann['Raw_MS'] / 1000) % 60
        minutes = (ann['Raw_MS'] / (1000 * 60)) % 60
        timestamp = f"{int(minutes):02d}:{int(seconds):02d}"
        
        final_rows.append({
            'ID': ann['ID'],
            'Time': timestamp,
            'Speaker': ann['Speaker'],
            'Text': ann['Text'],
            'Notes_Tier': ann['Notes_Tier'],
            'Notes_Text': ann['Notes_Text'],
            'Raw_MS': ann['Raw_MS']
        })
    
    # Sort strictly by chronology to maintain continuous flow
    final_rows.sort(key=lambda x: x['Raw_MS'])
    return final_rows

def main():
    all_rows = []
    for root_dir, dirs, files in os.walk("."):
        if any(skip in root_dir for skip in [".git", "scripts", "venv"]):
            continue
        for file in files:
            if file.endswith(".eaf"):
                file_path = os.path.join(root_dir, file)
                all_rows.extend(parse_eaf(file_path))
    
    output_path = 'metadata/master_transcription_list.csv'
    
    if all_rows:
        # Added tracking columns to map where categories and notes came from
        keys = ['ID', 'Time', 'Speaker', 'Text', 'Notes_Tier', 'Notes_Text']
        
        # Ensure output folder exists safely
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows)
            
        print(f"Success! Compiled master list with {len(all_rows)} lines across all dynamic tiers.")

if __name__ == "__main__":
    main()