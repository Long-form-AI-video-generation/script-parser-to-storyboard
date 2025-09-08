
import os
import fitz  # PyMuPDF
import requests
import argparse
from pathlib import Path
from dotenv import load_dotenv 
import json

load_dotenv()


# The script will now automatically look for the OPENROUTER_API_KEY in your .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "x-ai/grok-code-fast-1" 

if not OPENROUTER_API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found. Please create a .env file and add your key.")
    exit()

# --- Function Definitions ---

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text content from a given PDF file."""
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

def load_prompt_template(prompt_path: str) -> str:
    """Loads the master prompt template from a text file."""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at '{prompt_path}'")
        return ""

def parse_script_with_openrouter(script_text: str, prompt_template: str) -> str:
    """Sends the script text and a prompt to the OpenRouter model for parsing."""
    full_prompt = f"{prompt_template}\n\n---\n\nSCRIPT CONTENT:\n\n{script_text}"

    print(f"Sending script to the {MODEL} model for parsing... (This may take a moment)")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": script_text}
        ]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        parsed_content = response.json()["choices"][0]["message"]["content"]
        print(f"Successfully received parsed script from the {MODEL} model.")
        return parsed_content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with the OpenRouter API: {e}")
        return ""

def save_output_to_file(content: str, original_pdf_path: str):
    """Saves the parsed content to a new text file in the 'output' directory."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(original_pdf_path).stem
    output_filename = f"{base_name}_parsed.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Parsed script saved successfully to: '{output_path}'")

# --- Main Execution Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a script from a PDF file using the OpenRouter API.")
    parser.add_argument("pdf_path", help="The path to the input PDF script file.")
    parser.add_argument(
        "--prompt",
        default="prompts/master_parsing_prompt.txt",
        help="Path to the master prompt text file."
    )
    args = parser.parse_args()

    # --- Script Execution Flow ---
    master_prompt = load_prompt_template(args.prompt)
    if not master_prompt: exit()

    raw_script_text = extract_text_from_pdf(args.pdf_path)
    if not raw_script_text: exit()

    parsed_script = parse_script_with_openrouter(raw_script_text, master_prompt)
    if not parsed_script: exit()

    save_output_to_file(parsed_script, args.pdf_path)

