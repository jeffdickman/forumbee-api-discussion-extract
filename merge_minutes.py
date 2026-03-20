import os
from datetime import datetime
from PyPDF2 import PdfMerger

def merge_pdfs():
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize PDF merger
    merger = PdfMerger()
    
    # Get all PDF files in the minutes directory
    minutes_dir = os.path.join(os.path.dirname(__file__), 'minutes')
    pdf_files = [f for f in os.listdir(minutes_dir) if f.lower().endswith('.pdf')]
    
    # Sort files alphabetically
    pdf_files.sort()
    
    # Add each PDF to the merger
    for pdf in pdf_files:
        pdf_path = os.path.join(minutes_dir, pdf)
        merger.append(pdf_path)
        print(f"Added: {pdf}")
    
    # Create output filename with timestamp
    output_filename = f"{timestamp}_minutes.pdf"
    output_path = os.path.join(os.path.dirname(__file__), 'outputs', output_filename)
    
    # Create outputs directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write the merged PDF
    merger.write(output_path)
    merger.close()
    
    print(f"\nMerged PDF created: {output_filename}")

if __name__ == "__main__":
    merge_pdfs()
