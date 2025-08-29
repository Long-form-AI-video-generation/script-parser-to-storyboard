import os
import fitz  # PyMuPDF
import argparse
from pathlib import Path
from datetime import datetime 

# The scripts extracts all the text from a pdf file
# The script then splits the script to a smalled chunks based on an argument parse amount of characters
# returns the splitted txt files and saves them in .txt files in an output directory 

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a given PDF file.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        return ""
    try:
        doc = fitz.open(pdf_path)
        full_text = "".join(page.get_text() for page in doc)
        doc.close()
        print(f"Successfully extracted text from '{Path(pdf_path).name}'.")
        return full_text
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return ""

def chunk_text(text: str, chunk_size: int, overlap_size: int) -> list[str]:
    """
    Splits a long text into smaller, overlapping chunks.
    """
    if overlap_size >= chunk_size:
        raise ValueError("Overlap size must be smaller than chunk size.")

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap_size
        
    print(f"Text split into {len(chunks)} overlapping chunks.")
    return chunks

def save_chunks_to_files(chunks: list[str], original_pdf_path: str, chunk_size: int, overlap_size: int):
    """
    Saves each chunk to a separate .txt file and creates a manifest.
    """
    base_name = Path(original_pdf_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder_name = f"{base_name}_chunks_{timestamp}"
    output_dir = Path("output") / "chunked_scripts" / output_folder_name
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving chunks to: '{output_dir}'")

    chunk_paths = []
    for i, chunk_content in enumerate(chunks):
        chunk_filename = f"chunk_{i+1:03d}.txt" # e.g., chunk_001.txt
        chunk_path = output_dir / chunk_filename
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(chunk_content)
        chunk_paths.append(str(chunk_path))
    
    # a manifest file to save some meta datas 
    manifest_path = output_dir / "chunks_manifest.txt"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(f"Source PDF: {original_pdf_path}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Chunk Size (chars): {chunk_size}\n")
        f.write(f"Overlap Size (chars): {overlap_size}\n")
        f.write(f"Total Chunks: {len(chunks)}\n\n")
        f.write("--- Chunk Order ---\n")
        for i, path in enumerate(chunk_paths):
            f.write(f"Chunk {i+1:03d}: {Path(path).name}\n") 
            
    print(f"All {len(chunks)} chunks and manifest saved successfully.")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts and chunks a PDF script for offline LLM processing.")
    parser.add_argument("pdf_path", help="Path to the input PDF script file.")
    parser.add_argument("--chunk_size", type=int, default=4000, help="The character size of each text chunk.")
    parser.add_argument("--overlap_size", type=int, default=400, help="The character overlap between consecutive chunks.")
    args = parser.parse_args()

    
    raw_script_text = extract_text_from_pdf(args.pdf_path)
    if not raw_script_text:
        exit()
    
    script_chunks = chunk_text(raw_script_text, args.chunk_size, args.overlap_size)
    if not script_chunks:
        exit()

    save_chunks_to_files(script_chunks, args.pdf_path, args.chunk_size, args.overlap_size)
    print("\nOffline chunking complete. Chunks are ready.")