"""
Google Drive client for listing and accessing files without downloading.
Uses Google Drive API to get file URLs.
"""
import re
import os
from typing import List, Dict, Optional
from pathlib import Path


class GDriveClient:
    """Google Drive client using Drive API v3"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Drive client.
        
        Args:
            credentials_path: Path to credentials.json file
        """
        self.credentials_path = credentials_path
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            
            creds = None
            token_path = 'token.json'
            
            # Check if we have saved credentials
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If no valid credentials, let user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path or not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(
                            "credentials.json not found. Download it from Google Cloud Console:\n"
                            "1. Go to https://console.cloud.google.com/\n"
                            "2. Enable Google Drive API\n"
                            "3. Create OAuth 2.0 credentials\n"
                            "4. Download credentials.json"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            return True
            
        except ImportError:
            raise ImportError(
                "Google Drive API libraries not installed. Install with:\n"
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
    
    def extract_folder_id(self, url: str) -> str:
        """Extract folder ID from Google Drive URL"""
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
        List all files in a Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            List of file info dicts with id, name, mimeType, webViewLink
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        files = []
        page_token = None
        
        while True:
            # Query files in folder
            query = f"'{folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, webViewLink, webContentLink, size)",
                pageToken=page_token
            ).execute()
            
            items = results.get('files', [])
            files.extend(items)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        return files
    
    def get_public_url(self, file_id: str) -> str:
        """
        Get public URL for a file.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Public URL for the file
        """
        # Use Google Drive viewer URL
        return f"https://drive.google.com/uc?id={file_id}&export=download"
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get file metadata.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File metadata dict
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        file = self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, webViewLink, webContentLink, size"
        ).execute()
        
        return file
    
    def make_file_public(self, file_id: str) -> bool:
        """
        Make a file publicly accessible (requires appropriate permissions).
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            True if successful
        """
        try:
            if not self.service:
                raise RuntimeError("Not authenticated. Call authenticate() first.")
            
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            return True
        except Exception as e:
            print(f"Warning: Could not make file public: {e}")
            return False


class SimpleDriveClient:
    """
    Simplified client that works with publicly accessible Google Drive links
    without requiring authentication.
    """
    
    @staticmethod
    def extract_folder_id(url: str) -> str:
        """Extract folder ID from Google Drive URL"""
        patterns = [
            r'folders/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract folder ID from URL: {url}")
    
    @staticmethod
    def get_public_url(file_id: str, export_format: str = None) -> str:
        """
        Get public URL for a file.
        
        Args:
            file_id: Google Drive file ID
            export_format: Optional export format (e.g., 'pdf', 'txt')
            
        Returns:
            Public URL for the file
        """
        if export_format:
            return f"https://drive.google.com/uc?id={file_id}&export={export_format}"
        return f"https://drive.google.com/uc?id={file_id}"
    
    @staticmethod
    def get_view_url(file_id: str) -> str:
        """Get view URL for a file"""
        return f"https://drive.google.com/file/d/{file_id}/view"
    
    @staticmethod
    def create_file_list_from_ids(file_ids: List[str]) -> List[Dict]:
        """
        Create file list from known file IDs.
        
        Args:
            file_ids: List of Google Drive file IDs
            
        Returns:
            List of file info dicts
        """
        files = []
        for file_id in file_ids:
            files.append({
                'id': file_id,
                'name': f"file_{file_id}",
                'url': SimpleDriveClient.get_public_url(file_id),
                'view_url': SimpleDriveClient.get_view_url(file_id)
            })
        return files
