import xml.etree.ElementTree as ET
import os
import csv

def parse_eaf(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # 1. Map Time Slots
    time_order = root.find('TIME_ORDER')
    time_slots = {}
    if time_order is not None:
        for slot in time_order.findall('TIME_SLOT'):
            time_slots[slot.get('TIME_SLOT_ID')] = slot.get('TIME_VALUE')

    data = []
    # Use the folder name as the short identifier (e.g., 682-S1)
    identifier = os.path.basename(os.path.dirname(file_path))

    # 2. Extract Tier data
    for tier in root.findall('TIER'):
        tier_id = tier.get('TIER_ID')
        for annotation in tier.findall('.//ALIGNABLE_ANNOTATION'):
            ts_ref = annotation.get('TIME_SLOT_REF1')
            start_time = int(time_slots.get(ts_ref, 0))
            
            # Convert milliseconds to a readable MM:SS format for the CSV
            seconds = (start_time / 1000) % 60
            minutes = (start_time / (1000 * 60)) % 60
            timestamp = f"{int(minutes):02d}:{int(seconds):02d}"
            
            text_element = annotation.find('ANNOTATION_VALUE')
            text = text_element.text if text_element is not None else ""
            
            data.append({
                'ID': identifier,
                'Time': timestamp,
                'Speaker': tier_id,
                'Text': text,
                'Raw_MS': start_time  # Used for sorting only
            })
    
    # 3. Sort by raw milliseconds to keep the conversation flow
    data.sort(key=lambda x: x['Raw_MS'])
    return data

def main():
    all_rows = []
    # Scan the repo for .eaf files
    for root_dir, dirs, files in os.walk("."):
        if ".git" in root_dir or "scripts" in root_dir:
            continue
        for file in files:
            if file.endswith(".eaf"):
                file_path = os.path.join(root_dir, file)
                all_rows.extend(parse_eaf(file_path))
    
    output_path = 'metadata/master_transcription_list.csv'
    if all_rows:
        # Define columns for the CSV
        keys = ['ID', 'Time', 'Speaker', 'Text']
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"Success! Created master list with {len(all_rows)} lines.")

if __name__ == "__main__":
    main()