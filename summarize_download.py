#!/usr/bin/env python3
"""
Document Summarizer with file downloading.
Downloads files from Google Drive, extracts text, then summarizes.
"""
import argparse
import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List
import requests

sys.path.insert(0, str(Path(__file__).parent))

from document_summarizer.config import Config
from document_summarizer.file_parsers import FileParserFactory
from document_summarizer.summarizer import Summarizer


def download_file(file_id: str, output_path: Path) -> bool:
    """Download file from Google Drive"""
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    
    try:
        session = requests.Session()
        response = session.get(url, stream=True)
        
        # Handle large files with confirmation
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                params = {'id': file_id, 'confirm': value, 'export': 'download'}
                response = session.get(
                    "https://drive.google.com/uc",
                    params=params,
                    stream=True
                )
                break
        
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return True
    
    except Exception as e:
        print(f"  ✗ Download error: {e}")
        return False


def summarize_files(file_ids: List[str], api_key: str, model: str = None, output_file: str = None):
    """
    Download files, extract text, and summarize.
    
    Args:
        file_ids: List of Google Drive file IDs
        api_key: OpenRouter API key
        model: Model to use
        output_file: Output file path
    """
    print(f"\n{'='*60}")
    print("GOOGLE DRIVE DOCUMENT SUMMARIZER")
    print("(Download + Parse + Summarize)")
    print(f"{'='*60}\n")
    
    print(f"Processing {len(file_ids)} files...")
    print(f"Model: {model or Config.DEFAULT_MODEL}\n")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Temporary directory: {temp_dir}\n")
    
    try:
        # Initialize summarizer
        summarizer = Summarizer(api_key=api_key, model=model)
        
        # Download and parse files
        print(f"{'='*60}")
        print("DOWNLOADING AND PARSING FILES")
        print(f"{'='*60}\n")
        
        documents = []
        for i, file_id in enumerate(file_ids, 1):
            file_id = file_id.strip()
            if not file_id:
                continue
            
            print(f"[{i}/{len(file_ids)}] Processing: {file_id}")
            
            # Download to temp file
            temp_file = temp_dir / f"file_{i}"
            
            if not download_file(file_id, temp_file):
                continue
            
            # Try to detect file type from content
            try:
                # Try common extensions
                for ext in ['.pdf', '.docx', '.txt', '.html', '.xlsx']:
                    test_path = temp_dir / f"file_{i}{ext}"
                    shutil.copy(temp_file, test_path)
                    
                    try:
                        doc = FileParserFactory.parse_file(test_path)
                        if doc['content'] and len(doc['content']) > 50:
                            doc['file_id'] = file_id
                            doc['filename'] = f"document_{i}{ext}"
                            documents.append(doc)
                            print(f"  ✓ Parsed as {ext}: {len(doc['content'])} characters")
                            break
                    except:
                        continue
                else:
                    # Fallback: treat as text
                    doc = FileParserFactory.parse_file(temp_file)
                    doc['file_id'] = file_id
                    doc['filename'] = f"document_{i}.txt"
                    documents.append(doc)
                    print(f"  ✓ Parsed as text: {len(doc['content'])} characters")
            
            except Exception as e:
                print(f"  ✗ Parse error: {e}")
        
        if not documents:
            print("\n❌ No documents parsed successfully\n")
            return None
        
        # Summarize documents
        print(f"\n{'='*60}")
        print("GENERATING SUMMARIES")
        print(f"{'='*60}\n")
        
        summaries = []
        for i, doc in enumerate(documents, 1):
            print(f"[{i}/{len(documents)}] Summarizing: {doc['filename']}")
            
            try:
                summarizer.summarize_document(doc)
                summaries.append(doc)
                
                if doc.get('summary_status') == 'success':
                    print(f"  ✓ Summary generated")
                    snippet = doc['summary'][:150] + "..." if len(doc['summary']) > 150 else doc['summary']
                    print(f"  Preview: {snippet}\n")
                else:
                    print(f"  ✗ {doc.get('summary', 'Unknown error')}\n")
            
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
                doc['summary'] = f"Error: {e}"
                doc['summary_status'] = 'error'
                summaries.append(doc)
        
        # Generate master summary
        print(f"{'='*60}")
        print("GENERATING MASTER SUMMARY")
        print(f"{'='*60}\n")
        
        report = summarizer.generate_structured_summary(summaries)
        report['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'model_used': summarizer.model,
            'total_files': len(file_ids),
            'method': 'download_and_parse'
        }
        
        # Print report
        print_report(report)
        
        # Save to file
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Full report saved to: {output_path}")
        
        return report
    
    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
            print(f"\n✓ Cleaned up temporary files")
        except:
            pass


def print_report(report: dict):
    """Print summary report"""
    stats = report.get('statistics', {})
    
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}")
    print(f"Total Documents: {stats.get('total_documents', 0)}")
    print(f"Successful: {stats.get('successful_summaries', 0)}")
    print(f"Failed: {stats.get('failed_summaries', 0)}")
    print(f"Total Size: {stats.get('total_size_bytes', 0):,} bytes")
    
    print(f"\n{'='*60}")
    print("MASTER SUMMARY")
    print(f"{'='*60}\n")
    print(report.get('master_summary', 'No summary available'))
    print(f"\n{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Summarize Google Drive files by downloading and parsing them',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize files by IDs
  python summarize_download.py --file-ids ID1 ID2 ID3
  
  # From a text file
  python summarize_download.py --file-list file_ids.txt
  
  # With custom model
  python summarize_download.py --file-ids ID1 ID2 --model google/gemma-2-9b-it:free

Setup:
  export OPENROUTER_API_KEY=your_key_here
  Get free key from: https://openrouter.ai/
        """
    )
    
    parser.add_argument(
        '--file-ids',
        nargs='+',
        help='List of Google Drive file IDs'
    )
    
    parser.add_argument(
        '--file-list',
        type=str,
        help='Path to text file with file IDs (one per line)'
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
        '--output',
        type=str,
        default='summary_report.json',
        help='Output JSON file (default: summary_report.json)'
    )
    
    args = parser.parse_args()
    
    # Get file IDs
    file_ids = []
    
    if args.file_list:
        file_list_path = Path(args.file_list)
        if not file_list_path.exists():
            print(f"\n❌ Error: File not found: {args.file_list}\n")
            sys.exit(1)
        
        with open(file_list_path, 'r') as f:
            file_ids = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    elif args.file_ids:
        file_ids = args.file_ids
    
    else:
        print("\n❌ Error: Must provide either --file-ids or --file-list\n")
        parser.print_help()
        sys.exit(1)
    
    if not file_ids:
        print("\n❌ Error: No file IDs provided\n")
        sys.exit(1)
    
    # Set API key
    if args.api_key:
        Config.OPENROUTER_API_KEY = args.api_key
    
    # Validate API key
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Error: {e}\n")
        print("Setup:")
        print("  1. Get free API key: https://openrouter.ai/")
        print("  2. Set: export OPENROUTER_API_KEY=your_key")
        print("  3. Or use: --api-key your_key\n")
        sys.exit(1)
    
    # Run summarization
    try:
        report = summarize_files(
            file_ids=file_ids,
            api_key=args.api_key,
            model=args.model,
            output_file=args.output
        )
        
        if report:
            print("\n✓ Complete!")
        else:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
