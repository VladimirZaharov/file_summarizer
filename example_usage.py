#!/usr/bin/env python3
"""
Example usage of the Document Summarizer.

This script demonstrates how to use the document summarizer as a library.
"""

import os
from pathlib import Path
from document_summarizer.main import DocumentSummarizer
from document_summarizer.config import Config


def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===\n")
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  OPENROUTER_API_KEY not set!")
        print("Please set it with: export OPENROUTER_API_KEY=your_key_here")
        print("Get free key from: https://openrouter.ai/\n")
        return
    
    # Initialize summarizer
    summarizer = DocumentSummarizer()
    
    # Run on default folder (downloaded_files)
    print("Processing documents from default folder...")
    report = summarizer.run(output_file="example_report.json")
    
    # Print summary
    if report:
        print("\n✓ Success!")
        print(f"Processed {report['statistics']['total_documents']} documents")
        print(f"\nMaster Summary:\n{report['master_summary']}")


def example_custom_folder():
    """Example with custom folder"""
    print("\n=== Custom Folder Example ===\n")
    
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  OPENROUTER_API_KEY not set!")
        return
    
    # Specify custom folder
    custom_folder = Path("my_documents")
    
    if not custom_folder.exists():
        print(f"Folder {custom_folder} doesn't exist. Creating example...")
        custom_folder.mkdir(exist_ok=True)
        
        # Create a sample file
        sample_file = custom_folder / "sample.txt"
        sample_file.write_text("""
This is a sample document for testing the Document Summarizer.

The Document Summarizer is a modular Python application that:
- Parses various document types (PDF, DOCX, TXT, etc.)
- Uses AI to generate summaries
- Supports free OpenRouter models
- Provides detailed reports

It's designed to be extensible and easy to use.
        """)
        print(f"Created sample document: {sample_file}")
    
    # Run summarizer on custom folder
    summarizer = DocumentSummarizer(model="google/gemini-flash-1.5:free")
    report = summarizer.run(folder_path=custom_folder, output_file="custom_report.json")
    
    if report:
        print("\n✓ Custom folder processed successfully!")


def example_as_library():
    """Example using as a library"""
    print("\n=== Library Usage Example ===\n")
    
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  OPENROUTER_API_KEY not set!")
        return
    
    from document_summarizer.file_parsers import FileParserFactory
    from document_summarizer.summarizer import Summarizer
    
    # Create a test document
    test_file = Path("test_document.txt")
    test_file.write_text("""
Artificial Intelligence in 2026

AI has become increasingly sophisticated, with models capable of understanding
context, generating creative content, and assisting in complex tasks.
The technology is now more accessible than ever, with free APIs and open-source
tools available to developers worldwide.
    """)
    
    print("1. Parsing document...")
    document = FileParserFactory.parse_file(test_file)
    print(f"   Extracted {len(document['content'])} characters")
    
    print("\n2. Generating summary...")
    summarizer = Summarizer()
    summarizer.summarize_document(document)
    
    print(f"\n3. Summary:\n{document.get('summary', 'No summary')}")
    
    # Cleanup
    test_file.unlink()
    print("\n✓ Example complete!")


def show_configuration():
    """Show current configuration"""
    print("\n=== Current Configuration ===\n")
    print(f"API Key Set: {'Yes' if Config.OPENROUTER_API_KEY else 'No'}")
    print(f"Default Model: {Config.DEFAULT_MODEL}")
    print(f"Download Folder: {Config.DOWNLOAD_FOLDER}")
    print(f"Supported Extensions: {', '.join(Config.SUPPORTED_EXTENSIONS)}")
    print(f"\nAlternative Models:")
    for model in Config.ALTERNATIVE_MODELS:
        print(f"  - {model}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          Document Summarizer - Example Usage            ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Show configuration
    show_configuration()
    
    # You can uncomment the examples you want to run:
    
    # example_basic_usage()
    # example_custom_folder()
    # example_as_library()
    
    print("""
To run examples, uncomment them in the script or run:
  python -m document_summarizer.main --help

Remember to set your API key:
  export OPENROUTER_API_KEY=your_key_here

Get free API key from: https://openrouter.ai/
    """)
