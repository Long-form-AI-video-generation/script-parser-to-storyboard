import PyPDF2
import re

def load_script(pdf_path: str) -> str:

    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        
    text = re.sub(r'\s+', ' ', text).strip()
    return text
