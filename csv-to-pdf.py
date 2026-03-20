"""
CSV to PDF Converter Script

This script converts the most recent CSV file in the outputs directory to a PDF.
It wraps text at 75 characters and preserves all content.

Usage:
    python csv-to-pdf.py
"""

import os
import glob
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from textwrap import wrap
from PyPDF2 import PdfReader, PdfWriter

def get_latest_csv():
    """
    Get the most recent CSV file from the outputs directory.
    
    Returns:
        str: Path to the most recent CSV file
    """
    output_dir = "./outputs"
    csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found in outputs directory")
    return max(csv_files, key=os.path.getctime)

def wrap_text(text, width=75):
    """
    Wrap text to specified width, preserving newlines.
    
    Args:
        text (str): Text to wrap
        width (int): Maximum width in characters
        
    Returns:
        str: Wrapped text
    """
    if pd.isna(text):
        return ""
    
    # Split by newlines and wrap each line
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        wrapped_lines.extend(wrap(line, width=width))
    return '\n'.join(wrapped_lines)

def get_file_size_mb(file_path):
    """
    Get file size in megabytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def split_pdf(pdf_path, max_size_mb=17):
    """
    Split a PDF file into smaller files if it exceeds the maximum size.
    This function handles recursive splitting if needed.
    
    Args:
        pdf_path (str): Path to the PDF file to split
        max_size_mb (float): Maximum size in MB for each split file
        
    Returns:
        list: List of paths to the split PDF files
    """
    file_size_mb = get_file_size_mb(pdf_path)
    
    if file_size_mb <= max_size_mb:
        print(f"PDF size ({file_size_mb:.2f} MB) is within limit. No splitting needed.")
        return [pdf_path]
    
    print(f"PDF size ({file_size_mb:.2f} MB) exceeds {max_size_mb} MB limit. Splitting...")
    
    # Read the original PDF
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    # Calculate approximate pages per split based on file size ratio
    # This is a rough estimate - we'll refine as we go
    estimated_pages_per_split = int(total_pages * (max_size_mb / file_size_mb))
    if estimated_pages_per_split < 1:
        estimated_pages_per_split = 1
    
    split_files = []
    base_name = os.path.splitext(pdf_path)[0]
    part_number = 1
    page_start = 0
    
    while page_start < total_pages:
        # Create a new PDF writer for this split
        writer = PdfWriter()
        
        # Add pages to this split, starting with our estimate
        pages_in_this_split = min(estimated_pages_per_split, total_pages - page_start)
        
        for page_num in range(page_start, page_start + pages_in_this_split):
            writer.add_page(reader.pages[page_num])
        
        # Create the split file
        split_file_path = f"{base_name}_part{part_number}.pdf"
        
        with open(split_file_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Check if this split is still too large
        split_size_mb = get_file_size_mb(split_file_path)
        
        if split_size_mb > max_size_mb and pages_in_this_split > 1:
            # This split is still too large, we need to reduce pages
            os.remove(split_file_path)  # Remove the oversized file
            
            # Reduce the number of pages and try again
            estimated_pages_per_split = max(1, int(estimated_pages_per_split * 0.8))
            continue
        
        print(f"Created {split_file_path} ({split_size_mb:.2f} MB, {pages_in_this_split} pages)")
        split_files.append(split_file_path)
        
        page_start += pages_in_this_split
        part_number += 1
        
        # If we successfully created a split, we can use the same page count for the next one
        # unless we're near the end
        remaining_pages = total_pages - page_start
        if remaining_pages > 0 and remaining_pages < estimated_pages_per_split:
            estimated_pages_per_split = remaining_pages
    
    # Remove the original large file
    os.remove(pdf_path)
    print(f"Original file {pdf_path} removed after splitting into {len(split_files)} parts.")
    
    # Recursively check if any split files are still too large
    final_files = []
    for split_file in split_files:
        if get_file_size_mb(split_file) > max_size_mb:
            print(f"Split file {split_file} is still too large, splitting further...")
            further_splits = split_pdf(split_file, max_size_mb)
            final_files.extend(further_splits)
        else:
            final_files.append(split_file)
    
    return final_files

def create_pdf(csv_path):
    """
    Create a PDF from the CSV file.
    
    Args:
        csv_path (str): Path to the CSV file
    """
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Create PDF filename (same as CSV but with .pdf extension)
    pdf_path = os.path.splitext(csv_path)[0] + '.pdf'
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12
    )
    
    # Create story (content) for PDF
    story = []
    
    # Add title
    story.append(Paragraph("Forumbee Posts Export", title_style))
    story.append(Spacer(1, 12))
    
    # Process each post
    for index, row in df.iterrows():
        # Add post number
        story.append(Paragraph(f"Post {index + 1}", heading_style))
        
        # Add category
        story.append(Paragraph(f"Category: {row['category.name']}", body_style))
        
        # Add author
        story.append(Paragraph(f"Author: {row['author.name']}", body_style))
        
        # Add title
        story.append(Paragraph(f"Title: {row['title']}", body_style))
        
        # Add posted date
        story.append(Paragraph(f"Posted: {row['posted']}", body_style))
        
        # Add URL
        story.append(Paragraph(f"URL: {row['url']}", body_style))
        
        # Add content (wrapped)
        wrapped_content = wrap_text(row['textPlain'])
        story.append(Paragraph("Content:", body_style))
        story.append(Paragraph(wrapped_content, body_style))
        
        # Add separator
        story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    print(f"PDF created: {pdf_path}")
    
    return pdf_path

if __name__ == "__main__":
    try:
        # Get the most recent CSV file
        latest_csv = get_latest_csv()
        print(f"Processing: {latest_csv}")
        
        # Create PDF
        pdf_path = create_pdf(latest_csv)
        
        # Check file size and split if necessary
        print(f"\nChecking PDF file size...")
        file_size_mb = get_file_size_mb(pdf_path)
        print(f"PDF size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 17:
            print(f"PDF exceeds 17MB limit. Splitting into smaller files...")
            split_files = split_pdf(pdf_path, max_size_mb=17)
            print(f"\nSplitting complete! Created {len(split_files)} files:")
            for i, split_file in enumerate(split_files, 1):
                split_size = get_file_size_mb(split_file)
                print(f"  {i}. {split_file} ({split_size:.2f} MB)")
        else:
            print(f"PDF is within size limit. No splitting needed.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}") 