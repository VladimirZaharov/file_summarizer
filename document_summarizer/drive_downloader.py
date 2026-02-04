"""
Google Drive file downloader module.
Handles downloading files from Google Drive folders.
"""
import os
import re
import requests
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse, parse_qs


class DriveDownloader:
    """Download files from Google Drive"""
    
    def __init__(self, download_folder: Path):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
        self.session = requests.Session()
    
    def extract_folder_id(self, url: str) -> str:
        """Extract folder ID from Google Drive URL"""
        # Try different URL patterns
        patterns = [
            r'folders/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract folder ID from URL: {url}")
    
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """
        List all files in a Google Drive folder using the Drive API.
        
        Note: This requires the Google Drive API to be enabled.
        For a simpler approach, this method provides a template.
        In production, you should use google-api-python-client library.
        """
        # This is a simplified version. In production, use Google Drive API
        # with proper authentication via OAuth2 or Service Account
        
        print(f"Note: To list files from folder {folder_id}, you need to:")
        print("1. Enable Google Drive API")
        print("2. Set up OAuth2 credentials or Service Account")
        print("3. Use google-api-python-client library")
        print("\nFor this implementation, please manually download files")
        print("or provide them in the 'downloaded_files' folder")
        
        return []
    
    def download_file(self, file_id: str, filename: str) -> Path:
        """
        Download a single file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            filename: Name to save the file as
            
        Returns:
            Path to downloaded file
        """
        url = f"https://drive.google.com/uc?id={file_id}&export=download"
        
        try:
            response = self.session.get(url, stream=True)
            
            # Handle large files with confirmation token
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    params = {'id': file_id, 'confirm': value, 'export': 'download'}
                    response = self.session.get(
                        "https://drive.google.com/uc", 
                        params=params, 
                        stream=True
                    )
                    break
            
            file_path = self.download_folder / filename
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Downloaded: {filename}")
            return file_path
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            raise
    
    def download_folder(self, folder_url: str) -> List[Path]:
        """
        Download all files from a Google Drive folder.
        
        Note: This is a template. For full functionality, use Google Drive API.
        """
        folder_id = self.extract_folder_id(folder_url)
        files = self.list_files_in_folder(folder_id)
        
        downloaded_files = []
        for file_info in files:
            file_path = self.download_file(file_info['id'], file_info['name'])
            downloaded_files.append(file_path)
        
        return downloaded_files
    
    def scan_local_folder(self) -> List[Path]:
        """
        Scan local download folder for files.
        This is a fallback method when API access is not available.
        """
        files = []
        for file_path in self.download_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                files.append(file_path)
        
        return files
