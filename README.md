# Script Parser to Storyboard

> **Convert PDF scripts into structured scene breakdowns and visual storyboard panels with AI-powered pipelines.**

This repository provides a dual-pipeline system for transforming screenplay PDFs into production-ready outputs. The **Script Parsing Pipeline** extracts structured scene information using OpenRouter, while the **Storyboard Generation Pipeline** creates detailed visual panel descriptions using Google Gemini, with intelligent chunking to handle feature-length scripts.

---

## Badges

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)![License](https://img.shields.io/badge/license-MIT-green.svg)![Status](https://img.shields.io/badge/status-active-success.svg)![AI Providers](https://img.shields.io/badge/AI-OpenRouter%20%7C%20Gemini-orange.svg)

---

## Table of Contents

- [Features](#-features)
- [Installation & Setup](#-installation--setup)
- [Architecture Overview](#-architecture-overview)
- [The Two Pipelines](#-the-two-pipelines)
- [Example Usage](#-example-usage)
- [Development Guide](#-development-guide)
- [Contributing Guidelines](#-contributing-guidelines)
- [License](#-license)
- [Maintainers & Acknowledgements](#-maintainers--acknowledgements)

---

## Features

-   **Dual-Pipeline Design**: Choose between two independent workflows for different production needs:
    -   **Pipeline A (Script Parsing):** Quickly extracts scene headings, actions, and dialogue into a structured text format. Ideal for script analysis and data extraction.
    -   **Pipeline B (Storyboard Generation):** Creates detailed, visual storyboard panel descriptions with inferred camera shots. Perfect for pre-visualization and animation.

-   **Multi-Provider AI Strategy**: Leverages the unique strengths of different AI models:
    -   **OpenRouter (Grok)** is used for its speed and accuracy in structured text parsing.
    -   **Google Gemini** is used for its powerful visual reasoning and creative description capabilities.

-   **Intelligent Chunking for Large Scripts**: Pipeline B automatically handles feature-length scripts by:
    -   Splitting text into configurable, overlapping chunks to preserve context.
    -   Deduplicating panels generated from overlapping regions.
    -   Using a manifest file to ensure correct chunk ordering and processing.

-   **Template-Driven Prompts**: Easily customize the AI's output by editing plain text prompt templates, allowing for full control over the final format and style.

---

## Installation & Setup

### Prerequisites

-   **Python 3.10+**
-   **pip** package manager
-   **API Keys**:
    -   [OpenRouter API Key](https://openrouter.ai/) (for Pipeline A)
    -   [Google AI API Key](https://ai.google.dev/) (for Pipeline B)

### Installation Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Long-form-AI-video-generation/script-parser-to-storyboard.git
    cd script-parser-to-storyboard
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**

    Create a file named `.env` in the project root and add your API keys:

    ```text
    # .env
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    GOOGLE_API_KEY="your_google_api_key_here"
    ```
    **Important:** This file is ignored by Git to keep your keys secure.

4.  **Verify installation:**

    ```bash
    python src/parse_script.py --help
    python src/generate_storyboard.py --help
    ```

---

## Architecture Overview

The system is designed with two distinct, parallel pipelines that process a PDF script into different outputs, configured by separate prompt templates and API keys.

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                              │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────┐│
│  │  PDF Script  │  │ .env (API Keys)  │  │ Prompt Templates   ││
│  └──────────────┘  └──────────────────┘  └────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
         ┌──────────▼──────────┐ ┌─────▼──────────────────────┐
         │   PIPELINE A:       │ │   PIPELINE B:              │
         │   Script Parsing    │ │   Storyboard Generation    │
         │                     │ │                            │
         │  ┌──────────────┐  │ │  ┌──────────────────────┐  │
         │  │ PDF Extract  │  │ │  │ PDF Extract + Chunk  │  │
         │  └──────┬───────┘  │ │  └──────┬───────────────┘  │
         │         │          │ │         │                  │
         │  ┌──────▼───────┐  │ │  ┌──────▼───────────────┐  │
         │  │  OpenRouter  │  │ │  │   Google Gemini      │  │
         │  │  (Grok AI)   │  │ │  │   (Multi-chunk)      │  │
         │  └──────┬───────┘  │ │  └──────┬───────────────┘  │
         │         │          │ │         │                  │
         │  ┌──────▼───────┐  │ │  ┌──────▼───────────────┐  │
         │  │ Structured   │  │ │  │  Post-Process +      │  │
         │  │ Scene Text   │  │ │  │  Deduplication       │  │
         │  └──────────────┘  │ │  └──────────────────────┘  │
         └─────────────────────┘ └───────────────────────────┘
                    │                   │
         ┌──────────▼──────────┐ ┌─────▼──────────────────────┐
         │  output/             │ │  output/                   │
         │  *_parsed.txt        │ │  *_storyboard.md           │
         └─────────────────────┘ └───────────────────────────┘
```

---

## The Two Pipelines

### Pipeline A: Script Parsing

-   **Purpose**: To quickly extract structured scene information (headings, actions, dialogue) from a PDF into a clean text file.
-   **Workflow**: `PDF → Extract Text → OpenRouter (Grok) → Structured Scenes (.txt)`
-   **AI Provider**: OpenRouter (optimised for speed and text analysis).
-   **Output Format**:
    ```text
    SCENE_HEADING: INT. APARTMENT - NIGHT
    ACTION: Character enters room, looks around nervously.
    DIALOGUE: CHARACTER: I need to find it before they do.
    CAMERA_DIRECTIONS: CLOSE UP ON CHARACTER'S FACE.

    ---SCENE BREAK---
    ```

### Pipeline B: Storyboard Generation

-   **Purpose**: To generate detailed, visual storyboard panel descriptions, complete with inferred camera shots, suitable for pre-visualization.
-   **Workflow**: `PDF → Chunk Text → Gemini (per chunk) → Deduplicate → Storyboard (.md)`
-   **AI Provider**: Google Gemini (optimised for creative and visual reasoning).
-   **Output Format**:
    ```markdown
    PANEL 001
    SHOT_TYPE: ESTABLISHING SHOT
    SUBJECT: City skyline at night
    ACTION_DESCRIPTION: Wide view of neon-lit cityscape with rain falling.
    DIALOGUE:

    --- PANEL BREAK ---
    ```

---

## Example Usage

### Pipeline A: Script Parsing (Single Command)

```bash
# Basic usage
python src/parse_script.py input/my_script.pdf

# With a custom parsing prompt
python src/parse_script.py input/my_script.pdf --prompt prompts/custom_parsing.txt
```

-   **Output will be saved to:** `output/my_script_parsed.txt`

### Pipeline B: Storyboard Generation (Two-Step Process)

**Step 1: Chunk the script**

```bash
# Basic usage with default chunk settings
python src/parse_script_chunker.py input/my_script.pdf

# With custom chunk settings
python src/parse_script_chunker.py input/my_script.pdf --chunk_size 5000 --overlap_size 500
```

-   **Chunks will be saved to:** `output/chunked_scripts/my_script_chunks_YYYYMMDD_HHMMSS/`

**Step 2: Generate the storyboard from the chunks**

```bash
# Provide the path to the directory created in Step 1
python src/generate_storyboard.py output/chunked_scripts/my_script_chunks_.../
```

-   **Output will be saved to:** `output/my_script_chunks_..._storyboard.md`

---

## 🛠️ Development Guide

### Project Structure

```text
script-parser-to-storyboard/
├── src/                             # Core Python scripts
│   ├── parse_script.py              # Pipeline A: Script parsing
│   ├── parse_script_chunker.py      # Pipeline B, Step 1: Chunking
│   └── generate_storyboard.py       # Pipeline B, Step 2: Generation
├── prompts/                         # Customizable prompt templates
│   ├── master_parsing_prompt.txt
│   └── storyboard_generation_prompt.txt
├── output/                          # Generated outputs (ignored by Git)
├── requirements.txt                 # Python dependencies
└── .env                             # API keys (ignored by Git)
```

### Core Scripts Reference

| Script                        | Purpose                                     | AI Provider      |
| :---------------------------- | :------------------------------------------ | :--------------- |
| `parse_script.py`             | Runs the fast Script Parsing pipeline.      | OpenRouter (Grok)|
| `parse_script_chunker.py`     | Chunks a PDF for the Storyboard pipeline.   | (None)           |
| `generate_storyboard.py`      | Generates a storyboard from chunked files.  | Google Gemini    |

---

## Contributing Guidelines

Contributions are welcome! Please follow this workflow to submit changes.

1.  **Fork the repository.**
2.  **Create a feature branch** (`git checkout -b feature/your-new-feature`).
3.  **Commit your changes** (`git commit -m 'feat: Add some amazing feature'`).
4.  **Push to the branch** (`git push origin feature/your-new-feature`).
5.  **Open a Pull Request.**

Please adhere to **PEP 8** coding standards and include docstrings for new functions.

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## Maintainers & Acknowledgements

### Maintainers

**Long-form AI Video Generation Team**

-   Repository: [Long-form-AI-video-generation](https://github.com/Long-form-AI-video-generation)

### Acknowledgements

This project stands on the shoulders of giants. Special thanks to:

-   **PyMuPDF**, **OpenRouter**, and **Google Gemini** for their powerful tools and services.
-   The **Open Source Community** for providing the libraries and inspiration that make this project possible.

---

<div align="center">

**⭐ If this project helps your workflow, consider giving it a star! ⭐**

[⬆ Back to Top](#script-parser-to-storyboard)

</div>
