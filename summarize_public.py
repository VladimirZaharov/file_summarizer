#!/usr/bin/env python3
"""
Simple Google Drive Document Summarizer for public files.
No authentication required - just provide file IDs.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from document_summarizer.config import Config
from document_summarizer.url_summarizer import URLSummarizer


def get_public_url(file_id: str) -> str:
    """Get public URL for a Google Drive file"""
    return f"https://drive.google.com/uc?id={file_id}&export=download"


def summarize_files(file_ids: List[str], api_key: str, model: str = None, output_file: str = None):
    """
    Summarize Google Drive files by their IDs.
    
    Args:
        file_ids: List of Google Drive file IDs
        api_key: OpenRouter API key
        model: Model to use (optional)
        output_file: Output file path (optional)
    """
    print(f"\n{'='*60}")
    print("GOOGLE DRIVE PUBLIC FOLDER SUMMARIZER")
    print(f"{'='*60}\n")
    
    print(f"Processing {len(file_ids)} files...")
    print(f"Model: {model or Config.DEFAULT_MODEL}\n")
    
    # Initialize summarizer
    summarizer = URLSummarizer(api_key=api_key, model=model)
    
    # Process each file
    print(f"{'='*60}")
    print("GENERATING SUMMARIES")
    print(f"{'='*60}\n")
    
    summaries = []
    for i, file_id in enumerate(file_ids, 1):
        file_id = file_id.strip()
        if not file_id:
            continue
            
        print(f"[{i}/{len(file_ids)}] Processing file: {file_id}")
        
        file_url = get_public_url(file_id)
        
        try:
            summary = summarizer.summarize_document_url(
                file_url=file_url,
                filename=f"document_{i}"
            )
            summaries.append(summary)
            
            if summary['summary_status'] == 'success':
                print(f"  ✓ Summary generated")
                # Show snippet
                snippet = summary['summary'][:150] + "..." if len(summary['summary']) > 150 else summary['summary']
                print(f"  Preview: {snippet}\n")
            else:
                print(f"  ✗ Error: {summary['summary']}\n")
        
        except Exception as e:
            print(f"  ✗ Exception: {e}\n")
            summaries.append({
                'filename': f"document_{i}",
                'url': file_url,
                'file_id': file_id,
                'summary': f"Error: {e}",
                'summary_status': 'error'
            })
    
    # Generate master summary
    print(f"{'='*60}")
    print("GENERATING MASTER SUMMARY")
    print(f"{'='*60}\n")
    
    report = summarizer.generate_structured_summary(summaries)
    report['metadata'] = {
        'generated_at': datetime.now().isoformat(),
        'model_used': summarizer.model,
        'total_files': len(file_ids),
        'method': 'public_file_ids'
    }
    
    # Print results
    print_report(report)
    
    # Save to file
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Full report saved to: {output_path}")
    
    return report


def print_report(report: dict):
    """Print summary report"""
    stats = report.get('statistics', {})
    
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}")
    print(f"Total Documents: {stats.get('total_documents', 0)}")
    print(f"Successful: {stats.get('successful_summaries', 0)}")
    print(f"Failed: {stats.get('failed_summaries', 0)}")
    
    print(f"\n{'='*60}")
    print("MASTER SUMMARY")
    print(f"{'='*60}\n")
    print(report.get('master_summary', 'No summary available'))
    print(f"\n{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Summarize public Google Drive files without authentication',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize files by IDs
  python summarize_public.py --file-ids ID1 ID2 ID3
  
  # From a text file (one ID per line)
  python summarize_public.py --file-list file_ids.txt
  
  # With custom model and output
  python summarize_public.py --file-ids ID1 ID2 --model google/gemini-flash-1.5:free --output summary.json

How to get file IDs:
  1. Open Google Drive folder in browser
  2. Click on a file
  3. Copy ID from URL: https://drive.google.com/file/d/FILE_ID_HERE/view
  4. Repeat for all files

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
        
        print("\n✓ Complete!")
        
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
