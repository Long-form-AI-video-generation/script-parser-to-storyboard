import os
import google.generativeai as genai
import argparse
from pathlib import Path
from dotenv import load_dotenv
import re

# Load environment variables and configure the Gemini API
load_dotenv()
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found")
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-2.5-flash" 
except (ValueError, TypeError) as e:
    print(f"ERROR: Configuration failed. {e}")
    exit()

def split_storyboard_into_scenes(storyboard_text: str) -> list[str]:
    """
    Splits a full storyboard text into a list of scenes.
    A new scene is identified by the pattern "PANEL 001".
    """
    print("Splitting storyboard into individual scenes...")
    # We split the text at every occurrence of "PANEL 001" and keep the delimiter.
    # The (?=...) is a "positive lookahead" that finds the split point without consuming the text.
    scenes = re.split(r'(?=PANEL 001)', storyboard_text)
    
    # The first item might be empty or a header if the file starts with "PANEL 001", so we filter.
    cleaned_scenes = [scene.strip() for scene in scenes if scene.strip() and "PANEL" in scene]
    
    print(f"Found {len(cleaned_scenes)} distinct scenes to process.")
    return cleaned_scenes

def load_prompt_template(prompt_path: str) -> str:
    """Loads the prompt generation meta-prompt."""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at '{prompt_path}'")
        return ""

def generate_prompts_for_scene(scene_text: str, prompt_template: str) -> str:
    """
    Sends a single scene's storyboard to the Gemini API to generate its prompts.
    """
    full_prompt = f"{prompt_template}\n\n--- STORYBOARD CONTENT ---\n\n{scene_text}"
    
    try:
        model = genai.GenerativeModel(MODEL)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = model.generate_content(full_prompt, safety_settings=safety_settings)
        return response.text
    except Exception as e:
        print(f"An error occurred while communicating with the API: {e}")
        return f"--- ERROR PROCESSING SCENE ---\n{e}\n"

def save_generated_prompts(content: str, source_storyboard_path: str):
    """Saves the final combined prompts to a new Markdown file."""
    source_path = Path(source_storyboard_path)
    output_filename = f"{source_path.stem}_prompts_by_scene.md"
    output_path = Path("output") / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nFinal prompts saved successfully to: '{output_path}'")

# --- Main Execution Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates prompts from a storyboard file on a scene-by-scene basis.")
    parser.add_argument("storyboard_path", help="The path to the full storyboard file.")
    parser.add_argument("--prompt", default="../prompts/prompt_generation_meta_prompt.txt", help="Path to the prompt generation meta-prompt file.")
    args = parser.parse_args()

    meta_prompt = load_prompt_template(args.prompt)
    if not meta_prompt: exit()

    with open(args.storyboard_path, 'r', encoding='utf-8') as f:
        storyboard_content = f.read()
    if not storyboard_content: exit()

    # This is the new core logic
    scenes_to_process = split_storyboard_into_scenes(storyboard_content)
    if not scenes_to_process:
        print("No scenes were found in the storyboard file.")
        exit()

    all_generated_prompts = []
    for i, scene in enumerate(scenes_to_process):
        print(f"\n--- Processing Scene {i+1}/{len(scenes_to_process)} ---")
        generated_prompt_block = generate_prompts_for_scene(scene, meta_prompt)
        all_generated_prompts.append(generated_prompt_block)

    # Combine the processed output from all scenes into one file
    final_output = "\n\n".join(all_generated_prompts)
    save_generated_prompts(final_output, args.storyboard_path)

    print("\nScene-by-scene prompt generation complete.")