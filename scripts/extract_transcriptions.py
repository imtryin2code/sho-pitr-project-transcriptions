import xml.etree.ElementTree as ET
import os
import csv

def parse_eaf(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # This dictionary will store our transcriptions
    data = []
    
    # ELAN files store text in <ANNOTATION_VALUE> tags within <TIER> tags
    for tier in root.findall('TIER'):
        tier_id = tier.get('TIER_ID')
        for annotation in tier.findall('.//ANNOTATION_VALUE'):
            data.append({
                'Tier': tier_id,
                'Text': annotation.text
            })
    return data

def main():
    all_data = []
    # Loop through all directories in the repo
    for root_dir, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".eaf"):
                file_path = os.path.join(root_dir, file)
                print(f"Processing: {file_path}")
                all_data.extend(parse_eaf(file_path))
    
    # Save to a central CSV in the metadata folder
    output_file = 'metadata/master_transcription_list.csv'
    if all_data:
        keys = all_data[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_data)
        print(f"Success! Master list created at {output_file}")

if __name__ == "__main__":
    main()