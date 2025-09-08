import os
import google.generativeai as genai
import argparse
from pathlib import Path
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()


# --- Configuration for Google Gemini API ---
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-2.5-flash" 
except (ValueError, TypeError) as e:
    print(f"ERROR: Configuration failed. {e}")
    exit()
    

# --- Function Definitions ---

def load_chunk_files_from_manifest(chunks_directory: str) -> list[str]:
    """
    Reads the manifest file to get the correct order of chunks, then loads their content.
    """
    directory_path = Path(chunks_directory)
    manifest_path = directory_path / "chunks_manifest.txt"

    if not manifest_path.exists():
        print(f"Error: 'chunks_manifest.txt' not found in '{chunks_directory}'")
        return []

    print(f"Reading manifest from: '{manifest_path}'")
    chunk_filenames = []
    chunk_pattern = re.compile(r"Chunk \d+:\s*(chunk_\d+\.txt)")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = chunk_pattern.match(line.strip())
            print(match)
            if match:
                chunk_filenames.append(match.group(1))

    if not chunk_filenames:
        print("Error: No chunk files listed in the manifest.")
        return []

    print(f"Found {len(chunk_filenames)} chunks to process.")
    
    chunk_contents = []
    for filename in chunk_filenames:
        chunk_path = directory_path / filename
        if chunk_path.exists():
            with open(chunk_path, 'r', encoding='utf-8') as f:
                chunk_contents.append(f.read())
        else:
            print(f"Warning: Chunk file '{filename}' not found. Skipping.")

    return chunk_contents

def load_prompt_template(prompt_path: str) -> str:
    """Loads the storyboard generation prompt from a text file."""
    try:
        with open(prompt_path, 'r', encodings='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at '{prompt_path}'")
        return ""

def generate_storyboard_from_chunks(chunks: list[str], prompt_template: str) -> str:
    """
    Sends each chunk to the Gemini API to generate storyboard panels.
    """
    all_responses = []
    model = genai.GenerativeModel(MODEL)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    for i, chunk_content in enumerate(chunks):
        print(f"Generating storyboard for chunk {i+1}/{len(chunks)}...")
        full_prompt = f"{prompt_template}\n\n{chunk_content}"
        
        try:
            response = model.generate_content(full_prompt, safety_settings=safety_settings)
            all_responses.append(response.text)
        except Exception as e:
            print(f"An error occurred while processing chunk {i+1}: {e}")
            all_responses.append(f"--- ERROR PROCESSING CHUNK {i+1} ---")
            
    print("All chunks processed. Combining storyboard panels...")
    return "\n".join(all_responses)

def post_process_storyboard(raw_text: str) -> str:
    """
    Cleans up the combined storyboard text and attempts to remove duplicates.
    """
    panel_delimiter = "--- PANEL BREAK ---"
    all_panels_raw = raw_text.split(panel_delimiter)
    
    final_panels = []
    seen_action_descriptions = set()

    for panel_block in all_panels_raw:
        panel_block = panel_block.strip()
        if not panel_block:
            continue

        # Use the action description as a crude way to check for duplicate panels from overlap
        action_desc = ""
        lines = panel_block.split('\n')
        for line in lines:
            if line.strip().upper().startswith("ACTION_DESCRIPTION:"):
                action_desc = line.strip()
                break
        
        # If we haven't seen this exact action description before, add the panel
        if action_desc and action_desc not in seen_action_descriptions:
            final_panels.append(panel_block)
            seen_action_descriptions.add(action_desc)
        # If no action description is found, it might be a malformed block; add it anyway
        elif not action_desc:
            final_panels.append(panel_block)
            
    print(f"De-duplication complete. Kept {len(final_panels)} unique panels.")
    return f"\n\n{panel_delimiter}\n\n".join(final_panels)

def save_final_storyboard(content: str, source_directory: str):
    """Saves the final storyboard to a single Markdown file."""
    source_path = Path(source_directory)
    output_filename = f"{source_path.name}_storyboard.md" # Saving as Markdown for better formatting
    output_path = Path("output") / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Storyboard for {source_path.name}\n\n")
        f.write(content)
    print(f"Final storyboard saved successfully to: '{output_path}'")

# --- Main Execution Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a storyboard from pre-chunked script files using the Google Gemini API.")
    parser.add_argument("chunks_directory", help="The path to the directory containing the chunk files and manifest.")
    parser.add_argument("--prompt", default="../prompts/storyboard_generation_prompt.txt", help="Path to the storyboard generation prompt file.")
    args = parser.parse_args()

    # --- Execution Flow ---
    storyboard_prompt = load_prompt_template(args.prompt)
    if not storyboard_prompt: exit()

    script_chunks = load_chunk_files_from_manifest(args.chunks_directory)
    if not script_chunks: exit()

    raw_storyboard_output = generate_storyboard_from_chunks(script_chunks, storyboard_prompt)
    if not raw_storyboard_output: exit()

    final_storyboard = post_process_storyboard(raw_storyboard_output)

    save_final_storyboard(final_storyboard, args.chunks_directory)
    print("\nStoryboard generation complete.")