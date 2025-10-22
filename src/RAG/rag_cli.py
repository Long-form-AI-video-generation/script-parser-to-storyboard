"""
Simple CLI for the Anime Script RAG System

Basic commands for:
- Adding PDFs to the vector database
- Querying for relevant context
- Getting context for video generation
"""

import argparse
import sys
from pathlib import Path
from rag_system import AnimeScriptRAG


def main():
    parser = argparse.ArgumentParser(description="Anime Script RAG System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add PDF command
    add_parser = subparsers.add_parser('add', help='Add a PDF script to the RAG system')
    add_parser.add_argument('pdf_path', help='Path to the PDF file')
    add_parser.add_argument('--name', help='Name for the source (defaults to PDF filename)')
    add_parser.add_argument('--chunk-size', type=int, default=512, help='Chunk size for text processing')
    add_parser.add_argument('--chunk-overlap', type=int, default=50, help='Overlap between chunks')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system for relevant context')
    query_parser.add_argument('query', help='Search query')
    query_parser.add_argument('--top-k', type=int, default=5, help='Number of top results to return')
    query_parser.add_argument('--format', choices=['simple', 'detailed'], default='simple', 
                             help='Output format')
    
    # Context command (for video generation)
    context_parser = subparsers.add_parser('context', help='Get formatted context for video generation')
    context_parser.add_argument('prompt', help='Video generation prompt')
    context_parser.add_argument('--max-length', type=int, default=2000, 
                               help='Maximum context length')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show database information')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear the vector database')
    clear_parser.add_argument('--confirm', action='store_true', 
                             help='Confirm database clearing')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize RAG system
    rag = AnimeScriptRAG()
    
    if args.command == 'add':
        success = rag.add_pdf_to_rag(args.pdf_path, args.name)
        if success:
            print(f"✅ Successfully added {args.pdf_path} to RAG system")
        else:
            print(f"❌ Failed to add {args.pdf_path} to RAG system")
            sys.exit(1)
    
    elif args.command == 'query':
        results = rag.retrieve_relevant_context(args.query, args.top_k)
        
        if not results:
            print("No relevant results found.")
            return
        
        print(f"\n🔍 Query: '{args.query}'")
        print(f"📊 Found {len(results)} relevant results:\n")
        
        for i, result in enumerate(results, 1):
            if args.format == 'detailed':
                print(f"--- Result {i} ---")
                print(f"Similarity Score: {result['similarity_score']:.3f}")
                print(f"Source: {result['metadata']['source']['name']}")
                print(f"Chunk ID: {result['metadata']['chunk_id']}")
                print(f"Content: {result['text'][:200]}...")
                print()
            else:
                print(f"{i}. [{result['similarity_score']:.3f}] {result['text'][:100]}...")
    
    elif args.command == 'context':
        context = rag.get_rag_context_for_prompt(args.prompt, args.max_length)
        print("📝 RAG Context for Video Generation:")
        print("=" * 50)
        print(context)
    
    elif args.command == 'info':
        info = rag.get_database_info()
        print("📊 RAG Database Information:")
        print("=" * 30)
        for key, value in info.items():
            print(f"{key}: {value}")
    
    elif args.command == 'clear':
        if not args.confirm:
            print("⚠️  This will clear the entire vector database!")
            print("Use --confirm flag to proceed.")
            return
        
        import shutil
        if rag.vector_db_path.exists():
            shutil.rmtree(rag.vector_db_path)
            print("🗑️  Vector database cleared successfully")
        else:
            print("ℹ️  No vector database found to clear")


if __name__ == "__main__":
    main()
