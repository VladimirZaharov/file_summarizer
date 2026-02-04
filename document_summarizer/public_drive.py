"""
Public Google Drive folder parser.
Works with public folders without authentication.
"""
import re
import requests
from typing import List, Dict
from bs4 import BeautifulSoup


class PublicDriveParser:
    """Parse public Google Drive folders without authentication"""
    
    def __init__(self):
        self.session = requests.Session()
        # Mimic browser headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
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
    
    def get_files_from_public_folder(self, folder_url: str) -> List[Dict]:
        """
        Get list of files from public Google Drive folder.
        
        Args:
            folder_url: Public Google Drive folder URL
            
        Returns:
            List of file dicts with id, name, and url
        """
        folder_id = self.extract_folder_id(folder_url)
        
        # Try to fetch folder page
        try:
            # Use the folder view URL
            view_url = f"https://drive.google.com/drive/folders/{folder_id}"
            
            response = self.session.get(view_url)
            response.raise_for_status()
            
            # Parse HTML to extract file information
            files = self._parse_folder_html(response.text, folder_id)
            
            if not files:
                print("\n⚠️  Could not parse files from HTML.")
                print("Alternative method: Provide file IDs manually")
                print("\nTo get file IDs:")
                print(f"1. Open folder in browser: {view_url}")
                print("2. Click on each file")
                print("3. Copy ID from URL: https://drive.google.com/file/d/FILE_ID/view")
                print("\nThen run:")
                print("python summarize_gdrive.py --file-ids ID1 ID2 ID3\n")
            
            return files
            
        except Exception as e:
            print(f"Error accessing public folder: {e}")
            print("\nMake sure the folder is publicly accessible (Anyone with the link can view)")
            return []
    
    def _parse_folder_html(self, html: str, folder_id: str) -> List[Dict]:
        """
        Parse Google Drive folder HTML to extract file information.
        
        Note: This is fragile and may break if Google changes their HTML structure.
        """
        files = []
        
        try:
            # Look for file IDs in the HTML
            # Google Drive embeds file data in JavaScript
            
            # Pattern to find file IDs
            # This is a heuristic approach - may need adjustment
            file_id_pattern = r'"([a-zA-Z0-9_-]{25,})"'
            potential_ids = re.findall(file_id_pattern, html)
            
            # Filter to unique IDs that look like file IDs
            unique_ids = list(set([
                id for id in potential_ids 
                if len(id) >= 25 and len(id) <= 50 and id != folder_id
            ]))
            
            # Try to find file names in proximity to IDs
            for file_id in unique_ids[:20]:  # Limit to first 20 to avoid false positives
                # Create file entry
                files.append({
                    'id': file_id,
                    'name': f'file_{file_id[:8]}',  # Use partial ID as name
                    'url': f'https://drive.google.com/uc?id={file_id}',
                    'view_url': f'https://drive.google.com/file/d/{file_id}/view'
                })
            
        except Exception as e:
            print(f"Error parsing folder HTML: {e}")
        
        return files
    
    def create_file_dict(self, file_id: str, filename: str = None) -> Dict:
        """Create file dict from file ID"""
        return {
            'id': file_id,
            'name': filename or f'file_{file_id[:8]}',
            'url': f'https://drive.google.com/uc?id={file_id}',
            'view_url': f'https://drive.google.com/file/d/{file_id}/view'
        }
    
    @staticmethod
    def get_direct_download_url(file_id: str) -> str:
        """Get direct download URL for a file"""
        return f'https://drive.google.com/uc?id={file_id}&export=download'
    
    @staticmethod
    def get_preview_url(file_id: str) -> str:
        """Get preview URL for a file"""
        return f'https://drive.google.com/file/d/{file_id}/preview'


def get_public_file_ids_interactive(folder_url: str) -> List[str]:
    """
    Interactive helper to get file IDs from a public folder.
    Prints instructions for the user.
    """
    print("\n" + "="*60)
    print("MANUAL FILE ID EXTRACTION")
    print("="*60 + "\n")
    
    print(f"1. Open this URL in your browser:")
    print(f"   {folder_url}\n")
    
    print("2. For each file in the folder:")
    print("   - Click on the file")
    print("   - Look at the URL in your browser")
    print("   - Copy the FILE_ID from: https://drive.google.com/file/d/FILE_ID/view")
    print("   - Or right-click → Get link → Copy the ID from the link\n")
    
    print("3. Run the script with file IDs:")
    print("   python summarize_gdrive.py --file-ids ID1 ID2 ID3 ...\n")
    
    print("Alternative: Create a text file 'file_ids.txt' with one ID per line:")
    print("   ID1")
    print("   ID2")
    print("   ID3")
    print("   ...")
    print("\nThen run:")
    print("   python summarize_gdrive.py --file-list file_ids.txt\n")
    
    return []
