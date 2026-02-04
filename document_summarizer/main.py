"""
Main orchestrator for document summarization.
Coordinates downloading, parsing, and summarizing documents.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from .config import Config
from .drive_downloader import DriveDownloader
from .file_parsers import FileParserFactory
from .summarizer import Summarizer


class DocumentSummarizer:
    """Main orchestrator class"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the document summarizer.
        
        Args:
            api_key: OpenRouter API key (optional, can use env var)
            model: Model to use (optional, uses default from config)
        """
        self.config = Config
        self.downloader = DriveDownloader(Config.DOWNLOAD_FOLDER)
        self.summarizer = Summarizer(api_key=api_key, model=model)
    
    def process_local_files(self, folder_path: Path = None) -> List[Dict]:
        """
        Process files from a local folder.
        
        Args:
            folder_path: Path to folder with files (default: downloaded_files)
            
        Returns:
            List of parsed documents
        """
        folder = Path(folder_path) if folder_path else self.config.DOWNLOAD_FOLDER
        
        if not folder.exists():
            print(f"Folder not found: {folder}")
            return []
        
        files = list(folder.iterdir())
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        if not files:
            print(f"No files found in {folder}")
            return []
        
        print(f"\nFound {len(files)} files to process")
        
        parsed_documents = []
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] Parsing: {file_path.name}")
            
            try:
                document = FileParserFactory.parse_file(file_path)
                
                # Check if content was successfully extracted
                if document['content'] and not document['content'].startswith('Error'):
                    print(f"  ✓ Extracted {len(document['content'])} characters")
                    parsed_documents.append(document)
                else:
                    print(f"  ⚠ {document['content']}")
                    # Still add it, but mark it
                    document['parse_status'] = 'warning'
                    parsed_documents.append(document)
            
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        return parsed_documents
    
    def summarize_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Generate summaries for all documents.
        
        Args:
            documents: List of parsed documents
            
        Returns:
            List of documents with summaries
        """
        print(f"\n{'='*60}")
        print("GENERATING SUMMARIES")
        print(f"{'='*60}\n")
        
        for i, doc in enumerate(documents, 1):
            print(f"[{i}/{len(documents)}] Summarizing: {doc['filename']}")
            
            try:
                self.summarizer.summarize_document(doc)
                
                if doc.get('summary_status') == 'success':
                    print(f"  ✓ Summary generated ({len(doc['summary'])} characters)")
                else:
                    print(f"  ✗ {doc.get('summary', 'Unknown error')}")
            
            except Exception as e:
                print(f"  ✗ Error: {e}")
                doc['summary'] = f"Error: {e}"
                doc['summary_status'] = 'error'
        
        return documents
    
    def generate_report(self, summaries: List[Dict], output_file: str = None) -> Dict:
        """
        Generate final summary report.
        
        Args:
            summaries: List of documents with summaries
            output_file: Optional file to save report to
            
        Returns:
            Structured summary report
        """
        print(f"\n{'='*60}")
        print("GENERATING MASTER SUMMARY")
        print(f"{'='*60}\n")
        
        report = self.summarizer.generate_structured_summary(summaries)
        
        # Add metadata
        report['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'model_used': self.summarizer.model,
        }
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Report saved to: {output_path}")
        
        return report
    
    def run(self, folder_path: Path = None, output_file: str = None) -> Dict:
        """
        Run the complete summarization pipeline.
        
        Args:
            folder_path: Path to folder with documents
            output_file: Optional file to save report to
            
        Returns:
            Complete summary report
        """
        print(f"\n{'='*60}")
        print("DOCUMENT SUMMARIZER")
        print(f"{'='*60}\n")
        print(f"Model: {self.summarizer.model}")
        
        # Step 1: Parse files
        documents = self.process_local_files(folder_path)
        
        if not documents:
            print("\n⚠ No documents to process. Exiting.")
            return {}
        
        # Step 2: Generate summaries
        summaries = self.summarize_documents(documents)
        
        # Step 3: Generate master summary
        report = self.generate_report(summaries, output_file)
        
        # Print results
        self.print_summary_report(report)
        
        return report
    
    def print_summary_report(self, report: Dict):
        """Print summary report to console"""
        print(f"\n{'='*60}")
        print("SUMMARY REPORT")
        print(f"{'='*60}\n")
        
        stats = report.get('statistics', {})
        print(f"Total Documents: {stats.get('total_documents', 0)}")
        print(f"Successful Summaries: {stats.get('successful_summaries', 0)}")
        print(f"Failed Summaries: {stats.get('failed_summaries', 0)}")
        print(f"Total Size: {stats.get('total_size_bytes', 0):,} bytes")
        
        print("\nFile Types:")
        for ftype, count in stats.get('file_types', {}).items():
            print(f"  {ftype}: {count}")
        
        print(f"\n{'='*60}")
        print("MASTER SUMMARY")
        print(f"{'='*60}\n")
        print(report.get('master_summary', 'No summary available'))
        print(f"\n{'='*60}\n")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Summarize documents from a folder using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize files in default folder (downloaded_files)
  python -m document_summarizer.main
  
  # Summarize files in custom folder
  python -m document_summarizer.main --folder /path/to/documents
  
  # Save report to file
  python -m document_summarizer.main --output summary_report.json
  
  # Use specific model
  python -m document_summarizer.main --model google/gemini-flash-1.5:free
  
  # Set API key via environment variable
  export OPENROUTER_API_KEY=your_key_here
  python -m document_summarizer.main
        """
    )
    
    parser.add_argument(
        '--folder',
        type=str,
        help='Path to folder with documents (default: downloaded_files)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='summary_report.json',
        help='Output file for summary report (default: summary_report.json)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenRouter API key (or set OPENROUTER_API_KEY env var)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help=f'Model to use (default: {Config.DEFAULT_MODEL})'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save report to file'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        if args.api_key:
            Config.OPENROUTER_API_KEY = args.api_key
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        print("Please set your OpenRouter API key:")
        print("  1. Get free API key from: https://openrouter.ai/")
        print("  2. Set environment variable: export OPENROUTER_API_KEY=your_key")
        print("  3. Or use --api-key argument\n")
        sys.exit(1)
    
    # Run summarizer
    try:
        summarizer = DocumentSummarizer(
            api_key=args.api_key,
            model=args.model
        )
        
        output_file = None if args.no_save else args.output
        
        report = summarizer.run(
            folder_path=args.folder,
            output_file=output_file
        )
        
        if not report:
            sys.exit(1)
        
        print("\n✓ Summarization complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
