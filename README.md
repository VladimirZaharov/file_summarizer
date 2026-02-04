# Document Summarizer

A modular Python application that automatically summarizes documents using AI (OpenRouter API with free models). Supports both local files and direct Google Drive URLs without downloading.

## Features

- ✅ **Google Drive Integration**: Works with Google Drive URLs directly (no download needed)
- ✅ **Universal File Support**: Handles multiple document types (PDF, DOCX, TXT, HTML, Excel, RTF, Markdown, CSV)
- ✅ **Modular Architecture**: Easy to extend with new file parsers or LLM providers
- ✅ **Free AI Models**: Uses OpenRouter's free tier models (no credit card required)
- ✅ **Individual & Master Summaries**: Generates summaries for each document plus a comprehensive overview
- ✅ **Detailed Reports**: JSON output with statistics and metadata
- ✅ **Two Methods**: Google Drive API method or direct URL method

## Installation

### 1. Clone or Navigate to Repository

```bash
cd python
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Key

1. Get a free API key from [OpenRouter](https://openrouter.ai/) (no credit card required)
2. Set your API key:

```bash
# Option 1: Environment variable
export OPENROUTER_API_KEY=your_api_key_here

# Option 2: Create .env file
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Method 1: Google Drive URL (Recommended)

This method works directly with Google Drive URLs without downloading files.

#### Quick Start with Google Drive

```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY=your_key_here

# Using Google Drive API (requires one-time setup)
python summarize_gdrive.py --folder "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"

# OR using direct file IDs (for public files, no setup needed)
python summarize_gdrive.py --file-ids FILE_ID1 FILE_ID2 FILE_ID3
```

#### Google Drive API Setup

For private folders, you need to set up Google Drive API once:

1. Get free OpenRouter API key from [OpenRouter](https://openrouter.ai/)
2. Follow the [Google Drive Setup Guide](GDRIVE_SETUP.md) to get `credentials.json`
3. Run the script - browser will open for authentication (one-time)
4. Done! Future runs won't need authentication

See detailed instructions in [`GDRIVE_SETUP.md`](GDRIVE_SETUP.md).

#### Example: Practical Task

For the folder: `https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd`

```bash
# Option 1: With Google Drive API
python summarize_gdrive.py \
    --folder "https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd" \
    --credentials credentials.json \
    --output task_summary.json

# Option 2: If you know the file IDs and files are public
python summarize_gdrive.py \
    --file-ids FILE_ID1 FILE_ID2 FILE_ID3 \
    --output task_summary.json
```

### Method 2: Local Files

For local documents, use the traditional method:

1. Place your documents in the `downloaded_files` folder:

```bash
mkdir -p document_summarizer/downloaded_files
# Copy your documents there
```

2. Run the summarizer:

```bash
python -m document_summarizer.main
```

### Command Line Options

```bash
# Basic usage (uses downloaded_files folder)
python -m document_summarizer.main

# Use custom folder
python -m document_summarizer.main --folder /path/to/your/documents

# Specify output file
python -m document_summarizer.main --output my_summary.json

# Use different model
python -m document_summarizer.main --model google/gemini-flash-1.5:free

# Provide API key directly
python -m document_summarizer.main --api-key your_key_here

# Don't save to file (console only)
python -m document_summarizer.main --no-save

# Show help
python -m document_summarizer.main --help
```

### Google Drive Integration

To download files from Google Drive:

1. **Manual Method** (Recommended for simplicity):
   - Open the Google Drive folder link in your browser
   - Select all files → Right click → Download
   - Extract to `document_summarizer/downloaded_files/`

2. **Using Google Drive Downloader Script**:

```bash
python document_summarizer/utils/download_from_drive.py <folder_url>
```

Note: For full API integration, you'll need to set up Google Drive API credentials (see Advanced Usage below).

## Supported File Types

- **Documents**: PDF, DOCX, DOC, RTF, TXT, MD
- **Spreadsheets**: XLSX, XLS, CSV
- **Web**: HTML, HTM

### Adding New File Types

The modular architecture makes it easy to add new parsers:

```python
# In file_parsers.py, create a new parser class
class MyCustomParser:
    @staticmethod
    def can_parse(file_path: Path) -> bool:
        return file_path.suffix.lower() == '.mycustomtype'
    
    @staticmethod
    def parse(file_path: Path) -> str:
        # Your parsing logic here
        return extracted_text

# Register it
FileParserFactory.register_parser(MyCustomParser)
```

## Available Free Models

OpenRouter provides several free models. You can choose any of these:

- `google/gemma-2-9b-it:free` (Default)
- `google/gemini-flash-1.5:free`
- `meta-llama/llama-3.2-3b-instruct:free`
- `qwen/qwen-2-7b-instruct:free`

See [OpenRouter Models](https://openrouter.ai/models) for the latest free options.

## Project Structure

```
document_summarizer/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── main.py                  # Main orchestrator & CLI
├── drive_downloader.py      # Google Drive integration
├── file_parsers.py          # Modular file parsers
├── summarizer.py            # OpenRouter API integration
└── downloaded_files/        # Default folder for documents
```

## Output Format

The tool generates a JSON report with:

```json
{
  "master_summary": "Comprehensive summary of all documents...",
  "statistics": {
    "total_documents": 5,
    "successful_summaries": 5,
    "failed_summaries": 0,
    "total_size_bytes": 245678,
    "file_types": {
      ".pdf": 2,
      ".docx": 2,
      ".txt": 1
    }
  },
  "individual_summaries": [
    {
      "filename": "document1.pdf",
      "type": ".pdf",
      "size": 50000,
      "summary": "Summary of document1...",
      "summary_status": "success"
    }
  ],
  "metadata": {
    "generated_at": "2026-02-04T07:52:00",
    "model_used": "google/gemma-2-9b-it:free"
  }
}
```

## Advanced Usage

### Using as a Python Library

```python
from document_summarizer.main import DocumentSummarizer
from pathlib import Path

# Initialize
summarizer = DocumentSummarizer(
    api_key="your_key",
    model="google/gemini-flash-1.5:free"
)

# Run summarization
report = summarizer.run(
    folder_path=Path("my_documents"),
    output_file="output.json"
)

# Access results
print(report['master_summary'])
for doc in report['individual_summaries']:
    print(f"{doc['filename']}: {doc['summary']}")
```

### Google Drive API Setup (Optional)

For full Google Drive API integration:

1. Enable Google Drive API in Google Cloud Console
2. Create OAuth2 credentials or Service Account
3. Install additional dependencies:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

4. Update `drive_downloader.py` with your credentials

## Configuration

Edit [`config.py`](document_summarizer/config.py:1) to customize:

- Model selection
- Token limits
- Chunk sizes
- Output formats
- Supported file extensions

## Troubleshooting

### "PyPDF2 not installed" error

```bash
pip install PyPDF2
```

### "python-docx not installed" error

```bash
pip install python-docx
```

### API Rate Limits

Free tier models have rate limits. If you hit them:
- Wait a few seconds between requests
- Try a different free model
- Upgrade to a paid tier on OpenRouter

### Large Files

For very large documents:
- Files are automatically truncated to stay within token limits
- Consider splitting large documents before processing
- Use models with larger context windows

## Example: Practical Task

Given the Google Drive folder: `https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd`

1. Download files manually from the link
2. Place them in `document_summarizer/downloaded_files/`
3. Run:

```bash
export OPENROUTER_API_KEY=your_key
python -m document_summarizer.main --output task_summary.json
```

4. Check `task_summary.json` for the complete summary

## Contributing

The modular design makes it easy to extend:

- Add new file parsers in [`file_parsers.py`](document_summarizer/file_parsers.py:1)
- Add new LLM providers in [`summarizer.py`](document_summarizer/summarizer.py:1)
- Enhance downloaders in [`drive_downloader.py`](document_summarizer/drive_downloader.py:1)

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Open an issue on GitHub
