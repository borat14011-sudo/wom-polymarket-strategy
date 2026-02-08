#!/usr/bin/env python3
"""
Google Drive Uploader with OAuth Authentication
Uploads files to Google Drive and returns shareable links
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveUploader:
    def __init__(self, credentials_file='credentials.json'):
        """Initialize the Drive uploader with OAuth authentication."""
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API."""
        creds = None
        
        # Load existing token if available
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"{self.credentials_file} not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Successfully authenticated with Google Drive")
    
    def upload_file(self, file_path, folder_id=None, make_public=True):
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            folder_id: Optional folder ID to upload to
            make_public: Whether to make the file publicly accessible
            
        Returns:
            Dictionary with file info including webViewLink
        """
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            print(f"📤 Uploading {file_name} ({self._format_size(file_size)})...")
            
            # Set up file metadata
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaFileUpload(file_path, resumable=True)
            
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            print(f"✅ Uploaded: {file.get('name')} (ID: {file.get('id')})")
            
            # Make file public if requested
            if make_public:
                self._make_file_public(file.get('id'))
                print(f"🔗 Shareable link: {file.get('webViewLink')}")
            
            return file
            
        except HttpError as error:
            print(f"❌ Error uploading {file_path}: {error}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    def upload_folder(self, folder_path, drive_folder_id=None, make_public=True):
        """
        Upload all files from a local folder to Google Drive.
        
        Args:
            folder_path: Path to local folder
            drive_folder_id: Optional Drive folder ID
            make_public: Whether to make files public
            
        Returns:
            List of uploaded file info
        """
        uploaded_files = []
        
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        print(f"📁 Uploading folder: {folder_path}")
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_info = self.upload_file(file_path, drive_folder_id, make_public)
                    uploaded_files.append(file_info)
                except Exception as e:
                    print(f"⚠️  Skipped {file_path}: {e}")
                    continue
        
        print(f"✅ Uploaded {len(uploaded_files)} files")
        return uploaded_files
    
    def create_folder(self, folder_name, parent_id=None):
        """
        Create a new folder in Google Drive.
        
        Args:
            folder_name: Name of the folder to create
            parent_id: Optional parent folder ID
            
        Returns:
            Folder info dictionary
        """
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=folder_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        print(f"📂 Created folder: {folder.get('name')} (ID: {folder.get('id')})")
        return folder
    
    def _make_file_public(self, file_id):
        """Make a file publicly accessible."""
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
        except HttpError as error:
            print(f"⚠️  Could not make file public: {error}")
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def list_files(self, page_size=10):
        """List files in Google Drive."""
        try:
            results = self.service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            items = results.get('files', [])
            
            if not items:
                print('📄 No files found.')
            else:
                print('📄 Files:')
                for item in items:
                    print(f"  • {item['name']} ({item['mimeType']}) - {item['id']}")
            
            return items
            
        except HttpError as error:
            print(f"❌ Error listing files: {error}")
            raise


def main():
    """Example usage of the DriveUploader."""
    try:
        # Initialize uploader
        uploader = DriveUploader()
        
        # Example: Upload a single file
        # file_info = uploader.upload_file('example.txt')
        # print(f"File uploaded: {file_info}")
        
        # Example: List files
        # uploader.list_files()
        
        print("🚀 DriveUploader initialized successfully!")
        print("Use uploader.upload_file('path/to/file') to upload files")
        
    except Exception as e:
        print(f"❌ Failed to initialize DriveUploader: {e}")


if __name__ == '__main__':
    main()