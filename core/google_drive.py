from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config.settings import settings
from utils.logger import logger

class GoogleDriveUploader:
    def __init__(self):
        self.creds = Credentials(
            token=None,
            refresh_token=settings.GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def upload_file(self, file_path: str, file_name: str) -> str:
        """Upload file to Google Drive"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"File uploaded to Google Drive with ID: {file.get('id')}")
            return file.get('id')
            
        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {e}")
            return None