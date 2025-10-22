# Basic RAG System for Anime Script Processing

This directory contains a simple Retrieval-Augmented Generation (RAG) system designed to enhance anime script processing and video generation by providing relevant context from script databases.

## Overview

The RAG system consists of three main components:

1. **`rag_system.py`** - Core RAG functionality with vector database management
2. **`rag_cli.py`** - Simple command-line interface for managing the RAG system
3. **`rag_integration.py`** - Basic integration with existing storyboard generation workflow
4. **`test_rag_system.py`** - Test suite for validating RAG functionality

## Features

- **PDF Processing**: Extract text from anime script PDFs
- **Vector Database**: Store and search script embeddings using FAISS
- **Context Retrieval**: Find relevant script context for video generation prompts
- **Simple Integration**: Basic enhancement of storyboard generation workflow
- **CLI Interface**: Easy-to-use command-line tools for management

## Installation

1. Install the required dependencies:
```bash
pip install -r ../requirements.txt
```

2. The RAG system will automatically download the sentence transformer model on first use.

## Quick Start

### 1. Add a PDF Script to the RAG Database

```bash
cd src/RAG
python rag_cli.py add /path/to/your/anime_script.pdf --name "My Anime Script"
```

### 2. Query the Database

```bash
# Simple query
python rag_cli.py query "character dialogue about friendship"

# Detailed results
python rag_cli.py query "battle scene" --format detailed --top-k 3
```

### 3. Get Context for Video Generation

```bash
python rag_cli.py context "Generate a video of the main character discovering their powers"
```

### 4. Enhance a Storyboard

```bash
python rag_integration.py enhance /path/to/storyboard.md --output enhanced_storyboard.md
```

## Usage Examples

### Basic RAG Operations

```python
from rag_system import AnimeScriptRAG

# Initialize RAG system
rag = AnimeScriptRAG()

# Add a PDF script
rag.add_pdf_to_rag("anime_script.pdf", "My Script")

# Query for relevant context
results = rag.retrieve_relevant_context("character development scene", top_k=5)

# Get formatted context for video generation
context = rag.get_rag_context_for_prompt("Generate video of emotional scene")
```

### Integration with Existing Workflow

```python
from rag_integration import RAGPromptGenerator

# Initialize simple generator
generator = RAGPromptGenerator()

# Enhance a storyboard with RAG context
enhanced_storyboard = generator.enhance_storyboard_prompt(storyboard_text)

# Enhance a video generation prompt
enhanced_prompt = generator.enhance_video_generation_prompt("Create video of action scene")
```

## CLI Commands

### RAG Management (`rag_cli.py`)

- `add <pdf_path>` - Add a PDF script to the database
- `query <query>` - Search the database for relevant content
- `context <prompt>` - Get formatted context for video generation
- `info` - Show database information
- `clear --confirm` - Clear the entire database

### Integration (`rag_integration.py`)

- `enhance <storyboard_file>` - Enhance a storyboard with RAG context
- `enhance-prompt <prompt>` - Enhance a video generation prompt

## Configuration

The RAG system can be configured with the following parameters:

- **`embedding_model`**: Sentence transformer model (default: "all-MiniLM-L6-v2")
- **`chunk_size`**: Size of text chunks (default: 512 characters)
- **`chunk_overlap`**: Overlap between chunks (default: 50 characters)
- **`vector_db_path`**: Path to store vector database (default: "rag_vector_db")

## Testing

Run the test suite to validate the RAG system:

```bash
python test_rag_system.py
```

This will:
1. Create a sample anime script
2. Add it to the RAG database
3. Test various queries
4. Test storyboard enhancement
5. Clean up test files

## File Structure

```
RAG/
├── rag_system.py          # Core RAG functionality
├── rag_cli.py            # Command-line interface
├── rag_integration.py    # Workflow integration
├── test_rag_system.py    # Test suite
├── README.md             # This file
└── rag_vector_db/        # Vector database storage (created automatically)
    ├── faiss_index.bin   # FAISS vector index
    ├── chunks.pkl        # Text chunks
    ├── metadata.pkl      # Chunk metadata
    └── config.json       # Configuration
```

## How It Works

1. **PDF Processing**: Scripts are extracted and split into overlapping chunks
2. **Embedding Generation**: Each chunk is converted to a vector using sentence transformers
3. **Vector Storage**: Embeddings are stored in a FAISS index for fast similarity search
4. **Context Retrieval**: Queries are converted to embeddings and matched against stored vectors
5. **Context Enhancement**: Retrieved context is formatted and combined with generation prompts

## Integration with Main Workflow

The RAG system enhances the existing script-parser-to-storyboard workflow:

1. **Script Parsing**: Original scripts are processed and added to RAG database
2. **Storyboard Generation**: RAG context enhances storyboard creation
3. **Prompt Generation**: Video generation prompts are enriched with relevant script context
4. **Video Generation**: AI models receive better context for more accurate results

## Troubleshooting

### Common Issues

1. **Model Download**: First run may take time to download the sentence transformer model
2. **Memory Usage**: Large PDFs may require significant memory for processing
3. **File Permissions**: Ensure write permissions for the vector database directory
