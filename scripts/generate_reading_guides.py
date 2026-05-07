import csv
import os
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_guides():
    csv_path = 'metadata/master_transcription_list.csv'
    # Output directories
    md_output_base = 'exports/markdown'
    pdf_output_base = 'exports/pdfs'
    word_output_base = 'exports/word-docs'
    
    # Path to your Unicode font
    font_path = "scripts/DejaVuSans.ttf" 

    if not os.path.exists(csv_path):
        print("Error: Master CSV not found.")
        return

    # Ensure all directories exist
    os.makedirs(md_output_base, exist_ok=True)
    os.makedirs(pdf_output_base, exist_ok=True)
    os.makedirs(word_output_base, exist_ok=True)

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

        # --- 1. MARKDOWN GENERATION ---
        md_path = os.path.join(md_output_base, f"{story_id}_Reading_Guide.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Reading Guide: {story_id}\n\n| Time | Speaker | Text |\n| :--- | :--- | :--- |\n")
            for row in rows:
                text = row['Text']
                if any(name in row['Speaker'] for name in ["Joe", "Peter"]):
                    text = f"**{text}**"
                f.write(f"| {row['Time']} | {row['Speaker']} | {text} |\n")

        # --- 2. PDF GENERATION (Optimized for Unicode and Layout) ---
        pdf = FPDF()
        pdf.add_page()
        
        # Load custom font to prevent garbled text
        if os.path.exists(font_path):
            pdf.add_font("UniFont", style="", fname=font_path)
            font_family = "UniFont"
        else:
            print(f"Warning: Font not found at {font_path}, using Helvetica.")
            font_family = "Helvetica"

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, f"Joe Peter Project: {story_id}", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        for row in rows:
            is_joe = any(name in row['Speaker'] for name in ["Joe", "Peter"])
            
            # Start position for the row
            y_before = pdf.get_y()
            
            # Use Multi-cell for the Text to handle wrapping without overlapping
            pdf.set_font(font_family, size=11 if is_joe else 10)
            # The X-offset of 65 leaves room for Time (25) and Speaker (40)
            pdf.set_xy(75, y_before) 
            pdf.multi_cell(0, 8, row['Text'], border=1, new_x="LMARGIN", new_y="NEXT")
            
            y_after = pdf.get_y()
            row_height = y_after - y_before
            
            # Go back and draw the Time and Speaker cells to match the multi_cell height
            pdf.set_xy(10, y_before)
            pdf.set_font("Helvetica", 'B' if is_joe else '', 9)
            pdf.cell(25, row_height, row['Time'], border=1)
            pdf.cell(40, row_height, row['Speaker'], border=1)
            
            pdf.set_y(y_after) # Set cursor for next row

        pdf.output(os.path.join(pdf_output_base, f"{story_id}_Reading_Guide.pdf"))

        # --- 3. WORD DOCUMENT GENERATION ---
        doc = Document()
        doc_title = doc.add_heading(f'Reading Guide: {story_id}', 0)
        doc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Time'
        hdr_cells[1].text = 'Speaker'
        hdr_cells[2].text = 'Transcription'

        for row in rows:
            row_cells = table.add_row().cells
            row_cells[0].text = row['Time']
            row_cells[1].text = row['Speaker']
            
            # Format the text (Bold for Joe Peter)
            p = row_cells[2].paragraphs[0]
            run = p.add_run(row['Text'])
            if any(name in row['Speaker'] for name in ["Joe", "Peter"]):
                run.bold = True

        doc_path = os.path.join(word_output_base, f"{story_id}_Reading_Guide.docx")
        doc.save(doc_path)
        
    print(f"\nSuccess! Exported MD, PDF, and DOCX for {len(stories)} stories.")

if __name__ == "__main__":
    generate_guides()