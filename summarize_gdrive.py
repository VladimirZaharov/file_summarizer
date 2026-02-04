#!/usr/bin/env python3
"""
Google Drive Document Summarizer - Direct URL approach.
Summarizes documents from Google Drive without downloading.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from document_summarizer.config import Config
from document_summarizer.gdrive_client import GDriveClient, SimpleDriveClient
from document_summarizer.url_summarizer import URLSummarizer
from document_summarizer.public_drive import PublicDriveParser


def summarize_from_public_folder(folder_url: str, api_key: str, model: str = None) -> Dict:
    """
    Summarize documents from public Google Drive folder (no authentication needed).
    
    Args:
        folder_url: Google Drive folder URL
        api_key: OpenRouter API key
        model: Model to use for summarization
        
    Returns:
        Summary report dict
    """
    print(f"\n{'='*60}")
    print("GOOGLE DRIVE DOCUMENT SUMMARIZER (Public Folder)")
    print(f"{'='*60}\n")
    
    # Initialize parser
    parser = PublicDriveParser()
    
    # Try to get files from public folder
    print(f"Accessing public folder: {folder_url}")
    files = parser.get_files_from_public_folder(folder_url)
    
    if not files:
        print("\n⚠️  Could not automatically extract files from folder.")
        print("Please use --file-ids option with manual file IDs.")
        return {}
    
    print(f"\nFound {len(files)} files")
    
    # Initialize URL summarizer
    print(f"Initializing summarizer (Model: {model or Config.DEFAULT_MODEL})...")
    summarizer = URLSummarizer(api_key=api_key, model=model)
    
    # Summarize each file
    print(f"\n{'='*60}")
    print("GENERATING SUMMARIES")
    print(f"{'='*60}\n")
    
    summaries = []
    for i, file in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Processing: {file['name']}")
        
        try:
            summary = summarizer.summarize_document_url(
                file_url=file['url'],
                filename=file['name']
            )
            summaries.append(summary)
            
            if summary['summary_status'] == 'success':
                print(f"  ✓ Summary generated")
            else:
                print(f"  ✗ {summary['summary']}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            summaries.append({
                'filename': file['name'],
                'url': file['url'],
                'summary': f"Error: {e}",
                'summary_status': 'error'
            })
    
    # Generate master summary
    print(f"\n{'='*60}")
    print("GENERATING MASTER SUMMARY")
    print(f"{'='*60}\n")
    
    report = summarizer.generate_structured_summary(summaries)
    report['metadata'] = {
        'generated_at': datetime.now().isoformat(),
        'model_used': summarizer.model,
        'folder_url': folder_url,
        'method': 'public_folder_auto'
    }
    
    return report


def summarize_from_drive_api(folder_url: str, api_key: str, model: str = None, credentials_path: str = None) -> Dict:
    """
    Summarize documents using Google Drive API (requires authentication).
    
    Args:
        folder_url: Google Drive folder URL
        api_key: OpenRouter API key
        model: Model to use for summarization
        credentials_path: Path to Google Drive credentials.json
        
    Returns:
        Summary report dict
    """
    print(f"\n{'='*60}")
    print("GOOGLE DRIVE DOCUMENT SUMMARIZER (API Method)")
    print(f"{'='*60}\n")
    
    # Initialize Drive client
    drive = GDriveClient(credentials_path=credentials_path)
    
    print("Authenticating with Google Drive...")
    drive.authenticate()
    
    # Extract folder ID
    folder_id = drive.extract_folder_id(folder_url)
    print(f"Folder ID: {folder_id}")
    
    # List files
    print("\nListing files in folder...")
    files = drive.list_files_in_folder(folder_id)
    
    if not files:
        print("No files found in folder")
        return {}
    
    print(f"Found {len(files)} files:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file['name']} ({file['mimeType']})")
    
    # Initialize URL summarizer
    print(f"\nInitializing summarizer (Model: {model or Config.DEFAULT_MODEL})...")
    summarizer = URLSummarizer(api_key=api_key, model=model)
    
    # Summarize each file
    print(f"\n{'='*60}")
    print("GENERATING SUMMARIES")
    print(f"{'='*60}\n")
    
    summaries = []
    for i, file in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Processing: {file['name']}")
        
        # Get public URL
        file_url = drive.get_public_url(file['id'])
        
        try:
            summary = summarizer.summarize_document_url(
                file_url=file_url,
                filename=file['name']
            )
            summaries.append(summary)
            
            if summary['summary_status'] == 'success':
                print(f"  ✓ Summary generated")
            else:
                print(f"  ✗ {summary['summary']}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            summaries.append({
                'filename': file['name'],
                'url': file_url,
                'summary': f"Error: {e}",
                'summary_status': 'error'
            })
    
    # Generate master summary
    print(f"\n{'='*60}")
    print("GENERATING MASTER SUMMARY")
    print(f"{'='*60}\n")
    
    report = summarizer.generate_structured_summary(summaries)
    report['metadata'] = {
        'generated_at': datetime.now().isoformat(),
        'model_used': summarizer.model,
        'folder_url': folder_url,
        'method': 'google_drive_api'
    }
    
    return report


def summarize_from_file_ids(file_ids: List[str], api_key: str, model: str = None) -> Dict:
    """
    Summarize documents using known file IDs (no authentication required if files are public).
    
    Args:
        file_ids: List of Google Drive file IDs
        api_key: OpenRouter API key
        model: Model to use for summarization
        
    Returns:
        Summary report dict
    """
    print(f"\n{'='*60}")
    print("GOOGLE DRIVE DOCUMENT SUMMARIZER (Direct URL Method)")
    print(f"{'='*60}\n")
    
    print(f"Processing {len(file_ids)} files...")
    
    # Initialize URL summarizer
    print(f"Initializing summarizer (Model: {model or Config.DEFAULT_MODEL})...")
    summarizer = URLSummarizer(api_key=api_key, model=model)
    
    # Summarize each file
    print(f"\n{'='*60}")
    print("GENERATING SUMMARIES")
    print(f"{'='*60}\n")
    
    summaries = []
    for i, file_id in enumerate(file_ids, 1):
        print(f"[{i}/{len(file_ids)}] Processing file ID: {file_id}")
        
        # Get public URL
        file_url = SimpleDriveClient.get_public_url(file_id)
        
        try:
            summary = summarizer.summarize_document_url(
                file_url=file_url,
                filename=f"file_{file_id}"
            )
            summaries.append(summary)
            
            if summary['summary_status'] == 'success':
                print(f"  ✓ Summary generated")
            else:
                print(f"  ✗ {summary['summary']}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            summaries.append({
                'filename': f"file_{file_id}",
                'url': file_url,
                'summary': f"Error: {e}",
                'summary_status': 'error'
            })
    
    # Generate master summary
    print(f"\n{'='*60}")
    print("GENERATING MASTER SUMMARY")
    print(f"{'='*60}\n")
    
    report = summarizer.generate_structured_summary(summaries)
    report['metadata'] = {
        'generated_at': datetime.now().isoformat(),
        'model_used': summarizer.model,
        'method': 'direct_file_ids'
    }
    
    return report


def print_summary_report(report: Dict):
    """Print summary report to console"""
    print(f"\n{'='*60}")
    print("SUMMARY REPORT")
    print(f"{'='*60}\n")
    
    stats = report.get('statistics', {})
    print(f"Total Documents: {stats.get('total_documents', 0)}")
    print(f"Successful Summaries: {stats.get('successful_summaries', 0)}")
    print(f"Failed Summaries: {stats.get('failed_summaries', 0)}")
    
    print(f"\n{'='*60}")
    print("MASTER SUMMARY")
    print(f"{'='*60}\n")
    print(report.get('master_summary', 'No summary available'))
    print(f"\n{'='*60}\n")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Summarize documents from Google Drive using URLs (no download)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using Google Drive API (requires credentials.json)
  python summarize_gdrive.py --folder "https://drive.google.com/drive/folders/FOLDER_ID" \\
      --credentials credentials.json
  
  # Using direct file IDs (for public files, no auth needed)
  python summarize_gdrive.py --file-ids FILE_ID1 FILE_ID2 FILE_ID3
  
  # Specify model
  python summarize_gdrive.py --folder "https://..." --model google/gemini-flash-1.5:free
  
  # Save report
  python summarize_gdrive.py --folder "https://..." --output summary.json
  
Set API key:
  export OPENROUTER_API_KEY=your_key_here
        """
    )
    
    parser.add_argument(
        '--folder',
        type=str,
        help='Google Drive folder URL'
    )
    
    parser.add_argument(
        '--file-ids',
        nargs='+',
        help='List of Google Drive file IDs (for public files)'
    )
    
    parser.add_argument(
        '--credentials',
        type=str,
        help='Path to Google Drive credentials.json (for API method)'
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
        default='gdrive_summary.json',
        help='Output file for summary report (default: gdrive_summary.json)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save report to file'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.folder and not args.file_ids:
        print("\n❌ Error: Must provide either --folder or --file-ids\n")
        parser.print_help()
        sys.exit(1)
    
    # Set API key
    if args.api_key:
        Config.OPENROUTER_API_KEY = args.api_key
    
    # Validate API key
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        print("Please set your OpenRouter API key:")
        print("  1. Get free API key from: https://openrouter.ai/")
        print("  2. Set environment variable: export OPENROUTER_API_KEY=your_key")
        print("  3. Or use --api-key argument\n")
        sys.exit(1)
    
    # Run summarization
    try:
        if args.folder:
            # Use Google Drive API method
            report = summarize_from_drive_api(
                folder_url=args.folder,
                api_key=args.api_key,
                model=args.model,
                credentials_path=args.credentials
            )
        else:
            # Use direct file IDs method
            report = summarize_from_file_ids(
                file_ids=args.file_ids,
                api_key=args.api_key,
                model=args.model
            )
        
        if not report:
            sys.exit(1)
        
        # Print report
        print_summary_report(report)
        
        # Save to file
        if not args.no_save:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✓ Report saved to: {output_path}\n")
        
        print("✓ Summarization complete!")
        
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
