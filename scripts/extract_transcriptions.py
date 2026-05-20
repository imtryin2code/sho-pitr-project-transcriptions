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
    alignable_annotations = {} # annotation_id -> {start_time, end_time, speaker, text}
    ref_annotations = []       # List of dictionaries for dependent annotations

    # 2. Parse all tiers dynamically
    for tier in root.findall('TIER'):
        tier_id = tier.get('TIER_ID')
        
        # Process primary time-aligned parent tiers
        for ann in tier.findall('.//ALIGNABLE_ANNOTATION'):
            ann_id = ann.get('ANNOTATION_ID')
            ts_ref1 = ann.get('TIME_SLOT_REF1')
            ts_ref2 = ann.get('TIME_SLOT_REF2')
            
            start_time = int(time_slots.get(ts_ref1, 0))
            end_time = int(time_slots.get(ts_ref2, 0))
            
            text_el = ann.find('ANNOTATION_VALUE')
            text = text_el.text if text_el is not None else ""
            
            alignable_annotations[ann_id] = {
                'ID': identifier,
                'Raw_Start_MS': start_time,
                'Raw_End_MS': end_time,
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
            existing_tier = alignable_annotations[parent_id]['Notes_Tier']
            existing_text = alignable_annotations[parent_id]['Notes_Text']
            
            if existing_text:
                alignable_annotations[parent_id]['Notes_Tier'] = f"{existing_tier} | {ref['Tier_Name']}"
                alignable_annotations[parent_id]['Notes_Text'] = f"{existing_text} | {ref['Text']}"
            else:
                alignable_annotations[parent_id]['Notes_Tier'] = ref['Tier_Name']
                alignable_annotations[parent_id]['Notes_Text'] = ref['Text']

    # 4. Format timelines with millisecond tracking precision (MM:SS.mmm)
    final_rows = []
    for ann in alignable_annotations.values():
        # Retain floating point remainders to stop alignment drift
        start_total_seconds = ann['Raw_Start_MS'] / 1000.0
        start_minutes = int(start_total_seconds // 60)
        start_seconds = start_total_seconds % 60
        # Formats cleanly to 2-digit minute, 2-digit whole second, and 3-digit millisecond
        start_timestamp = f"{start_minutes:02d}:{start_seconds:06.3f}"
        
        end_total_seconds = ann['Raw_End_MS'] / 1000.0
        end_minutes = int(end_total_seconds // 60)
        end_seconds = end_total_seconds % 60
        end_timestamp = f"{end_minutes:02d}:{end_seconds:06.3f}"
        
        final_rows.append({
            'ID': ann['ID'],
            'Start Time': start_timestamp,
            'End Time': end_timestamp,
            'Time': start_timestamp, # Keeps backward compatibility with template layouts
            'Speaker': ann['Speaker'],
            'Text': ann['Text'],
            'Notes_Tier': append_clean_tier_names(ann),
            'Notes_Text': ann['Notes_Text'],
            'Raw_Start_MS': ann['Raw_Start_MS']
        })
    
    final_rows.sort(key=lambda x: x['Raw_Start_MS'])
    return final_rows

def append_clean_tier_names(ann):
    return ann['Notes_Tier']

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
        keys = ['ID', 'Start Time', 'End Time', 'Time', 'Speaker', 'Text', 'Notes_Tier', 'Notes_Text']
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows)
            
        print(f"Success! Compiled master list with precise sub-second bounds across {len(all_rows)} rows.")

if __name__ == "__main__":
    main()