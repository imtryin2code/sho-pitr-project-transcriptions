import csv
import os
from fpdf import FPDF

def generate_guides():
    csv_path = 'metadata/master_transcription_list.csv'
    md_output_base = 'exports'
    pdf_output_base = 'exports/pdfs'
    
    # Path to your Unicode font - Make sure this file exists!
    # If using DejaVuSans.ttf in the scripts folder, use: font_path = "scripts/DejaVuSans.ttf"
    font_path = "scripts/DejaVuSans.ttf" 

    if not os.path.exists(csv_path):
        print("Error: Master CSV not found. Please run the extraction script first.")
        return

    os.makedirs(pdf_output_base, exist_ok=True)

    stories = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            story_id = row['ID']
            if story_id not in stories:
                stories[story_id] = []
            stories[story_id].append(row)

    for story_id, rows in stories.items():
        print(f"Processing {story_id}...")

        # --- 1. GENERATE MARKDOWN (.md) ---
        md_path = os.path.join(md_output_base, f"{story_id}_Reading_Guide.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Reading Guide: {story_id}\n\n")
            f.write(f"**Source:** 1941 Metal Disc Recording\n")
            f.write(f"**Participants:** Jack Marr (English) & Joe Peter (Chinook Jargon)\n\n")
            f.write("| Time | Speaker | Text |\n")
            f.write("| :--- | :--- | :--- |\n")
            for row in rows:
                text = row['Text']
                if "Joe" in row['Speaker'] or "Peter" in row['Speaker']:
                    text = f"**{text}**"
                f.write(f"| {row['Time']} | {row['Speaker']} | {text} |\n")

        # --- 2. GENERATE PDF (.pdf) ---
        pdf = FPDF()
        pdf.add_page()
        
        # Register Font
        if os.path.exists(font_path):
            # We call it 'UniFont' to ensure no confusion with system defaults
            pdf.add_font("UniFont", style="", fname=font_path)
            pdf.set_font("UniFont", size=12)
        else:
            print(f"Font not found at {font_path}, using Helvetica fallback.")
            pdf.set_font("Helvetica", size=12)

        # Header
        pdf.cell(0, 10, f"Joe Peter Project: {story_id}", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("UniFont", size=10)
        pdf.cell(0, 10, "1941 Metal Disc Transcriptions", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Table Header
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(20, 10, "Time", border=1, fill=True)
        pdf.cell(35, 10, "Speaker", border=1, fill=True)
        pdf.cell(135, 10, "Transcription", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # Table Rows
        for row in rows:
            is_joe = "Joe" in row['Speaker'] or "Peter" in row['Speaker']
            
            # Start position
            x, y = pdf.get_x(), pdf.get_y()
            
            # We use a consistent font but bold the Jargon text if possible 
            # Note: regular ArialUnicodeMS doesn't always have a separate 'bold' file,
            # so we use font size to differentiate.
            pdf.set_font("UniFont", size=11 if is_joe else 10)

            # Calculate height for multi_cell
            # This is a trick to keep borders aligned
            pdf.multi_cell(135, 10, row['Text'], border=1, new_x="LMARGIN", new_y="NEXT")
            end_y = pdf.get_y()
            height = end_y - y

            # Go back to draw the Time and Speaker boxes with the calculated height
            pdf.set_xy(x, y)
            pdf.cell(20, height, row['Time'], border=1)
            pdf.cell(35, height, row['Speaker'], border=1)
            
            # Reset Y to the bottom of the row for the next entry
            pdf.set_y(end_y)

        pdf_path = os.path.join(pdf_output_base, f"{story_id}_Reading_Guide.pdf")
        pdf.output(pdf_path)
        
    print(f"\nFinished! Check 'exports/' for Markdown and 'exports/pdfs/' for PDFs.")

if __name__ == "__main__":
    generate_guides()