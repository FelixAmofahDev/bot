"""
Google Drive file storage module.

Handles uploading audio files to Google Drive using OAuth2 user authentication.
Returns shareable URLs that can be stored in the database.
"""
import asyncio
import logging
import os
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# Cache for the Drive service client
_drive_service = None
SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_oauth2_credentials() -> UserCredentials:
    """
    Load or create OAuth2 user credentials.
    
    First run: Opens browser for user to authenticate
    Subsequent runs: Uses cached token.json
    """
    token_path = "token.json"
    creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
    
    if not creds_path:
        raise RuntimeError(
            "GOOGLE_DRIVE_CREDENTIALS_PATH not set. "
            "Download OAuth2 credentials from Google Cloud Console"
        )
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")
    
    creds = None
    
    # Load cached token if exists
    if os.path.exists(token_path):
        try:
            creds = UserCredentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("✅ Loaded cached OAuth2 token")
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing expired token...")
                creds.refresh(Request())
                # Save the refreshed token
                with open(token_path, "w") as token_file:
                    token_file.write(creds.to_json())
            
            return creds
        except Exception as e:
            logger.warning("Failed to load cached token: %s, re-authenticating...", e)
    
    # Create new credentials from OAuth flow
    logger.info("🔐 Starting OAuth2 authentication flow...")
    logger.info("⚠️ A browser window will open - please authorize the application")
    
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save token for future runs
    with open(token_path, "w") as token_file:
        token_file.write(creds.to_json())
    
    logger.info("✅ OAuth2 authentication successful! Token saved for future use")
    return creds


def _get_drive_service():
    """
    Lazily initialize and cache the Google Drive service client.
    Thread-safe for use with asyncio.to_thread.
    """
    global _drive_service
    
    if _drive_service is None:
        creds = _get_oauth2_credentials()
        _drive_service = build("drive", "v3", credentials=creds)
        logger.info("✅ Google Drive service initialized")
    
    return _drive_service


def _upload_file_sync(file_path: str, file_name: str, folder_id: Optional[str] = None) -> str:
    """
    Synchronous wrapper for Google Drive upload.
    
    Args:
        file_path: Local path to the audio file
        file_name: Name to give the file on Google Drive
        folder_id: Optional Google Drive folder ID to upload to
    
    Returns:
        Shareable URL to the uploaded file
    
    Raises:
        FileNotFoundError: If local file doesn't exist
        HttpError: If Drive API call fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    service = _get_drive_service()
    logger.info("📤 Starting upload to Google Drive: %s (file_path: %s)", file_name, file_path)
    
    try:
        # Prepare file metadata
        file_metadata = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]
            logger.info("📁 Uploading to folder: %s", folder_id)
        else:
            logger.info("📁 Uploading to root folder (no folder_id specified)")
        
        # Upload file with MediaFileUpload for proper streaming
        media = MediaFileUpload(file_path, resumable=True)
        logger.info("📨 Calling Google Drive API...")
        drive_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        file_id = drive_file.get("id")
        logger.info("✅ Upload successful! File ID: %s", file_id)
        
        # Make file publicly accessible (anyone with link can view)
        logger.info("🔓 Making file public...")
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        logger.info("✅ File is now publicly accessible")
        
        # Generate shareable link
        shareable_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        logger.info("✅ Shareable URL: %s", shareable_url)
        return shareable_url
        
    except HttpError as e:
        logger.error("❌ Google Drive API HTTP error: %s", e)
        raise
    except Exception as e:
        logger.error("❌ Failed to upload to Google Drive: %s", e)
        raise


async def upload_file_to_drive(
    file_path: str,
    file_name: str,
    folder_id: Optional[str] = None
) -> str:
    """
    Async wrapper for uploading a file to Google Drive.
    
    This function runs the blocking Google Drive API calls in a thread pool,
    allowing the async bot to remain responsive.
    
    Args:
        file_path: Local path to the audio file
        file_name: Name to give the file on Google Drive
        folder_id: Optional Google Drive folder ID to upload to
    
    Returns:
        Shareable URL to the uploaded file
    
    Raises:
        FileNotFoundError: If local file doesn't exist
        HttpError: If Drive API call fails
        RuntimeError: If credentials not configured
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _upload_file_sync,
        file_path,
        file_name,
        folder_id
    )
