"""
Configuration module for document summarizer.
Manages API keys and settings.
"""
import os
from pathlib import Path


class Config:
    """Configuration class for document summarizer"""
    
    # OpenRouter API settings
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
    
    # Free model options from OpenRouter
    # You can change this to any free model available
    DEFAULT_MODEL = 'google/gemma-2-9b-it:free'  # Free tier model
    ALTERNATIVE_MODELS = [
        'meta-llama/llama-3.2-3b-instruct:free',
        'google/gemini-flash-1.5:free',
        'qwen/qwen-2-7b-instruct:free',
    ]
    
    # Google Drive settings
    DOWNLOAD_FOLDER = Path('downloaded_files')
    
    # Summarization settings
    MAX_TOKENS_PER_CHUNK = 8000  # Maximum tokens per document chunk
    SUMMARY_MAX_LENGTH = 500  # Maximum words for individual summaries
    FINAL_SUMMARY_MAX_LENGTH = 1000  # Maximum words for final summary
    
    # Supported file types
    SUPPORTED_EXTENSIONS = {
        '.txt', '.pdf', '.docx', '.doc', '.rtf', 
        '.csv', '.xlsx', '.xls', '.md', '.html'
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY not set. Please set it as an environment variable "
                "or in a .env file"
            )
        
        # Create download folder if it doesn't exist
        cls.DOWNLOAD_FOLDER.mkdir(exist_ok=True)
        
        return True
