#!/usr/bin/env python3
"""
Gmail Service Module
Handles all Gmail API operations and actions
"""

import base64
import logging
import os
import io
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GMAIL_SCOPES, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class GmailService:
    """Service class for Gmail API operations"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.setup_gmail_api()
    
    def setup_gmail_api(self):
        """Setup Gmail API authentication"""
        try:
            # Check if credentials file exists
            if os.path.exists('token.json'):
                self.credentials = Credentials.from_authorized_user_file('token.json', GMAIL_SCOPES)
            
            # If no valid credentials available, let user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        logger.error("credentials.json not found. Please download it from Google Cloud Console.")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', GMAIL_SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())
            
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail API setup successful")
            
        except Exception as e:
            logger.error(f"Failed to setup Gmail API: {e}")
            raise
    
    def search_emails_with_pdf_attachments(self, query: str) -> List[Dict]:
        """Search for emails with PDF attachments"""
        try:
            # Search for emails with PDF attachments
            results = self.service.users().messages().list(userId='me', q=query).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails with PDF attachments")
            
            # Get full message details
            detailed_messages = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                detailed_messages.append(msg)
            
            return detailed_messages
            
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []
    
    def get_attachment_data(self, message_id: str, attachment_id: str) -> Optional[str]:
        """Get attachment data for a specific message and attachment"""
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=attachment_id
            ).execute()
            return attachment['data']
        except HttpError as error:
            logger.error(f"Error getting attachment data: {error}")
            return None
    
    def create_label_if_not_exists(self, label_name: str) -> Optional[str]:
        """Create a label if it doesn't exist and return label ID"""
        try:
            # Check if label already exists
            labels = self.service.users().labels().list(userId='me').execute()
            
            for label in labels.get('labels', []):
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(userId='me', body=label_object).execute()
            logger.info(f"Created new label: {label_name}")
            return created_label['id']
            
        except HttpError as error:
            logger.error(f"An error occurred creating label: {error}")
            return None
    
    def add_label_to_message(self, message_id: str, label_id: str):
        """Add a label to a message"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            logger.info(f"Added label to message {message_id}")
            
        except HttpError as error:
            logger.error(f"An error occurred adding label: {error}")
    
    def is_service_available(self) -> bool:
        """Check if Gmail service is properly initialized"""
        return self.service is not None 