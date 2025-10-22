"""
Simple RAG Integration

Basic integration with the script-parser-to-storyboard workflow.
Provides relevant context from the script database for video generation prompts.
"""

import os
import argparse
from pathlib import Path
from typing import Optional
from rag_system import AnimeScriptRAG


class RAGPromptGenerator:
    """
    Simple prompt generator that uses RAG context to improve video generation prompts.
    """
    
    def __init__(self, rag_db_path: str = "rag_vector_db"):
        """
        Initialize the RAG prompt generator.
        
        Args:
            rag_db_path: Path to the RAG vector database
        """
        self.rag = AnimeScriptRAG(vector_db_path=rag_db_path)
    
    def enhance_storyboard_prompt(self, storyboard_text: str) -> str:
        """
        Enhance a storyboard with RAG context for better video generation.
        
        Args:
            storyboard_text: The storyboard text to enhance
            
        Returns:
            Enhanced storyboard with RAG context
        """
        # Extract key information from storyboard for RAG query
        rag_query = self._extract_rag_query_from_storyboard(storyboard_text)
        
        # Get relevant context from RAG system
        rag_context = self.rag.get_rag_context_for_prompt(rag_query, max_context_length=1500)
        
        # Combine original storyboard with RAG context
        enhanced_storyboard = f"{rag_context}\n\n=== STORYBOARD CONTENT ===\n{storyboard_text}"
        
        return enhanced_storyboard
    
    def enhance_video_generation_prompt(self, video_prompt: str) -> str:
        """
        Enhance a video generation prompt with RAG context.
        
        Args:
            video_prompt: The original video generation prompt
            
        Returns:
            Enhanced prompt with relevant script context
        """
        # Get relevant context from RAG system
        rag_context = self.rag.get_rag_context_for_prompt(video_prompt, max_context_length=1000)
        
        # Combine prompt with context
        enhanced_prompt = f"{rag_context}\n\n=== VIDEO GENERATION PROMPT ===\n{video_prompt}"
        
        return enhanced_prompt
    
    def _extract_rag_query_from_storyboard(self, storyboard_text: str) -> str:
        """
        Extract a simple query from storyboard text for RAG retrieval.
        
        Args:
            storyboard_text: The storyboard text
            
        Returns:
            Extracted query string
        """
        # Simple extraction: look for action descriptions and dialogue
        lines = storyboard_text.split('\n')
        query_parts = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('ACTION_DESCRIPTION:'):
                action = line.replace('ACTION_DESCRIPTION:', '').strip()
                if action:
                    query_parts.append(action)
            elif line.startswith('DIALOGUE:'):
                dialogue = line.replace('DIALOGUE:', '').strip()
                if dialogue:
                    query_parts.append(dialogue)
        
        # Combine query parts
        if query_parts:
            return ' '.join(query_parts[:2])  # Use first 2 relevant parts
        else:
            # Fallback: use first 100 characters
            return storyboard_text[:100].strip()
    
    def process_storyboard_file(self, storyboard_file_path: str, 
                              output_path: Optional[str] = None) -> str:
        """
        Process a storyboard file and enhance it with RAG context.
        
        Args:
            storyboard_file_path: Path to the storyboard file
            output_path: Optional output path (defaults to input file with _enhanced suffix)
            
        Returns:
            Path to the enhanced storyboard file
        """
        storyboard_path = Path(storyboard_file_path)
        
        # Read the storyboard file
        with open(storyboard_path, 'r', encoding='utf-8') as f:
            storyboard_content = f.read()
        
        # Enhance with RAG context
        enhanced_content = self.enhance_storyboard_prompt(storyboard_content)
        
        # Determine output path
        if output_path is None:
            output_path = storyboard_path.parent / f"{storyboard_path.stem}_enhanced{storyboard_path.suffix}"
        
        # Save enhanced storyboard
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ Enhanced storyboard saved to: {output_path}")
        return str(output_path)


def main():
    """Simple CLI for RAG integration."""
    parser = argparse.ArgumentParser(description="Simple RAG Integration for Storyboard Enhancement")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Enhance storyboard command
    enhance_parser = subparsers.add_parser('enhance', help='Enhance a storyboard with RAG context')
    enhance_parser.add_argument('storyboard_file', help='Path to the storyboard file')
    enhance_parser.add_argument('--output', help='Output path for enhanced storyboard')
    
    # Enhance prompt command
    prompt_parser = subparsers.add_parser('enhance-prompt', help='Enhance a video generation prompt')
    prompt_parser.add_argument('prompt', help='Video generation prompt to enhance')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize RAG generator
    generator = RAGPromptGenerator()
    
    if args.command == 'enhance':
        output_path = generator.process_storyboard_file(args.storyboard_file, args.output)
        print(f"Enhanced storyboard saved to: {output_path}")
    
    elif args.command == 'enhance-prompt':
        enhanced_prompt = generator.enhance_video_generation_prompt(args.prompt)
        print("Enhanced Video Generation Prompt:")
        print("=" * 40)
        print(enhanced_prompt)


if __name__ == "__main__":
    main()
